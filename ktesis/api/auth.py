import frappe

def is_ktesis_admin():
    roles = frappe.get_roles()
    return "Ktesis Admin" in roles or "System Manager" in roles
