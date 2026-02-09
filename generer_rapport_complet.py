"""
Script principal pour générer un rapport financier complet avec ratios corrects

Ce script orchestre toute la chaîne de traitement :
1. Enrichissement du JSON avec les ratios financiers
2. Génération des prompts enrichis
3. (Optionnel) Génération du PDF final

Usage : python generer_rapport_complet.py
"""

import os
import sys


def executer_commande(commande, description):
    """Exécute une commande et affiche le résultat"""
    print("\n" + "="*80)
    print(f"ÉTAPE : {description}")
    print("="*80)
    print(f"Commande : {commande}\n")

    resultat = os.system(commande)

    if resultat != 0:
        print(f"\n[ERREUR] La commande a échoué avec le code {resultat}")
        return False

    print(f"\n[OK] {description} terminé")
    return True


def main():
    print("\n" + "="*80)
    print("GÉNÉRATION COMPLÈTE DU RAPPORT FINANCIER")
    print("="*80)
    print("\nCe script exécute les étapes suivantes :")
    print("1. Enrichissement du JSON avec les ratios financiers")
    print("2. Génération des prompts enrichis pour le LLM")
    print("\n" + "="*80)

    reponse = input("\nContinuer ? (o/n) : ")
    if reponse.lower() not in ['o', 'oui', 'y', 'yes']:
        print("Abandon.")
        return

    # Étape 1 : Enrichissement des JSON avec les ratios
    if not executer_commande(
        "python enrichir_json_avec_ratios.py",
        "Enrichissement des JSON avec les ratios financiers"
    ):
        print("\n[ERREUR] Impossible de continuer.")
        return

    # Étape 2 : Génération des prompts enrichis
    if not executer_commande(
        "python generer_prompts_enrichis_depuis_json.py",
        "Génération des prompts enrichis"
    ):
        print("\n[ERREUR] Impossible de continuer.")
        return

    print("\n" + "="*80)
    print("GÉNÉRATION TERMINÉE AVEC SUCCÈS")
    print("="*80)
    print("\nProchaines étapes :")
    print("1. Ouvrir le fichier : PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx")
    print("2. Copier les prompts de la colonne 'Prompt_Complete'")
    print("3. Les envoyer à un LLM (Claude, Mistral, GPT-4, etc.)")
    print("4. Coller les réponses dans la colonne 'Reponse_Attendue'")
    print("5. Sauvegarder le fichier Excel")
    print("6. Générer le PDF final avec : python generer_rapport_excel_vers_pdf.py")
    print("\n" + "="*80)
    print("\nIMPORTANT : Les ratios financiers sont maintenant calculés correctement !")
    print("Exemple : Part charges de personnel = 45.1% (et non 39.3%)")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[ANNULÉ] Opération interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n[ERREUR] : {e}")
        import traceback
        traceback.print_exc()
