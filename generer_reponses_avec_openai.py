"""
Script pour générer les réponses aux prompts en utilisant une API LLM
(OpenAI, Anthropic/Claude, DeepSeek, Gemini, etc.) au lieu de copier-coller
manuellement les réponses depuis l'Excel.

Usage:
    python generer_reponses_avec_openai.py

IMPORTANT : Avant d'exécuter ce script, assurez-vous d'avoir :
1. Configuré votre fichier .env avec le provider LLM et la clé API
2. Installé les dépendances : pip install -r requirements.txt

Pour changer de provider LLM, modifiez LLM_PROVIDER dans votre fichier .env :
    LLM_PROVIDER=openai     # Pour OpenAI GPT
    LLM_PROVIDER=anthropic  # Pour Anthropic Claude
    LLM_PROVIDER=deepseek   # Pour DeepSeek
    LLM_PROVIDER=gemini     # Pour Google Gemini
"""

import pandas as pd
import os
import time
from llm_client import creer_client_llm, afficher_configuration

# Configuration
FICHIER_EXCEL = "PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx"
FICHIER_EXCEL_SORTIE = "PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx"

# Délai entre les requêtes pour éviter les rate limits (en secondes)
DELAI_ENTRE_REQUETES = 1


def initialiser_client_llm():
    """Initialise le client LLM (OpenAI, Anthropic, etc.)"""
    try:
        client = creer_client_llm()
        return client
    except Exception as e:
        raise ValueError(f"Impossible d'initialiser le client LLM : {e}")


def generer_reponse_llm(client, prompt):
    """Génère une réponse en utilisant l'API LLM configurée"""
    try:
        return client.generer_reponse(prompt)
    except Exception as e:
        print(f"  [ERREUR] Erreur lors de l'appel API : {e}")
        return None


def generer_toutes_reponses(force=False, type_rapport=None):
    """Génère toutes les réponses pour les prompts de l'Excel

    Args:
        force (bool): Si True, régénère toutes les réponses même si elles existent déjà
        type_rapport (str): 'Mono-annee' ou 'Multi-annees'. Si None, traite tous les types.
    """

    print("\n" + "="*80)
    print("GÉNÉRATION DES RÉPONSES AVEC API LLM")
    if force:
        print("MODE : Régénération forcée de toutes les réponses")
    if type_rapport:
        print(f"TYPE : {type_rapport}")
    print("="*80 + "\n")

    # Afficher la configuration LLM
    afficher_configuration()
    print()

    # 1. Initialiser le client LLM
    print("[ÉTAPE 1/4] Initialisation du client LLM...")
    try:
        client = initialiser_client_llm()
        print(f"  [OK] Client initialisé : {client.get_provider_name()}")
    except ValueError as e:
        print(f"  [ERREUR] {e}")
        return

    # 2. Charger l'Excel
    print("\n[ÉTAPE 2/4] Chargement de l'Excel...")
    df = pd.read_excel(FICHIER_EXCEL)
    print(f"  [OK] {len(df)} lignes chargées")

    # Filtrer par type de rapport si spécifié
    if type_rapport:
        df_filtre = df[df['Type_Rapport'] == type_rapport]
        print(f"  [INFO] Filtrage par type : {type_rapport} ({len(df_filtre)} lignes)")
    else:
        df_filtre = df
        print(f"  [INFO] Aucun filtrage par type (tous les rapports)")

    # Filtrer les lignes qui ont un prompt mais pas encore de réponse
    if force:
        # Mode force : traiter toutes les lignes qui ont un prompt
        lignes_a_traiter = df_filtre[df_filtre['Prompt_Complete'].notna()]
        print(f"  [INFO] Mode force activé : toutes les réponses seront régénérées")
    else:
        # Mode normal : traiter uniquement les lignes sans réponse
        lignes_a_traiter = df_filtre[
            df_filtre['Prompt_Complete'].notna() &
            (df_filtre['Reponse_Attendue'].isna() | (df_filtre['Reponse_Attendue'] == ''))
        ]

    nb_lignes = len(lignes_a_traiter)
    print(f"  [INFO] {nb_lignes} lignes à traiter (prompts sans réponse)")

    if nb_lignes == 0:
        print("\n  Toutes les réponses ont déjà été générées !")
        return

    # 3. Générer les réponses
    print("\n[ÉTAPE 3/4] Génération des réponses...")

    nb_reponses_generees = 0
    nb_erreurs = 0

    for idx, row in lignes_a_traiter.iterrows():
        nom_poste = row['Nom_Poste']
        type_rapport = row['Type_Rapport']
        prompt = row['Prompt_Complete']

        print(f"\n  [{nb_reponses_generees + 1}/{nb_lignes}] {nom_poste} ({type_rapport})...")

        # Générer la réponse
        reponse = generer_reponse_llm(client, prompt)

        if reponse:
            # Écrire la réponse dans le DataFrame
            df.at[idx, 'Reponse_Attendue'] = reponse
            nb_reponses_generees += 1
            print(f"  [OK] Réponse générée ({len(reponse)} caractères)")
        else:
            nb_erreurs += 1
            print(f"  [ERREUR] Impossible de générer la réponse")

        # Attendre avant la prochaine requête pour éviter les rate limits
        if nb_reponses_generees < nb_lignes:
            time.sleep(DELAI_ENTRE_REQUETES)

    # 4. Sauvegarder l'Excel
    print(f"\n[ÉTAPE 4/4] Sauvegarde de l'Excel...")
    df.to_excel(FICHIER_EXCEL_SORTIE, index=False)
    print(f"  [OK] Fichier sauvegardé : {FICHIER_EXCEL_SORTIE}")

    # Statistiques finales
    print("\n" + "="*80)
    print(f"[OK] GÉNÉRATION TERMINÉE")
    print(f"  Réponses générées : {nb_reponses_generees}")
    print(f"  Erreurs : {nb_erreurs}")
    print(f"  Fichier : {FICHIER_EXCEL_SORTIE}")
    print("="*80 + "\n")

    print("Prochaines étapes :")
    print("1. Vérifier les réponses dans l'Excel")
    print("2. Générer le rapport PDF/Word avec :")
    print("   - python generer_rapport_excel_vers_pdf.py")
    print("   - python generer_rapport_excel_vers_word.py")


if __name__ == "__main__":
    import sys

    # Vérifier si l'option --force est passée
    force = "--force" in sys.argv or "-f" in sys.argv

    # Vérifier le type de rapport
    type_rapport = None
    if "--mono" in sys.argv:
        type_rapport = "Mono-annee"
    elif "--multi" in sys.argv:
        type_rapport = "Multi-annees"

    try:
        generer_toutes_reponses(force=force, type_rapport=type_rapport)
    except Exception as e:
        print(f"\n[ERREUR] : {e}")
        import traceback
        traceback.print_exc()
