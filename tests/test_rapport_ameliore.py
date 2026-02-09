"""
Script de test pour vérifier la qualité des textes générés
"""

from parser_budget_v2_complet import ParserBudget
from generateur_rapport_ameliore import AnalyseurTexteAmeliore

# Parser les données
print("Parsing du PDF...")
parser = ParserBudget()
budget = parser.parser_bilan_pdf('bilan.pdf')

# Créer l'analyseur
print("\nCréation de l'analyseur...")
analyseur = AnalyseurTexteAmeliore(budget)

# Afficher quelques extraits
print("\n" + "="*80)
print("EXTRAIT DU RAPPORT GENERE")
print("="*80 + "\n")

print(analyseur.analyser_produits_fonctionnement())
print("\n" + "-"*80 + "\n")

print(analyseur.analyser_impots_locaux())
print("\n" + "-"*80 + "\n")

print(analyseur.analyser_autres_impots())
print("\n" + "-"*80 + "\n")

print(analyseur.analyser_charges_fonctionnement())
print("\n" + "-"*80 + "\n")

print(analyseur.analyser_ebf())
print("\n" + "-"*80 + "\n")

print(analyseur.analyser_caf_nette())
print("\n" + "-"*80 + "\n")

print(analyseur.analyser_fonds_roulement())
