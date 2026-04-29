import os
import frappe

def run():
	path = frappe.get_app_path("ktesis", "ktesis", "doctype")
	print("Path:", path)
	print("Exists:", os.path.exists(path))
	if os.path.exists(path):
		print("Contents:", os.listdir(path))
