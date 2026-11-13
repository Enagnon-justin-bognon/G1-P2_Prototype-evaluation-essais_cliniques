"""
Analyse d'un article par Google Gemini.

Choix méthodologique :
- Le modèle ne produit pas de verdict définitif.
- Il identifie ce qui est rapporté, cite le passage utilisé,
  et signale les informations absentes ou ambiguës.
- La température est fixée à 0 pour réduire la variabilité.

Choix technique :
- Nous envoyons les passages du PDF au modèle.
- Nous demandons une réponse JSON structurée.
- Nous validons ensuite la citation dans validator.py.

Important :
- Gemini peut être configuré pour respecter un schéma JSON.
- Cela réduit fortement le risque de réponse mal formée.
"""

import json
from typing import List

from google import genai
from google.genai import types

from src.config import get_api_key, get_model_name


def build_analysis_prompt(criterion: dict, chunks: List[dict]) -> str:
    """
    Construit l'instruction envoyée à Gemini pour analyser un critère.

    Args:
        criterion (dict): critère issu de la grille.
        chunks (List[dict]): passages du PDF.

    Returns:
        str: prompt complet.
    """
    passages_text = ""

    for chunk in chunks:
        passages_text += (
            f"\n\n--- PASSAGE {chunk['chunk_id']} "
            f"(page {chunk['page']}) ---\n"
            f"{chunk['text']}"
        )

    prompt = f"""
Tu es un assistant de lecture critique d'essais cliniques randomisés.

Ta tâche est d'aider un lecteur à examiner le critère suivant :
"{criterion['question']}"

Résultat évalué : {criterion.get('resultat_evalue', 'Critère de jugement principal')}

Règles obligatoires :
1. Utilise uniquement les passages fournis.
2. N'invente jamais une information absente.
3. Cite exactement un passage du document dans le champ "preuve".
4. Indique l'identifiant du passage utilisé dans "chunk_id".
5. Si l'information est absente, réponds "information_non_retrouvee".
6. Si l'information est présente mais incomplète, réponds
   "information_rapportee_partiellement".
7. Si l'information est ambiguë, réponds "information_ambigue".
8. Si une vérification humaine est nécessaire, réponds
   "a_verifier_humainement".
9. Ne conclus jamais à un risque de biais sans justification claire.

Valeurs autorisées pour "proposition" :
- information_rapportee_clairement
- information_rapportee_partiellement
- information_ambigue
- information_non_retrouvee
- a_verifier_humainement

Passages du document :
{passages_text}
"""

    return prompt


def get_response_schema() -> dict:
    """
    Définit le schéma JSON attendu en sortie.

    Ce schéma garantit que Gemini renvoie toujours les mêmes champs.
    """
    return {
        "type": "object",
        "properties": {
            "critere": {"type": "string"},
            "constat": {"type": "string"},
            "preuve": {"type": "string"},
            "chunk_id": {"type": "string"},
            "page": {"type": "integer"},
            "proposition": {
                "type": "string",
                "enum": [
                    "information_rapportee_clairement",
                    "information_rapportee_partiellement",
                    "information_ambigue",
                    "information_non_retrouvee",
                    "a_verifier_humainement",
                ],
            },
            "justification": {"type": "string"},
            "point_a_verifier": {"type": "string"},
        },
        "required": [
            "critere",
            "constat",
            "preuve",
            "chunk_id",
            "page",
            "proposition",
            "justification",
            "point_a_verifier",
        ],
    }


def analyze_criterion(criterion: dict, chunks: List[dict]) -> dict:
    """
    Analyse un critère méthodologique ou statistique avec Gemini.

    Args:
        criterion (dict): critère issu de la grille.
        chunks (List[dict]): passages du PDF.

    Returns:
        dict: réponse structurée du modèle.
    """
    client = genai.Client(api_key=get_api_key())

    prompt = build_analysis_prompt(criterion, chunks)

    response = client.models.generate_content(
        model=get_model_name(),
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=get_response_schema(),
        ),
    )

    # Gemini renvoie le JSON dans response.text.
    analysis = json.loads(response.text)

    # Ajout de métadonnées utiles pour la traçabilité.
    analysis["model"] = get_model_name()
    analysis["temperature"] = 0

    return analysis