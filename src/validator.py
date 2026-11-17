"""
Validation des citations produites par le modèle avec tolérance aux sauts de ligne et césures.
"""

import re
import unicodedata
from typing import List, Dict


def _normalize_text(text: str) -> str:
    """
    Normalise le texte pour permettre une comparaison robuste
    face aux sauts de ligne, césures et espaces insécables issus de l'extraction PDF.
    """
    if not text:
        return ""

    # Normalisation Unicode (NFKC pour résoudre ligatures fi, fl, etc.)
    text = unicodedata.normalize("NFKC", text)

    # Remplacement des césures de fin de ligne (ex: "inter-\nvention" -> "intervention")
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

    # Remplacement de tous les espaces blancs / retours chariot par un espace simple
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def validate_citations(
    analysis: Dict,
    chunks: List[dict],
) -> Dict:
    """
    Vérifie que les citations renvoient à des passages réels
    et enrichit les citations avec le numéro de page source.
    """

    chunks_by_id = {
        chunk["chunk_id"]: chunk
        for chunk in chunks
    }

    validated_citations = []

    for criterion in analysis.get("criteria", []):
        criterion_id = criterion.get("id")
        citations = criterion.get("citations", [])

        for citation in citations:
            chunk_id = citation.get("chunk_id")
            quoted_text = citation.get("text", "")

            if chunk_id not in chunks_by_id:
                validated_citations.append(
                    {
                        "criterion_id": criterion_id,
                        "chunk_id": chunk_id,
                        "page": None,
                        "status": "citation_introuvable",
                        "message": "Le passage indiqué n'existe pas.",
                        "quoted_text": quoted_text,
                    }
                )
                continue

            chunk_info = chunks_by_id[chunk_id]
            source_text = chunk_info.get("text", "")
            page_number = chunk_info.get("page")

            # Enrichir la citation avec la page pour l'interface
            citation["page"] = page_number

            # 1. Vérification exacte directe
            exact_match = quoted_text and quoted_text in source_text

            # 2. Vérification normalisée (espaces, césures, sauts de lignes)
            norm_match = False
            if not exact_match and quoted_text:
                norm_quote = _normalize_text(quoted_text)
                norm_source = _normalize_text(source_text)
                norm_match = norm_quote in norm_source

            if quoted_text and not (exact_match or norm_match):
                validated_citations.append(
                    {
                        "criterion_id": criterion_id,
                        "chunk_id": chunk_id,
                        "page": page_number,
                        "status": "citation_non_concordante",
                        "message": "Le texte cité ne correspond pas au passage.",
                        "quoted_text": quoted_text,
                    }
                )
                continue

            validated_citations.append(
                {
                    "criterion_id": criterion_id,
                    "chunk_id": chunk_id,
                    "page": page_number,
                    "status": "citation_valide",
                    "message": "La citation correspond au passage.",
                    "quoted_text": quoted_text,
                }
            )

    analysis["citations_validees"] = validated_citations

    return analysis
