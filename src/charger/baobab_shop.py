import json


def charger_baobab(chemin, journal) -> list[dict]:
    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)

    items = data["items"]

    if len(items) != data["count"]:
        journal.append(("Baobab Shop", "-", "count différent du nombre d'articles", "aucune"))

    resultats = []
    for item in items:
        sku = item.get("sku")
        titre = item.get("title")
        pricing = item.get("pricing", {})
        montant = pricing.get("amount")
        livraison = pricing.get("delivery_fee", 0)
        stock = item.get("stock", 0)

        if montant is None:
            prix_paye = None
            journal.append(("Baobab Shop", sku, "prix null", "prix_paye = None"))
        else:
            prix_paye = montant + livraison

        disponible = stock > 0

        ligne = {
            "enseigne": "Baobab Shop",
            "id_source": sku,
            "nom_brut": titre,
            "prix_paye": prix_paye,
            "disponible": disponible,
        }
        resultats.append(ligne)

    return resultats