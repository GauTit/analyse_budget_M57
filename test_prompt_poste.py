import json
import sys
sys.path.insert(0, 'src')
from generer_prompts_enrichis_depuis_json import generer_donnees_multi_annees, generer_prompt_multi_annees

# Charger le JSON multi-années
with open('output/donnees_multi_annees.json', 'r', encoding='utf-8') as f:
    data_json_multi = json.load(f)

# Tester pour un poste spécifique
nom_poste = 'Produits_fonctionnement_evolution'

donnees = generer_donnees_multi_annees(nom_poste, data_json_multi)
prompt_complet = generer_prompt_multi_annees(nom_poste, donnees, data_json_multi)

# Écrire dans un fichier UTF-8
with open('test_prompt_poste_output.txt', 'w', encoding='utf-8') as output:
    output.write("="*80 + "\n")
    output.write(f"EXEMPLE DE PROMPT COMPLET POUR : {nom_poste}\n")
    output.write("="*80 + "\n\n")
    # Afficher seulement les 2000 premiers caractères pour voir la structure
    output.write(prompt_complet[:2000])
    output.write("\n\n[...] (prompt tronqué pour lisibilité)\n")

print("Fichier genere : test_prompt_poste_output.txt")
