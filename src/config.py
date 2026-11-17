"""
Chargement de la grille d'évaluation.
"""

from pathlib import Path
from typing import Dict, Optional

import yaml


def load_grille(path: Optional[str] = None) -> Dict:
    """
    Charge la grille d'évaluation depuis un fichier YAML.
    Résout le chemin relativement à la racine du projet si nécessaire.
    """
    root_dir = Path(__file__).resolve().parent.parent

    if path is None:
        grille_path = root_dir / "config" / "grille.yaml"
    else:
        grille_path = Path(path)
        if not grille_path.is_absolute() and not grille_path.exists():
            candidate = root_dir / path
            if candidate.exists():
                grille_path = candidate

    if not grille_path.exists():
        raise FileNotFoundError(
            f"Fichier de grille introuvable : {grille_path}"
        )

    with open(grille_path, "r", encoding="utf-8") as file:
        grille = yaml.safe_load(file)

    return grille
