"""
Tests unitaires du module validator.

Objectif :
- Vérifier qu'une citation valide est reconnue.
- Vérifier qu'une citation introuvable est signalée.
- Vérifier qu'une citation non concordante est signalée.
- Vérifier que la tolérance aux sauts de ligne / césures fonctionne.
- Vérifier que le numéro de page est enrichi.
"""

from src.validator import validate_citations


def test_validate_citations_valid():
    chunks = [
        {
            "chunk_id": "page1_chunk1",
            "page": 1,
            "text": "La randomisation a été réalisée par tirage au sort.",
        }
    ]

    analysis = {
        "criteria": [
            {
                "id": "randomisation",
                "citations": [
                    {
                        "chunk_id": "page1_chunk1",
                        "text": "La randomisation a été réalisée par tirage au sort.",
                    }
                ],
            }
        ]
    }

    result = validate_citations(analysis, chunks)

    assert result["citations_validees"][0]["status"] == "citation_valide"
    assert result["criteria"][0]["citations"][0]["page"] == 1


def test_validate_citations_normalized_whitespace():
    chunks = [
        {
            "chunk_id": "page2_chunk1",
            "page": 2,
            "text": "Les participants\nont été   randomisés en 1:1.",
        }
    ]

    analysis = {
        "criteria": [
            {
                "id": "randomisation",
                "citations": [
                    {
                        "chunk_id": "page2_chunk1",
                        "text": "Les participants ont été randomisés en 1:1.",
                    }
                ],
            }
        ]
    }

    result = validate_citations(analysis, chunks)

    assert result["citations_validees"][0]["status"] == "citation_valide"


def test_validate_citations_missing_chunk():
    chunks = []

    analysis = {
        "criteria": [
            {
                "id": "randomisation",
                "citations": [
                    {
                        "chunk_id": "page1_chunk1",
                        "text": "Texte quelconque.",
                    }
                ],
            }
        ]
    }

    result = validate_citations(analysis, chunks)

    assert (
        result["citations_validees"][0]["status"]
        == "citation_introuvable"
    )


def test_validate_citations_text_not_matching():
    chunks = [
        {
            "chunk_id": "page1_chunk1",
            "page": 1,
            "text": "La randomisation a été réalisée par tirage au sort.",
        }
    ]

    analysis = {
        "criteria": [
            {
                "id": "randomisation",
                "citations": [
                    {
                        "chunk_id": "page1_chunk1",
                        "text": "Texte totalement inventé.",
                    }
                ],
            }
        ]
    }

    result = validate_citations(analysis, chunks)

    assert (
        result["citations_validees"][0]["status"]
        == "citation_non_concordante"
    )
