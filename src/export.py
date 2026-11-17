"""
Export des résultats d'analyse au format CSV.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def export_analysis_to_csv(
    analysis: Dict,
    output_dir: str = "results",
    filename: Optional[str] = None,
) -> str:
    """
    Exporte les résultats d'analyse dans un fichier CSV horodaté.
    Résout le chemin relativement à la racine du projet si le dossier n'est pas absolu.
    """
    root_dir = Path(__file__).resolve().parent.parent
    output_path = Path(output_dir)
    if not output_path.is_absolute():
        output_path = root_dir / output_dir

    output_path.mkdir(parents=True, exist_ok=True)

    analysis_id = analysis.get("analysis_id", "analyse")

    if filename:
        file_name = filename if filename.endswith(".csv") else f"{filename}.csv"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{analysis_id}_{timestamp}.csv"

    file_path = output_path / file_name

    fieldnames = [
        "criterion_id",
        "criterion_label",
        "status",
        "justification",
        "citations",
        "pages",
        "human_check_needed",
    ]

    with open(
        file_path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter=";",
        )

        writer.writeheader()

        for criterion in analysis.get("criteria", []):
            citations = criterion.get("citations", [])
            chunk_ids = ", ".join(c.get("chunk_id", "") for c in citations if c.get("chunk_id"))
            pages = ", ".join(str(c.get("page", "")) for c in citations if c.get("page"))

            writer.writerow(
                {
                    "criterion_id": criterion.get("id", ""),
                    "criterion_label": criterion.get("label", ""),
                    "status": criterion.get("status", ""),
                    "justification": criterion.get("justification", ""),
                    "citations": chunk_ids,
                    "pages": pages,
                    "human_check_needed": criterion.get(
                        "human_check_needed",
                        False,
                    ),
                }
            )

    return str(file_path)
