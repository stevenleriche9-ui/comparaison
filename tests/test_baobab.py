from src.charger.baobab_shop import charger_baobab

chemin = "data/original/baobab_shop.json"

def charger():
    journal = []
    lignes = charger_baobab(chemin, journal)
    return lignes, journal

def trouver(lignes, sku):
    for ligne in lignes :
        if ligne["id_source"] == sku:
            return ligne
        return None 
    

def test_nombre_ligne():
    lignes, _ = charger() 
    assert len(lignes) == 26


def test_prix_null_none():
    lignes, _= charger()
    iron = None
    for ligne in lignes :
        if ligne["id_source"] == "BB27999":
            iron = ligne
            break
    assert iron["prix_paye"] is None
    assert sum(1 for ligne in lignes if ligne["prix_paye"] is None) == 1



def test_indisponible():
    lignes, _ = charger()
    indispos = {l["id_source"] for l in lignes if not l["disponible"]}
    assert indispos == {"BB03433", "BB16464","BB30124"}


def test_champs_presents():
    lignes, _ = charger()
    attendus = {"enseigne", "id_source", "nom_brut", "prix_paye", "disponible"}
    for ligne in lignes:
        assert attendus <= set(ligne.keys())