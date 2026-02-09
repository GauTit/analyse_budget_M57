import json
import pprint

# Charger le JSON multi-années
with open('output/donnees_multi_annees.json', encoding='utf-8') as f:
    data = json.load(f)

ratios = data.get('ratios_financiers', {})

print("="*80)
print("TEST DES RATIOS MULTI-ANNEES")
print("="*80)

print(f"\nType de ratios_financiers: {type(ratios)}")
print(f"Cles: {list(ratios.keys())}")

if 'ratios_par_annee' in ratios:
    print("\n" + "="*80)
    print("RATIOS PAR ANNEE")
    print("="*80)

    for annee in sorted(ratios['ratios_par_annee'].keys()):
        print(f"\n=== ANNEE {annee} ===")
        ratios_annee = ratios['ratios_par_annee'][annee]
        print(f"Part charges personnel: {ratios_annee.get('part_charges_personnel_pct')}%")
        print(f"Taux epargne brute: {ratios_annee.get('taux_epargne_brute_pct')}%")
        print(f"Capacite desendettement: {ratios_annee.get('capacite_desendettement_annees')} annees")

    print("\n" + "="*80)
    print("EVOLUTIONS SUR LA PERIODE")
    print("="*80)

    evolutions = ratios.get('evolutions', {})
    if evolutions:
        for nom_ratio, evo_data in list(evolutions.items())[:5]:
            print(f"\n{nom_ratio}:")
            print(f"  {evo_data['valeur_debut']:.1f} -> {evo_data['valeur_fin']:.1f}")
            print(f"  Evolution totale: {evo_data['evolution_totale']:+.1f}")
            print(f"  Evolution moyenne annuelle: {evo_data['evolution_moyenne_annuelle']:+.1f}")

else:
    print("\n[WARN] Pas de ratios_par_annee trouve")
    print("Contenu actuel de ratios_financiers:")
    pprint.pprint(ratios)
