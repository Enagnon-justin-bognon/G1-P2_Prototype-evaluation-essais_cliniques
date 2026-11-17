"""
Extraction du texte depuis un fichier PDF avec PyMuPDF.
"""

from pathlib import Path
from typing import List, Union, Optional, Callable

import pymupdf


def extract_text_from_pdf(
    pdf_path: Union[str, Path],
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[dict]:
    """
    Extrait le texte d'un PDF, page par page.
    Utilise sort=True pour respecter l'ordre de lecture des articles multi-colonnes.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"Fichier PDF introuvable : {pdf_path}"
        )

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    pages = []

    try:
        for index, page in enumerate(doc, start=1):
            # sort=True trie les blocs de texte dans l'ordre naturel de lecture
            # évitant l'entrelacement des colonnes dans les articles scientifiques (NEJM, Lancet, etc.)
            raw_text = page.get_text("text", sort=True) or ""
            cleaned_text = raw_text.replace("\r\n", "\n").strip()

            pages.append(
                {
                    "page": index,
                    "text": cleaned_text,
                }
            )

            if progress_callback:
                progress_callback(index, total_pages)
    finally:
        doc.close()

    total_characters = sum(
        len(page["text"])
        for page in pages
    )

    if total_characters == 0:
        raise ValueError(
            "Aucun texte n'a pu être extrait du PDF. "
            "Le fichier est peut-être scanné ou protégé."
        )

    return pages
