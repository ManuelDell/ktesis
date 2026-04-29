import json
import os
import frappe

def sync():
	doctype_dir = frappe.get_app_path("ktesis", "doctype")
	order = ["abschreibung", "fahrzeug", "wohnung", "darlehen", "bankkonto", "vertrag"]
	for folder in order:
		folder_path = os.path.join(doctype_dir, folder)
		json_path = os.path.join(folder_path, f"{folder}.json")
		if not os.path.exists(json_path):
			print(f"Missing {json_path}")
			continue
		if frappe.db.exists("DocType", folder.capitalize() if folder != "abschreibung" else "Abschreibung"):
			print(f"Skipping {folder} (already exists)")
			continue
		print(f"Processing {folder} ...")
		with open(json_path, "r") as f:
			data = json.load(f)
		if data.get("doctype") != "DocType":
			print(f"  -> Not a DocType JSON, skipping")
			continue
		try:
			doc = frappe.get_doc(data)
			doc.insert(ignore_permissions=True)
			print(f"  -> OK")
		except Exception as e:
			print(f"  -> ERROR: {e}")
	frappe.db.commit()

if __name__ == "__main__":
	sync()
