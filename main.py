import time

from src.charger.baobab_shop import charger_baobab
from src.charger.marche_lagune import charger_lagune
from src.charger.comptoir_ivoire import charger_comptoir
from src.correspondant import charger_catalogue, rapprocher, trouver_produit
from src.comparaison import (charger_noms, construire_prix, comparer, synthese,
                             calculer_panier, PANIER)
from src.historique import (lire_historique, analyser, analyser_naif,
                            resume_par_source)
from src.resultats import (afficher_tableau, ecrire_csv, ecrire_excel,
                           journal_en_lignes, formater)
DOSSIER = "data/original/"
SORTIE = "sortie/"
ENSEIGNES = ["Baobab Shop", "Marché Lagune", "Comptoir Ivoire"]
COLONNES_COMPARATIF = ["produit_id", "nom"] + ENSEIGNES + ["moins_cher", "ecart_fcfa", "ecart_pct"]

MENU = """
===== COMPARATEUR DE PRIX  =====
1. Charger et nettoyer les données
2. Journal de nettoyage
3. Comparatif des prix
4. Synthèse
5. Panier de rentrée
6. Historique : Black Friday
7. Exporter les résultats en CSV
8. Mesurer les performances
9. Rechercher un produit
0. Quitter
"""


def chrono(fonction, *args):
    debut = time.perf_counter()
    resultat = fonction(*args)
    return resultat, time.perf_counter() - debut


def construire_etat():
    journal = []
    debut = time.perf_counter()
    catalogue, index = charger_catalogue(DOSSIER + "catalogue_reference.csv")
    lignes = {
        "Baobab Shop": charger_baobab(DOSSIER + "baobab_shop.json", journal),
        "Marché Lagune": charger_lagune(DOSSIER + "marche_lagune.csv", journal),
        "Comptoir Ivoire": charger_comptoir(DOSSIER + "comptoir_ivoire.xlsx", journal),
    }
    fin_chargement = time.perf_counter()
    for liste in lignes.values():
        rapprocher(liste, catalogue, index, journal)
    fin_rapprochement = time.perf_counter()
    noms = charger_noms(DOSSIER + "catalogue_reference.csv")
    prix = construire_prix(lignes)
    return {
        "journal": journal,
        "lignes": lignes,
        "catalogue": catalogue,
        "index": index,
        "noms": noms,
        "prix": prix,
        "comparatif": comparer(prix, noms, ENSEIGNES),
        "t_chargement": fin_chargement - debut,
        "t_rapprochement": fin_rapprochement - fin_chargement,
    }


def option_charger(etat):
    etat.clear()
    etat.update(construire_etat())
    resume = []
    for enseigne, lignes in etat["lignes"].items():
        resume.append({
            "enseigne": enseigne,
            "articles": len(lignes),
            "sans_prix": sum(1 for l in lignes if l["prix_paye"] is None),
            "indisponibles": sum(1 for l in lignes if not l["disponible"]),
            "rapproches": sum(1 for l in lignes if l["produit_id"] is not None),
        })
    afficher_tableau(resume, ["enseigne", "articles", "sans_prix", "indisponibles", "rapproches"])
    print(f"\n{len(etat['journal'])} remarques enregistrées dans le journal (option 2).")


def option_journal(etat):
    afficher_tableau(journal_en_lignes(etat["journal"]), ["source", "id", "probleme", "action"], 60)


def option_comparatif(etat):
    afficher_tableau(etat["comparatif"], COLONNES_COMPARATIF)
    print(f"\n{len(etat['comparatif'])} produits comparés (au moins 2 prix valides et en stock).")


def option_synthese(etat):
    victoires, moyennes, top3 = synthese(etat["comparatif"], ENSEIGNES)
    lignes = [{
        "enseigne": e,
        "fois_moins_chere": victoires[e],
        "ecart_moyen_fcfa": moyennes[e][0],
        "ecart_moyen_pct": moyennes[e][1],
    } for e in ENSEIGNES]
    afficher_tableau(lignes, ["enseigne", "fois_moins_chere", "ecart_moyen_fcfa", "ecart_moyen_pct"])
    print("\nTrois produits où il y a le plus à gagner à comparer :")
    afficher_tableau(top3, ["produit_id", "nom", "moins_cher", "ecart_fcfa", "ecart_pct"])
    meilleur = max(ENSEIGNES, key=victoires.get)
    print(f"\nEnseigne la plus souvent la moins chère : {meilleur}")


def option_panier(etat):
    par_enseigne, optimal, achats = calculer_panier(etat["prix"], PANIER, ENSEIGNES)
    lignes = [{
        "enseigne": e,
        "total_fcfa": par_enseigne[e]["total"],
        "articles_manquants": ", ".join(par_enseigne[e]["manquants"]) or "-",
    } for e in ENSEIGNES]
    afficher_tableau(lignes, ["enseigne", "total_fcfa", "articles_manquants"])
    complets = {e: r["total"] for e, r in par_enseigne.items() if r["total"] is not None}
    gagnant = None
    if complets:
        gagnant = min(complets, key=complets.get)
        print(f"\nPanier complet le moins cher : {gagnant} ({formater(complets[gagnant])} FCFA)")
    print("\nEn achetant chaque article là où il est le moins cher :")
    detail = [{
        "produit_id": pid,
        "nom": etat["noms"][pid],
        "quantite": PANIER[pid],
        "enseigne": achat[0],
        "montant": achat[1],
    } for pid, achat in achats.items() if achat]
    afficher_tableau(detail, ["produit_id", "nom", "quantite", "enseigne", "montant"])
    print(f"Total : {formater(optimal)} FCFA")
    if gagnant:
        print(f"Économie par rapport au meilleur panier unique : "
              f"{formater(complets[gagnant] - optimal)} FCFA")


def option_historique(etat):
    if "historique" not in etat:
        etat["historique"] = analyser(lire_historique(DOSSIER + "historique_prix.csv"))
    stats = etat["historique"]
    afficher_tableau(resume_par_source(stats),
                     ["source", "produits", "variation_bf_pct", "moins_chers_en_bf", "verdict"])
    print("\nvariation_bf_pct : prix moyen du 24 au 30 novembre 2025 par rapport à la moyenne de l'année.")
    saisie = input("Détail d'un produit (ex. P01, Entrée pour passer) : ").strip().upper()
    if saisie:
        detail = [l for l in stats if l["produit_id"] == saisie]
        afficher_tableau(detail, ["source", "produit_id", "prix_moyen", "prix_moyen_bf", "variation_pct"])


def option_export(etat):
    ecrire_excel(etat["comparatif"], COLONNES_COMPARATIF, SORTIE + "comparatif.xlsx")
    ecrire_csv(journal_en_lignes(etat["journal"]),
               ["source", "id", "probleme", "action"], SORTIE + "journal.csv")
    victoires, moyennes, _ = synthese(etat["comparatif"], ENSEIGNES)
    lignes = [{
        "enseigne": e,
        "fois_moins_chere": victoires[e],
        "ecart_moyen_fcfa": moyennes[e][0],
        "ecart_moyen_pct": moyennes[e][1],
    } for e in ENSEIGNES]
    ecrire_csv(lignes, ["enseigne", "fois_moins_chere", "ecart_moyen_fcfa", "ecart_moyen_pct"],
               SORTIE + "synthese.csv")
    print(f"Fichiers écrits dans {SORTIE} : comparatif.xlsx, journal.csv, synthese.csv")

def option_performances(etat):
    lignes, t_lecture = chrono(lire_historique, DOSSIER + "historique_prix.csv")
    rapide, t_rapide = chrono(analyser, lignes)
    naif, t_naif = chrono(analyser_naif, lignes)
    mesures = [
        {"etape": "Chargement des 3 enseignes", "duree_ms": round(etat["t_chargement"] * 1000, 1)},
        {"etape": "Rapprochement (index inversé)", "duree_ms": round(etat["t_rapprochement"] * 1000, 1)},
        {"etape": f"Lecture de l'historique ({len(lignes)} lignes)", "duree_ms": round(t_lecture * 1000, 1)},
        {"etape": "Historique : une seule passe (dictionnaire)", "duree_ms": round(t_rapide * 1000, 1)},
        {"etape": "Historique : version naïve (filtres répétés)", "duree_ms": round(t_naif * 1000, 1)},
    ]
    afficher_tableau(mesures, ["etape", "duree_ms"], 50)
    """print(f"\nRésultats identiques : {'oui' if rapide == naif else 'non'}")
    if t_rapide > 0:
        print(f"La passe unique est environ {t_naif / t_rapide:.0f} fois plus rapide.")
    print("\nStructures utilisées :")
    print("- dictionnaire {produit_id: {enseigne: prix}} : accès direct en O(1)")
    print("- index inversé {mot: [produit_id]} : on ne score que les produits qui partagent un mot")
    print("- ensemble (set) pour les doublons et les mots d'un nom : test d'appartenance en O(1)")
    print("- heapq.nlargest pour le top 3 : O(n log 3) au lieu d'un tri complet")"""


def option_recherche(etat):
    saisie = input("Nom du produit : ").strip()
    if not saisie:
        return
    pid, score = trouver_produit(saisie, etat["catalogue"], etat["index"])
    if pid is None:
        print("Produit non reconnu dans le catalogue.")
        return
    print(f"\n{pid} - {etat['noms'][pid]} (confiance {score:.2f})")
    offres = etat["prix"].get(pid, {})
    if not offres:
        print("Aucune enseigne ne le propose avec un prix valide et en stock.")
        return
    classement = [{"enseigne": e, "prix_fcfa": p} for e, p in sorted(offres.items(), key=lambda x: x[1])]
    afficher_tableau(classement, ["enseigne", "prix_fcfa"])
    meilleur = classement[0]
    message = f"\nRecommandation : acheter chez {meilleur['enseigne']} ({formater(meilleur['prix_fcfa'])} FCFA)"
    if len(classement) > 1:
        gain = classement[-1]["prix_fcfa"] - meilleur["prix_fcfa"]
        message += f", soit {formater(gain)} FCFA de moins que l'offre la plus chère"
    if meilleur["enseigne"] == "Comptoir Ivoire":
        message += " (retrait en boutique)"
    print(message + ".")


ACTIONS = {
    "1": option_charger,
    "2": option_journal,
    "3": option_comparatif,
    "4": option_synthese,
    "5": option_panier,
    "6": option_historique,
    "7": option_export,
    "8": option_performances,
    "9": option_recherche,
}


def main():
    etat = {}
    while True:
        print(MENU)
        try:
            choix = input("Votre choix : ").strip()
            if choix == "0":
                print("Au revoir.")
                break
            action = ACTIONS.get(choix)
            if action is None:
                print("Choix invalide.")
                continue
            if choix != "1" and not etat:
                print("Chargez d'abord les données (option 1).")
                continue
            action(etat)
            input("\nAppuyez sur Entrée pour continuer...")
        except (EOFError, KeyboardInterrupt):
            print("\nAu revoir.")
            break


if __name__ == "__main__":
    main()