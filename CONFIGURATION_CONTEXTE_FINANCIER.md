# Configuration du Contexte Financier par Poste

## 🎯 Objectif

Réduire les coûts de tokens et améliorer la précision du LLM en n'incluant le contexte financier global **que pour les postes qui en ont vraiment besoin**.

## 📊 Recommandations par poste

### ✅ CONTEXTE COMPLET (INCLURE_CONTEXTE_FINANCIER = True)

Ces postes **ont besoin** du contexte financier global pour leur analyse :

**Mono-année :**
- ✅ **Analyse_globale_intelligente** : Besoin de TOUT (CAF, dette, FDR, etc.)
- ✅ **Resultat_comptable** : Doit articuler avec CAF et équilibre global
- ✅ **CAF_brute** : Besoin des ratios d'épargne et de la dette
- ✅ **CAF_nette** : Besoin du remboursement dette et dépenses équipement
- ✅ **Encours_dette** : Besoin CAF brute, taux épargne pour évaluer soutenabilité
- ✅ **Fonds_roulement** : Besoin dette, CAF pour évaluer sécurité financière

**Multi-années :**
- ✅ **Analyse_tendances_globales** : Besoin de TOUT

---

### ⚡ CONTEXTE MINIMAL (INCLURE_CONTEXTE_FINANCIER = False)

Ces postes **n'ont PAS besoin** du contexte financier global :

**Recettes (mono-année) :**
- ⚡ **Produits_de_fonctionnement** : Analyse isolée, pas besoin CAF/dette
- ⚡ **Impots_locaux** : Analyse fiscale isolée
- ⚡ **DGF** : Dotation isolée, pas besoin des autres agrégats ✅ *Déjà configuré*
- ⚡ **Produits_services_domaine** : Recette isolée

**Dépenses (mono-année) :**
- ⚡ **Charges_de_fonctionnement** : Analyse isolée
- ⚡ **Charges_de_personnel** : Poste isolé, pas besoin CAF/dette
- ⚡ **Achats_charges_externes** : Poste isolé

**Investissement (mono-année) :**
- ⚡ **Depenses_equipement** : Peut être analysé isolément
- ⚡ **Emprunts_contractes** : Nouveau flux, pas besoin du stock
- ⚡ **Subventions_recues** : Recette isolée

**Multi-années :**
- ⚡ **Produits_fonctionnement_evolution** : Évolution isolée
- ⚡ **Charges_fonctionnement_evolution** : Évolution isolée
- ⚡ **Charges_personnel_evolution** : Évolution isolée
- ⚡ **Depenses_equipement_evolution** : Évolution isolée
- 🤔 **CAF_brute_evolution** : Peut bénéficier du contexte
- 🤔 **Encours_dette_evolution** : Peut bénéficier du contexte

---

## 🔧 Comment configurer un poste ?

### Ouvrir le fichier du poste

```bash
# Exemple : DGF
prompts/postes/mono_annee/dgf.py
```

### Ajouter la constante dans la section CONFIGURATION

```python
# ============================================
# CONFIGURATION DU POSTE
# ============================================

CHEMIN_JSON = "fonctionnement.produits.dgf"
NOM_POSTE = "DGF"
TYPE_RAPPORT = "Mono-annee"

# Inclure le contexte financier global complet ?
# - True : Inclut CAF brute, encours dette, ratios clés (+ de tokens)
# - False : Inclut uniquement commune, exercice, population, strate (économie de tokens)
INCLURE_CONTEXTE_FINANCIER = False  # ⚡ Économie de tokens
```

### Modifier la fonction generer_prompt()

Remplacer :
```python
contexte_financier = regles_globales.construire_contexte_financier_global(
    metadata_dict, agregats, ratios_dict
)
```

Par :
```python
# Choisir le type de contexte selon la configuration du poste
if INCLURE_CONTEXTE_FINANCIER:
    # Contexte complet avec tous les agrégats financiers
    contexte_financier = regles_globales.construire_contexte_financier_global(
        metadata_dict, agregats, ratios_dict
    )
else:
    # Contexte minimal (seulement commune, exercice, population, strate)
    contexte_financier = regles_globales.construire_contexte_minimal(metadata_dict)
```

---

## 💡 Bénéfices attendus

### Économie de tokens

**Exemple pour DGF :**

**AVANT (contexte complet) :**
```
CONTEXTE FINANCIER GLOBAL DE LA COMMUNE :

Commune: ROSOY
Exercice: 2024
Population: 1102 habitants
Strate démographique: 500 à 2000 habitants

ÉQUILIBRES FINANCIERS:
- Résultat de fonctionnement: 171 k€
- CAF brute: 172 k€
- CAF nette: 79 k€
- Encours de dette: 1144 k€
- Dépenses d'équipement: 59 k€
- Fonds de roulement: -250 k€ (négatif)

RATIOS CLÉS:
- Taux d'épargne brute (CAF brute / RRF): 13.9% (seuil de confort: > 15% ; seuil d'alerte usuel: < 8%)
- Part des charges de personnel dans les DRF: 46.1%
- Capacité de désendettement (encours / CAF brute): 6.7 années (alerte: > 12 ans ; zone critique: > 15 ans)
```
**~200 tokens**

**APRÈS (contexte minimal) :**
```
CONTEXTE :

Commune: ROSOY
Exercice: 2024
Population: 1102 habitants
Strate démographique: 500 à 2000 habitants
```
**~40 tokens**

**→ Économie de ~160 tokens par prompt DGF** 🎉

---

## 📈 Impact global

Si on applique le contexte minimal à **10 postes sur 14 mono-année** :

- **Avant** : 14 postes × 200 tokens = **2800 tokens de contexte**
- **Après** : 4 postes × 200 tokens + 10 postes × 40 tokens = **1200 tokens de contexte**
- **Économie** : **1600 tokens par génération de rapport** ✅

Avec un coût moyen de **$0.03 / 1000 tokens input** (GPT-4) :
- **Économie par rapport** : ~$0.048 ≈ 5 centimes
- **Sur 100 rapports** : ~$4.80 d'économie

---

## 🚀 Prochaines étapes

1. **Configurer tous les postes** selon les recommandations ci-dessus
2. **Tester** avec quelques prompts pour vérifier la qualité
3. **Ajuster** si certains postes ont besoin de plus de contexte

Le fichier **dgf.py** est déjà configuré comme exemple ✅
