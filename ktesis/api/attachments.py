import frappe


@frappe.whitelist()
def get_attachments(doctype, docname):
	"""Return files attached to a given document."""
	files = frappe.get_all(
		"File",
		filters={
			"attached_to_doctype": doctype,
			"attached_to_name": docname,
		},
		fields=["name", "file_name", "file_url", "file_size", "creation", "is_private"],
		order_by="creation desc",
	)
	return files


@frappe.whitelist()
def delete_attachment(name):
	"""Delete a file by name."""
	frappe.delete_doc("File", name, ignore_permissions=False)
	return {"status": "ok"}
