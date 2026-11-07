import re 
from openpyxl import load_workbook

chemin = "data/original/comptoir_ivoire.xlsx"
journal = []

def en_nombre(valeur)-> float:
    if valeur is None :
        return None
    if isinstance(valeur, (int,float)):
        return float(valeur)
    chiffres = re.sub(r"\D", "", str(valeur))
    return float(chiffres) if chiffres else None

def charger_comptoir(chemin, journal)-> list [dict]:
    resultats = []
    wb = load_workbook(chemin , read_only =True,  data_only = True)
    ws = wb["Tarifs octobre 2026"]
    for ligne in ws.iter_rows(min_row=4, values_only=True):
        code, article,rayon,prix_cat,remise,quantite,date_maj =ligne[:7]
        if code is None :
            continue
        prix = en_nombre(prix_cat)
        taux = en_nombre(remise) or 0
        if prix is None :
            journal.append(("Comptoir Ivoire", code, "prix absent", "prix_pay = None"))
            prix_paye = None
        else :
            prix_paye = round(prix * (1 - taux / 100))

        disponible = (en_nombre(quantite) or 0) > 0
        resultats.append({
            "enseigne": "Comptoir Ivoire",
            "id_source": str(code).strip(),
            "nom_brut": str(article).strip(),
            "prix_paye": prix_paye,
            "disponible": disponible,
        })
    return resultats