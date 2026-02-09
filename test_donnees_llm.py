import json
import sys
sys.path.insert(0, 'src')
from generer_prompts_enrichis_depuis_json import generer_donnees_multi_annees

# Charger le JSON multi-années
with open('output/donnees_multi_annees.json', 'r', encoding='utf-8') as f:
    data_json_multi = json.load(f)

# Écrire dans un fichier UTF-8
with open('test_llm_output.txt', 'w', encoding='utf-8') as output:
    output.write("="*80 + "\n")
    output.write("EXEMPLE : Ce que le LLM verra pour 'Produits_fonctionnement_evolution'\n")
    output.write("="*80 + "\n\n")

    donnees = generer_donnees_multi_annees('Produits_fonctionnement_evolution', data_json_multi)
    output.write(donnees)

    output.write("\n\n" + "="*80 + "\n")
    output.write("EXEMPLE : Ce que le LLM verra pour 'Analyse_tendances_globales'\n")
    output.write("="*80 + "\n\n")

    donnees_globales = generer_donnees_multi_annees('Analyse_tendances_globales', data_json_multi)
    output.write(donnees_globales[:3000])
    output.write("\n\n[...] (texte tronqué pour lisibilité)\n")

print("Fichier genere : test_llm_output.txt")
