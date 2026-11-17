"""
Tests unitaires du module export.

Objectif :
- Vérifier que l'export crée bien un fichier CSV.
- Vérifier que le fichier contient les colonnes attendues.
"""

from src.export import export_analysis_to_csv


def test_export_analysis_to_csv_creates_file(tmp_path):
    analysis = {
        "analysis_id": "test",
        "criteria": [],
    }

    file_path = export_analysis_to_csv(
        analysis,
        output_dir=str(tmp_path),
    )

    assert file_path is not None


def test_export_analysis_to_csv_contains_headers(tmp_path):
    analysis = {
        "analysis_id": "test",
        "criteria": [],
    }

    file_path = export_analysis_to_csv(
        analysis,
        output_dir=str(tmp_path),
    )

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    assert "criterion_id" in content
    assert "criterion_label" in content
    assert "status" in content