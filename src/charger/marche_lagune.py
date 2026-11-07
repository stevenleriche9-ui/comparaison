import csv
import re


def nettoyer_prix(texte):
    chiffres = re.sub(r"\D", "", texte or "")
    if chiffres == "":
        return None
    return int(chiffres)


def charger_lagune(chemin, journal) -> list[dict]:
    resultats = []
    vus = set()
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        lecteur = csv.DictReader(f, delimiter=";")
        for ligne in lecteur:
            ref = ligne["reference"].strip()
            if ref in vus:
                journal.append(("Marché Lagune", ref, "doublon", "ligne ignorée"))
                continue
            vus.add(ref)

            nom = ligne["designation"].strip()
            prix = nettoyer_prix(ligne["prix"])
            ancien = nettoyer_prix(ligne["ancien_prix"])

            if prix is None:
                journal.append(("Marché Lagune", ref, "prix absent ou sur demande", "prix_paye = None"))
            elif ancien is not None and prix > 2 * ancien:
                journal.append(("Marché Lagune", ref, "prix aberrant", "prix_paye = None"))
                prix = None

            disponible = ligne["disponibilite"].strip().lower() != "rupture"

            resultats.append({
                "enseigne": "Marché Lagune",
                "id_source": ref,
                "nom_brut": nom,
                "prix_paye": prix,
                "disponible": disponible,
            })
    return resultats