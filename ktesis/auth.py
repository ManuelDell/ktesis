import frappe
from frappe import _


def get_home_page(user):
    """Return None to let Frappe use the default desk as home page."""
    return None
