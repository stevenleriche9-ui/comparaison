import csv
import heapq

PANIER = {"P04": 1, "P12": 1, "P14": 2, "P15": 1, "P28": 1}
SEPARATEUR = " / "


def charger_noms(chemin):
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        return {l["produit_id"].strip(): l["nom"].strip() for l in csv.DictReader(f)}


def construire_prix(lignes_par_enseigne):
    prix = {}
    for enseigne, lignes in lignes_par_enseigne.items():
        for ligne in lignes:
            if ligne["produit_id"] is None:
                continue
            if ligne["prix_paye"] is None or not ligne["disponible"]:
                continue
            prix.setdefault(ligne["produit_id"], {})[enseigne] = ligne["prix_paye"]
    return prix


def comparer(prix, noms, enseignes):
    resultat = []
    for pid in sorted(prix):
        offres = prix[pid]
        if len(offres) < 2:
            continue
        minimum = min(offres.values())
        maximum = max(offres.values())
        gagnants = [e for e in enseignes if offres.get(e) == minimum]
        ligne = {"produit_id": pid, "nom": noms[pid]}
        for e in enseignes:
            ligne[e] = offres.get(e)
        ligne["moins_cher"] = SEPARATEUR.join(gagnants)
        ligne["prix_min"] = minimum
        ligne["ecart_fcfa"] = maximum - minimum
        ligne["ecart_pct"] = round((maximum - minimum) / minimum * 100, 1)
        resultat.append(ligne)
    return resultat


def synthese(comparatif, enseignes):
    victoires = {e: 0 for e in enseignes}
    ecarts = {e: [] for e in enseignes}
    for ligne in comparatif:
        for gagnant in ligne["moins_cher"].split(SEPARATEUR):
            victoires[gagnant] += 1
        for e in enseignes:
            if ligne[e] is not None:
                diff = ligne[e] - ligne["prix_min"]
                ecarts[e].append((diff, diff / ligne["prix_min"] * 100))
    moyennes = {}
    for e, valeurs in ecarts.items():
        if valeurs:
            moyennes[e] = (
                round(sum(v[0] for v in valeurs) / len(valeurs)),
                round(sum(v[1] for v in valeurs) / len(valeurs), 1),
            )
        else:
            moyennes[e] = (None, None)
    top3 = heapq.nlargest(3, comparatif, key=lambda l: l["ecart_fcfa"])
    return victoires, moyennes, top3


def calculer_panier(prix, panier, enseignes):
    par_enseigne = {}
    for e in enseignes:
        total = 0
        manquants = []
        for pid, qte in panier.items():
            p = prix.get(pid, {}).get(e)
            if p is None:
                manquants.append(pid)
            else:
                total += p * qte
        par_enseigne[e] = {
            "total": None if manquants else total,
            "manquants": manquants,
        }
    optimal = 0
    achats = {}
    for pid, qte in panier.items():
        offres = prix.get(pid)
        if not offres:
            achats[pid] = None
            continue
        e = min(offres, key=offres.get)
        achats[pid] = (e, offres[e] * qte)
        optimal += offres[e] * qte
    return par_enseigne, optimal, achats