"""
Postes budgétaires mono-année

Chaque fichier contient :
- CONTEXTE_ESSENTIEL : Doctrine M57 spécifique au poste
- TEXTE_PERSONNALISE : Phrase d'inspiration pour la section 1
- CHEMIN_JSON : Chemin vers les données dans le JSON
- ANGLE_SPECIFIQUE : Angle d'analyse spécifique
- generer_prompt(data_json, texte_personnalise) : Fonction principale
"""

__all__ = [
    'analyse_globale_intelligente',
    'produits_de_fonctionnement',
    'impots_locaux',
    'dgf',
    'charges_de_fonctionnement',
    'charges_de_personnel',
    'resultat_comptable',
    'caf_brute',
    'caf_nette',
    'depenses_equipement',
    'emprunts_contractes',
    'subventions_recues',
    'encours_dette',
    'fonds_roulement'
]
