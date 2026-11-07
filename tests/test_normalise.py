import pytest
from src.normalise import normaliser

PAIRES = [
    ("Clé USB SanDisk 64 Go", "CLE USB SANDISK 64GB"),
    ("Seagate Expansion 1TB", "DD externe Seagate 1To"),
    ("LG Air Conditioner 1HP", "Climatiseur LG 1 CV"),
    ("HP Laptop 250 G9 (i5, 8GB, 512GB SSD)", "HP 250 G9 Core i5 8 Go 512 Go"),
    ('TV Hisense 32"', "TV Hisense 32 pouces"),
    ("Mixeur Moulinex 1,5 L", "Moulinex Blender 1.5L"),
    ("Philips Steam Iron", "Fer à repasser Philips"),
]


@pytest.mark.parametrize("nom_a, nom_b", PAIRES)
def test_memes_mots(nom_a, nom_b):
    assert normaliser(nom_a) == normaliser(nom_b)


DIFFERENTS = [
    ("Samsung Galaxy A15 128 Go", "Samsung Galaxy A25 128 Go"),
    ("Tecno Spark 20 128 Go", "Tecno Camon 30 256 Go"),
    ("Climatiseur LG 1 CV", "Climatiseur Hisense 1.5 CV"),
]


@pytest.mark.parametrize("nom_a, nom_b", DIFFERENTS)
def test_produits_differents(nom_a, nom_b):
    assert normaliser(nom_a) != normaliser(nom_b)