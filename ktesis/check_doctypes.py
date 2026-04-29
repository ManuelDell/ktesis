import frappe

def check():
	rows = frappe.db.sql("SELECT name FROM `tabDocType` WHERE module='Ktesis'", as_list=True)
	print("DocTypes in Ktesis:")
	for r in rows:
		print(" -", r[0])

if __name__ == "__main__":
	check()
