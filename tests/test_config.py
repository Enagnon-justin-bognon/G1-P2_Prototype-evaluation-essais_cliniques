"""
Tests unitaires du module config.

Objectif :
- Vérifier que la grille YAML se charge sans erreur.
- Vérifier qu'elle contient les 8 critères méthodologiques et statistiques.
- Vérifier que chaque critère possède un id, un label et un referentiel.
- Vérifier la présence des statuts autorisés.
"""

from src.config import load_grille


def test_load_grille_returns_valid_structure():
    grille = load_grille()
    assert isinstance(grille, dict)
    assert "criteres" in grille
    assert "propositions_autorisees" in grille


def test_load_grille_contains_eight_criteria():
    grille = load_grille()
    criteres = grille["criteres"]
    assert len(criteres) == 8

    expected_ids = {
        "randomisation",
        "aveuglement",
        "ecarts_interventions",
        "donnees_manquantes",
        "mesure_resultat_principal",
        "taille_echantillon",
        "analyse_principale",
        "resultats_precision",
    }

    found_ids = {c["id"] for c in criteres}
    assert found_ids == expected_ids


def test_load_grille_criteria_have_required_fields():
    grille = load_grille()
    for critere in grille["criteres"]:
        assert "id" in critere
        assert "label" in critere
        assert "referentiel" in critere
        assert "question" in critere
        assert len(critere["label"]) > 0
