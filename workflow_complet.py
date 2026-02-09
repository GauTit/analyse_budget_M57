"""
Script maître pour automatiser tout le workflow de génération de rapport budgétaire
de A à Z : JSON enrichi → Prompts → Réponses LLM → PDF/Word

Usage:
    python workflow_complet.py

Le script demande si vous voulez générer un rapport mono-année ou multi-années,
puis exécute automatiquement toutes les étapes.
"""

import sys
import os
from datetime import datetime

# Charger les variables d'environnement depuis .env si disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv pas installé, on continue sans


def afficher_banniere():
    """Affiche la bannière du workflow"""
    print("\n" + "="*80)
    print("WORKFLOW COMPLET - GÉNÉRATION AUTOMATIQUE DE RAPPORT BUDGÉTAIRE")
    print("="*80 + "\n")


def afficher_etape(numero, total, titre):
    """Affiche le titre d'une étape"""
    print("\n" + "-"*80)
    print(f"[ÉTAPE {numero}/{total}] {titre}")
    print("-"*80 + "\n")


def executer_avec_gestion_erreur(fonction, nom_etape):
    """Exécute une fonction et gère les erreurs"""
    try:
        fonction()
        print(f"\n✓ {nom_etape} : SUCCÈS")
        return True
    except Exception as e:
        print(f"\n✗ {nom_etape} : ERREUR")
        print(f"  Détail : {e}")
        import traceback
        traceback.print_exc()
        return False


def workflow_mono_annee():
    """Workflow complet pour rapport mono-année"""

    print("\n>>> MODE SÉLECTIONNÉ : RAPPORT MONO-ANNÉE\n")

    # Étape 0 : Générer le JSON initial depuis le PDF
    afficher_etape(1, 6, "Génération du JSON initial depuis le PDF")

    from generer_json_initial import main as generer_json_initial
    if not executer_avec_gestion_erreur(generer_json_initial, "Génération du JSON initial"):
        return False

    # Étape 1 : Enrichir le JSON avec les ratios financiers
    afficher_etape(2, 6, "Enrichissement du JSON avec les ratios financiers")

    from enrichir_json_avec_ratios import main as enrichir_json
    if not executer_avec_gestion_erreur(enrichir_json, "Enrichissement du JSON"):
        return False

    # Étape 2 : Générer les prompts enrichis
    afficher_etape(3, 6, "Génération des prompts enrichis")

    from generer_prompts_enrichis_depuis_json import main as generer_prompts
    if not executer_avec_gestion_erreur(generer_prompts, "Génération des prompts"):
        return False

    # Étape 3 : Générer les réponses avec OpenAI (MONO-ANNÉE UNIQUEMENT)
    afficher_etape(4, 6, "Génération des réponses avec OpenAI GPT-4.1 mini (MONO-ANNÉE)")

    from generer_reponses_avec_openai import generer_toutes_reponses
    # Forcer la régénération et filtrer par type mono-année
    if not executer_avec_gestion_erreur(
        lambda: generer_toutes_reponses(force=True, type_rapport="Mono-annee"),
        "Génération des réponses LLM mono-année"
    ):
        return False

    # Étape 4 : Générer le rapport PDF
    afficher_etape(5, 6, "Génération du rapport PDF")

    from generer_rapport_excel_vers_pdf import generer_rapport_pdf
    if not executer_avec_gestion_erreur(generer_rapport_pdf, "Génération du PDF"):
        return False

    # Étape 5 : Générer le rapport Word
    afficher_etape(6, 6, "Génération du rapport Word")

    from generer_rapport_excel_vers_word import generer_rapport_word
    if not executer_avec_gestion_erreur(generer_rapport_word, "Génération du Word"):
        return False

    return True


def workflow_multi_annees():
    """Workflow complet pour rapport multi-années"""

    print("\n>>> MODE SÉLECTIONNÉ : RAPPORT MULTI-ANNÉES\n")

    # Étape 1 : Générer le JSON multi-années
    afficher_etape(1, 5, "Génération du JSON multi-années")

    from generer_json_multi_annees import main as generer_json_multi
    if not executer_avec_gestion_erreur(generer_json_multi, "Génération du JSON multi-années"):
        return False

    # Étape 2 : Générer les prompts enrichis (inclut le multi-années)
    afficher_etape(2, 5, "Génération des prompts enrichis multi-années")

    from generer_prompts_enrichis_depuis_json import main as generer_prompts
    if not executer_avec_gestion_erreur(generer_prompts, "Génération des prompts"):
        return False

    # Étape 3 : Générer les réponses avec OpenAI (MULTI-ANNÉES UNIQUEMENT)
    afficher_etape(3, 5, "Génération des réponses avec OpenAI GPT-4.1 mini (MULTI-ANNÉES)")

    from generer_reponses_avec_openai import generer_toutes_reponses
    # Forcer la régénération et filtrer par type multi-années
    if not executer_avec_gestion_erreur(
        lambda: generer_toutes_reponses(force=True, type_rapport="Multi-annees"),
        "Génération des réponses LLM multi-années"
    ):
        return False

    # Étape 4 : Générer le rapport PDF multi-années
    afficher_etape(4, 5, "Génération du rapport PDF multi-années")

    from generer_rapport_multi_annees import generer_rapport_pdf as generer_rapport_pdf_multi
    if not executer_avec_gestion_erreur(generer_rapport_pdf_multi, "Génération du PDF"):
        return False

    # Étape 5 : Générer le rapport Word multi-années
    afficher_etape(5, 5, "Génération du rapport Word multi-années")

    from generer_rapport_multi_annees_word import generer_rapport_word as generer_rapport_word_multi
    if not executer_avec_gestion_erreur(generer_rapport_word_multi, "Génération du Word"):
        return False

    return True


def main():
    """Point d'entrée principal"""

    afficher_banniere()

    # Demander le mode
    print("Quel type de rapport voulez-vous générer ?")
    print("  1. Rapport mono-année")
    print("  2. Rapport multi-années")
    print()

    choix = input("Votre choix (1 ou 2) : ").strip()

    if choix not in ["1", "2"]:
        print("\n✗ Choix invalide. Veuillez entrer 1 ou 2.")
        return

    # Confirmation
    type_rapport = "mono-année" if choix == "1" else "multi-années"
    print(f"\n⚠ Vous allez générer un rapport {type_rapport}.")
    print("Ce processus va :")
    print("  - Enrichir/Générer les JSONs")
    print("  - Générer les prompts")
    print("  - Appeler l'API OpenAI (coût potentiel)")
    print("  - Générer les rapports PDF et Word")
    print()

    confirmation = input("Voulez-vous continuer ? (o/n) : ").strip().lower()

    if confirmation != "o":
        print("\n✗ Workflow annulé.")
        return

    # Vérifier la clé API OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("\n✗ ERREUR : La clé API OpenAI n'est pas configurée.")
        print("  Veuillez définir la variable d'environnement OPENAI_API_KEY.")
        print()
        print("  Windows PowerShell :")
        print('    $env:OPENAI_API_KEY = "votre-cle-api-ici"')
        print()
        print("  Windows CMD :")
        print('    set OPENAI_API_KEY=votre-cle-api-ici')
        return

    # Démarrer le chronomètre
    debut = datetime.now()

    # Exécuter le workflow approprié
    if choix == "1":
        succes = workflow_mono_annee()
    else:
        succes = workflow_multi_annees()

    # Calculer le temps écoulé
    fin = datetime.now()
    duree = fin - debut

    # Afficher le résultat final
    print("\n" + "="*80)
    if succes:
        print("✓ WORKFLOW TERMINÉ AVEC SUCCÈS")
        print(f"  Durée totale : {duree}")
        print()
        print("Fichiers générés :")
        if choix == "1":
            print("  - output/donnees_enrichies.json")
            print("  - PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx")
            print("  - output/rapport_analyse_mono_annee.pdf")
            print("  - output/rapport_analyse_mono_annee.docx")
        else:
            print("  - output/donnees_multi_annees.json")
            print("  - PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx")
            print("  - output/rapport_analyse_multi_annees.pdf")
            print("  - output/rapport_analyse_multi_annees.docx")
    else:
        print("✗ WORKFLOW INTERROMPU (ERREUR)")
        print(f"  Durée : {duree}")
        print()
        print("Vérifiez les messages d'erreur ci-dessus pour identifier le problème.")

    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ Workflow interrompu par l'utilisateur (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERREUR FATALE : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
