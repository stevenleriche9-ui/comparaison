import csv
from src.resultats import formater, ecrire_csv


def test_formater():
    assert formater(None) == "-"
    assert formater(1234567) == "1 234 567"
    assert formater(12.5) == "12.5"
    assert formater("abc") == "abc"


def test_ecrire_csv(tmp_path):
    chemin = tmp_path / "sortie" / "test.csv"
    ecrire_csv([{"a": 1, "b": None}], ["a", "b"], str(chemin))
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.reader(f, delimiter=";"))
    assert lignes == [["a", "b"], ["1", ""]]