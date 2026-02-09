# Guide Rapide - Génération de Rapport Budgétaire

## 🚀 Démarrage rapide (3 étapes)

### 1. Installer les dépendances

```bash
pip install pandas odfpy reportlab matplotlib python-docx openai
```

### 2. Configurer la clé API OpenAI

**Windows PowerShell** :
```powershell
$env:OPENAI_API_KEY = "votre-cle-api-ici"
```

**Windows CMD** :
```cmd
set OPENAI_API_KEY=votre-cle-api-ici
```

### 3. Lancer le workflow automatique

```bash
python workflow_complet.py
```

Le script vous guidera pour choisir entre :
- Rapport mono-année
- Rapport multi-années

Et générera automatiquement **tout** de A à Z ! 🎉

---

## 📁 Fichiers générés

### Rapport mono-année
- `output/donnees_enrichies.json` - Données enrichies avec ratios
- `PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx` - Prompts et réponses
- `output/rapport_analyse_mono_annee.pdf` - Rapport PDF final
- `output/rapport_analyse_mono_annee.docx` - Rapport Word final

### Rapport multi-années
- `output/donnees_multi_annees.json` - Données multi-années
- `PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx` - Prompts et réponses
- `output/rapport_analyse_multi_annees.pdf` - Rapport PDF final
- `output/rapport_analyse_multi_annees.docx` - Rapport Word final

---

## ⚙️ Configuration avancée

### Modifier le modèle OpenAI

Éditez `generer_reponses_avec_openai.py` :

```python
MODEL = "gpt-4.1-mini"  # Par défaut
# Ou utilisez :
# MODEL = "gpt-4-turbo"
# MODEL = "gpt-3.5-turbo"
```

### Modifier la température (créativité)

```python
TEMPERATURE = 0.7  # Par défaut (0.0 = déterministe, 1.0 = créatif)
```

### Modifier la longueur des réponses

```python
MAX_TOKENS = 2000  # Par défaut
```

---

## 🔧 Dépannage

### ❌ "OPENAI_API_KEY not found"
→ Vérifiez que la variable d'environnement est bien configurée

### ❌ "Rate limit exceeded"
→ Augmentez `DELAI_ENTRE_REQUETES` dans `generer_reponses_avec_openai.py`

### ❌ "Model not found: gpt-4.1-mini"
→ Vérifiez que le modèle existe ou changez pour `gpt-4-turbo` ou `gpt-3.5-turbo`

### ❌ Réponses tronquées
→ Augmentez `MAX_TOKENS` dans `generer_reponses_avec_openai.py`

---

## 💰 Estimation des coûts

Pour GPT-4.1 mini :
- ~20-30 prompts par rapport
- ~500 tokens par prompt
- ~500 tokens par réponse
- **Coût total : quelques centimes** par rapport complet

Pour GPT-4-turbo :
- **Coût total : quelques dizaines de centimes** par rapport complet

---

## 📚 Documentation complète

Consultez [README_OPENAI.md](README_OPENAI.md) pour :
- Workflow manuel étape par étape
- Liste complète des modèles disponibles
- Configuration détaillée
- Exemples d'utilisation avancée
