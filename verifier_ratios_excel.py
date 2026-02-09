import pandas as pd

df = pd.read_excel('PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx')

# Extraire le prompt de synthèse globale
prompt = df[df['Nom_Poste'] == 'Analyse_globale_intelligente']['Donnees_Injectees'].values[0]

print("="*80)
print("VÉRIFICATION DES RATIOS DANS LE PROMPT GÉNÉRÉ")
print("="*80)

lines = prompt.split('\n')
for line in lines:
    if any(keyword in line for keyword in ['Part charges', 'Taux d', 'Ratio', 'couverture']):
        print(line)

print("\n" + "="*80)
print("RÉSULTAT")
print("="*80)
print("\nSi vous voyez 'Part charges de personnel : 45.1%', c'est CORRECT ✓")
print("Si vous voyez 'Part charges de personnel : 39.3%', c'est FAUX ✗")
