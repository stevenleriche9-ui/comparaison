from src.charger.comptoir_ivoire import charger_comptoir

CHEMIN = "data/original/comptoir_ivoire.xlsx"


def charger():
    journal = []
    lignes = charger_comptoir(CHEMIN, journal)
    return lignes, journal


def trouver(lignes, code):
    for ligne in lignes:
        if ligne["id_source"] == code:
            return ligne
    return None


def test_nombre_lignes():
    lignes, _ = charger()
    assert len(lignes) == 22


def test_remise_appliquee():
    lignes, _ = charger()
    assert trouver(lignes, "CI200")["prix_paye"] == 92990


def test_sans_remise():
    lignes, _ = charger()
    assert trouver(lignes, "CI201")["prix_paye"] == 150300


def test_remise_cinq_pour_cent():
    lignes, _ = charger()
    assert trouver(lignes, "CI207")["prix_paye"] == 287375


def test_prix_texte_nettoye():
    lignes, _ = charger()
    assert trouver(lignes, "CI216")["prix_paye"] == 279300


def test_indisponibles():
    lignes, _ = charger()
    indispos = {l["id_source"] for l in lignes if not l["disponible"]}
    assert indispos == {"CI214", "CI217"}


def test_aucun_prix_none():
    lignes, _ = charger()
    assert all(l["prix_paye"] is not None for l in lignes)