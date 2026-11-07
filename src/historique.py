import csv

BF_DEBUT = "2025-11-24"
BF_FIN = "2025-11-30"


def lire_historique(chemin):
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        return [(l["date"], l["source"], l["produit_id"], int(l["prix_fcfa"]))
                for l in csv.DictReader(f)]


def construire_ligne(source, pid, total, nb, total_bf, nb_bf):
    moyenne = total / nb
    moyenne_bf = total_bf / nb_bf if nb_bf else None
    variation = None
    if moyenne_bf is not None:
        variation = round((moyenne_bf - moyenne) / moyenne * 100, 1)
    return {
        "source": source,
        "produit_id": pid,
        "prix_moyen": round(moyenne),
        "prix_moyen_bf": round(moyenne_bf) if moyenne_bf is not None else None,
        "variation_pct": variation,
    }


def analyser(lignes):
    stats = {}
    for date, source, pid, prix in lignes:
        s = stats.setdefault((source, pid), [0, 0, 0, 0])
        s[0] += prix
        s[1] += 1
        if BF_DEBUT <= date <= BF_FIN:
            s[2] += prix
            s[3] += 1
    return [construire_ligne(source, pid, *s) for (source, pid), s in sorted(stats.items())]


def analyser_naif(lignes):
    cles = sorted({(l[1], l[2]) for l in lignes})
    resultat = []
    for source, pid in cles:
        prix = [l[3] for l in lignes if l[1] == source and l[2] == pid]
        prix_bf = [l[3] for l in lignes
                   if l[1] == source and l[2] == pid and BF_DEBUT <= l[0] <= BF_FIN]
        resultat.append(construire_ligne(source, pid, sum(prix), len(prix),
                                         sum(prix_bf), len(prix_bf)))
    return resultat


def resume_par_source(stats):
    groupes = {}
    for ligne in stats:
        groupes.setdefault(ligne["source"], []).append(ligne)
    resume = []
    for source, lignes in groupes.items():
        valeurs = [l["variation_pct"] for l in lignes if l["variation_pct"] is not None]
        moyenne = round(sum(valeurs) / len(valeurs), 1) if valeurs else None
        if moyenne is not None and moyenne < -1:
            verdict = "Acheter pendant le Black Friday"
        else:
            verdict = "Pas de promotion au Black Friday"
        resume.append({
            "source": source,
            "produits": len(lignes),
            "variation_bf_pct": moyenne,
            "moins_chers_en_bf": sum(1 for v in valeurs if v < 0),
            "verdict": verdict,
        })
    return resume