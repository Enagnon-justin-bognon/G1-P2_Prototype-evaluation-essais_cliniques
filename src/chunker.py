"""
Découpage du texte en passages identifiables avec gestion du chevauchement.
"""

from typing import List


def create_chunks(
    pages: List[dict],
    max_characters: int = 2500,
    overlap_characters: int = 200,
) -> List[dict]:
    """
    Transforme les pages extraites en passages analysables.
    Prend en charge un chevauchement (overlap) optionnel pour éviter
    de tronquer les phrases méthodologiques importantes à cheval entre deux passages.
    """

    chunks = []
    chunk_counter = 0

    for page in pages:
        page_number = page.get("page", 1)
        page_text = page.get("text", "")

        paragraphs = [
            paragraph.strip()
            for paragraph in page_text.split("\n\n")
            if paragraph.strip()
        ]

        # Si pas de double saut de ligne ou paragraphe unique
        if not paragraphs and page_text.strip():
            paragraphs = [page_text.strip()]

        current_text = ""

        for paragraph in paragraphs:
            # Si un paragraphe seul dépasse la taille max, on le découpe en sous-parties
            if len(paragraph) > max_characters:
                # Vider ce qui précédait si non vide
                if current_text.strip():
                    chunk_counter += 1
                    chunks.append(
                        {
                            "chunk_id": f"page{page_number}_chunk{chunk_counter}",
                            "page": page_number,
                            "text": current_text.strip(),
                        }
                    )
                    current_text = ""

                # Découper le long paragraphe par tranches avec overlap
                start = 0
                while start < len(paragraph):
                    end = start + max_characters
                    sub_part = paragraph[start:end].strip()
                    if sub_part:
                        chunk_counter += 1
                        chunks.append(
                            {
                                "chunk_id": f"page{page_number}_chunk{chunk_counter}",
                                "page": page_number,
                                "text": sub_part,
                            }
                        )
                    step = max(max_characters - overlap_characters, 1)
                    start += step
                continue

            # Cas où ajouter le paragraphe dépasse max_characters
            if len(current_text) + len(paragraph) + 2 > max_characters and current_text:
                chunk_counter += 1
                chunks.append(
                    {
                        "chunk_id": f"page{page_number}_chunk{chunk_counter}",
                        "page": page_number,
                        "text": current_text.strip(),
                    }
                )

                # Conserver un chevauchement si possible
                if overlap_characters > 0 and len(current_text) > overlap_characters:
                    overlap_seed = current_text[-overlap_characters:].strip()
                    current_text = overlap_seed + "\n\n" + paragraph
                else:
                    current_text = paragraph
            else:
                current_text = (
                    current_text + "\n\n" + paragraph
                    if current_text
                    else paragraph
                )

        if current_text.strip():
            chunk_counter += 1
            chunks.append(
                {
                    "chunk_id": f"page{page_number}_chunk{chunk_counter}",
                    "page": page_number,
                    "text": current_text.strip(),
                }
            )

    return chunks
