from src.charger.marche_lagune import charger_lagune 

chemin = "data/original/marche_lagune.csv"

def charger():
    journal = []
    lignes = charger_lagune(chemin, journal)
    return lignes, journal

def trouver(lignes, ref):
    for ligne in lignes :
        if ligne["id_source"] == ref:
            return ligne
    return None 

def test_nombre_ligne():
    lignes, _ = charger() 
    assert len(lignes) == 28

def test_prix_texte_nettoye():
    lignes, _ =charger()
    assert trouver(lignes, "ML-1000")["prix_paye"] == 102900

def test_prix_none():
    lignes, _ = charger()
    sans_prix = {l["id_source"] for l in lignes if l["prix_paye"] is None}
    assert sans_prix == {"ML-1021","ML-1119","ML-1168"}

def test_prix_aberrant_rejete():
    lignes, journal = charger()
    assert trouver(lignes, "ML-1021")["prix_paye"] is None
    assert any("ML-1021" in str(e) for e in journal)

def test_indisponibles():
    lignes, _ = charger()
    indispos = {l["id_source"] for l in lignes if not l["disponible"]}
    assert indispos == {"ML-1000", "ML-1014", "ML-1049", "ML-1084", "ML-1147", "ML-1168"}





