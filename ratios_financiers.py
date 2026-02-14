"""
Module de calcul des ratios financiers pour l'analyse budgétaire M14/M57
Centralise tous les calculs de ratios pour garantir cohérence et exactitude
"""


def calculer_ratio_charges_personnel(charges_personnel_k, charges_caf_k):
    """
    Calcule la part des charges de personnel dans les charges CAF
    Ratio : charges_personnel / charges_caf * 100
    """
    if not charges_caf_k or charges_caf_k == 0:
        return None
    return round((charges_personnel_k / charges_caf_k) * 100, 1)


def calculer_taux_epargne_brute(caf_brute_k, produits_caf_k):
    """
    Calcule le taux d'épargne brute
    Ratio : CAF brute / produits CAF * 100
    Indicateur de la capacité à dégager de l'épargne
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((caf_brute_k / produits_caf_k) * 100, 1)


def calculer_taux_epargne_nette(caf_nette_k, produits_caf_k):
    """
    Calcule le taux d'épargne nette
    Ratio : CAF nette / produits CAF * 100
    Indicateur de l'autofinancement disponible pour investir
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((caf_nette_k / produits_caf_k) * 100, 1)


def calculer_capacite_desendettement(encours_dette_k, caf_brute_k):
    """
    Calcule la capacité de désendettement
    Ratio : encours dette / CAF brute (en années)
    Seuil prudentiel : < 12 ans
    """
    if not caf_brute_k or caf_brute_k == 0:
        return None
    return round(encours_dette_k / caf_brute_k, 1)


def calculer_ratio_endettement(encours_dette_k, produits_caf_k):
    """
    Calcule le ratio d'endettement
    Ratio : encours dette / produits CAF * 100
    Mesure le poids de la dette par rapport à la richesse
    Si > 100%, la dette représente plus d'une année de fonctionnement
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((encours_dette_k / produits_caf_k) * 100, 1)


def calculer_ratio_effort_equipement(depenses_equipement_k, produits_caf_k):
    """
    Calcule le ratio d'effort d'équipement
    Ratio : dépenses équipement / produits CAF * 100
    Mesure la part des produits consacrée à l'investissement
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((depenses_equipement_k / produits_caf_k) * 100, 1)


def calculer_ratio_autonomie_fiscale(impots_locaux_k, produits_caf_k):
    """
    Calcule le ratio d'autonomie fiscale
    Ratio : impôts locaux / produits CAF * 100
    Mesure la part de la fiscalité locale dans les recettes
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((impots_locaux_k / produits_caf_k) * 100, 1)


def calculer_ratio_rigidite_fonctionnement(charges_personnel_k, charges_financieres_k, produits_caf_k):
    """
    Calcule le ratio de rigidité du fonctionnement
    Ratio : (charges personnel + charges financières) / produits CAF * 100
    Mesure la part des charges incompressibles dans les recettes
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    charges_rigides_k = (charges_personnel_k or 0) + (charges_financieres_k or 0)
    return round((charges_rigides_k / produits_caf_k) * 100, 1)


def calculer_taux_couverture_depenses_equipement(caf_nette_k, depenses_equipement_k):
    """
    Calcule le taux de couverture des dépenses d'équipement par la CAF nette
    Ratio : CAF nette / dépenses équipement * 100
    Mesure la capacité à financer les dépenses d'équipement par l'autofinancement net

    IMPORTANT (doctrine M57) :
    - Ce ratio mesure uniquement la couverture des dépenses d'équipement (immobilisations)
    - Il ne couvre pas l'ensemble de la section d'investissement
    """
    if not depenses_equipement_k or depenses_equipement_k == 0:
        return None
    return round((caf_nette_k / depenses_equipement_k) * 100, 1)


def calculer_coefficient_mobilisation_caf(remboursement_capital_k, caf_brute_k):
    """
    Calcule le coefficient de mobilisation de la CAF
    Ratio : Remboursement capital / CAF brute * 100
    Mesure quelle part de l'épargne est 'prélevée' par la dette avant même de pouvoir investir

    Interprétation :
    - < 50% : Marge de manœuvre confortable pour l'investissement
    - 50-70% : Mobilisation modérée de l'épargne
    - > 70% : Forte mobilisation, capacité d'investissement réduite
    """
    if not caf_brute_k or caf_brute_k == 0:
        return None
    return round((remboursement_capital_k / caf_brute_k) * 100, 1)


def calculer_taux_autofinancement_investissement_productif(caf_nette_k, total_emplois_investissement_k, remboursement_capital_k):
    """
    Calcule le taux d'autofinancement de l'investissement productif par la CAF nette
    Ratio : CAF nette / (Total emplois investissement - Remboursement capital) * 100

    IMPORTANT (doctrine M57) :
    - La CAF nette = CAF brute - Remboursement capital
    - Elle finance les emplois d'investissement hors remboursement capital
    - Ces emplois incluent : dépenses d'équipement + subventions d'équipement versées + opérations financières
    """
    emplois_productifs_k = (total_emplois_investissement_k or 0) - (remboursement_capital_k or 0)

    if not emplois_productifs_k or emplois_productifs_k == 0:
        return None
    return round((caf_nette_k / emplois_productifs_k) * 100, 1)


def calculer_ratio_achats_externes(achats_charges_externes_k, charges_caf_k):
    """
    Calcule la part des achats et charges externes dans les charges CAF
    Ratio : achats et charges externes / charges CAF * 100
    """
    if not charges_caf_k or charges_caf_k == 0:
        return None
    return round((achats_charges_externes_k / charges_caf_k) * 100, 1)


def calculer_tous_les_ratios(data_json):
    """
    Calcule tous les ratios financiers à partir du JSON enrichi
    Retourne un dictionnaire avec tous les ratios
    """

    # Extraction des valeurs du JSON
    produits_caf_k = data_json.get('fonctionnement', {}).get('produits', {}).get('produits_caf', {}).get('montant_k', 0)
    impots_locaux_k = data_json.get('fonctionnement', {}).get('produits', {}).get('impots_locaux', {}).get('montant_k', 0)

    charges_caf_k = data_json.get('fonctionnement', {}).get('charges', {}).get('charges_caf', {}).get('montant_k', 0)
    charges_personnel_k = data_json.get('fonctionnement', {}).get('charges', {}).get('charges_personnel', {}).get('montant_k', 0)
    achats_charges_externes_k = data_json.get('fonctionnement', {}).get('charges', {}).get('achats_charges_externes', {}).get('montant_k', 0)
    charges_financieres_k = data_json.get('fonctionnement', {}).get('charges', {}).get('charges_financieres', {}).get('montant_k', 0)

    caf_brute_k = data_json.get('autofinancement', {}).get('caf_brute', {}).get('montant_k', 0)
    caf_nette_k = data_json.get('autofinancement', {}).get('caf_nette', {}).get('montant_k', 0)

    depenses_equipement_k = data_json.get('investissement', {}).get('emplois', {}).get('depenses_equipement', {}).get('montant_k', 0)
    total_emplois_investissement_k = data_json.get('investissement', {}).get('emplois', {}).get('total_k', 0)
    remboursement_capital_k = data_json.get('investissement', {}).get('emplois', {}).get('remboursement_emprunts', {}).get('montant_k', 0)

    encours_dette_k = data_json.get('endettement', {}).get('encours_total', {}).get('montant_k', 0)

    # Calcul de tous les ratios
    ratios = {
        'part_charges_personnel_pct': calculer_ratio_charges_personnel(charges_personnel_k, charges_caf_k),
        'taux_epargne_brute_pct': calculer_taux_epargne_brute(caf_brute_k, produits_caf_k),
        'taux_epargne_nette_pct': calculer_taux_epargne_nette(caf_nette_k, produits_caf_k),
        'capacite_desendettement_annees': calculer_capacite_desendettement(encours_dette_k, caf_brute_k),
        'ratio_endettement_pct': calculer_ratio_endettement(encours_dette_k, produits_caf_k),
        'ratio_effort_equipement_pct': calculer_ratio_effort_equipement(depenses_equipement_k, produits_caf_k),
        'ratio_autonomie_fiscale_pct': calculer_ratio_autonomie_fiscale(impots_locaux_k, produits_caf_k),
        'ratio_rigidite_fonctionnement_pct': calculer_ratio_rigidite_fonctionnement(
            charges_personnel_k, charges_financieres_k, produits_caf_k
        ),
        'coefficient_mobilisation_caf_pct': calculer_coefficient_mobilisation_caf(remboursement_capital_k, caf_brute_k),
        # Ratios conformes à la doctrine M57
        'taux_couverture_depenses_equipement_pct': calculer_taux_couverture_depenses_equipement(caf_nette_k, depenses_equipement_k),
        'taux_autofinancement_investissement_productif_pct': calculer_taux_autofinancement_investissement_productif(
            caf_nette_k, total_emplois_investissement_k, remboursement_capital_k
        ),
        'part_achats_externes_pct': calculer_ratio_achats_externes(achats_charges_externes_k, charges_caf_k),

        # DEPRECATED : Ancien nom conservé pour rétrocompatibilité
        'taux_couverture_investissement_pct': calculer_taux_couverture_depenses_equipement(caf_nette_k, depenses_equipement_k)
    }

    return ratios


def enrichir_json_avec_ratios(data_json):
    """
    Enrichit le JSON avec une section 'ratios_financiers' contenant tous les ratios calculés
    Modifie le dictionnaire en place et le retourne
    """
    ratios = calculer_tous_les_ratios(data_json)

    # Ajouter une section ratios_financiers au JSON
    data_json['ratios_financiers'] = ratios

    return data_json


# =============================================================================
# FONCTIONS POUR LES DONNÉES MULTI-ANNÉES
# =============================================================================

def calculer_ratios_annee_specifique(bilan_annuel):
    """
    Calcule tous les ratios pour un bilan d'une année spécifique
    Le bilan doit avoir la structure : fonctionnement, autofinancement, investissement, endettement
    """
    return calculer_tous_les_ratios(bilan_annuel)


def calculer_evolution_ratio(ratios_debut, ratios_fin, nom_ratio):
    """
    Calcule l'évolution d'un ratio entre deux années
    Retourne l'évolution en points de pourcentage (pour les %) ou en années (pour capacité désendettement)
    """
    valeur_debut = ratios_debut.get(nom_ratio)
    valeur_fin = ratios_fin.get(nom_ratio)

    if valeur_debut is None or valeur_fin is None:
        return None

    return round(valeur_fin - valeur_debut, 1)


def calculer_tous_ratios_multi_annees(data_json_multi):
    """
    Calcule tous les ratios pour chaque année dans un JSON multi-années

    Structure attendue :
    {
        "bilans_annuels": {
            "2022": {...},
            "2023": {...},
            "2024": {...}
        }
    }

    Retourne :
    {
        "ratios_par_annee": {
            "2022": {...ratios...},
            "2023": {...ratios...},
            "2024": {...ratios...}
        },
        "evolutions": {
            "ratio_xxx": {
                "valeur_debut": X,
                "valeur_fin": Y,
                "evolution": Z,
                "evolution_moyenne_annuelle": W
            }
        }
    }
    """
    bilans_annuels = data_json_multi.get('bilans_annuels', {})

    if not bilans_annuels:
        return None

    # Récupérer les années disponibles et les trier
    annees = sorted([int(a) for a in bilans_annuels.keys()])

    if len(annees) < 2:
        return None

    # Calculer les ratios pour chaque année
    ratios_par_annee = {}
    for annee in annees:
        bilan = bilans_annuels[str(annee)]
        ratios_par_annee[str(annee)] = calculer_ratios_annee_specifique(bilan)

    # Calculer les évolutions
    premiere_annee = str(annees[0])
    derniere_annee = str(annees[-1])
    nb_annees = annees[-1] - annees[0]

    ratios_debut = ratios_par_annee[premiere_annee]
    ratios_fin = ratios_par_annee[derniere_annee]

    evolutions = {}
    for nom_ratio in ratios_debut.keys():
        evolution = calculer_evolution_ratio(ratios_debut, ratios_fin, nom_ratio)

        if evolution is not None:
            valeur_debut = ratios_debut[nom_ratio]
            valeur_fin = ratios_fin[nom_ratio]
            evolution_moyenne = round(evolution / nb_annees, 1) if nb_annees > 0 else 0

            evolutions[nom_ratio] = {
                'valeur_debut': valeur_debut,
                'valeur_fin': valeur_fin,
                'evolution_totale': evolution,
                'evolution_moyenne_annuelle': evolution_moyenne,
                'nb_annees': nb_annees
            }

    return {
        'ratios_par_annee': ratios_par_annee,
        'evolutions': evolutions
    }


def enrichir_json_multi_annees_avec_ratios(data_json_multi):
    """
    Enrichit un JSON multi-années avec les ratios calculés pour chaque année
    Modifie le dictionnaire en place et le retourne
    """
    ratios_multi = calculer_tous_ratios_multi_annees(data_json_multi)

    if ratios_multi:
        data_json_multi['ratios_financiers'] = ratios_multi

    return data_json_multi


if __name__ == "__main__":
    # Test avec un exemple
    import json

    print("="*80)
    print("TEST DU MODULE DE CALCUL DES RATIOS FINANCIERS")
    print("="*80)

    # Charger le JSON mono-année
    try:
        with open('output/donnees_enrichies.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"\nCommune : {data['metadata']['commune']}")
        print(f"Exercice : {data['metadata']['exercice']}")

        # Calculer tous les ratios
        ratios = calculer_tous_les_ratios(data)

        print("\n--- RATIOS CALCULÉS ---\n")
        for nom_ratio, valeur in ratios.items():
            if valeur is not None:
                if 'annees' in nom_ratio:
                    print(f"{nom_ratio:.<50} {valeur:.1f} années")
                else:
                    print(f"{nom_ratio:.<50} {valeur:.1f} %")
            else:
                print(f"{nom_ratio:.<50} N/A")

        # Comparer avec l'ancien calcul erroné
        charges_personnel = data['fonctionnement']['charges']['charges_personnel']['montant_k']
        charges_total = data['fonctionnement']['charges']['total']['montant_k']
        charges_caf = data['fonctionnement']['charges']['charges_caf']['montant_k']

        ancien_calcul = round((charges_personnel / charges_total) * 100, 1)
        nouveau_calcul = ratios['part_charges_personnel_pct']

        print("\n" + "="*80)
        print("COMPARAISON : Part des charges de personnel")
        print("="*80)
        print(f"Ancien calcul (FAUX) : {charges_personnel} / {charges_total} = {ancien_calcul}%")
        print(f"Nouveau calcul (CORRECT) : {charges_personnel} / {charges_caf} = {nouveau_calcul}%")
        print(f"Écart : {nouveau_calcul - ancien_calcul:.1f} points de pourcentage")

    except FileNotFoundError:
        print("\n[ERREUR] Fichier 'output/donnees_enrichies.json' non trouvé")
        print("Veuillez exécuter le script depuis le répertoire du projet")
