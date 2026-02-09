"""
Script pour tester différentes combinaisons de formules pour trouver les bons résultats
Valeurs attendues:
- EBF : 201k€
- CAF brute : 192k€
- CAF nette : 86k€
"""

import requests
import json

def fetch_balance_data(siren, annee):
    """Récupère les données de l'API"""
    base_url = f"https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/balances-comptables-des-communes-en-{annee}/records"

    all_records = []
    offset = 0
    limit = 100

    while True:
        params = {
            "where": f"siren={siren}",
            "limit": limit,
            "offset": offset
        }

        response = requests.get(base_url, params=params)
        data = response.json()
        records = data.get('results', [])

        if not records:
            break

        all_records.extend(records)

        if len(records) < limit:
            break

        offset += limit

    # Filtrer budget principal
    return [r for r in all_records if r.get('cbudg') == '1']

def test_combinaisons(records):
    """Teste différentes combinaisons de formules"""

    # Construire dictionnaires
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
        """Somme selon le mode : 'flux_net', 'credit', ou 'debit'"""
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

    def comptes_terminaison_9(classe):
        return [f"{classe}{i}9" for i in range(10)]

    # Remboursement emprunts (constant)
    remb_emprunts = somme(['163','164','1671','1672','1675','1678','1681','1682'],
                          'debit', ['16449','1645'])

    print("="*80)
    print("TEST DE DIFFÉRENTES COMBINAISONS")
    print("="*80)
    print(f"Remboursement emprunts : {remb_emprunts:,.2f} €")
    print()

    # COMBO 1 : Flux net uniquement
    print("--- COMBO 1 : Flux net uniquement ---")
    prod_caf_1 = somme(['70','71','72','73','74','75','76','77','79'], 'flux_net',
                       ['75882','775','776','777'])
    chg_caf_1 = -somme(['60','61','62','63','64','65','66','67'], 'flux_net',
                       ['65882','675','676'])
    ebf_1 = prod_caf_1 - chg_caf_1
    caf_1 = somme('7', 'flux_net') + somme('6', 'flux_net')
    caf_nette_1 = caf_1 - remb_emprunts

    print(f"  EBF : {ebf_1:,.2f} € (attendu 201k)")
    print(f"  CAF brute : {caf_1:,.2f} € (attendu 192k)")
    print(f"  CAF nette : {caf_nette_1:,.2f} € (attendu 86k)")
    print()

    # COMBO 2 : Crédits/Débits séparés pour Produits/Charges CAF
    print("--- COMBO 2 : Crédits/Débits séparés pour Produits/Charges CAF ---")
    prod_caf_2 = somme(['70','71','72','73','74','75','76','77','79'], 'credit',
                       ['75882','775','776','777'])
    chg_caf_2 = somme(['60','61','62','63','64','65','66','67'], 'debit',
                      ['65882','675','676'])
    ebf_2 = prod_caf_2 - chg_caf_2
    caf_2 = somme('7', 'credit') - somme('6', 'debit')
    caf_nette_2 = caf_2 - remb_emprunts

    print(f"  EBF : {ebf_2:,.2f} € (attendu 201k)")
    print(f"  CAF brute : {caf_2:,.2f} € (attendu 192k)")
    print(f"  CAF nette : {caf_nette_2:,.2f} € (attendu 86k)")
    print()

    # COMBO 3 : Produits CAF en crédit, Charges CAF en débit, mais soustraire comptes à terminaison en 9
    print("--- COMBO 3 : Crédits/Débits avec soustraction terminaison 9 ---")
    prod_caf_3 = (somme(['70','71','72','73','74','75','76','77'], 'credit',
                        ['75882','775','776','777']) +
                  somme('79', 'flux_net'))
    chg_caf_3 = (somme(['60','61','62','63','64','65','66','67'], 'debit',
                       ['65882','675','676']))
    ebf_3 = prod_caf_3 - chg_caf_3
    caf_3 = (somme('7', 'credit') - somme(comptes_terminaison_9('7'), 'debit') -
             somme('6', 'debit') + somme(comptes_terminaison_9('6'), 'credit'))
    caf_nette_3 = caf_3 - remb_emprunts

    print(f"  EBF : {ebf_3:,.2f} € (attendu 201k)")
    print(f"  CAF brute : {caf_3:,.2f} € (attendu 192k)")
    print(f"  CAF nette : {caf_nette_3:,.2f} € (attendu 86k)")
    print()

    # COMBO 4 : Total produits/charges fonc moins opérations d'ordre
    print("--- COMBO 4 : A - opérations ordre / B - opérations ordre ---")
    total_A = somme('7', 'credit') - somme(comptes_terminaison_9('7'), 'debit')
    total_B = somme('6', 'debit') - somme(comptes_terminaison_9('6'), 'credit')

    # Produits CAF = Total A moins produits financiers/exceptionnels sans opérations ordre
    prod_caf_4 = somme(['70','71','72','73','74','75','76','77'], 'credit',
                       ['75882','775','776','777']) + somme('79', 'flux_net')

    # Charges CAF = Total B moins charges financières/exceptionnelles sans opérations ordre
    chg_caf_4 = somme(['60','61','62','63','64','65','66','67'], 'debit',
                      ['65882','675','676'])

    ebf_4 = prod_caf_4 - chg_caf_4
    caf_4 = total_A - total_B
    caf_nette_4 = caf_4 - remb_emprunts

    print(f"  Total A : {total_A:,.2f} €")
    print(f"  Total B : {total_B:,.2f} €")
    print(f"  EBF : {ebf_4:,.2f} € (attendu 201k)")
    print(f"  CAF brute : {caf_4:,.2f} € (attendu 192k)")
    print(f"  CAF nette : {caf_nette_4:,.2f} € (attendu 86k)")
    print()

    # COMBO 5 : EBF avec uniquement 70-75 et 60-65 en flux net
    print("--- COMBO 5 : EBF = flux net 70-75 moins flux net 60-65 ---")
    prod_7075 = somme(['70','71','72','73','74','75'], 'flux_net')
    chg_6065 = somme(['60','61','62','63','64','65'], 'flux_net')
    ebf_5 = prod_7075 + chg_6065  # chg_6065 est déjà négatif

    # CAF = Résultat + retraitements
    resultat = somme('7', 'flux_net') + somme('6', 'flux_net')
    retraitement = (somme(['65882','675','676'], 'debit') -
                    somme(['75882','775','776','777'], 'credit'))
    caf_5 = resultat + retraitement
    caf_nette_5 = caf_5 - remb_emprunts

    print(f"  Produits 70-75 : {prod_7075:,.2f} €")
    print(f"  Charges 60-65 : {chg_6065:,.2f} €")
    print(f"  EBF : {ebf_5:,.2f} € (attendu 201k)")
    print(f"  CAF brute : {caf_5:,.2f} € (attendu 192k)")
    print(f"  CAF nette : {caf_nette_5:,.2f} € (attendu 86k)")
    print()

    # COMBO 6 : Crédits nets (70-75) - Débits nets (60-65) pour EBF
    print("--- COMBO 6 : EBF = Crédits(70-75) - Débits(60-65) ---")
    prod_7075_cre = somme(['70','71','72','73','74','75'], 'credit')
    chg_6065_deb = somme(['60','61','62','63','64','65'], 'debit')
    ebf_6 = prod_7075_cre - chg_6065_deb

    caf_6 = total_A - total_B
    caf_nette_6 = caf_6 - remb_emprunts

    print(f"  Produits crédits 70-75 : {prod_7075_cre:,.2f} €")
    print(f"  Charges débits 60-65 : {chg_6065_deb:,.2f} €")
    print(f"  EBF : {ebf_6:,.2f} € (attendu 201k)")
    print(f"  CAF brute : {caf_6:,.2f} € (attendu 192k)")
    print(f"  CAF nette : {caf_nette_6:,.2f} € (attendu 86k)")
    print()

    print("="*80)
    print("ANALYSE DES ÉCARTS")
    print("="*80)

    combos = [
        ("COMBO 1", ebf_1, caf_1, caf_nette_1),
        ("COMBO 2", ebf_2, caf_2, caf_nette_2),
        ("COMBO 3", ebf_3, caf_3, caf_nette_3),
        ("COMBO 4", ebf_4, caf_4, caf_nette_4),
        ("COMBO 5", ebf_5, caf_5, caf_nette_5),
        ("COMBO 6", ebf_6, caf_6, caf_nette_6),
    ]

    target_ebf = 201000
    target_caf = 192000
    target_caf_nette = 86000

    meilleur_score = float('inf')
    meilleur_combo = None

    for nom, ebf, caf, caf_nette in combos:
        ecart_ebf = abs(ebf - target_ebf)
        ecart_caf = abs(caf - target_caf)
        ecart_caf_nette = abs(caf_nette - target_caf_nette)
        score = ecart_ebf + ecart_caf + ecart_caf_nette

        print(f"{nom}:")
        print(f"  Écarts: EBF={ecart_ebf:,.0f} CAF={ecart_caf:,.0f} CAF nette={ecart_caf_nette:,.0f}")
        print(f"  Score total: {score:,.0f}")

        if score < meilleur_score:
            meilleur_score = score
            meilleur_combo = nom

        print()

    print(f"MEILLEUR COMBO : {meilleur_combo} (score: {meilleur_score:,.0f})")

if __name__ == "__main__":
    print("Récupération des données...")
    records = fetch_balance_data("200053395", "2024")
    print(f"Données récupérées : {len(records)} enregistrements")
    print()

    test_combinaisons(records)
