"""
Test pour vérifier que les ratios sont bien extraits du PDF
"""
import sys
sys.path.append('src')

from parsers.parser_budget_v2_complet import ParserBudget

# Parser le PDF
parser = ParserBudget()
budget = parser.parser_bilan_pdf('docs/bilan.pdf')

print("="*80)
print("RATIOS EXTRAITS DU PDF bilan.pdf")
print("="*80)

print("\n=== FONCTIONNEMENT ===")
print(f"Impôts locaux ratio: {budget.get('impots_locaux_ratio')}% (strate: {budget.get('impots_locaux_ratio_moy')}%)")
print(f"DGF ratio: {budget.get('dgf_ratio')}% (strate: {budget.get('dgf_ratio_moy')}%)")
print(f"Charges personnel ratio: {budget.get('charges_personnel_ratio')}% (strate: {budget.get('charges_personnel_ratio_moy')}%)")
print(f"Achats externes ratio: {budget.get('achats_charges_ext_ratio')}% (strate: {budget.get('achats_charges_ext_ratio_moy')}%)")
print(f"Charges financières ratio: {budget.get('charges_financieres_ratio')}% (strate: {budget.get('charges_financieres_ratio_moy')}%)")

print("\n=== AUTOFINANCEMENT ===")
print(f"EBF ratio: {budget.get('ebf_ratio')}% (strate: {budget.get('ebf_ratio_moy')}%)")
print(f"CAF brute ratio: {budget.get('caf_brute_ratio')}% (strate: {budget.get('caf_brute_ratio_moy')}%)")
print(f"CAF nette ratio: {budget.get('caf_nette_ratio')}% (strate: {budget.get('caf_nette_ratio_moy')}%)")

print("\n=== ENDETTEMENT ===")
print(f"Dette totale ratio: {budget.get('dette_totale_ratio')}% (strate: {budget.get('dette_totale_ratio_moy')}%)")
print(f"Annuité dette ratio: {budget.get('annuite_dette_ratio')}% (strate: {budget.get('annuite_dette_ratio_moy')}%)")

print("\n=== INVESTISSEMENT ===")
print(f"Dépenses équipement ratio: {budget.get('depenses_equipement_ratio')}% (strate: {budget.get('depenses_equipement_ratio_moy')}%)")

print("\n" + "="*80)
print("COMPARAISON AVEC LE PDF")
print("="*80)
print("\nSelon le PDF (page 1, colonne 'Ratios de structure') :")
print("- Charges de personnel : devrait être 45,10% (commune) et 44,61% (strate)")
print("- Impôts Locaux : devrait être 32,28% (commune) et 42,52% (strate)")
print("- DGF : devrait être 27,78% (commune) et 17,22% (strate)")

print("\nSelon le PDF (page 2, section AUTOFINANCEMENT) :")
print("- EBF : devrait être 30,15% (commune) et 21,29% (strate)")
print("- CAF : devrait être 28,07% (commune) et 19,83% (strate)")
print("- CAF nette : devrait être 17,38% (commune) et 11,88% (strate)")

print("\n" + "="*80)
