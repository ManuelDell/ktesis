app_name = "ktesis"
app_title = "Ktesis"
app_publisher = "Dells Dienste"
app_description = "Eine Haus und Vermögensverwaltungsapp. Mit übersicht für Dokumente, Bankanbindung zum read und co."
app_email = "manuel@diedells.de"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "ktesis",
		"logo": "/assets/ktesis/logo.svg",
		"title": "Ktesis",
		"route": "/ktesis",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ktesis/css/ktesis.css"
# app_include_js = "/assets/ktesis/js/ktesis.js"

# include js, css files in header of web template
# web_include_css = "/assets/ktesis/css/ktesis.css"
# web_include_js = "/assets/ktesis/js/ktesis.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ktesis/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ktesis/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "ktesis.utils.jinja_methods",
# 	"filters": "ktesis.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ktesis.install.before_install"
after_install = "ktesis.install.after_install"

# Bench CLI Commands
# ------------------
commands = ["ktesis.commands"]

# Permissions
has_permission = {
    "Fahrzeug": "ktesis.permissions.has_ktesis_permission",
    "Wohnung": "ktesis.permissions.has_ktesis_permission",
    "Bankkonto": "ktesis.permissions.has_ktesis_permission",
    "Bankbuchung": "ktesis.permissions.has_ktesis_permission",
    "Darlehen": "ktesis.permissions.has_ktesis_permission",
    "Vertrag": "ktesis.permissions.has_ktesis_permission",
    "Abschreibung": "ktesis.permissions.has_ktesis_permission",
}


# Uninstallation
# ------------

# before_uninstall = "ktesis.uninstall.before_uninstall"
# after_uninstall = "ktesis.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ktesis.utils.before_app_install"
# after_app_install = "ktesis.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ktesis.utils.before_app_uninstall"
# after_app_uninstall = "ktesis.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ktesis.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ktesis.tasks.all"
# 	],
# 	"daily": [
# 		"ktesis.tasks.daily"
# 	],
# 	"hourly": [
# 		"ktesis.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ktesis.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ktesis.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "ktesis.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "ktesis.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ktesis.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ktesis.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ktesis.utils.before_request"]
# after_request = ["ktesis.utils.after_request"]

# Job Events
# ----------
# before_job = ["ktesis.utils.before_job"]
# after_job = ["ktesis.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ktesis.auth.validate"
# ]

# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

