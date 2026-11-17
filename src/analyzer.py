"""
Analyse méthodologique et statistique d'un essai clinique avec Gemini.
"""

import json
import os
import random
import time
from typing import Dict, List, Optional, Callable

from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

try:
    import streamlit as st
except ImportError:
    st = None

from google import genai
from google.genai import types


def analyze_article(
    chunks: List[dict],
    grille: Dict,
    progress_callback: Optional[Callable[[str], None]] = None,
    error_callback: Optional[Callable[[str], None]] = None,
    max_chunks: Optional[int] = None,
    model_override: Optional[str] = None,
) -> Optional[Dict]:
    """
    Analyse un article rapportant un essai clinique randomisé
    en groupes parallèles à l'aide de Gemini.

    Args:
        chunks: Liste des passages extraits du document.
        grille: Dictionnaire contenant les critères d'évaluation.
        progress_callback: Fonction de notification de la progression.
        error_callback: Fonction de notification d'erreur.
        max_chunks: Nombre max de chunks à envoyer (None = analyse complète).
        model_override: Nom de modèle pour surcharger la variable d'environnement.
    """

    def report_error(message: str) -> None:
        if error_callback:
            error_callback(message)
        elif st is not None:
            st.error(message)
        else:
            print(f"[ERREUR] {message}")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        report_error(
            "La clé GEMINI_API_KEY n'est pas définie. "
            "Vérifiez le fichier .env ou les secrets Streamlit."
        )
        return None

    model_name = (
        model_override
        or os.getenv("GEMINI_MODEL")
        or "gemini-2.5-flash"
    ).strip()

    client = genai.Client(api_key=api_key)

    if max_chunks and max_chunks > 0:
        chunks_to_send = chunks[:max_chunks]
    else:
        chunks_to_send = chunks

    text_to_analyze = "\n\n".join(
        f"[{chunk['chunk_id']} - Page {chunk.get('page', '?')}]\n{chunk['text']}"
        for chunk in chunks_to_send
    )

    criteria = grille.get("criteria", grille.get("criteres", []))

    if not criteria:
        report_error(
            "Aucun critère d'évaluation n'a été trouvé dans la grille. "
            "Vérifiez le fichier config/grille.yaml."
        )
        return None

    criteria_text = "\n".join(
        f"- {criterion.get('id', '')} ({criterion.get('referentiel', '')}) : "
        f"{criterion.get('question', criterion.get('label', ''))}"
        for criterion in criteria
    )

    prompt = f"""Tu es un expert méthodologiste et biostatisticien spécialisé dans la lecture critique d'essais cliniques randomisés en groupes parallèles.

Ta mission :
- Analyser rigoureusement l'article fourni en te concentrant sur le critère de jugement principal (primary endpoint).
- Évaluer chacun des 8 critères méthodologiques et statistiques suivants :
{criteria_text}

Règles strictes :
1. Base toutes tes affirmations UNIQUEMENT sur le texte fourni. Ne jamais inventer ou supposer d'information non écrite.
2. Pour chaque critère, cite le ou les extraits textuels exacts prouvant ton évaluation, avec leur identifiant de passage (chunk_id).
3. Le champ "status" doit être OBLIGATOIREMENT choisi parmi les 5 valeurs exactes suivantes :
   - "information_rapportee_clairement" : si l'information requise est explicitement et complètement décrite.
   - "information_rapportee_partiellement" : si l'information est mentionnée mais incomplète.
   - "information_ambigue" : si les éléments rapportés sont contradictoires ou imprécis.
   - "information_non_retrouvee" : si le texte ne mentionne pas cet élément.
   - "a_verifier_humainement" : si une interprétation humaine complexe ou un doute méthodologique subsiste.
4. Si une vérification humaine est conseillée, active "human_check_needed": true.

Format de sortie attendu (JSON pur uniquement) :
{{
  "analysis_id": "analyse_1",
  "criteria": [
    {{
      "id": "identifiant_du_critere",
      "label": "Nom lisible du critère",
      "status": "information_rapportee_clairement",
      "justification": "Explication synthétique et factuelle basée sur le texte.",
      "citations": [
        {{
          "chunk_id": "page1_chunk1",
          "text": "Extrait exact du passage"
        }}
      ],
      "human_check_needed": false
    }}
  ]
}}

Texte intégral à analyser :

{text_to_analyze}
"""

    max_attempts = 3
    raw_text = ""

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1,
    )

    for attempt in range(1, max_attempts + 1):
        try:
            raw_text = ""

            for stream_chunk in client.models.generate_content_stream(
                model=model_name,
                contents=prompt,
                config=config,
            ):
                if stream_chunk.text:
                    raw_text += stream_chunk.text
                    if progress_callback:
                        progress_callback(
                            f"Gemini analyse l'article avec {model_name}… "
                            f"({len(raw_text)} caractères reçus)"
                        )

            break

        except Exception as error:
            error_message = str(error)

            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                report_error(
                    f"Le quota Gemini est temporairement atteint pour le modèle {model_name}.\n\n"
                    "Veuillez patienter avant de relancer l'analyse ou changer de modèle."
                )
                return None

            if "API key not valid" in error_message:
                report_error(
                    "La clé API Gemini n'est pas valide. "
                    "Vérifiez la valeur de GEMINI_API_KEY."
                )
                return None

            if "model" in error_message.lower() and "not found" in error_message.lower():
                report_error(
                    f"Le modèle '{model_name}' n'est pas disponible ou introuvable "
                    "pour cette clé API. Essayez de définir GEMINI_MODEL=gemini-2.5-flash ou gemini-2.0-flash dans .env."
                )
                return None

            if attempt == max_attempts:
                report_error(
                    f"Une erreur est survenue pendant l'analyse avec Gemini (modèle {model_name}) :\n\n"
                    f"{error_message}"
                )
                return None

            wait_time = min(2 ** attempt, 30)
            jitter = random.uniform(0, 1)

            if progress_callback:
                progress_callback(
                    f"Gemini est momentanément indisponible. "
                    f"Nouvelle tentative dans {wait_time + jitter:.0f} secondes…"
                )

            time.sleep(wait_time + jitter)

    if not raw_text.strip():
        report_error("Gemini n'a renvoyé aucune réponse. Veuillez réessayer.")
        return None

    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
    cleaned_text = cleaned_text.strip()

    try:
        analysis = json.loads(cleaned_text)
    except json.JSONDecodeError as error:
        report_error(
            f"Gemini n'a pas renvoyé un format JSON valide : {error}\n\n"
            f"Début de la réponse reçue :\n{cleaned_text[:500]}"
        )
        return None

    if not isinstance(analysis, dict) or not analysis.get("criteria"):
        report_error("La réponse de Gemini n'a pas la structure attendue ou ne contient aucun critère.")
        return None

    analysis["model_used"] = model_name
    analysis["chunks_analyzed"] = len(chunks_to_send)
    analysis["total_chunks"] = len(chunks)

    if len(chunks_to_send) < len(chunks):
        analysis["coverage_warning"] = (
            f"L'analyse a porté sur un échantillon de {len(chunks_to_send)} passages "
            f"sur un total de {len(chunks)}."
        )

    return analysis
