# Analyseur Budgétaire Automatisé

Système d'analyse automatique des bilans budgétaires des collectivités territoriales françaises (format DGFiP) avec génération de rapports via LLM.

## 📋 Vue d'ensemble

Ce projet permet de :
1. **Parser** des fichiers PDF budgétaires (format DGFiP)
2. **Extraire** automatiquement toutes les données financières
3. **Calculer** les ratios et indicateurs clés
4. **Structurer** les données en JSON avec métadonnées de contexte
5. **Générer** un rapport d'analyse via LLM (Ollama local)

## 🗂️ Structure du projet

```
CODEBASE/
├── src/
│   ├── parsers/          # Extraction et parsing des PDFs
│   ├── generators/       # Génération de rapports et visualisations
│   ├── analysis/         # Outils d'analyse et validation
│   ├── utils.py          # Fonctions utilitaires
│   ├── converter.py      # Conversions de formats
│   └── refactor_script.py
│
├── tests/                # Scripts de test
├── docs/                 # PDFs sources et documentation
├── output/               # Fichiers générés (JSON, rapports)
├── venv/                 # Environnement virtuel Python
│
├── main.py               # Point d'entrée principal
├── README.md             # Ce fichier
└── CLAUDE.md             # Guidelines de développement
```

## 📁 Détail des modules

### 🔍 `src/parsers/` - Extraction des données

| Fichier | Description |
|---------|-------------|
| **`parser_budget.py`** | Parser principal : extrait TOUTES les données du PDF bilan (fonctionnement, investissement, fiscalité, etc.) via regex déterministes |
| **`pdf_extractor.py`** | Extraction des métadonnées : nom commune, population, strate, exercice |
| `parser_budget_v2_complet.py` | Version alternative du parser (legacy) |

**Usage :**
```python
from src.parsers.parser_budget import parser_bilan_pdf
budget = parser_bilan_pdf('docs/bilan.pdf')
```

### 🎯 `src/generators/` - Génération de rapports

| Fichier | Description |
|---------|-------------|
| **`generer_json_llm.py`** | ⭐ **MODULE CLÉ** : Transforme les données brutes en JSON structuré avec contexte et métadonnées pour le LLM |
| **`generer_rapport_llm.py`** | ⭐ **MODULE CLÉ** : Interface avec Ollama pour générer le rapport d'analyse en langage naturel |
| `generateur_rapport_ameliore.py` | Génération de rapports PDF avec graphiques |
| `graphiques.py` | Création de visualisations (matplotlib) |
| `rapport.py` | Génération de rapports statiques |

**Usage principal :**
```python
# Génération JSON structuré
from src.generators.generer_json_llm import generer_json_pour_llm
json_data = generer_json_pour_llm('docs/bilan.pdf')

# Génération rapport via LLM
from src.generators.generer_rapport_llm import generer_rapport_par_sections
rapport = generer_rapport_par_sections('docs/bilan.pdf', model='llama3.2')
```

### 📊 `src/analysis/` - Analyse et validation

| Fichier | Description |
|---------|-------------|
| `analyseur_texte.py` | Analyse textuelle des données |
| `comparer_donnees.py` | Comparaison entre exercices ou communes |
| `detecteur_lignes_manquantes.py` | Détection de données manquantes |
| `systeme_surveillance.py` | Surveillance et alertes |
| `verifier_extraction.py` | Validation de l'extraction |

### 🧪 `tests/` - Scripts de test

- `test_ollama.py` : Test de génération de rapport via Ollama
- `test_rapport_ameliore.py` : Test de génération PDF
- `test_refactoring.py` : Tests divers

## 🚀 Installation

### Prérequis

```bash
# Python 3.8+
python --version

# Installer les dépendances
pip install pdfplumber fpdf requests matplotlib
```

### Configuration Ollama (pour LLM local)

```bash
# 1. Télécharger Ollama : https://ollama.ai

# 2. Télécharger un modèle
ollama pull llama3.2

# 3. Lancer le serveur Ollama
ollama serve
```

## 📖 Guide d'utilisation

### Workflow complet

```python
# 1. Parser le PDF
from src.parsers.parser_budget import parser_bilan_pdf
budget = parser_bilan_pdf('docs/bilan.pdf')

# 2. Générer le JSON structuré
from src.generators.generer_json_llm import generer_json_pour_llm, sauvegarder_json
json_data = generer_json_pour_llm('docs/bilan.pdf')
sauvegarder_json(json_data, 'output/budget_structure.json')

# 3. Générer le rapport d'analyse via LLM
from src.generators.generer_rapport_llm import generer_rapport_par_sections
rapport = generer_rapport_par_sections(
    'docs/bilan.pdf',
    model='llama3.2',
    fichier_sortie='output/rapport_analyse.txt'
)
```

### Script de test rapide

```bash
# Test complet avec Ollama
python tests/test_ollama.py
```

### Via le main

```bash
python main.py
```

## 🧠 Architecture LLM

### Principe

```
PDF Bilan
    ↓
[Parser] → Données brutes (dict)
    ↓
[Calculateur] → Ratios, écarts, contextes
    ↓
[JSON Builder] → JSON structuré avec métadonnées
    ↓
[Prompt Builder] → Prompt optimisé
    ↓
[Ollama LLM] → Rapport en langage naturel
```

### Structure JSON

Le JSON généré contient :
- **Chiffres bruts** : montants, par habitant, moyennes strate
- **Calculs faits** : ratios, pourcentages, écarts
- **Contexte intelligent** :
  - `comparaison_strate` : "egal", "superieur", "tres_superieur", etc.
  - `niveau` : "excellent", "bon", "moyen", "faible", "tres_eleve"
  - `alerte` : `true`/`false` pour signaler les points critiques
  - Métadonnées exploitables : "marge_disponible", "couvre_investissements"

### Pourquoi cette approche ?

✅ **Pas d'hallucination** : tous les calculs sont faits en Python (déterministe)
✅ **LLM comme rédacteur** : il transforme juste les données en texte fluide
✅ **Contexte pré-calculé** : le LLM sait ce qui est "bon" ou "alerte"
✅ **Économique** : ~3000 tokens = $0.03-0.04 par rapport (ou gratuit avec Ollama)

## 🎯 Modules clés

### 1. `parser_budget.py` - Le parser déterministe

Extrait **100% déterministe** (aucune hallucination) :
- Section Fonctionnement (produits, charges, résultat)
- Section Investissement (ressources, emplois)
- Section Autofinancement (EBF, CAF brute/nette)
- Section Endettement (encours, annuité, capacité désendettement)
- Section Fiscalité (bases, taux, produits)

### 2. `generer_json_llm.py` - Le structureur intelligent

Transforme les données brutes en JSON exploitable :
- Calcule tous les ratios clés
- Compare à la strate (écarts en %)
- Génère des métadonnées de contexte
- Identifie automatiquement les alertes

### 3. `generer_rapport_llm.py` - Le générateur de rapport

Deux modes :
- **Mode 1 requête** : Plus rapide (1-2 min)
- **Mode sections** : Plus fiable, génère section par section (3-5 min)

## 📊 Modèles Ollama recommandés

| Modèle | Qualité | Vitesse | Français | Recommandation |
|--------|---------|---------|----------|----------------|
| `llama3.2` | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Recommandé |
| `mistral` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Excellent pour FR |
| `llama2` | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Rapide mais moins bon |
| `gemma2` | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Alternative solide |

## 🔧 Configuration

### Variables d'environnement (optionnel)

```bash
# URL Ollama (par défaut: http://localhost:11434)
export OLLAMA_URL="http://localhost:11434"

# Modèle par défaut
export OLLAMA_MODEL="llama3.2"
```

### Personnaliser le prompt

Modifiez `src/generators/generer_rapport_llm.py` fonction `construire_prompt()` pour adapter :
- La structure du rapport
- Le ton et style
- Les sections à générer
- Les règles d'interprétation

## 📈 Exemples de résultats

### JSON structuré (`output/budget_pour_llm.json`)

```json
{
  "synthese": {
    "resultat_fonctionnement_k": 105,
    "caf_brute_k": 107,
    "ratio_dette_caf_annees": 3.73,
    "contexte": {
      "sante_financiere": "bonne",
      "capacite_desendettement": "excellent"
    }
  },
  "fonctionnement": {
    "charges": {
      "detail": {
        "charges_personnel": {
          "montant_k": 107,
          "pct_total": 37.42,
          "contexte": {
            "comparaison_strate": "tres_superieur",
            "ecart_strate_pct": 52.0,
            "niveau": "tres_eleve",
            "alerte": true
          }
        }
      }
    }
  }
}
```

### Rapport généré (`output/rapport_analyse.txt`)

```
RAPPORT D'ANALYSE BUDGÉTAIRE
==================================================

Commune: MARCOLS-LES-EAUX
Exercice: 2024
Population: 279 habitants

SYNTHÈSE GÉNÉRALE
-----------------

La commune de MARCOLS-LES-EAUX présente une situation financière
globalement saine avec un résultat de fonctionnement excédentaire
de 105 k€ et une capacité d'autofinancement brute de 107 k€...

[Point de vigilance] Les charges de personnel s'élèvent à 107 k€,
représentant 37,4% des charges totales, un niveau nettement
supérieur à la strate (+52%)...
```

## 🐛 Dépannage

### Ollama ne répond pas

```bash
# Vérifier qu'Ollama tourne
curl http://localhost:11434/api/tags

# Relancer le serveur
ollama serve
```

### Erreur de parsing PDF

- Vérifier que le PDF est au format DGFiP standard
- Tester avec `verifier_extraction.py`

### Rapport incomplet

- Essayer le mode "par sections" au lieu d'1 requête
- Augmenter le timeout dans `generer_rapport_llm.py`
- Vérifier que le modèle Ollama est bien téléchargé

## 📝 TODO / Améliorations futures

- [ ] Support de plusieurs PDFs en batch
- [ ] Comparaison multi-exercices
- [ ] Export en PDF avec graphiques
- [ ] Dashboard web interactif
- [ ] Support d'autres formats de bilans
- [ ] Analyse prédictive (tendances)

## 📄 Licence

Projet académique - Usage libre pour formation

## 👤 Auteur

Projet développé dans le cadre d'une étude technique en IA

---

**Note** : Ce README est généré automatiquement. Consultez `CLAUDE.md` pour les guidelines de développement.
