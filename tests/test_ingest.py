"""
Tests unitaires du module ingest.

Objectif :
- Vérifier qu'une erreur est levée si le fichier n'existe pas.
- Vérifier qu'une erreur est levée si le PDF est vide ou sans texte.
- Vérifier l'extraction correcte page par page sur un PDF valide.
- Vérifier le fonctionnement de la callback de progression.
"""

import pytest
import pymupdf
from src.ingest import extract_text_from_pdf


def test_extract_text_file_not_found(tmp_path):
    missing_file = tmp_path / "absent.pdf"
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(missing_file)


def test_extract_text_empty_pdf(tmp_path):
    pdf_path = tmp_path / "empty.pdf"
    doc = pymupdf.open()
    doc.new_page()  # Page blanche sans texte
    doc.save(str(pdf_path))
    doc.close()

    with pytest.raises(ValueError, match="Aucun texte"):
        extract_text_from_pdf(pdf_path)


def test_extract_text_valid_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = pymupdf.open()

    p1 = doc.new_page()
    p1.insert_text((50, 50), "Texte page un.")

    p2 = doc.new_page()
    p2.insert_text((50, 50), "Texte page deux.")

    doc.save(str(pdf_path))
    doc.close()

    pages = extract_text_from_pdf(pdf_path)

    assert len(pages) == 2
    assert pages[0]["page"] == 1
    assert "Texte page un" in pages[0]["text"]
    assert pages[1]["page"] == 2
    assert "Texte page deux" in pages[1]["text"]


def test_extract_text_progress_callback(tmp_path):
    pdf_path = tmp_path / "progress.pdf"
    doc = pymupdf.open()
    doc.new_page().insert_text((50, 50), "Page 1")
    doc.new_page().insert_text((50, 50), "Page 2")
    doc.save(str(pdf_path))
    doc.close()

    calls = []

    def callback(current, total):
        calls.append((current, total))

    extract_text_from_pdf(pdf_path, progress_callback=callback)

    assert len(calls) == 2
    assert calls[0] == (1, 2)
    assert calls[1] == (2, 2)
