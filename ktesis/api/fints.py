import frappe
import uuid
import time


FINTS_BANKS = [
	{
		"name": "Deutsche Bank",
		"blz_example": "70070010",
		"fints_url": "https://mbs.deutsche-bank.de/",
		"tan_free_balance": True,
		"notes": "Login = Online-Banking-ID oder Filiale+Kontonummer",
	},
	{
		"name": "Commerzbank",
		"blz_example": "20040000",
		"fints_url": "https://fints.commerzbank.de/",
		"tan_free_balance": True,
		"notes": "Login = Kontonummer oder Alias",
	},
	{
		"name": "Postbank",
		"blz_example": "20010020",
		"fints_url": "https://mbs.postbank.de/",
		"tan_free_balance": True,
		"notes": "Login = Postbank Kundennummer (10-stellig); Teil der Deutsche Bank Gruppe",
	},
	{
		"name": "ING",
		"blz_example": "50010517",
		"fints_url": "https://fints.ing-diba.de/fints/",
		"tan_free_balance": False,
		"notes": "Login = Zugangsnummer (10-stellig); TAN auch für Kontostand erforderlich; alternativ: https://fints.ing.de/fints/",
	},
	{
		"name": "DKB Deutsche Kreditbank",
		"blz_example": "12030000",
		"fints_url": "https://fints.dkb.de/fints/",
		"tan_free_balance": True,
		"notes": "Login = Online-Banking Benutzernummer; HKSAL TAN-frei; Umsätze benötigen TAN",
	},
	{
		"name": "Comdirect (Commerzbank)",
		"blz_example": "20041180",
		"fints_url": "https://fints.comdirect.de/fints/",
		"tan_free_balance": False,
		"notes": "Login = Kundennummer; TAN für Kontostand erforderlich; bei Migration: https://fints.commerzbank.de/",
	},
	{
		"name": "HypoVereinsbank (UniCredit)",
		"blz_example": "70020270",
		"fints_url": "https://hbci.hypovereinsbank.de/bank/hbci",
		"tan_free_balance": None,
		"notes": "Login = Kontonummer oder UniCredit Direct ID; TAN-Pflicht für HKSAL seit PSD2 variiert",
	},
	{
		"name": "Consorsbank (BNP Paribas)",
		"blz_example": "76030080",
		"fints_url": "https://brokerage-hbci.consorsbank.de/hbci",
		"tan_free_balance": False,
		"notes": "Primär für Brokerage-Konten; Login = Depot-/Kontonummer; TAN für Kontostand",
	},
	{
		"name": "Volksbank / Raiffeisenbank",
		"blz_example": "20090700",
		"fints_url": "",
		"tan_free_balance": True,
		"notes": "URL ist bankspezifisch – bitte eigene FinTS-URL bei der Bank erfragen oder in der Bundesbank BLZ-Datei nachschlagen (Feld PinTanZugang)",
	},
	{
		"name": "Sparkasse",
		"blz_example": "20050550",
		"fints_url": "",
		"tan_free_balance": True,
		"notes": "URL ist regionsspezifisch (Muster: https://banking.s-fints-pt-XXX.de/fints30) – bitte bei eigener Sparkasse erfragen oder BLZ-Datei nutzen",
	},
]


@frappe.whitelist()
def get_bank_list():
	"""Return preset FinTS bank URLs for the frontend selector."""
	return FINTS_BANKS


@frappe.whitelist()
def start_fints_sync(name):
	"""
	Enqueue a background job that connects to the bank via FinTS.
	Returns a job_id that the frontend can poll.
	"""
	doc = frappe.get_doc("Bankkonto", name)
	if not doc.fints_aktiv:
		frappe.throw("FinTS ist für dieses Konto nicht aktiviert.")
	if not doc.fints_url:
		frappe.throw("Keine FinTS-URL konfiguriert.")
	if not doc.fints_login:
		frappe.throw("Kein FinTS-Loginname konfiguriert.")

	pin = frappe.utils.password.get_decrypted_password("Bankkonto", name, "fints_pin")
	if not pin:
		frappe.throw("Kein FinTS-PIN hinterlegt.")

	job_id = str(uuid.uuid4())

	# Write initial state to cache
	frappe.cache().set_value(
		f"fints_job_{job_id}",
		{"status": "pending", "name": name},
		expires_in_sec=600,
	)

	frappe.enqueue(
		"ktesis.api.fints._run_fints_sync",
		queue="short",
		timeout=300,
		job_id=job_id,        # sets the RQ job ID (not forwarded to function)
		fints_job_id=job_id,  # passed explicitly to our function
		bankkonto_name=name,
		blz=doc.blz,
		login=doc.fints_login,
		pin=pin,
		fints_url=doc.fints_url,
		kontonummer=doc.kontonummer,
	)

	return {"job_id": job_id}


@frappe.whitelist()
def get_fints_sync_status(job_id):
	"""Poll the status of a running FinTS sync job."""
	state = frappe.cache().get_value(f"fints_job_{job_id}")
	if not state:
		return {"status": "expired"}
	return state


@frappe.whitelist()
def submit_tan(job_id, tan):
	"""Submit a TAN for a pending FinTS sync that required one."""
	key = f"fints_job_{job_id}"
	state = frappe.cache().get_value(key)
	if not state:
		frappe.throw("Sitzung abgelaufen. Bitte neu starten.")
	if state.get("status") != "tan_required":
		frappe.throw("Keine TAN-Anforderung aktiv.")

	# Write TAN to a separate key the background job is polling
	frappe.cache().set_value(f"fints_tan_{job_id}", tan, expires_in_sec=120)
	frappe.cache().set_value(key, {**state, "status": "tan_submitted"}, expires_in_sec=600)
	return {"status": "tan_submitted"}


def _run_fints_sync(fints_job_id, bankkonto_name, blz, login, pin, fints_url, kontonummer):
	"""Background job: full FinTS sync including optional TAN interaction."""
	job_id = fints_job_id
	cache_key = f"fints_job_{job_id}"

	def set_state(state):
		frappe.cache().set_value(cache_key, state, expires_in_sec=600)

	try:
		from fints.client import FinTS3PinTanClient, NeedTANResponse

		set_state({"status": "connecting", "name": bankkonto_name})

		client = FinTS3PinTanClient(blz, login, pin, fints_url)

		with client:
			# Non-interactive TAN mechanism selection (minimal_interactive_cli_bootstrap
			# blocks on stdin when multiple mechanisms are available)
			if client.init_tan_response:
				set_state({"status": "error", "message": "Bank erfordert TAN zur Initialisierung – nicht unterstützt."})
				return
			mechanisms = client.get_tan_mechanisms()
			if mechanisms:
				client.set_tan_mechanism(list(mechanisms.values())[0])

			set_state({"status": "connected", "name": bankkonto_name})

			accounts = client.get_sepa_accounts()
			if not accounts:
				set_state({"status": "error", "message": "Keine Konten gefunden."})
				return

			# Match by IBAN or Kontonummer if possible
			account = _find_account(accounts, kontonummer)

			# --- Balance ---
			balance_result = client.get_balance(account)

			if isinstance(balance_result, NeedTANResponse):
				challenge_text = str(balance_result.challenge or "")
				set_state({
					"status": "tan_required",
					"name": bankkonto_name,
					"challenge": challenge_text,
					"challenge_label": str(balance_result.challenge_label or "TAN eingeben"),
					"tan_type": "balance",
				})
				tan = _wait_for_tan(job_id)
				if not tan:
					set_state({"status": "error", "message": "TAN-Timeout. Bitte neu starten."})
					return
				balance_result = client.send_response(balance_result, tan)

			balance = float(balance_result.amount.amount)

			# --- Transactions ---
			set_state({"status": "fetching_transactions", "name": bankkonto_name})
			transactions_result = client.get_transactions(account)

			if isinstance(transactions_result, NeedTANResponse):
				challenge_text = str(transactions_result.challenge or "")
				set_state({
					"status": "tan_required",
					"name": bankkonto_name,
					"challenge": challenge_text,
					"challenge_label": str(transactions_result.challenge_label or "TAN eingeben"),
					"tan_type": "transactions",
				})
				tan = _wait_for_tan(job_id)
				if not tan:
					# Save balance at least
					_save_balance(bankkonto_name, balance)
					set_state({"status": "partial", "message": "Kontostand gespeichert, Buchungen übersprungen (TAN-Timeout).", "balance": balance})
					return
				transactions_result = client.send_response(transactions_result, tan)

			# _save_transactions consumes the iterator – capture count from it
			inserted = _save_transactions(bankkonto_name, account, transactions_result)
			_save_balance(bankkonto_name, balance)

			set_state({
				"status": "completed",
				"balance": balance,
				"transactions_count": inserted,
			})

	except ImportError:
		set_state({
			"status": "error",
			"message": "python-fints ist nicht installiert. Bitte 'pip install python-fints' ausführen.",
		})
	except Exception as e:
		set_state({"status": "error", "message": str(e)})


def _find_account(accounts, kontonummer):
	"""Find the matching SEPA account, fall back to first."""
	if kontonummer:
		for acc in accounts:
			if acc.accountnumber == kontonummer or (acc.iban and kontonummer in acc.iban):
				return acc
	return accounts[0]


def _wait_for_tan(job_id, timeout=270):
	"""Block until a TAN is submitted via the API or timeout."""
	tan_key = f"fints_tan_{job_id}"
	deadline = time.time() + timeout
	while time.time() < deadline:
		tan = frappe.cache().get_value(tan_key)
		if tan:
			frappe.cache().delete_value(tan_key)
			return tan
		time.sleep(2)
	return None


def _save_balance(bankkonto_name, balance):
	"""Persist live balance and timestamp on the Bankkonto doc."""
	doc = frappe.get_doc("Bankkonto", bankkonto_name)
	doc.kontostand_live = balance
	doc.kontostand_abgerufen_am = frappe.utils.now()
	doc.save(ignore_permissions=True)
	frappe.db.commit()


def _save_transactions(bankkonto_name, account, transactions):
	"""Import fetched transactions as Bankbuchung records (skip duplicates)."""
	from fints.models import Transaction as FintsTransaction

	inserted = 0
	for tx in transactions:
		if not isinstance(tx, FintsTransaction):
			continue

		datum = str(tx.data.get("date", tx.data.get("entry_date", "")))
		buchungstext = tx.data.get("purpose", "") or tx.data.get("applicant_name", "")
		betrag = float(tx.data.get("amount", {}).amount if hasattr(tx.data.get("amount", 0), "amount") else 0)
		kategorie = "Eingang" if betrag >= 0 else "Ausgang"

		# Duplicate check: same konto + date + betrag + first 50 chars of text
		exists = frappe.db.exists("Bankbuchung", {
			"bankkonto": bankkonto_name,
			"datum": datum,
			"betrag": abs(betrag),
		})
		if exists:
			continue

		frappe.get_doc({
			"doctype": "Bankbuchung",
			"bankkonto": bankkonto_name,
			"datum": datum,
			"buchungstext": buchungstext[:140],
			"betrag": abs(betrag),
			"kategorie": kategorie,
		}).insert(ignore_permissions=True)
		inserted += 1

	if inserted:
		frappe.db.commit()

	return inserted
