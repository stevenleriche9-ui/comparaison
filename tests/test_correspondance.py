import pytest
from src.correspondant import charger_catalogue, trouver_produit, rapprocher
from src.charger.baobab_shop import charger_baobab
from src.charger.marche_lagune import charger_lagune
from src.charger.comptoir_ivoire import charger_comptoir

CATALOGUE, INDEX = charger_catalogue("data/original/catalogue_reference.csv")


@pytest.mark.parametrize("nom, attendu", [
    ("Galaxy A15 128GB - Samsung", "P01"),
    ("SAMSUNG GALAXY A25 (128GB)", "P02"),
    ("Samsun Galaxy A15 128Go", "P01"),
    ("Tecno Spark 20", "P04"),
    ("Itel A70", "P08"),
    ("HP 250 G9 i5", "P11"),
    ("Frigo Hisense 205L", "P20"),
    ('TV SAMSUNG 43" CRYSTAL UHD 4K', "P22"),
    ("Clim LG 1CV", "P24"),
    ("Electric Kettle 1.7L", "P29"),
    ("Hisense Air Conditioner 1.5HP", "P30"),
])
def test_bon_produit(nom, attendu):
    pid, _ = trouver_produit(nom, CATALOGUE, INDEX)
    assert pid == attendu


def test_produit_inconnu():
    pid, _ = trouver_produit("Aspirateur Dyson V15", CATALOGUE, INDEX)
    assert pid is None


def test_tout_rapproche_sans_doublon():
    sources = [
        charger_baobab("data/original/baobab_shop.json", []),
        charger_lagune("data/original/marche_lagune.csv", []),
        charger_comptoir("data/original/comptoir_ivoire.xlsx", []),
    ]
    for lignes in sources:
        rapprocher(lignes, CATALOGUE, INDEX, [])
        ids = [l["produit_id"] for l in lignes]
        assert None not in ids
        assert len(ids) == len(set(ids))