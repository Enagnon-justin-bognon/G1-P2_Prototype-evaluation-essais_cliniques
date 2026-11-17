# 🩺 Prototype d'aide à la lecture critique des essais cliniques

> **Groupe G1-P2**  
> Outil d'assistance méthodologique et biostatistique pour l'évaluation des essais cliniques randomisés (ECR) en groupes parallèles.

---

## 🎯 Objectif du projet

Ce prototype est une **aide à la lecture critique** d'articles scientifiques publiés au format PDF. 

Il a pour vocation d'assister les cliniciens, méthodologistes, pharmaciens ou chercheurs à repérer, extraire et évaluer rapidement les composantes méthodologiques et statistiques fondamentales relatives au **critère de jugement principal** (*primary endpoint*).

> ⚠️ **Avertissement éthique & méthodologique** :  
> Cet outil constitue une **aide non substitutive**. Il ne remplace en aucun cas le jugement critique humain, l'expertise médicale ou une lecture intégrale de l'article. L'absence de mention d'un élément dans le texte ne prouve pas nécessairement une mauvaise conduite de l'essai, mais signale un manque de transparence dans le compte rendu.

---

## 📐 Cadre méthodologique & Grille d'évaluation

L'évaluation s'appuie sur une grille structurée de **8 critères** définie dans [`config/grille.yaml`](config/grille.yaml), alignée sur les standards internationaux de la recherche clinique :

* **RoB 2 (Cochrane)** : Évaluation du risque de biais dans les essais randomisés.
* **CONSORT 2025** : Transparence et exhaustivité du compte rendu des essais.
* **ICH E9 & E9(R1)** : Principes statistiques, cadre des estimands et gestion des événements intercurrents.

### Les 8 critères évalués :
1. **Randomisation et dissimulation de l'allocation** *(RoB 2)* : Génération de la séquence aléatoire et préservation du secret de l'attribution.
2. **Aveuglement / Insu** *(RoB 2 / CONSORT)* : Mise en œuvre du double/simple aveugle pour les patients, soignants, évaluateurs des critères et biostatisticiens.
3. **Écarts aux interventions prévues** *(RoB 2)* : Gestion de l'observance, des interruptions de traitement et des co-interventions.
4. **Données manquantes et perdus de vue** *(RoB 2 / CONSORT / ICH E9)* : Quantification des perdus de vue sur le critère principal et validité des méthodes d'imputation/analyse.
5. **Mesure du critère de jugement principal** *(RoB 2)* : Outils de mesure, validité métrologique, calendrier de recueil et qualification des évaluateurs.
6. **Taille de l'échantillon et puissance** *(CONSORT 2025)* : Justification de l'effectif calculé, hypothèses d'effet attendu, risques alpha et bêta.
7. **Analyse principale et population** *(ICH E9(R1) / CONSORT)* : Population analysée (intention de traiter - ITT, ITT modifiée, per protocole), estimand ciblé et traitement des événements intercurrents.
8. **Résultats, précision et sensibilité** *(CONSORT / ICH E9)* : Estimation de la taille de l'effet, intervalles de confiance à 95 %, valeurs p et robustesse via analyses de sensibilité.

### Statuts standardisés attribués :
Chaque critère est qualifié selon l'une des 5 propositions officielles :
* ✅ **`information_rapportee_clairement`** : L'information requise est explicitement et exhaustivement décrite.
* ⚡ **`information_rapportee_partiellement`** : L'information est mentionnée mais incomplète.
* ❓ **`information_ambigue`** : Les éléments rapportés sont flous, contradictoires ou imprécis.
* 🔍 **`information_non_retrouvee`** : L'élément recherché n'apparaît nulle part dans le document analysé.
* 🧐 **`a_verifier_humainement`** : Une interprétation humaine complexe ou un doute méthodologique spécifique subsiste.

---

## ⚙️ Pipeline de traitement & Système anti-hallucination

```
   ┌─────────────────┐
   │   Article PDF   │ (Texte intégral, format multi-colonnes)
   └────────┬────────┘
            │
            ▼
┌───────────────────────┐
│     src/ingest.py     │ Extraction PyMuPDF avec tri des colonnes (`sort=True`)
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│    src/chunker.py     │ Découpage en passages identifiés avec chevauchement (overlap 200 car.)
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│   src/analyzer.py     │ Requête LLM Google Gemini (Structured Outputs JSON)
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│   src/validator.py    │ 🛡️ VALIDATION ANTI-HALLUCINATION
│                       │ Vérification textuelle exacte/normalisée des citations
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│        app.py         │ Interface Streamlit interactive, cartes visuelles,
│                       │ citations sourcées (avec numéros de pages) et exports
└───────────────────────┘
```

### Le verrou anti-hallucination :
Dans le domaine médical, l'exactitude des preuves est primordiale. Chaque citation fournie par Gemini est vérifiée par `src/validator.py` contre le texte original extrait :
* 🟢 **Citation vérifiée** : L'extrait est rigoureusement présent dans le passage indiqué.
* 🔴 **Citation non concordante** : Le modèle a tronqué ou reformulé le texte de manière non conforme.
* ⚪ **Passage non localisé** : L'identifiant du passage n'existe pas.

---

## 📁 Structure du dépôt

```text
├── app.py                  # Interface web Streamlit
├── config/
│   └── grille.yaml         # Grille d'évaluation méthodologique (indépendante du code)
├── src/
│   ├── ingest.py           # Ingestion PDF avec ordre de lecture naturel (PyMuPDF)
│   ├── chunker.py          # Découpage avec chevauchement contextuel
│   ├── analyzer.py         # Moteur d'analyse IA (Google Gemini 1.0+ SDK)
│   ├── validator.py        # Contrôle anti-hallucination et localisation des pages
│   ├── storage.py          # Sauvegarde horodatée des analyses en JSON
│   ├── export.py           # Export tabulaire des résultats en CSV
│   └── config.py           # Chargement et validation de la grille YAML
├── tests/                  # Suite de tests unitaires automatisés (pytest)
│   ├── test_chunker.py
│   ├── test_config.py
│   ├── test_export.py
│   ├── test_ingest.py
│   ├── test_storage.py
│   └── test_validator.py
├── .env.example            # Gabarit des variables d'environnement
├── requirements.txt        # Dépendances Python
└── README.md
```

---

## 🚀 Installation et exécution locale

### 1. Prérequis
* Python 3.10 ou supérieur
* Une clé d'API Google AI Studio (Gemini)

### 2. Cloner le projet
```bash
git clone https://github.com/Enagnon-justin-bognon/G1-P2_Prototype-evaluation-essais_cliniques.git
cd G1-P2_Prototype-evaluation-essais_cliniques
```

### 3. Créer et activer l'environnement virtuel
```bash
# Sous Windows (PowerShell) :
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Sous Linux / macOS :
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 5. Configurer la clé d'API
Créez un fichier `.env` à la racine du projet (copiez `.env.example`) :
```env
GEMINI_API_KEY=votre_cle_api_secrete
GEMINI_MODEL=gemini-3.5-flash
```

### 6. Lancer l'application
```bash
streamlit run app.py
```
L'application s'ouvrira automatiquement à l'adresse `http://localhost:8501`.

---

## 🧪 Tests unitaires

Pour exécuter l'ensemble des tests de validation :
```bash
pytest -v
```

---

## 🔒 Sécurité et bonnes pratiques

* **Protection des clés secrètes** : Le fichier `.env` et les secrets Streamlit (`.streamlit/secrets.toml`) sont strictement exclus du dépôt via `.gitignore`.
* **Confidentialité** : Les fichiers PDF téléversés sont traités dans des répertoires temporaires auto-nettoyés dès l'extraction achevée.
