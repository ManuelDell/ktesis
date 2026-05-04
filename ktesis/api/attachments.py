import frappe


@frappe.whitelist()
def get_attachments(doctype, docname):
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
	frappe.delete_doc("File", name, ignore_permissions=False)
	return {"status": "ok"}


@frappe.whitelist()
def rename_attachment(name, new_name):
	file_doc = frappe.get_doc("File", name)
	old_name = file_doc.file_name or ""
	ext = old_name.rsplit(".", 1)[-1] if "." in old_name else ""
	new_name = new_name.strip()
	if ext and not new_name.lower().endswith("." + ext.lower()):
		new_name = f"{new_name}.{ext}"
	file_doc.file_name = new_name
	file_doc.save(ignore_permissions=True)
	return {"status": "ok", "file_name": file_doc.file_name}
