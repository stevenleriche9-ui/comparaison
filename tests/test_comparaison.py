from src.comparaison import construire_prix, comparer, synthese, calculer_panier

ENSEIGNES = ["A", "B", "C"]


def ligne(pid, prix, dispo=True):
    return {"produit_id": pid, "prix_paye": prix, "disponible": dispo}


DONNEES = {
    "A": [ligne("P01", 100), ligne("P02", 200, False), ligne("P03", None), ligne("P04", 50)],
    "B": [ligne("P01", 120), ligne("P02", 150), ligne("P03", 80), ligne("P04", 50)],
    "C": [ligne("P01", 110), ligne("P02", 160)],
}
NOMS = {"P01": "Un", "P02": "Deux", "P03": "Trois", "P04": "Quatre"}


def test_exclut_rupture_et_prix_none():
    prix = construire_prix(DONNEES)
    assert prix["P02"] == {"B": 150, "C": 160}
    assert prix["P03"] == {"B": 80}


def test_comparatif_ecart_et_gagnant():
    comp = comparer(construire_prix(DONNEES), NOMS, ENSEIGNES)
    p01 = [l for l in comp if l["produit_id"] == "P01"][0]
    assert p01["moins_cher"] == "A"
    assert p01["ecart_fcfa"] == 20
    assert p01["ecart_pct"] == 20.0


def test_un_seul_prix_exclu_du_comparatif():
    comp = comparer(construire_prix(DONNEES), NOMS, ENSEIGNES)
    assert "P03" not in [l["produit_id"] for l in comp]


def test_egalite_donne_deux_gagnants():
    comp = comparer(construire_prix(DONNEES), NOMS, ENSEIGNES)
    p04 = [l for l in comp if l["produit_id"] == "P04"][0]
    assert p04["moins_cher"] == "A / B"


def test_synthese_victoires_et_top():
    comp = comparer(construire_prix(DONNEES), NOMS, ENSEIGNES)
    victoires, moyennes, top3 = synthese(comp, ENSEIGNES)
    assert victoires == {"A": 2, "B": 2, "C": 0}
    assert top3[0]["produit_id"] == "P01"
    assert moyennes["C"][0] == 10


def test_panier_incomplet_et_optimal():
    prix = construire_prix(DONNEES)
    par_enseigne, optimal, achats = calculer_panier(prix, {"P01": 2, "P02": 1}, ENSEIGNES)
    assert par_enseigne["A"]["total"] is None
    assert par_enseigne["A"]["manquants"] == ["P02"]
    assert par_enseigne["B"]["total"] == 390
    assert optimal == 2 * 100 + 150
    assert achats["P01"] == ("A", 200)