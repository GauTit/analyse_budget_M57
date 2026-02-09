"""
Analyse détaillée des retraitements de la CAF
"""

import requests

def fetch_balance_data(siren, annee):
    base_url = f"https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/balances-comptables-des-communes-en-{annee}/records"
    all_records = []
    offset = 0
    limit = 100

    while True:
        params = {"where": f"siren={siren}", "limit": limit, "offset": offset}
        response = requests.get(base_url, params=params)
        data = response.json()
        records = data.get('results', [])
        if not records:
            break
        all_records.extend(records)
        if len(records) < limit:
            break
        offset += limit

    return [r for r in all_records if r.get('cbudg') == '1']

def analyse_retraitements(records):
    comptes_dict = {}
    for record in records:
        compte = str(record.get('compte', ''))
        if not compte:
            continue

        credit = record.get('obnetcre', 0) or 0
        debit = record.get('obnetdeb', 0) or 0
        flux_net = credit - debit

        if compte not in comptes_dict:
            comptes_dict[compte] = {'credit': 0, 'debit': 0, 'flux_net': 0}

        comptes_dict[compte]['credit'] += credit
        comptes_dict[compte]['debit'] += debit
        comptes_dict[compte]['flux_net'] += flux_net

    def somme(prefixes, mode='flux_net', exclusions=None):
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        if exclusions is None:
            exclusions = []
        if isinstance(exclusions, str):
            exclusions = [exclusions]

        total = 0
        for compte, vals in comptes_dict.items():
            if any(compte.startswith(p) for p in prefixes):
                if not any(compte.startswith(e) for e in exclusions):
                    total += vals[mode]
        return round(total, 2)

    print("="*80)
    print("ANALYSE DES RETRAITEMENTS CAF")
    print("="*80)

    # Résultat de base
    resultat = somme('7', 'flux_net') + somme('6', 'flux_net')
    print(f"Résultat comptable (flux net 7 + flux net 6) : {resultat:,.2f} €")
    print()

    # Retraitements selon spécification
    print("Retraitements selon spécification M57 :")
    retraitement_675 = somme('675', 'debit')
    retraitement_676 = somme('676', 'debit')
    retraitement_65882 = somme('65882', 'debit')
    retraitement_775 = somme('775', 'credit')
    retraitement_776 = somme('776', 'credit')
    retraitement_777 = somme('777', 'credit')
    retraitement_75882 = somme('75882', 'credit')

    print(f"  + Débits 675 : {retraitement_675:,.2f} €")
    print(f"  + Débits 676 : {retraitement_676:,.2f} €")
    print(f"  + Débits 65882 : {retraitement_65882:,.2f} €")
    print(f"  - Crédits 775 : {retraitement_775:,.2f} €")
    print(f"  - Crédits 776 : {retraitement_776:,.2f} €")
    print(f"  - Crédits 777 : {retraitement_777:,.2f} €")
    print(f"  - Crédits 75882 : {retraitement_75882:,.2f} €")

    total_retraitement_spec = (retraitement_675 + retraitement_676 + retraitement_65882 -
                                retraitement_775 - retraitement_776 - retraitement_777 - retraitement_75882)
    print(f"  TOTAL retraitements (spec) : {total_retraitement_spec:,.2f} €")
    print()

    caf_spec = resultat + total_retraitement_spec
    print(f"CAF selon spécification : {caf_spec:,.2f} € (attendu 192k)")
    print(f"Écart : {192000 - caf_spec:,.2f} €")
    print()

    # Peut-être que les comptes à terminaison en 9 des classes 6 et 7 jouent un rôle ?
    print("="*80)
    print("ANALYSE DES COMPTES À TERMINAISON EN 9")
    print("="*80)

    comptes_9_classe7 = []
    comptes_9_classe6 = []

    for i in range(10):
        for j in range(10):
            c7 = f"7{i}{j}9"
            c6 = f"6{i}{j}9"
            if c7 in comptes_dict:
                comptes_9_classe7.append((c7, comptes_dict[c7]))
            if c6 in comptes_dict:
                comptes_9_classe6.append((c6, comptes_dict[c6]))

    if comptes_9_classe7:
        print("Comptes classe 7 à terminaison en 9 :")
        for compte, vals in comptes_9_classe7:
            print(f"  {compte}: flux_net={vals['flux_net']:,.2f} credit={vals['credit']:,.2f} debit={vals['debit']:,.2f}")

    if comptes_9_classe6:
        print("Comptes classe 6 à terminaison en 9 :")
        for compte, vals in comptes_9_classe6:
            print(f"  {compte}: flux_net={vals['flux_net']:,.2f} credit={vals['credit']:,.2f} debit={vals['debit']:,.2f}")

    print()

    # Test : CAF en excluant les opérations d'ordre
    print("="*80)
    print("TEST : CAF EN EXCLUANT LES OPÉRATIONS D'ORDRE")
    print("="*80)

    def comptes_terminaison_9(classe):
        return [f"{classe}{i}9" for i in range(10)]

    total_A = somme('7', 'credit') - somme(comptes_terminaison_9('7'), 'debit')
    total_B = somme('6', 'debit') - somme(comptes_terminaison_9('6'), 'credit')

    print(f"Total A (crédits 7 - débits comptes à term. 9) : {total_A:,.2f} €")
    print(f"Total B (débits 6 - crédits comptes à term. 9) : {total_B:,.2f} €")

    caf_test = total_A - total_B + total_retraitement_spec
    print(f"CAF (A - B + retraitements) : {caf_test:,.2f} € (attendu 192k)")
    print(f"Écart : {192000 - caf_test:,.2f} €")
    print()

    # Analyse flux net des comptes 67 et 77
    print("="*80)
    print("ANALYSE DES COMPTES 67 ET 77")
    print("="*80)

    flux_67 = somme('67', 'flux_net')
    flux_77 = somme('77', 'flux_net')
    print(f"Flux net compte 67 : {flux_67:,.2f} €")
    print(f"Flux net compte 77 : {flux_77:,.2f} €")
    print(f"Flux net 67 + 77 : {flux_67 + flux_77:,.2f} €")
    print()

    # CAF en ajoutant flux net 67 et 77
    caf_test2 = resultat + total_retraitement_spec + flux_67 + flux_77
    print(f"CAF (résultat + retraitements + flux 67+77) : {caf_test2:,.2f} € (attendu 192k)")
    print(f"Écart : {192000 - caf_test2:,.2f} €")
    print()

if __name__ == "__main__":
    print("Récupération des données...")
    records = fetch_balance_data("200053395", "2024")
    print(f"Données récupérées : {len(records)} enregistrements\n")

    analyse_retraitements(records)
