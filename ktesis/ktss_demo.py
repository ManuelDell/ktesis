import frappe

def run():
    for dt in ["Bankbuchung","Bankkonto","Fahrzeug","Wohnung","Darlehen","Vertrag","Abschreibung","Budgetposten"]:
        for doc in frappe.get_all(dt, pluck="name"):
            frappe.delete_doc(dt, doc, force=True)
    frappe.db.commit()

    k1 = frappe.get_doc({"doctype":"Bankkonto","bezeichnung":"DKB Girokonto","bank":"Deutsche Kreditbank","kontotyp":"Girokonto","kontostand_manuell":4280.55}).insert(ignore_permissions=True)
    k2 = frappe.get_doc({"doctype":"Bankkonto","bezeichnung":"ING Tagesgeld","bank":"ING-DiBa","kontotyp":"Tagesgeld","kontostand_manuell":18500.00}).insert(ignore_permissions=True)

    transactions = [
        ("2026-04-01",k1.name,"Gehalt April - Mueller GmbH",3200.00,"Einkommen"),
        ("2026-04-02",k1.name,"REWE Markt",-87.40,"Lebensmittel"),
        ("2026-04-03",k1.name,"Stadtwerke Strom",-62.00,"Wohnen"),
        ("2026-04-05",k1.name,"Miete April",-950.00,"Wohnen"),
        ("2026-04-07",k1.name,"Netflix",-17.99,"Freizeit"),
        ("2026-04-08",k1.name,"Tankstelle HEM",-68.30,"Mobilitaet"),
        ("2026-04-10",k1.name,"REWE Markt",-54.20,"Lebensmittel"),
        ("2026-04-15",k1.name,"Freelance-Rechnung Nr. 12",800.00,"Einkommen"),
        ("2026-04-18",k1.name,"Allianz Versicherung",-9.50,"Versicherung"),
        ("2026-04-20",k1.name,"ALDI Einkauf",-43.80,"Lebensmittel"),
        ("2026-04-22",k1.name,"Spotify",-9.99,"Freizeit"),
        ("2026-04-30",k1.name,"Tilgung Baufinanzierung",-780.00,"Wohnen"),
        ("2026-03-01",k1.name,"Gehalt Maerz - Mueller GmbH",3200.00,"Einkommen"),
        ("2026-03-05",k1.name,"Miete Maerz",-950.00,"Wohnen"),
        ("2026-03-10",k1.name,"REWE Markt",-91.20,"Lebensmittel"),
        ("2026-03-15",k1.name,"Tankstelle Shell",-74.50,"Mobilitaet"),
        ("2026-03-20",k1.name,"FitX Fitnessstudio",-39.90,"Freizeit"),
        ("2026-02-01",k1.name,"Gehalt Februar - Mueller GmbH",3200.00,"Einkommen"),
        ("2026-02-05",k1.name,"Miete Februar",-950.00,"Wohnen"),
        ("2026-02-12",k1.name,"REWE Markt",-78.60,"Lebensmittel"),
    ]

    for d,k,t,b,kat in transactions:
        frappe.get_doc({"doctype":"Bankbuchung","datum":d,"bankkonto":k,"buchungstext":t,"betrag":b,"buchungskategorie":kat,"kategorie":"Eingang" if b>0 else "Ausgang"}).insert(ignore_permissions=True)

    frappe.get_doc({"doctype":"Fahrzeug","kennzeichen":"M-AB-4521","hersteller":"BMW","marke":"BMW","modell":"320d Touring","baujahr":2021,"kilometerstand":42800,"anschaffungswert":38500.00}).insert(ignore_permissions=True)
    frappe.get_doc({"doctype":"Wohnung","bezeichnung":"ETW Muenchen-Schwabing","strasse":"Schleissheimer Str. 88","plz":"80797","ort":"Muenchen","wohnflaeche":72.5,"kaufpreis":485000.00,"baujahr":1998,"monatliche_nebenkosten":220.00}).insert(ignore_permissions=True)
    frappe.get_doc({"doctype":"Darlehen","bezeichnung":"Baufinanzierung Schwabing","bank":"Sparkasse Muenchen","darlehensbetrag":320000.00,"zinssatz":3.85,"laufzeit_jahre":25,"monatliche_rate":780.00,"beginn":"2022-01-01"}).insert(ignore_permissions=True)

    frappe.get_doc({"doctype":"Vertrag","titel":"Netflix Streaming","vertragstyp":"Sonstiges","vertragspartner":"Netflix","vertragsbeginn":"2022-03-01","vertragsende":"2026-08-31","kuendigungsfrist":1,"kosten_monatlich":17.99,"aktiv":1}).insert(ignore_permissions=True)
    frappe.get_doc({"doctype":"Vertrag","titel":"KFZ-Versicherung BMW","vertragstyp":"Versicherung","vertragspartner":"ADAC Versicherung AG","vertragsbeginn":"2021-10-01","vertragsende":"2026-09-30","kuendigungsfrist":3,"kosten_monatlich":89.00,"aktiv":1}).insert(ignore_permissions=True)
    frappe.get_doc({"doctype":"Vertrag","titel":"Haftpflichtversicherung","vertragstyp":"Versicherung","vertragspartner":"Allianz","vertragsbeginn":"2020-01-01","vertragsende":"2026-12-31","kuendigungsfrist":3,"kosten_monatlich":9.50,"aktiv":1}).insert(ignore_permissions=True)
    frappe.get_doc({"doctype":"Vertrag","titel":"Fitnessstudio FitX","vertragstyp":"Sonstiges","vertragspartner":"FitX GmbH","vertragsbeginn":"2025-01-01","vertragsende":"2026-05-31","kuendigungsfrist":2,"kosten_monatlich":39.90,"aktiv":1}).insert(ignore_permissions=True)

    for kat,b in [("Wohnen",1200),("Mobilitaet",150),("Versicherung",120),("Lebensmittel",400),("Freizeit",150),("Sonstiges",200)]:
        frappe.get_doc({"doctype":"Budgetposten","kategorie":kat,"betrag_monatlich":b}).insert(ignore_permissions=True)

    frappe.db.commit()
    print("OK")
