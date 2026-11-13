"""
Chargement de la configuration du prototype.

Ce module fonctionne à la fois :
- en local, avec un fichier .env ;
- sur Streamlit Community Cloud, avec les Secrets configurés dans Streamlit.

La clé API n'est jamais écrite dans le code ni versionnée sur GitHub.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st
import yaml


# Dossier racine du projet.
BASE_DIR = Path(__file__).resolve().parent.parent

# Chargement du fichier .env s'il existe.
# Ce fichier est utile uniquement en local.
# Sur Streamlit Cloud, la clé est lue via st.secrets.
load_dotenv(BASE_DIR / ".env")

# Chemins des données générées par le prototype.
DATA_DIR = BASE_DIR / "data"
ARTICLES_DIR = DATA_DIR / "articles"
OUTPUTS_DIR = DATA_DIR / "outputs"
CORRECTIONS_DIR = DATA_DIR / "corrections"
USAGE_LOG_PATH = DATA_DIR / "ia_usage_log.csv"

# Fichier de la grille méthodologique.
GRILLE_PATH = BASE_DIR / "config" / "grille.yaml"


def ensure_data_folders() -> None:
    """
    Crée les dossiers nécessaires s'ils n'existent pas.
    """
    for folder in [ARTICLES_DIR, OUTPUTS_DIR, CORRECTIONS_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def load_grille() -> dict:
    """
    Charge la grille méthodologique depuis config/grille.yaml.

    Returns:
        dict: contenu de la grille.

    Raises:
        FileNotFoundError: si le fichier de grille est absent.
    """
    if not GRILLE_PATH.exists():
        raise FileNotFoundError(
            f"Le fichier de grille est introuvable : {GRILLE_PATH}"
        )

    with open(GRILLE_PATH, "r", encoding="utf-8") as file:
        grille = yaml.safe_load(file)

    if not grille.get("criteres"):
        raise ValueError(
            "La grille ne contient aucun critère. "
            "Vérifie le fichier config/grille.yaml."
        )

    return grille


def get_api_key() -> str:
    """
    Récupère la clé API Gemini.

    Ordre de recherche :
    1. Secrets Streamlit Cloud.
    2. Variable d'environnement GEMINI_API_KEY.
    """
    api_key = None

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "La clé API GEMINI_API_KEY est absente.\n\n"
            "En local : crée un fichier .env à partir de .env.example.\n"
            "Sur Streamlit Cloud : ajoute la clé dans les Secrets."
        )

    return api_key


def get_model_name() -> str:
    """
    Récupère le nom du modèle Gemini.

    Ordre de recherche :
    1. Secrets Streamlit Cloud.
    2. Variable d'environnement GEMINI_MODEL.
    3. Valeur par défaut.
    """
    model_name = None

    try:
        model_name = st.secrets["GEMINI_MODEL"]
    except Exception:
        model_name = None

    if not model_name:
        model_name = os.getenv("GEMINI_MODEL")

    return model_name or "gemini-2.0-flash"