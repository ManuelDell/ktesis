import frappe


def has_ktesis_permission(doc, user=None, permission_type=None):
    """
    All logged-in users have full CRUD access to Ktesis documents.
    Guests have no access.
    """
    user = user or frappe.session.user
    if user and user != "Guest":
        return True
    return False
