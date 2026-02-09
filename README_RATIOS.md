# Module de Calcul des Ratios Financiers

## Problème Identifié

Le rapport financier généré affichait un **ratio incorrect** pour la "Part des charges de personnel" :
- **Valeur affichée (FAUSSE)** : 39,3%
- **Valeur correcte** : 45,1%
- **Écart** : 5,8 points de pourcentage

### Cause
Le ratio était calculé par rapport aux **charges totales** (incluant opérations d'ordre) au lieu des **charges CAF** (charges réelles décaissables).

## Solution Mise en Place

### Nouveaux Fichiers Créés

1. **[ratios_financiers.py](ratios_financiers.py)** - Module principal
   - Calcule 10 ratios financiers essentiels
   - Fonctions de calcul individuelles pour chaque ratio
   - Fonction `calculer_tous_les_ratios()` pour tout calculer d'un coup
   - Fonction `enrichir_json_avec_ratios()` pour enrichir le JSON

2. **[enrichir_json_avec_ratios.py](enrichir_json_avec_ratios.py)** - Script d'enrichissement
   - Enrichit les fichiers JSON avec les ratios calculés
   - Crée une sauvegarde automatique avant modification
   - Ajoute une section `ratios_financiers` au JSON

3. **[generer_rapport_complet.py](generer_rapport_complet.py)** - Script orchestrateur
   - Exécute toute la chaîne de traitement
   - Enrichissement → Génération des prompts

4. **[ratios_supplementaires_futurs.py](ratios_supplementaires_futurs.py)** - Ratios additionnels
   - 16 ratios financiers supplémentaires
   - Prêts à être intégrés si besoin

5. **[RATIOS_CORRECTION.txt](RATIOS_CORRECTION.txt)** - Documentation complète
   - Rapport détaillé de la correction
   - Explications techniques

### Fichiers Modifiés

- **[generer_prompts_enrichis_depuis_json.py](generer_prompts_enrichis_depuis_json.py)**
  - Utilise maintenant les ratios pré-calculés du JSON
  - Plus de recalcul "à la volée" (source d'erreurs)
  - Ajout de ratios supplémentaires dans la synthèse globale

## Utilisation

### Workflow Complet (Automatique)

```bash
python generer_rapport_complet.py
```

Ce script exécute automatiquement :
1. Enrichissement du JSON avec les ratios
2. Génération des prompts enrichis

### Workflow Manuel (Étape par Étape)

#### Étape 1 : Enrichir le JSON avec les ratios

```bash
python enrichir_json_avec_ratios.py
```

Cette commande :
- Charge `output/donnees_enrichies.json`
- Calcule tous les ratios financiers
- Crée une sauvegarde `output/donnees_enrichies_AVANT_RATIOS.json`
- Ajoute la section `ratios_financiers` au JSON
- Sauvegarde le JSON enrichi

#### Étape 2 : Générer les prompts enrichis

```bash
python generer_prompts_enrichis_depuis_json.py
```

Cette commande :
- Charge le JSON enrichi avec les ratios
- Génère les prompts avec les ratios corrects
- Sauvegarde dans `PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx`

#### Étape 3 : Générer le rapport final

```bash
python generer_rapport_excel_vers_pdf.py
```

## Ratios Calculés

Le module calcule **10 ratios financiers** :

### 1. Part des charges de personnel
- **Formule** : charges_personnel / charges_caf × 100
- **Mesure** : Rigidité de la structure de fonctionnement

### 2. Taux d'épargne brute
- **Formule** : CAF brute / produits CAF × 100
- **Mesure** : Capacité à dégager de l'épargne

### 3. Taux d'épargne nette
- **Formule** : CAF nette / produits CAF × 100
- **Mesure** : Autofinancement disponible pour investir

### 4. Capacité de désendettement
- **Formule** : encours dette / CAF brute (en années)
- **Mesure** : Capacité à rembourser la dette
- **Seuil prudentiel** : < 12 ans

### 5. Ratio d'endettement
- **Formule** : encours dette / produits CAF × 100
- **Mesure** : Poids de la dette par rapport à la richesse

### 6. Ratio d'effort d'équipement
- **Formule** : dépenses équipement / produits CAF × 100
- **Mesure** : Part des produits consacrée à l'investissement

### 7. Ratio d'autonomie fiscale
- **Formule** : impôts locaux / produits CAF × 100
- **Mesure** : Part de la fiscalité locale dans les recettes

### 8. Ratio de rigidité du fonctionnement
- **Formule** : (charges personnel + charges financières) / produits CAF × 100
- **Mesure** : Part des charges incompressibles

### 9. Taux de couverture de l'investissement
- **Formule** : CAF nette / dépenses équipement × 100
- **Mesure** : Capacité à financer l'investissement par l'épargne propre

### 10. Part des achats et charges externes
- **Formule** : achats et charges externes / charges CAF × 100
- **Mesure** : Part des dépenses de gestion courante

## Exemple de Résultats (Champagnac 2024)

```
Part des charges de personnel.......... 45.1% (vs 39.3% incorrect)
Taux d'épargne brute................... 28.1%
Taux d'épargne nette................... 17.4%
Capacité de désendettement............. 2.2 années
Ratio d'endettement.................... 63.0%
Ratio d'effort d'équipement............ 38.8%
Ratio d'autonomie fiscale.............. 32.3%
Ratio de rigidité du fonctionnement.... 34.2%
Taux de couverture de l'investissement. 44.7%
Part des achats et charges externes.... 34.1%
```

## Structure du JSON Enrichi

Après enrichissement, le JSON contient une nouvelle section :

```json
{
  "metadata": { ... },
  "fonctionnement": { ... },
  "autofinancement": { ... },
  "investissement": { ... },
  "endettement": { ... },
  "ratios_financiers": {
    "part_charges_personnel_pct": 45.1,
    "taux_epargne_brute_pct": 28.1,
    "taux_epargne_nette_pct": 17.4,
    "capacite_desendettement_annees": 2.2,
    "ratio_endettement_pct": 63.0,
    "ratio_effort_equipement_pct": 38.8,
    "ratio_autonomie_fiscale_pct": 32.3,
    "ratio_rigidite_fonctionnement_pct": 34.2,
    "taux_couverture_investissement_pct": 44.7,
    "part_achats_externes_pct": 34.1
  }
}
```

## Ajouter de Nouveaux Ratios

Pour ajouter un nouveau ratio :

### 1. Dans `ratios_financiers.py`

```python
def calculer_nouveau_ratio(param1_k, param2_k):
    """Description du ratio"""
    if not param2_k or param2_k == 0:
        return None
    return round((param1_k / param2_k) * 100, 1)
```

### 2. Ajouter à `calculer_tous_les_ratios()`

```python
def calculer_tous_les_ratios(data_json):
    # ... extractions ...

    ratios = {
        # ... ratios existants ...
        'nouveau_ratio_pct': calculer_nouveau_ratio(param1_k, param2_k)
    }
    return ratios
```

### 3. Utiliser dans `generer_prompts_enrichis_depuis_json.py`

```python
nouveau_ratio = extraire_valeur_json(data_json, 'ratios_financiers.nouveau_ratio_pct') or 0
```

## Ratios Supplémentaires Disponibles

Le fichier [ratios_supplementaires_futurs.py](ratios_supplementaires_futurs.py) contient 16 ratios additionnels prêts à l'emploi :

- Ratios de fonctionnement (4)
- Ratios d'investissement (3)
- Ratios d'endettement (3)
- Ratios de trésorerie et liquidité (2)
- Ratios de performance (2)
- Ratios intercommunaux (2)

## Tests et Validation

Pour tester le module :

```bash
python ratios_financiers.py
```

Pour vérifier les ratios dans le JSON :

```bash
python -c "import json; data = json.load(open('output/donnees_enrichies.json', encoding='utf-8')); print(data.get('ratios_financiers', {}))"
```

Pour vérifier les ratios dans l'Excel généré :

```bash
python verifier_ratios_excel.py
```

## Recommandations

1. **TOUJOURS** enrichir le JSON avec les ratios AVANT de générer les prompts
2. Vérifier la présence de la section `ratios_financiers` dans le JSON
3. **Ne JAMAIS** laisser le LLM calculer des ratios numériques
   - Les LLM peuvent se tromper dans les calculs
   - Les ratios doivent être pré-calculés en Python
   - Le LLM doit uniquement les analyser et les interpréter

## Graphiques

Tous les ratios peuvent être représentés visuellement :
- Comparaisons avec la strate
- Évolutions temporelles
- Ratios en cascade (waterfall charts)
- Tableaux de bord de synthèse

Pour ajouter des graphiques, modifier les scripts de génération de rapport (PDF/Word).

## Auteur & Date

- **Date de création** : 2026-02-05
- **Problème corrigé** : Calcul incorrect de la part des charges de personnel
- **Version** : 1.0

---

**Pour toute question ou amélioration, consultez :**
- [RATIOS_CORRECTION.txt](RATIOS_CORRECTION.txt) - Rapport détaillé
- [ratios_supplementaires_futurs.py](ratios_supplementaires_futurs.py) - Ratios additionnels
