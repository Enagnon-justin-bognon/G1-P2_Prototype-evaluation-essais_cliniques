"""
Sauvegarde des résultats d'analyse au format JSON.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def save_analysis(
    analysis: Dict,
    output_dir: str = "results",
    filename: Optional[str] = None,
) -> str:
    """
    Sauvegarde le résultat d'analyse dans un fichier JSON horodaté.
    Résout le chemin relativement à la racine du projet si le dossier n'est pas absolu.
    """
    root_dir = Path(__file__).resolve().parent.parent
    output_path = Path(output_dir)
    if not output_path.is_absolute():
        output_path = root_dir / output_dir

    output_path.mkdir(parents=True, exist_ok=True)

    if filename:
        file_name = filename if filename.endswith(".json") else f"{filename}.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"analyse_{timestamp}.json"

    file_path = output_path / file_name

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            analysis,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return str(file_path)
