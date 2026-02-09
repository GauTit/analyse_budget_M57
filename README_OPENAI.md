# Génération automatique de rapports budgétaires avec OpenAI

## ⚡ Workflow complet automatisé (RECOMMANDÉ)

### Script maître tout-en-un

Utilisez le script `workflow_complet.py` pour exécuter automatiquement toutes les étapes :

```bash
python workflow_complet.py
```

Le script vous demandera :
1. **Mono-année ou multi-années ?**
2. Confirmation avant de lancer le workflow

Puis il exécutera automatiquement dans l'ordre :
1. ✅ Génération/enrichissement du JSON
2. ✅ Génération des prompts enrichis
3. ✅ Appel à l'API OpenAI pour générer les réponses
4. ✅ Génération du rapport PDF
5. ✅ Génération du rapport Word

**Avantage** : Un seul script, tout est automatisé. Pas besoin d'exécuter les scripts un par un.

---

## Configuration

### 1. Installer les dépendances

```bash
pip install pandas odfpy reportlab matplotlib python-docx openai
```

Ou utiliser le fichier `requirements.txt` :
```bash
bash requirements.txt
```

### 2. Configurer la clé API OpenAI

Vous devez obtenir une clé API OpenAI depuis [platform.openai.com](https://platform.openai.com).

#### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY = "votre-cle-api-ici"
```

#### Windows (CMD)
```cmd
set OPENAI_API_KEY=votre-cle-api-ici
```

#### Linux/Mac
```bash
export OPENAI_API_KEY=votre-cle-api-ici
```

Pour une configuration permanente, ajoutez la clé dans vos variables d'environnement système.

## 📋 Workflow manuel (étape par étape)

Si vous préférez exécuter les étapes manuellement :

### Étape 1 : Enrichir le JSON avec les ratios financiers

```bash
python enrichir_json_avec_ratios.py
```

Cela crée/met à jour :
- `output/donnees_enrichies.json` (mono-année)
- `output/donnees_multi_annees.json` (multi-années)

### Étape 2 : Générer les prompts enrichis

```bash
python generer_prompts_enrichis_depuis_json.py
```

Cela met à jour l'Excel `PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx` avec :
- Les données injectées dans chaque prompt
- Les prompts complets prêts à être envoyés à l'API

### Étape 3 : Générer les réponses avec OpenAI GPT-4.1 mini

```bash
python generer_reponses_avec_openai.py
```

Le script va :
1. Lire tous les prompts de l'Excel
2. Appeler l'API OpenAI pour chaque prompt
3. Écrire les réponses dans la colonne `Reponse_Attendue`
4. Sauvegarder l'Excel mis à jour

**Note** : Le script traite uniquement les lignes qui ont un prompt mais pas encore de réponse.

### Étape 4 : Générer le rapport final

#### Format PDF
```bash
python generer_rapport_excel_vers_pdf.py
```

#### Format Word
```bash
python generer_rapport_excel_vers_word.py
```

Les rapports sont générés dans le dossier `output/`.

## Configuration du script OpenAI

Vous pouvez modifier les paramètres dans `generer_reponses_avec_openai.py` :

```python
# Modèle à utiliser
MODEL = "gpt-4.1-mini"  # Changez selon vos besoins

# Paramètres de l'API
TEMPERATURE = 0.7  # Créativité (0.0 = déterministe, 1.0 = créatif)
MAX_TOKENS = 2000  # Longueur maximale de la réponse

# Délai entre les requêtes (en secondes)
DELAI_ENTRE_REQUETES = 1
```

## Modèles OpenAI disponibles

- `gpt-4.1-mini` : Rapide et économique
- `gpt-4` : Plus puissant mais plus coûteux
- `gpt-4-turbo` : Bon compromis performance/coût
- `gpt-3.5-turbo` : Le plus rapide et économique

## Coûts estimés

Pour GPT-4.1 mini (prix indicatifs, vérifiez sur [openai.com/pricing](https://openai.com/pricing)) :
- ~20-30 prompts dans l'Excel
- ~500 tokens par prompt en entrée
- ~500 tokens par réponse en sortie
- Coût total estimé : quelques centimes par génération complète

## Dépannage

### Erreur "OPENAI_API_KEY not found"
Assurez-vous d'avoir configuré la variable d'environnement correctement.

### Rate limit errors
Si vous avez trop de requêtes, augmentez `DELAI_ENTRE_REQUETES` dans le script.

### Réponses incomplètes
Augmentez `MAX_TOKENS` si les réponses sont tronquées.

### Erreur de modèle
Vérifiez que le modèle `gpt-4.1-mini` existe. Sinon, utilisez `gpt-4-turbo` ou `gpt-3.5-turbo`.
