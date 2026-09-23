<h1 align="center">🤖 rooted-agent</h1>

<p align="center">
  Un agent IA en ligne de commande, propulsé par un modèle local (Ollama).<br/>
  <sub>Chat · Lecture de fichiers · Outils · Mémoire · Espaces de travail</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white"/>&nbsp;
  <img src="https://img.shields.io/badge/LLM-Ollama-000000?style=flat&logo=ollama&logoColor=white"/>&nbsp;
  <img src="https://img.shields.io/badge/Interface-CLI-555?style=flat"/>&nbsp;
  <img src="https://img.shields.io/badge/Statut-Projet%20perso-15803d?style=flat"/>&nbsp;
  <img src="https://img.shields.io/badge/%C3%89tat-En%20pause-b45309?style=flat"/>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>
</p>

## Sommaire

- [Contexte](#-contexte)
- [Objectif du projet](#-objectif-du-projet)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Configuration](#-configuration)
- [Portée du projet](#-portée-du-projet)
- [Ce que ce projet m'a apporté](#-ce-que-ce-projet-ma-apporté)
- [Licence](#-licence)

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## 🎯 Contexte

**rooted-agent** est un agent conversationnel qui s'exécute entièrement en local, dans le terminal. Il s'appuie sur [Ollama](https://ollama.com) pour faire tourner un modèle de langage (par défaut `qwen2.5:7b-instruct`) **sans dépendre d'une API cloud** : aucune donnée n'est envoyée à l'extérieur, tout reste sur la machine.

Le point de départ était une conviction simple : **ne dépendre d'aucune IA cloud** -> ni payante, ni bridée, ni ayant accès à mes données. Je voulais un assistant qui tourne chez moi, sur mon matériel, et sous mon contrôle.

Au-delà de la confidentialité, l'objectif était d'apprendre : comprendre, en le construisant moi-même, **comment fonctionne un agent IA**. La gestion d'une conversation, l'injection d'un contexte (instructions système, mémoire), et surtout le mécanisme d'**appel d'outils** (tool calling) qui permet au modèle d'agir sur le système soit créer et éditer des fichiers, lire des documents, générer des diagrammes.

> ℹ️ **Preuve de concept.** J'ai mené ce projet jusqu'à comprendre l'essentiel du fonctionnement d'un agent IA, puis je l'ai mis en pause (voir [Portée du projet](#-portée-du-projet)). Il documente une étape de mon apprentissage sur les agents et l'IA locale.

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## 💡 Objectif du projet

- **Construire un agent IA de A à Z**, plutôt que d'utiliser un framework tout fait.
- **Rester 100 % local et privé** grâce à Ollama —> pas de clé API, pas de cloud.
- **Implémenter le tool calling** : donner au modèle la capacité d'agir (fichiers, diagrammes, recherche).
- **Gérer un contexte riche** : message système, instructions développeur, mémoire persistante, spécialisations.
- **Offrir une expérience terminal soignée** : sélection de fichiers, espaces de travail, rendu Markdown.

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **Chat local** | Conversation en streaming avec un modèle Ollama, rendu en Markdown |
| **Appel d'outils** | Le modèle peut créer, éditer des fichiers et générer des diagrammes |
| **Lecture de fichiers** | Support de `.txt`, `.md`, code, `.json`, `.docx`, `.odt`, `.pdf` |
| **Espaces de travail** | Sélection d'un dossier/fichiers de référence ajoutés au contexte |
| **Mémoire** | Contexte persistant (préférences, projets) injecté dans la conversation |
| **Spécialisations** | Profils d'expertise activables (ex. « code expert ») |
| **Confirmations** | Les actions sensibles (écriture de fichier) demandent une validation |
| **Whitelist** | Les opérations sont restreintes à des dossiers autorisés |

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## 🏗️ Architecture

```
rooted-agent/
├── main.py                  # Point d'entrée — boucle de chat (Typer + Rich)
│
├── core/                    # Cœur de l'agent
│   ├── llmEngine.py         # Communication avec l'API Ollama (stream / outils)
│   ├── chatBuilder.py       # Assemble le contexte (système + mémoire + specialisation)
│   ├── toolsManager.py      # Registre et exécution des outils
│   ├── commandHandler.py    # Commandes internes ($load, $workspace, $exit…)
│   ├── filesManager.py      # Sélecteur de fichiers/dossiers interactif
│   ├── memoryManager.py     # Conversion de la mémoire en contexte
│   ├── system.py            # Chemins, confirmations, backups, whitelist
│   └── notifications.py     # Affichage console
│
├── tools/                   # Outils disponibles pour le modèle
│   ├── read_file.py         # Lecture multi-formats
│   ├── make_file.py         # Création de fichiers
│   ├── edit_file.py         # Édition de fichiers (avec validation JSON, docx, odt)
│   ├── diagram.py           # Rendu de diagrammes Mermaid / Graphviz
│   └── fake_web.py          # Recherche web simulée (placeholder)
│
├── config/                  # Configuration (JSON)
│   ├── default.json         # Modèle, température, API Ollama, whitelist
│   ├── systemMessages.json  # Message système de l'agent
│   ├── developerInstructions.json
│   └── specializations/     # Profils d'expertise
│
└── data/
    └── memory.json          # Mémoire persistante
```

**Le flux d'une requête :** l'utilisateur écrit → `chatBuilder` assemble le contexte → `llmEngine` interroge Ollama → si le modèle demande un outil, `toolsManager` l'exécute (après confirmation) → la réponse finale est rendue en Markdown.

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## 📦 Installation

**Prérequis :** [Ollama](https://ollama.com) installé et lancé, avec un modèle téléchargé.

```bash
# 1. Cloner le dépôt
git clone https://github.com/mg-root/rooted-agent.git
cd rooted-agent

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Récupérer le modèle par défaut
ollama pull qwen2.5:7b-instruct
```

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## 🚀 Utilisation

```bash
python main.py chat              # démarre une conversation
python main.py chat --include-tools   # active l'appel d'outils
```

**Commandes internes** (préfixe `$`) :

| Commande | Rôle |
|----------|------|
| `$load` | Charger des fichiers dans le contexte |
| `$workspace` | Définir un espace de travail (dossier ou fichiers) |
| `$workspace -get` | Afficher l'espace de travail courant |
| `$workspace -remove` | Réinitialiser l'espace de travail |
| `$exit` | Quitter |

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## ⚙️ Configuration

Tout se règle dans `config/default.json` :

```json
{
    "model": "qwen2.5:7b-instruct",
    "temperature": 0.2,
    "ollama_api": "http://localhost:11434/api",
    "whitelist_workspaces": ["/chemin/autorisé"],
    "prefix": "$"
}
```

- **`model`** — le modèle Ollama utilisé.
- **`whitelist_workspaces`** — les seuls dossiers où l'agent peut lire/écrire.
- **`prefix`** — le préfixe des commandes internes.

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## 🚧 Portée du projet

Ce projet est une **preuve de concept**, développée fin 2025 pour l'apprentissage. Je l'ai mené jusqu'à ce que j'aie compris l'essentiel de ce que je voulais explorer : boucle de conversation, injection de contexte, appel d'outils ; puis mis en pause.

Deux raisons à cette pause, assumées :
- **La contrainte matérielle** : faire tourner en local un modèle assez capable pour aller au bout de l'idée demande des ressources (VRAM) que je n'avais pas ; un modèle 7B suffisait à valider le concept, pas à en faire un outil réellement puissant.
- **L'apprentissage visé était atteint :** j'avais compris ce que je cherchais à comprendre. J'ai depuis réinvesti ces acquis dans mon parcours en cybersécurité.

**Ce qui fonctionne**
- Boucle de chat en streaming avec Ollama
- Lecture multi-formats et espaces de travail
- Assemblage du contexte (système, mémoire, spécialisation)
- Outils de création / édition de fichiers et de diagrammes

**Ce qui n'a pas été poussé plus loin**
- Sauvegarde des conversations
- Système de backup automatique avant modification
- Recherche web réelle (aujourd'hui simulée)
- Tests automatisés

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## 🎓 Ce que ce projet m'a apporté

- **Le fonctionnement interne d'un agent IA** : boucle de conversation, gestion du contexte, appel d'outils.
- **L'intégration d'un LLM local** via l'API d'Ollama, en streaming comme en mode outils.
- **La conception d'une architecture modulaire** séparant cœur, outils et configuration.
- **Les enjeux de sécurité d'un agent qui agit sur le système** : whitelist de dossiers, confirmations avant écriture, sauvegardes.

<p align="center"><img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/></p>

## 📄 Licence

Distribué sous licence **MIT**.
