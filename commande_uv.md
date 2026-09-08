# Initialisation de la commande uv

`uv init . --python=3.12`

# Intialiser le virtual environment
`uv venv --python=3.12`

# Activer le virtual environment
## sous macOS / Linux
`source .venv/bin/activate`
## sous Windows
`.venv\Scripts\activate`


# Créer le requirements.txt

créer un fichier à la racine du projet nommé `requirements.txt` et y ajouter les dépendances nécessaires.
Par exemple :
```
openai>=1.30
langchain>=0.3
langchain-openai>=0.2
nh3
```

# Installer les dépendances

` uv add -r requirements.txt`