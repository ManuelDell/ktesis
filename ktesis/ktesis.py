from __future__ import unicode_literals
from frappe import _


def get_data():
	return [
		{
			"label": _("Vermögen"),
			"items": [
				{
					"type": "doctype",
					"name": "Fahrzeug",
					"label": "Fahrzeug",
					"description": "Fahrzeug- und Kfz-Verwaltung"
				},
				{
					"type": "doctype",
					"name": "Wohnung",
					"label": "Wohnung",
					"description": "Immobilien und Wohnungen"
				},
				{
					"type": "doctype",
					"name": "Bankkonto",
					"label": "Bankkonto",
					"description": "Bankkonten und Kreditkarten"
				}
			]
		},
		{
			"label": _("Verträge & Finanzen"),
			"items": [
				{
					"type": "doctype",
					"name": "Vertrag",
					"label": "Vertrag",
					"description": "Vertragsverwaltung"
				},
				{
					"type": "doctype",
					"name": "Darlehen",
					"label": "Darlehen",
					"description": "Darlehen und Kredite"
				}
			]
		}
	]
