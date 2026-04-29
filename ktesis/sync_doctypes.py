import json
import os
import frappe
from frappe.modules.import_file import import_file_by_path

def sync():
	doctype_dir = frappe.get_app_path("ktesis", "ktesis", "doctype")
	for folder in os.listdir(doctype_dir):
		folder_path = os.path.join(doctype_dir, folder)
		json_path = os.path.join(folder_path, f"{folder}.json")
		if os.path.isdir(folder_path) and os.path.exists(json_path):
			print(f"Importing {folder} ...")
			try:
				import_file_by_path(json_path, force=True)
				print(f"  -> OK")
			except Exception as e:
				print(f"  -> ERROR: {e}")
	frappe.db.commit()

if __name__ == "__main__":
	sync()
