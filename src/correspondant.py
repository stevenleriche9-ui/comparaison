import csv
from collections import Counter
from src.normalise import normaliser

SEUIL = 0.4
MARGE = 0.15


def charger_catalogue(chemin):
    catalogue = {}
    index = {}
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        for ligne in csv.DictReader(f):
            pid = ligne["produit_id"].strip()
            mots = normaliser(ligne["nom"])
            catalogue[pid] = mots
            for mot in mots:
                index.setdefault(mot, []).append(pid)
    return catalogue, index


def trouver_produit(nom, catalogue, index):
    mots = normaliser(nom)
    communs = Counter()
    for mot in mots:
        for pid in index.get(mot, []):
            communs[pid] += 1

    scores = []
    for pid, nb in communs.items():
        union = len(mots) + len(catalogue[pid]) - nb
        scores.append((nb / union, pid))
    scores.sort(reverse=True)

    if not scores:
        return None, 0
    meilleur, pid = scores[0]
    second = scores[1][0] if len(scores) > 1 else 0
    if meilleur >= SEUIL and meilleur - second >= MARGE:
        return pid, meilleur
    return None, meilleur


def rapprocher(lignes, catalogue, index, journal):
    for ligne in lignes:
        pid, score = trouver_produit(ligne["nom_brut"], catalogue, index)
        ligne["produit_id"] = pid
        if pid is None:
            journal.append((ligne["enseigne"], ligne["id_source"],
                            "article non rapproché", "à vérifier"))
        elif score < 0.7:
            journal.append((ligne["enseigne"], ligne["id_source"],
                            f"rapprochement partiel ({score:.2f}) vers {pid}", "conservé"))
    return lignes