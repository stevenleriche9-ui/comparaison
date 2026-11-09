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

def ecrire_excel(lignes, colonnes, chemin, titre="Comparatif"):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    dossier = os.path.dirname(chemin)
    if dossier:
        os.makedirs(dossier, exist_ok=True)

    classeur = Workbook()
    feuille = classeur.active
    feuille.title = titre

    trait = Side(style="thin", color="000000")
    bordure = Border(left=trait, right=trait, top=trait, bottom=trait)
    fond_entete = PatternFill("solid", start_color="D9E1F2")

    feuille.append(colonnes)
    for ligne in lignes:
        feuille.append([ligne.get(c) for c in colonnes])

    for rangee in feuille.iter_rows(min_row=1, max_row=feuille.max_row,
                                    min_col=1, max_col=len(colonnes)):
        for cellule in rangee:
            cellule.border = bordure
            cellule.font = Font(name="Arial", size=10, bold=(cellule.row == 1))
            if cellule.row == 1:
                cellule.fill = fond_entete
                cellule.alignment = Alignment(horizontal="center", vertical="center")
            elif isinstance(cellule.value, int):
                cellule.number_format = "#,##0"
            elif isinstance(cellule.value, float):
                cellule.number_format = "0.0"

    for i, colonne in enumerate(colonnes, start=1):
        largeur = max(len(str(colonne)),
                      max((len(formater(l.get(colonne))) for l in lignes), default=0))
        feuille.column_dimensions[get_column_letter(i)].width = largeur + 3

    feuille.freeze_panes = "A2"
    classeur.save(chemin)