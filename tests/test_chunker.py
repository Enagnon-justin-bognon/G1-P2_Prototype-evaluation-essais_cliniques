"""
Tests unitaires du module chunker.

Objectif :
- Vérifier que le découpage crée bien des passages.
- Vérifier que chaque passage a un identifiant unique.
- Vérifier que le numéro de page est conservé.
"""

from src.chunker import create_chunks


def test_create_chunks_returns_list():
    pages = [
        {
            "page": 1,
            "text": "Premier paragraphe.\n\nDeuxième paragraphe.",
        }
    ]

    chunks = create_chunks(pages)

    assert isinstance(chunks, list)
    assert len(chunks) > 0


def test_create_chunks_has_unique_ids():
    pages = [
        {
            "page": 1,
            "text": "Premier paragraphe.\n\nDeuxième paragraphe.",
        }
    ]

    chunks = create_chunks(pages)

    ids = [chunk["chunk_id"] for chunk in chunks]

    assert len(ids) == len(set(ids))


def test_create_chunks_keeps_page_number():
    pages = [
        {
            "page": 2,
            "text": "Texte de la page 2.",
        }
    ]

    chunks = create_chunks(pages)

    assert all(chunk["page"] == 2 for chunk in chunks)