import csv
import os


def formater(valeur):
    if valeur is None:
        return "-"
    if isinstance(valeur, bool):
        return "oui" if valeur else "non"
    if isinstance(valeur, int):
        return f"{valeur:,}".replace(",", " ")
    if isinstance(valeur, float):
        return f"{valeur:,.1f}".replace(",", " ")
    return str(valeur)


def afficher_tableau(lignes, colonnes, largeur_max=34):
    if not lignes:
        print("Aucune donnée.")
        return
    cellules = [[formater(l.get(c))[:largeur_max] for c in colonnes] for l in lignes]
    largeurs = [max(len(c), max(len(r[i]) for r in cellules)) for i, c in enumerate(colonnes)]
    print(" | ".join(c.ljust(largeurs[i]) for i, c in enumerate(colonnes)))
    print("-+-".join("-" * w for w in largeurs))
    for r in cellules:
        print(" | ".join(v.ljust(largeurs[i]) for i, v in enumerate(r)))


def journal_en_lignes(journal):
    return [{"source": s, "id": i, "probleme": p, "action": a} for s, i, p, a in journal]


def ecrire_csv(lignes, colonnes, chemin):
    dossier = os.path.dirname(chemin)
    if dossier:
        os.makedirs(dossier, exist_ok=True)
    with open(chemin, "w", encoding="utf-8-sig", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes, delimiter=";", extrasaction="ignore")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)