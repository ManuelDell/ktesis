import frappe
from frappe import _

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/ktesis"
		raise frappe.Redirect

	boot = {
		"user": frappe.session.user,
		"csrf_token": frappe.local.session.data.csrf_token
		if hasattr(frappe.local.session, "data") and frappe.local.session.data
		else "",
		"site_name": frappe.local.site,
	}
	context.boot = boot
