"""
Postes budgétaires multi-années (évolution)

Chaque fichier contient :
- CONTEXTE_ESSENTIEL : Doctrine M57 du poste mono-année correspondant (importée)
- CONSIGNES_ANALYSE : Consignes spécifiques pour l'analyse pluriannuelle
- CLE_TENDANCE : Clé du JSON tendances_globales (None pour Analyse_tendances_globales)
- generer_prompt(data_json_multi) : Fonction principale
"""

__all__ = [
    'analyse_tendances_globales',
    'produits_fonctionnement_evolution',
    'charges_fonctionnement_evolution',
    'charges_personnel_evolution',
    'caf_brute_evolution',
    'encours_dette_evolution',
    'depenses_equipement_evolution'
]
