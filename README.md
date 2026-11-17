# Prototype d'aide à l'évaluation des essais cliniques

## Objectif du projet

Ce prototype est une **aide à la lecture critique** d'essais cliniques publiés.

Il ne remplace pas le jugement humain.

Il vise à aider un lecteur à repérer, dans un article, les éléments méthodologiques et statistiques importants concernant le **critère principal**.

## Périmètre actuel

Le prototype analyse uniquement :

- les essais cliniques randomisés en groupes parallèles ;
- les articles disponibles en texte intégral ;
- le critère principal de l'essai ;
- une grille de 8 critères.

## Grille d'évaluation

La grille distingue trois types d'informations :

- RoB 2 : risque de biais ;
- CONSORT 2025 : transparence du compte rendu ;
- ICH E9 et E9(R1) : principes statistiques.

Les 8 critères sont :

1. Randomisation
2. Aveuglement
3. Écarts aux interventions prévues
4. Données manquantes
5. Mesure du résultat principal
6. Taille de l'échantillon
7. Analyse principale et population analysée
8. Résultats et précision

## Fonctionnement

1. L'utilisateur téléverse un PDF.
2. Le texte est extrait page par page.
3. Le texte est découpé en passages identifiables.
4. Le modèle analyse le critère principal selon la grille.
5. Les citations sont vérifiées automatiquement.
6. Les résultats sont affichés et exportables.

## Technologies utilisées

- Python
- Streamlit
- Gemini
- pypdf
- pytest

## Installation locale

1. Cloner le dépôt.
2. Créer un environnement virtuel.
3. Installer les dépendances.

```bash
pip install -r requirements.txt
```

4. Créer un fichier `.env` avec les variables suivantes :

```env
GEMINI_API_KEY= cle_api
GEMINI_MODEL= gemini-2.0-flash
```

5. Lancer l'application.

```bash
streamlit run app.py
```

## Sécurité

La clé API ne doit jamais être partagée ou publiée.

Les fichiers suivants doivent rester hors du dépôt :

- `.env`
- `.streamlit/secrets.toml`

## Limites connues

- L'outil ne remplace pas une lecture critique humaine.
- L'absence d'une mention ne prouve pas une mauvaise conduite de l'essai.
- Les PDF scannés peuvent ne pas être analysés correctement.
- Les citations doivent toujours être vérifiées par un humain.
- Le périmètre est limité aux essais en groupes parallèles.

## Tests

Pour lancer les tests :

```bash
pytest
```

## Déploiement

L'application est déployée sur Streamlit Community Cloud.

Le déploiement nécessite :

- un dépôt GitHub ;
- un fichier `requirements.txt` ;
- un fichier d'entrée `app.py` ;
- les secrets configurés dans Streamlit Cloud.

Streamlit Community Cloud permet de déployer une application à partir d'un dépôt GitHub et d'un fichier d'entrée.