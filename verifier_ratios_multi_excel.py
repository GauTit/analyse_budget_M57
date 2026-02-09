import pandas as pd

df = pd.read_excel('PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx')

# Extraire le prompt d'analyse tendances globales
prompt = df[df['Nom_Poste'] == 'Analyse_tendances_globales']['Donnees_Injectees'].values[0]

print("="*80)
print("VERIFICATION DES RATIOS MULTI-ANNEES DANS L'EXCEL")
print("="*80)

# Rechercher les sections de ratios
if "RATIOS FINANCIERS PAR ANNÉE" in prompt:
    print("\n[OK] Section 'RATIOS FINANCIERS PAR ANNEE' trouvee")

    # Extraire et afficher les lignes contenant les ratios
    lines = prompt.split('\n')
    in_ratios_section = False

    for line in lines:
        if "RATIOS FINANCIERS PAR ANNÉE" in line or "RATIOS FINANCIERS PAR ANNEE" in line:
            in_ratios_section = True
            print("\n" + "="*80)
            print(line)
            print("="*80)
        elif "ÉVOLUTIONS DES RATIOS" in line or "EVOLUTIONS DES RATIOS" in line:
            print("\n" + "="*80)
            print(line)
            print("="*80)
        elif in_ratios_section and line.strip():
            print(line)

    # Vérifier des valeurs spécifiques
    print("\n" + "="*80)
    print("VERIFICATION DES VALEURS")
    print("="*80)

    if "Part charges personnel : 41.1%" in prompt:
        print("[OK] Part charges personnel 2022 : 41.1% (correct)")
    if "Part charges personnel : 49.5%" in prompt:
        print("[OK] Part charges personnel 2024 : 49.5% (correct)")
    if "+8.4 pts" in prompt:
        print("[OK] Evolution : +8.4 pts (correct)")

else:
    print("\n[ERREUR] Section 'RATIOS FINANCIERS PAR ANNEE' NON trouvee !")
    print("Les ratios multi-annees ne sont pas integres dans le prompt")

print("\n" + "="*80)
