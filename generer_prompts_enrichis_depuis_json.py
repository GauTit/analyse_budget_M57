"""
Wrapper de compatibilité pour l'ancien système

Ce fichier maintient la compatibilité avec les scripts existants qui importent
ou exécutent generer_prompts_enrichis_depuis_json.py

Le nouveau système modulaire se trouve dans prompts/
- prompts/main.py : Orchestrateur principal
- prompts/regles_globales.py : Règles M57 centralisées
- prompts/postes/*.py : Un fichier par poste budgétaire

L'ancien fichier monolithique a été archivé dans archive/generer_prompts_enrichis_depuis_json.py
"""

# Import du nouveau système
from prompts.main import main

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SYSTEME MODULAIRE ACTIVE")
    print("Architecture : prompts/main.py + prompts/postes/*.py")
    print("Ancien systeme archive dans : archive/generer_prompts_enrichis_depuis_json.py")
    print("="*80)
    main()
