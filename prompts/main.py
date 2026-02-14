"""
Script principal pour générer les prompts enrichis dans l'Excel
à partir des vraies valeurs du JSON et des contextes "L'essentiel"

IMPORTANT : Ce script nécessite que le JSON ait été enrichi avec les ratios financiers.
Exécuter d'abord 'enrichir_json_avec_ratios.py' si ce n'est pas déjà fait.

Architecture modulaire :
- Chaque poste budgétaire a son propre fichier Python dans prompts/postes/
- Les règles M57 globales sont centralisées dans regles_globales.py
- main.py charge dynamiquement les modules et génère les prompts
"""

import pandas as pd
import json
import os
import sys
import importlib
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fichiers
FICHIER_JSON_MONO = "output/donnees_enrichies.json"
FICHIER_JSON_MULTI = "output/donnees_multi_annees.json"
FICHIER_EXCEL_BASE = "PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx"
FICHIER_EXCEL_SORTIE = "PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx"

# ============================================
# MAPPING POSTES -> MODULES
# ============================================

POSTES_MONO_ANNEE = {
    "Analyse_globale_intelligente": "analyse_globale_intelligente",
    "Produits_de_fonctionnement": "produits_de_fonctionnement",
    "Impots_locaux": "impots_locaux",
    "DGF": "dgf",
    "Charges_de_fonctionnement": "charges_de_fonctionnement",
    "Charges_de_personnel": "charges_de_personnel",
    "Resultat_comptable": "resultat_comptable",
    "CAF_brute": "caf_brute",
    "CAF_nette": "caf_nette",
    "Depenses_equipement": "depenses_equipement",
    "Emprunts_contractes": "emprunts_contractes",
    "Subventions_recues": "subventions_recues",
    "Encours_dette": "encours_dette",
    "Fonds_roulement": "fonds_roulement"
}

POSTES_MULTI_ANNEES = {
    "Analyse_tendances_globales": "analyse_tendances_globales",
    "Produits_fonctionnement_evolution": "produits_fonctionnement_evolution",
    "Charges_fonctionnement_evolution": "charges_fonctionnement_evolution",
    "Charges_personnel_evolution": "charges_personnel_evolution",
    "CAF_brute_evolution": "caf_brute_evolution",
    "Encours_dette_evolution": "encours_dette_evolution",
    "Depenses_equipement_evolution": "depenses_equipement_evolution"
}


def charger_module_poste(nom_module, type_rapport="Mono-annee"):
    """
    Charge dynamiquement un module de poste

    Args:
        nom_module: Nom du fichier module (sans .py)
        type_rapport: "Mono-annee" ou "Multi-annees"

    Returns:
        module: Module chargé avec ses fonctions generer_prompt, etc.
    """
    try:
        # Déterminer le sous-dossier selon le type
        sous_dossier = "mono_annee" if type_rapport == "Mono-annee" else "multi_annees"
        module = importlib.import_module(f"prompts.postes.{sous_dossier}.{nom_module}")
        return module
    except ImportError as e:
        print(f"  [ERREUR] Impossible de charger le module {nom_module} ({type_rapport}): {e}")
        return None


def generer_donnees_injectees(nom_poste, data_json, module_poste):
    """
    Génère les données injectées pour un poste mono-année

    Args:
        nom_poste: Nom du poste
        data_json: JSON complet
        module_poste: Module du poste chargé dynamiquement

    Returns:
        str: Données formatées pour l'Excel
    """
    try:
        # Extraire les données avec le module
        poste_data = module_poste.extraire_donnees(data_json)

        # Formater les données
        donnees_formatees = module_poste.formater_donnees(poste_data, data_json)

        return donnees_formatees
    except Exception as e:
        print(f"  [WARN] Erreur lors de la génération des données pour {nom_poste}: {e}")
        return "Données non disponibles"


def generer_donnees_multi_annees(nom_poste, data_json_multi, module_poste):
    """
    Génère les données injectées pour un poste multi-années

    Args:
        nom_poste: Nom du poste
        data_json_multi: JSON multi-années complet
        module_poste: Module du poste chargé dynamiquement

    Returns:
        str: Données formatées pour l'Excel
    """
    try:
        # Extraire les métadonnées
        metadata = data_json_multi.get('metadata', {})

        # Extraire les données avec le module
        donnees_poste = module_poste.extraire_donnees(data_json_multi)

        # Formater les données
        donnees_formatees = module_poste.formater_donnees(donnees_poste, metadata)

        return donnees_formatees
    except Exception as e:
        print(f"  [WARN] Erreur lors de la génération des données multi-années pour {nom_poste}: {e}")
        return "Données non disponibles"


def main():
    print("\n" + "="*80)
    print("GENERATION DES PROMPTS ENRICHIS DEPUIS LE JSON (ARCHITECTURE MODULAIRE)")
    print("="*80 + "\n")

    # 1. Charger les JSONs
    print("[1/5] Chargement des JSONs...")

    # Charger JSON mono-année
    if not os.path.exists(FICHIER_JSON_MONO):
        print(f"  [ERREUR] Fichier JSON mono-année introuvable : {FICHIER_JSON_MONO}")
        return

    with open(FICHIER_JSON_MONO, 'r', encoding='utf-8') as f:
        data_json_mono = json.load(f)
    print(f"  [OK] JSON mono-annee charge : {data_json_mono['metadata']['commune']} - {data_json_mono['metadata']['exercice']}")

    # Charger JSON multi-années si disponible
    data_json_multi = None
    if os.path.exists(FICHIER_JSON_MULTI):
        with open(FICHIER_JSON_MULTI, 'r', encoding='utf-8') as f:
            data_json_multi = json.load(f)
        print(f"  [OK] JSON multi-annees charge : {data_json_multi['metadata']['commune']} - Periode {data_json_multi['metadata']['periode_debut']}-{data_json_multi['metadata']['periode_fin']}")
    else:
        print(f"  [WARN] JSON multi-annees non trouve : {FICHIER_JSON_MULTI}")

    # 2. Charger l'Excel de base
    print("\n[2/5] Chargement de l'Excel de base...")
    if not os.path.exists(FICHIER_EXCEL_BASE):
        print(f"  [ERREUR] Fichier Excel introuvable : {FICHIER_EXCEL_BASE}")
        return

    df = pd.read_excel(FICHIER_EXCEL_BASE)
    print(f"  [OK] {len(df)} lignes chargees")

    # 3. Générer les prompts enrichis
    print("\n[3/5] Generation des prompts enrichis (chargement dynamique des modules)...")
    nb_generes = 0
    nb_erreurs = 0

    for idx, row in df.iterrows():
        nom_poste = row['Nom_Poste']
        type_rapport = row['Type_Rapport']

        # Traiter les postes mono-année
        if type_rapport == 'Mono-annee' and nom_poste in POSTES_MONO_ANNEE:
            nom_module = POSTES_MONO_ANNEE[nom_poste]

            # Charger le module dynamiquement
            module_poste = charger_module_poste(nom_module, type_rapport)
            if not module_poste:
                print(f"  [ERREUR] {nom_poste} : module non charge")
                nb_erreurs += 1
                continue

            try:
                # Générer les données injectées
                donnees = generer_donnees_injectees(nom_poste, data_json_mono, module_poste)

                # Récupérer le texte personnalisé de l'Excel si disponible
                texte_personnalise = None
                if not pd.isna(row.get('Texte_Positionnement_Personnalise', '')):
                    texte_personnalise = row.get('Texte_Positionnement_Personnalise', '')

                # Générer le prompt avec le module
                prompt_enrichi = module_poste.generer_prompt(data_json_mono, texte_personnalise)

                # Mettre à jour l'Excel
                df.at[idx, 'Donnees_Injectees'] = donnees
                df.at[idx, 'Prompt_Complete'] = prompt_enrichi

                # Sauvegarder le texte personnalisé si disponible dans le module
                if hasattr(module_poste, 'TEXTE_PERSONNALISE') and module_poste.TEXTE_PERSONNALISE:
                    df.at[idx, 'Texte_Positionnement_Personnalise'] = module_poste.TEXTE_PERSONNALISE

                nb_generes += 1
                print(f"  [OK] {nom_poste}")

            except Exception as e:
                print(f"  [ERREUR] {nom_poste} : {e}")
                nb_erreurs += 1

        # Traiter les postes multi-années
        elif type_rapport == 'Multi-annees' and nom_poste in POSTES_MULTI_ANNEES:
            if not data_json_multi:
                print(f"  [WARN] {nom_poste} : JSON multi-annees non disponible")
                continue

            nom_module = POSTES_MULTI_ANNEES[nom_poste]

            # Charger le module dynamiquement
            module_poste = charger_module_poste(nom_module, type_rapport)
            if not module_poste:
                print(f"  [ERREUR] {nom_poste} : module non charge")
                nb_erreurs += 1
                continue

            try:
                # Générer les données injectées
                donnees = generer_donnees_multi_annees(nom_poste, data_json_multi, module_poste)

                # Générer le prompt avec le module
                prompt_enrichi = module_poste.generer_prompt(data_json_multi)

                # Mettre à jour l'Excel
                df.at[idx, 'Donnees_Injectees'] = donnees
                df.at[idx, 'Prompt_Complete'] = prompt_enrichi

                nb_generes += 1
                print(f"  [OK] {nom_poste} (multi-annees)")

            except Exception as e:
                print(f"  [ERREUR] {nom_poste} (multi-annees) : {e}")
                nb_erreurs += 1

        else:
            print(f"  [WARN] {nom_poste} ({type_rapport}) : poste non reconnu ou type non supporte")

    print(f"\n  Total generes : {nb_generes} prompts")
    print(f"  Total erreurs : {nb_erreurs}")

    # 4. Sauvegarder
    print("\n[4/5] Sauvegarde de l'Excel enrichi...")
    df.to_excel(FICHIER_EXCEL_SORTIE, index=False)
    print(f"  [OK] Fichier sauvegarde : {FICHIER_EXCEL_SORTIE}")

    print("\n" + "="*80)
    print("GENERATION TERMINEE")
    print("="*80 + "\n")
    print("Prochaines etapes :")
    print("1. Ouvrir l'Excel : PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx")
    print("2. Verifier les prompts dans la colonne 'Prompt_Complete'")
    print("3. Generer les reponses LLM avec :")
    print("   python generer_reponses_avec_openai.py")
    print("4. Generer le rapport final avec :")
    print("   - python generer_rapport_excel_vers_pdf.py")
    print("   - python generer_rapport_excel_vers_word.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERREUR] : {e}")
        import traceback
        traceback.print_exc()
