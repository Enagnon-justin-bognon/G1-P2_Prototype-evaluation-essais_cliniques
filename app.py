"""
Application Streamlit d'aide à la lecture critique des essais cliniques randomisés en groupes parallèles.

Groupe G1-P2.
"""

import json
import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

from src.config import load_grille
from src.ingest import extract_text_from_pdf
from src.chunker import create_chunks
from src.analyzer import analyze_article
from src.validator import validate_citations
from src.storage import save_analysis
from src.export import export_analysis_to_csv


st.set_page_config(
    page_title="Lecture critique des essais cliniques",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1180px;
    }

    h1 {
        font-weight: 800;
    }

    .hero {
        background: linear-gradient(
            135deg,
            rgba(59, 130, 246, 0.18) 0%,
            rgba(139, 92, 246, 0.18) 100%
        );
        border: 1px solid rgba(148, 163, 184, 0.25);
        padding: 2.2rem;
        border-radius: 18px;
        margin-bottom: 2rem;
    }

    .hero h1 {
        margin-bottom: 0.5rem;
    }

    .hero p {
        opacity: 0.85;
        margin-bottom: 0;
    }

    .group-badge {
        display: inline-block;
        background-color: rgba(148, 163, 184, 0.18);
        border: 1px solid rgba(148, 163, 184, 0.35);
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    .panel {
        background-color: rgba(148, 163, 184, 0.10);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 16px;
        padding: 1.4rem;
        margin-bottom: 1.5rem;
    }

    .step-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .step-text {
        opacity: 0.80;
        font-size: 0.95rem;
        margin-bottom: 0;
    }

    .result-card {
        background-color: rgba(148, 163, 184, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 16px;
        padding: 1.3rem;
        margin-bottom: 1.2rem;
        border-left: 6px solid rgba(148, 163, 184, 0.6);
    }

    /* Statuts d'évaluation alignés sur grille.yaml */
    .status-claire {
        border-left-color: rgba(34, 197, 94, 0.9);
    }

    .status-partielle {
        border-left-color: rgba(59, 130, 246, 0.9);
    }

    .status-ambigue {
        border-left-color: rgba(245, 158, 11, 0.9);
    }

    .status-non-retrouvee {
        border-left-color: rgba(148, 163, 184, 0.9);
    }

    .status-humain {
        border-left-color: rgba(168, 85, 247, 0.9);
    }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }

    .badge-claire {
        background-color: rgba(34, 197, 94, 0.18);
        color: #22c55e;
    }

    .badge-partielle {
        background-color: rgba(59, 130, 246, 0.18);
        color: #3b82f6;
    }

    .badge-ambigue {
        background-color: rgba(245, 158, 11, 0.18);
        color: #f59e0b;
    }

    .badge-non-retrouvee {
        background-color: rgba(148, 163, 184, 0.18);
        color: #94a3b8;
    }

    .badge-humain {
        background-color: rgba(168, 85, 247, 0.18);
        color: #a855f7;
    }

    .citation-box {
        background-color: rgba(148, 163, 184, 0.10);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 10px;
        padding: 0.8rem;
        margin-top: 0.6rem;
        font-size: 0.9rem;
    }

    .warning-box {
        background-color: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-left: 5px solid rgba(245, 158, 11, 0.8);
        padding: 1rem;
        border-radius: 10px;
        margin-top: 2rem;
    }

    .stButton > button {
        width: 100%;
        border-radius: 12px;
        font-weight: 700;
        padding: 0.6rem 1rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_status_presentation(raw_status: str) -> dict:
    """
    Associe un statut issu de la grille YAML à ses classes CSS et libellé lisible.
    """
    status_key = (raw_status or "").strip().lower()

    mapping = {
        "information_rapportee_clairement": {
            "label": "Information rapportée clairement",
            "icon": "✅",
            "css_class": "status-claire",
            "badge_class": "badge-claire",
        },
        "information_rapportee_partiellement": {
            "label": "Information rapportée partiellement",
            "icon": "⚡",
            "css_class": "status-partielle",
            "badge_class": "badge-partielle",
        },
        "information_ambigue": {
            "label": "Information ambiguë",
            "icon": "❓",
            "css_class": "status-ambigue",
            "badge_class": "badge-ambigue",
        },
        "information_non_retrouvee": {
            "label": "Information non retrouvée",
            "icon": "🔍",
            "css_class": "status-non-retrouvee",
            "badge_class": "badge-non-retrouvee",
        },
        "a_verifier_humainement": {
            "label": "À vérifier humainement",
            "icon": "🧐",
            "css_class": "status-humain",
            "badge_class": "badge-humain",
        },
    }

    if status_key in mapping:
        return mapping[status_key]

    # Fallback pour statuts partiels ou imprévus
    if "clairement" in status_key or ("conforme" in status_key and "non" not in status_key):
        return mapping["information_rapportee_clairement"]
    if "partielle" in status_key:
        return mapping["information_rapportee_partiellement"]
    if "ambigu" in status_key:
        return mapping["information_ambigue"]
    if "non_retrouv" in status_key or "non retrouv" in status_key:
        return mapping["information_non_retrouvee"]
    if "humain" in status_key:
        return mapping["a_verifier_humainement"]

    return {
        "label": raw_status or "Statut indéterminé",
        "icon": "⚠️",
        "css_class": "status-ambigue",
        "badge_class": "badge-ambigue",
    }


# Initialisation du Session State pour persister les résultats lors des téléchargements
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "json_path" not in st.session_state:
    st.session_state.json_path = None
if "csv_path" not in st.session_state:
    st.session_state.csv_path = None
if "analyzed_file_name" not in st.session_state:
    st.session_state.analyzed_file_name = None


with st.sidebar:
    st.markdown("## 🩺 Lecture critique")
    st.markdown(
        """
        **Groupe G1-P2**

        Cet outil aide à analyser un article scientifique rapportant
        un essai clinique randomisé en groupes parallèles.

        Il évalue automatiquement huit critères méthodologiques
        et statistiques concernant le **critère de jugement principal**.
        """
    )

    st.divider()

    st.markdown("### 📌 Comment l'utiliser")
    st.markdown(
        """
        1. Téléversez l'article au format PDF.  
        2. Lancez l'analyse.  
        3. Consultez les résultats et les citations avec pages sources.  
        4. Téléchargez le rapport JSON ou CSV.  
        """
    )

    st.divider()

    model_display = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    st.caption(f"🤖 Modèle configuré : `{model_display}`")

    st.divider()

    st.markdown("### ⚠️ Avertissement")
    st.markdown(
        """
        Les résultats constituent une **aide à la lecture critique**.
        Ils ne remplacent pas le jugement humain, l'expertise
        méthodologique ou une lecture complète de l'article.
        """
    )


st.markdown(
    """
    <div class="hero">
        <span class="group-badge">Groupe G1-P2</span>
        <h1>Aide à la lecture critique des essais cliniques</h1>
        <p>
            Téléversez un article scientifique rapportant un essai clinique
            randomisé en groupes parallèles, puis obtenez une analyse
            structurée fondée sur le texte intégral de l'article.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(
        """
        <div class="panel">
            <div class="step-title">1. Téléversez l'article</div>
            <p class="step-text">
                Sélectionnez un article scientifique au format PDF (texte sélectionnable).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="panel">
            <div class="step-title">2. Lancez l'analyse</div>
            <p class="step-text">
                Extraction multi-colonnes, segmentation et analyse avec Gemini.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


uploaded_file = st.file_uploader(
    "Téléversez l'article au format PDF",
    type=["pdf"],
    help="L'article doit rapporter un essai clinique randomisé en groupes parallèles et contenir un texte accessible.",
)

if uploaded_file is None:
    # Réinitialisation si l'utilisateur retire le fichier
    if st.session_state.analyzed_file_name is not None:
        st.session_state.analysis = None
        st.session_state.chunks = []
        st.session_state.json_path = None
        st.session_state.csv_path = None
        st.session_state.analyzed_file_name = None

    st.info(
        "Veuillez téléverser un article scientifique au format PDF pour commencer l'analyse."
    )
    st.stop()


# Réinitialiser les résultats précédents si un nouveau fichier différent est téléversé
if st.session_state.analyzed_file_name != uploaded_file.name:
    st.session_state.analysis = None
    st.session_state.chunks = []
    st.session_state.json_path = None
    st.session_state.csv_path = None

st.success(f"Fichier chargé : **{uploaded_file.name}**")


if st.button("🚀 Analyser l'article", type="primary", use_container_width=True):
    with st.status("Analyse en cours…", expanded=True) as status:
        st.write("Extraction du texte du PDF (ordre de lecture conservé)…")
        progress_bar = st.progress(0, text="Extraction du PDF…")

        def update_extraction_progress(current_page, total_pages):
            progress = current_page / total_pages
            progress_bar.progress(
                progress,
                text=f"Extraction : page {current_page} sur {total_pages}",
            )

        # Utilisation de TemporaryDirectory pour garantir la suppression automatique des fichiers temporaires
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_pdf_path, "wb") as temp_file:
                temp_file.write(uploaded_file.getvalue())

            try:
                pages = extract_text_from_pdf(
                    temp_pdf_path,
                    progress_callback=update_extraction_progress,
                )
            except Exception as error:
                st.error(f"Erreur lors de l'extraction du PDF : {error}")
                st.stop()

        st.write(f"✅ {len(pages)} pages extraites.")
        progress_bar.progress(1.0, text="Extraction terminée.")

        st.write("Découpage du texte en passages avec chevauchement contextuel…")
        chunks = create_chunks(pages)
        st.write(f"✅ {len(chunks)} passages créés.")

        if not chunks:
            st.error("Aucun passage exploitable n'a pu être extrait du PDF.")
            st.stop()

        st.write("Analyse méthodologique et statistique avec Gemini…")

        def update_gemini_progress(message: str):
            st.write(message)

        grille = load_grille()

        analysis = analyze_article(
            chunks=chunks,
            grille=grille,
            progress_callback=update_gemini_progress,
        )

        if analysis is None:
            status.update(label="Analyse interrompue.", state="error")
            st.stop()

        st.write("Validation anti-hallucination des citations…")
        analysis = validate_citations(
            analysis=analysis,
            chunks=chunks,
        )

        json_path = save_analysis(analysis)
        csv_path = export_analysis_to_csv(analysis)

        # Enregistrement dans st.session_state
        st.session_state.analysis = analysis
        st.session_state.chunks = chunks
        st.session_state.json_path = json_path
        st.session_state.csv_path = csv_path
        st.session_state.analyzed_file_name = uploaded_file.name

        status.update(label="Analyse terminée avec succès.", state="complete")


# Affichage persistant des résultats (indépendant des ré-exécutions lors du clic sur les boutons d'export)
if st.session_state.analysis is not None:
    analysis = st.session_state.analysis
    chunks = st.session_state.chunks
    json_path = st.session_state.json_path
    csv_path = st.session_state.csv_path

    st.success("L'analyse a été réalisée avec succès.")

    if analysis.get("coverage_warning"):
        st.warning(analysis["coverage_warning"])

    st.markdown("## 📊 Résultats de l'évaluation")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.metric(
            label="Critères évalués",
            value=len(analysis.get("criteria", [])),
        )

    with col_b:
        st.metric(
            label="Passages analysés",
            value=len(chunks),
        )

    with col_c:
        citations_valides = sum(
            1 for c in analysis.get("citations_validees", [])
            if c.get("status") == "citation_valide"
        )
        total_citations = len(analysis.get("citations_validees", []))
        st.metric(
            label="Citations vérifiées",
            value=f"{citations_valides}/{total_citations}",
        )

    st.divider()

    for criterion in analysis.get("criteria", []):
        raw_status = criterion.get("status", "")
        pres = get_status_presentation(raw_status)

        st.markdown(
            f"""
            <div class="result-card {pres['css_class']}">
                <div class="step-title">
                    {pres['icon']} {criterion.get('label', criterion.get('id', 'Critère'))}
                </div>
                <span class="badge {pres['badge_class']}">
                    {pres['label']}
                </span>
                <p>
                    {criterion.get('justification', '')}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        citations = criterion.get("citations", [])

        if citations:
            with st.expander(f"📄 Voir les citations sources ({len(citations)})"):
                for citation in citations:
                    page_info = citation.get('page')
                    page_str = f"Page {page_info}" if page_info else "Page non spécifiée"
                    st.markdown(
                        f"""
                        <div class="citation-box">
                            <strong>Passage :</strong> {citation.get('chunk_id', 'Inconnu')} &nbsp;|&nbsp; <strong>{page_str}</strong><br>
                            <strong>Extrait cité :</strong><br>
                            <em>« {citation.get('text', '')} »</em>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        if criterion.get("human_check_needed"):
            st.warning("⚠️ Une vérification humaine complémentaire est recommandée pour ce critère.")

    st.divider()

    st.markdown("## 📥 Télécharger les résultats")

    col_download_1, col_download_2 = st.columns(2)

    with col_download_1:
        if json_path and Path(json_path).exists():
            with open(json_path, "r", encoding="utf-8") as file:
                json_data = file.read()

            st.download_button(
                label="Télécharger le rapport JSON",
                data=json_data,
                file_name=Path(json_path).name,
                mime="application/json",
                use_container_width=True,
            )

    with col_download_2:
        if csv_path and Path(csv_path).exists():
            with open(csv_path, "r", encoding="utf-8-sig") as file:
                csv_data = file.read()

            st.download_button(
                label="Télécharger le rapport CSV",
                data=csv_data,
                file_name=Path(csv_path).name,
                mime="text/csv",
                use_container_width=True,
            )

    st.markdown(
        """
        <div class="warning-box">
            <strong>⚠️ Aide non substitutive</strong><br>
            Les résultats générés sont une assistance à la lecture critique.
            Ils doivent systématiquement être vérifiés par un lecteur humain qualifié.
            L'outil ne remplace pas une lecture intégrale de l'article ni une expertise méthodologique ou médicale.
        </div>
        """,
        unsafe_allow_html=True,
    )
