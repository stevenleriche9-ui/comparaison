# Comparateur de prix 

Programme Python en ligne de commande qui compare les prix de trois enseignes d'Abidjan (**Baobab Shop**, **Marché Lagune**, **Comptoir Ivoire**) à partir de fichiers dans trois formats différents (JSON, CSV, Excel). Il nettoie les données, rapproche chaque article d'un catalogue de référence, puis répond à deux questions : *où acheter ?* et *quand acheter ?*

## Fonctionnalités

- Chargement de trois sources hétérogènes (JSON, CSV, XLSX) vers un format interne unique
- Nettoyage des données avec un journal de toutes les anomalies détectées
- Normalisation des noms de produits et rapprochement avec le catalogue (index inversé, score de confiance)
- Comparatif des prix : enseigne la moins chère, écart en FCFA et en %
- Synthèse par enseigne et top 3 des plus gros écarts
- Panier de rentrée : meilleur panier d'une seule enseigne, ou panier optimal en achetant chaque article là où il est le moins cher
- Analyse de l'historique (20 876 relevés) : faut-il acheter pendant le Black Friday ?
- Recherche d'un produit par son nom
- Mesure des performances (version naïve et version optimisée)
- Export des résultats (comparatif Excel avec bordures, journal et synthèse en CSV)

## Structure du projet

```
comparaison/
├── main.py                  # Menu en console et orchestration
├── requirements.txt         # Dépendances
├── data/
│   ├── original/            # Données brutes des enseignes + catalogue + historique
│   └── propre/              # Données nettoyées et normalisées (générées)
├── sortie/                  # Résultats exportés (générés)
├── src/
│   ├── charger/             # Un chargeur par enseigne
│   │   ├── baobab_shop.py   #   JSON
│   │   ├── marche_lagune.py #   CSV (prix en texte, séparateur « ; »)
│   │   └── comptoir_ivoire.py #   Excel
│   ├── normalise.py         # Normalisation des noms de produits
│   ├── correspondant.py     # Rapprochement avec le catalogue
│   ├── comparaison.py       # Comparatif, synthèse, panier
│   ├── historique.py        # Analyse du Black Friday
│   └── resultats.py         # Affichage en tableau et exports
└── tests/                   # Tests unitaires (pytest)
```

## Installation

Prérequis : Python 3.10 ou plus récent.

```bash
# Créer et activer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

# Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

```bash
python main.py
```

Le menu s'affiche :

```
===== COMPARATEUR DE PRIX - ABIDJAN =====
1. Charger et nettoyer les données
2. Journal de nettoyage
3. Comparatif des prix
4. Synthèse
5. Panier de rentrée
6. Historique : Black Friday
7. Exporter les résultats
8. Mesurer les performances
9. Rechercher un produit
0. Quitter
```

Commence toujours par l'**option 1** : les autres options en dépendent.

## Fichiers générés

| Fichier | Contenu |
|---|---|
| `data/propre/*.csv` | Articles de chaque enseigne avec nom normalisé et produit du catalogue associé |
| `sortie/comparatif.xlsx` | Tableau comparatif avec bordures, prix en nombres |
| `sortie/journal.csv` | Anomalies détectées pendant le nettoyage |
| `sortie/synthese.csv` | Synthèse par enseigne |

Ferme `comparatif.xlsx` dans Excel avant de relancer l'export, sinon Windows bloque l'écriture.

## Comment ça marche

1. **Chargement** : chaque enseigne a son chargeur, qui produit des lignes au même format (enseigne, identifiant, nom brut, prix payé, disponibilité). Les prix en texte (« 102 900 FCFA ») sont convertis en nombres.
2. **Normalisation** : les noms sont passés en minuscules, sans accents, avec des alias (`gb` → `go`, `clim` → `climatiseur`) et sans mots parasites. Le résultat est un ensemble de mots.
3. **Rapprochement** : un index inversé `{mot: [produits]}` limite le calcul du score aux produits qui partagent au moins un mot. Un score inférieur à 0,7 est conservé mais signalé dans le journal.
4. **Comparaison** : un dictionnaire `{produit_id: {enseigne: prix}}` donne un accès direct aux prix. Seuls les produits avec au moins deux prix valides et en stock sont comparés.
5. **Historique** : le prix moyen du 24 au 30 novembre est comparé à la moyenne de l'année pour chaque enseigne.

## Résultats sur les données fournies

- 3 enseignes, 30 produits au catalogue, 20 876 relevés de prix
- 23 produits comparés, 100 % des articles rapprochés, 17 remarques au journal
- Comptoir Ivoire est le moins cher le plus souvent (10 produits), devant Baobab Shop (9) et Marché Lagune (6)
- Panier optimal : 477 575 FCFA, soit 6 500 FCFA d'économie face au meilleur panier d'une seule enseigne
- Black Friday : environ −11 % chez Baobab Shop et Marché Lagune, +3,8 % chez Comptoir Ivoire

## Performances

L'analyse de l'historique en une seule passe (dictionnaire) est environ 12 fois plus rapide que la version naïve qui refiltre les données à chaque produit (≈ 7 ms contre ≈ 80 ms), pour des résultats identiques. La complexité globale est linéaire en la taille de l'historique.

## Tests

```bash
pytest
```

Les tests couvrent les chargeurs, la normalisation, le rapprochement, la comparaison et les résultats.

## Dépendances

- `openpyxl` : lecture et écriture des fichiers Excel
- `pandas`
- `pytest` : tests unitaires