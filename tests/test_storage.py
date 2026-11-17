"""
Tests unitaires du module storage.

Objectif :
- Vérifier que la sauvegarde crée bien un fichier JSON.
- Vérifier que le fichier contient les données attendues.
"""

import json

from src.storage import save_analysis


def test_save_analysis_creates_file(tmp_path):
    analysis = {
        "analysis_id": "test",
        "criteria": [],
    }

    file_path = save_analysis(
        analysis,
        output_dir=str(tmp_path),
    )

    assert file_path is not None


def test_save_analysis_contains_data(tmp_path):
    analysis = {
        "analysis_id": "test",
        "criteria": [],
    }

    file_path = save_analysis(
        analysis,
        output_dir=str(tmp_path),
    )

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["analysis_id"] == "test"