"""
Package postes : Modules de postes budgétaires

Structure organisée en deux sous-packages :

postes/
├── mono_annee/      # 14 postes budgétaires mono-année
│   └── [fichiers .py pour chaque poste]
└── multi_annees/    # 7 postes budgétaires multi-années (évolution)
    └── [fichiers .py pour chaque poste]

Chaque fichier contient :
- CONTEXTE_ESSENTIEL : Doctrine M57 spécifique au poste
- TEXTE_PERSONNALISE : Phrase d'inspiration (mono-année uniquement)
- generer_prompt() : Fonction de génération du prompt complet

Pour importer un poste :
    from prompts.postes.mono_annee import dgf
    from prompts.postes.multi_annees import analyse_tendances_globales
"""

__all__ = ['mono_annee', 'multi_annees']
