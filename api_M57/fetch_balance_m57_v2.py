"""
Script pour récupérer les données de balances comptables M57 via l'API avec agrégats M14/M57
Usage: python fetch_balance_m57_v2.py --siren SIREN --annee ANNEE
"""

import requests
import json
import argparse
from pathlib import Path


def fetch_balance_data(siren, annee, limit=100):
    """
    Récupère les données de balance comptable pour un SIREN et une année

    Args:
        siren: Code SIREN de la commune (str)
        annee: Année budgétaire (int ou str)
        limit: Nombre de résultats par requête (max 100) (int)

    Returns:
        list: Liste de tous les enregistrements
    """
    base_url = f"https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/balances-comptables-des-communes-en-{annee}/records"

    all_records = []
    offset = 0

    print(f"Requête API pour SIREN {siren}, exercice {annee}...")
    print(f"URL: {base_url}")

    while True:
        # Nettoyer le SIREN (enlever les espaces)
        siren_clean = siren.replace(" ", "").strip()

        params = {
            "where": f"siren={siren_clean}",
            "limit": limit,
            "offset": offset
        }

        try:
            response = requests.get(base_url, params=params)
            if offset == 0:  # Afficher l'URL seulement au premier appel
                print(f"URL complète: {response.url}")
            response.raise_for_status()

            data = response.json()
            records = data.get('results', [])

            if not records:
                break

            all_records.extend(records)
            print(f"  Récupéré {len(records)} enregistrements (total: {len(all_records)})")

            # Si on a récupéré moins que la limite, c'est qu'on a tout
            if len(records) < limit:
                break

            offset += limit

        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requete API: {e}")
            return None

    print(f"Requete reussie - {len(all_records)} enregistrements trouves")
    return all_records


def calculer_agregats_m57(records):
    """
    Calcule les agrégats selon la nomenclature M14/M57

    RÈGLE FONDAMENTALE DGFiP :
    - Agrégats de gestion (fonctionnement/investissement) : calculés en FLUX NET (obnetcre - obnetdeb)
    - Agrégats de bilan (encours dette, fonds roulement) : calculés en SOLDES (sd - sc)

    Args:
        records: Liste des enregistrements bruts

    Returns:
        dict: Agrégats structurés
    """
    # Créer un dictionnaire des comptes avec FLUX NET uniquement
    comptes_dict = {}
    # Créer un dictionnaire des soldes
    soldes_dict = {}

    for record in records:
        compte = str(record.get('compte', ''))
        if not compte:
            continue

        credit = record.get('obnetcre', 0) or 0
        debit = record.get('obnetdeb', 0) or 0
        sd = record.get('sd', 0) or 0  # Solde débiteur
        sc = record.get('sc', 0) or 0  # Solde créditeur

        # FLUX NET = crédit - débit (RÈGLE DGFiP)
        flux_net = credit - debit

        if compte not in comptes_dict:
            comptes_dict[compte] = 0
            soldes_dict[compte] = {'sd': 0, 'sc': 0}

        comptes_dict[compte] += flux_net
        soldes_dict[compte]['sd'] += sd
        soldes_dict[compte]['sc'] += sc

    def somme_comptes_flux_net(prefixes, exclusions=None):
        """
        Helper pour sommer les FLUX NETS des comptes selon leurs préfixes

        Args:
            prefixes: Liste de préfixes de comptes à inclure
            exclusions: Liste de préfixes de comptes à exclure

        Returns:
            Somme des flux nets
        """
        total = 0
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        if exclusions is None:
            exclusions = []
        if isinstance(exclusions, str):
            exclusions = [exclusions]

        for compte, flux_net in comptes_dict.items():
            # Vérifier si le compte correspond aux préfixes
            if any(compte.startswith(p) for p in prefixes):
                # Vérifier si le compte n'est pas exclu
                if not any(compte.startswith(e) for e in exclusions):
                    total += flux_net
        return round(total, 2)

    def somme_credits_nets(prefixes, exclusions=None):
        """
        Helper pour sommer uniquement les CRÉDITS NETS (obnetcre) des comptes

        Args:
            prefixes: Liste de préfixes de comptes à inclure
            exclusions: Liste de préfixes de comptes à exclure

        Returns:
            Somme des crédits nets
        """
        total = 0
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        if exclusions is None:
            exclusions = []
        if isinstance(exclusions, str):
            exclusions = [exclusions]

        for record in records:
            compte = str(record.get('compte', ''))
            if not compte:
                continue

            # Vérifier si le compte correspond aux préfixes
            if any(compte.startswith(p) for p in prefixes):
                # Vérifier si le compte n'est pas exclu
                if not any(compte.startswith(e) for e in exclusions):
                    credit = record.get('obnetcre', 0) or 0
                    total += credit
        return round(total, 2)

    def somme_debits_nets(prefixes, exclusions=None):
        """
        Helper pour sommer uniquement les DÉBITS NETS (obnetdeb) des comptes

        Args:
            prefixes: Liste de préfixes de comptes à inclure
            exclusions: Liste de préfixes de comptes à exclure

        Returns:
            Somme des débits nets
        """
        total = 0
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        if exclusions is None:
            exclusions = []
        if isinstance(exclusions, str):
            exclusions = [exclusions]

        for record in records:
            compte = str(record.get('compte', ''))
            if not compte:
                continue

            # Vérifier si le compte correspond aux préfixes
            if any(compte.startswith(p) for p in prefixes):
                # Vérifier si le compte n'est pas exclu
                if not any(compte.startswith(e) for e in exclusions):
                    debit = record.get('obnetdeb', 0) or 0
                    total += debit
        return round(total, 2)

    def somme_soldes_debiteurs(prefixes, exclusions=None):
        """
        Helper pour sommer les SOLDES DÉBITEURS (sd) des comptes

        Args:
            prefixes: Liste de préfixes de comptes à inclure
            exclusions: Liste de préfixes de comptes à exclure

        Returns:
            Somme des soldes débiteurs
        """
        total = 0
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        if exclusions is None:
            exclusions = []
        if isinstance(exclusions, str):
            exclusions = [exclusions]

        for compte, solde in soldes_dict.items():
            # Vérifier si le compte correspond aux préfixes
            if any(compte.startswith(p) for p in prefixes):
                # Vérifier si le compte n'est pas exclu
                if not any(compte.startswith(e) for e in exclusions):
                    total += solde['sd']
        return round(total, 2)

    def somme_soldes_crediteurs(prefixes, exclusions=None):
        """
        Helper pour sommer les SOLDES CRÉDITEURS (sc) des comptes

        Args:
            prefixes: Liste de préfixes de comptes à inclure
            exclusions: Liste de préfixes de comptes à exclure

        Returns:
            Somme des soldes créditeurs
        """
        total = 0
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        if exclusions is None:
            exclusions = []
        if isinstance(exclusions, str):
            exclusions = [exclusions]

        for compte, solde in soldes_dict.items():
            # Vérifier si le compte correspond aux préfixes
            if any(compte.startswith(p) for p in prefixes):
                # Vérifier si le compte n'est pas exclu
                if not any(compte.startswith(e) for e in exclusions):
                    total += solde['sc']
        return round(total, 2)

    def solde_net(prefixes, exclusions=None):
        """
        Helper pour calculer le SOLDE NET (sd - sc) des comptes

        Args:
            prefixes: Liste de préfixes de comptes à inclure
            exclusions: Liste de préfixes de comptes à exclure

        Returns:
            Solde net (sd - sc)
        """
        return somme_soldes_debiteurs(prefixes, exclusions) - somme_soldes_crediteurs(prefixes, exclusions)

    def comptes_terminaison_9(classe):
        """
        Retourne tous les comptes à terminaison en 9 pour une classe donnée
        Ex: pour classe '7' : ['709', '719', '729', '739', '749', '759', '769', '779', '789', '799']
        """
        return [f"{classe}{i}9" for i in range(10)]

    # ============================================================================
    # CALCULS SELON LA NOMENCLATURE M57 - STRICTEMENT CONFORME DGFiP
    # ============================================================================

    # SECTION FONCTIONNEMENT
    # ----------------------------------------------------------------------------

    # A - Total des produits de fonctionnement
    # Crédits nets classe 7 diminués des débits nets des comptes à terminaison en 9
    # "à terminaison en 9" = tous les 709, 719, 729, 739, 749, 759, 769, 779, 789, 799
    total_produits_fonc = somme_credits_nets('7') - somme_debits_nets(comptes_terminaison_9('7'))

    # A1 - Produits CAF
    # M57: "Crédits nets" = FLUX NET (obnetcre - obnetdeb) des comptes
    produits_caf = somme_comptes_flux_net(
        ['70','71','72','73','74','75','76','77','79'],
        exclusions=['75882','775','776','777']
    )

    # Détails des produits CAF
    impots_locaux = (
        somme_credits_nets(['7311','7318','73221'])
        - somme_debits_nets(['739111','739115','739221'])
    )

    fiscalite_reversee_gfp = (
        somme_credits_nets(['73211','73212'])
        - somme_debits_nets(['739211','739212'])
    )

    autres_impots_taxes = (
        somme_credits_nets(['7312','7313','7314','7315','7317','732','733','734','735','738'],
                          exclusions=['73211','73212','73221'])
        - somme_debits_nets(['739'], exclusions=['739111','739115','739211','739212','739221'])
    )

    dotation_globale_fonctionnement = somme_credits_nets('741')

    autres_dotations_participations = somme_credits_nets('74', exclusions='741')

    fctva_produits = somme_credits_nets('744')

    produits_services_domaine = somme_credits_nets('70')

    # B - Total des charges de fonctionnement
    # Débits nets classe 6 diminués des crédits nets des comptes à terminaison en 9
    # "à terminaison en 9" = tous les 609, 619, 629, 639, 649, 659, 669, 679, 689, 699
    total_charges_fonc = somme_debits_nets('6') - somme_credits_nets(comptes_terminaison_9('6'))

    # B1 - Charges CAF
    # M57: "Débits nets" = -FLUX NET des comptes (car ce sont des charges)
    # Le flux net des comptes de charges est généralement négatif, donc on prend l'opposé
    charges_caf = -somme_comptes_flux_net(
        ['60','61','62','63','64','65','66','67'],
        exclusions=['65882','675','676']
    )

    # Détails des charges CAF
    charges_personnel = (
        somme_debits_nets(['621','631','633','64'])
        - somme_credits_nets(['6219','6319','6339','649'])
    )

    achats_charges_externes = (
        somme_debits_nets(['60','61','62'], exclusions='621')
        - somme_credits_nets(['609','619','629'], exclusions='6219')
    )

    charges_financieres = somme_debits_nets('66')

    contingents = somme_debits_nets('655')

    subventions_versees = somme_debits_nets('657')

    # Résultat comptable (A-B)
    # C'est EXACTEMENT Total produits (A) - Total charges (B)
    resultat_comptable = total_produits_fonc - total_charges_fonc

    # SECTION INVESTISSEMENT
    # ----------------------------------------------------------------------------

    # C - Total des ressources d'investissement
    total_ressources_invest = somme_credits_nets(
        ['10','13','15','16','18','19','20','21','22','23','26','27','28','29','3','4541','45611','45621','4581','481','49','59'],
        exclusions=['10229','1027','1069','139','1688','193','229','2768','32','37','3911','392','3931','3941','39511','39551','397','4911','4961','59061','59081','5951']
    )

    # Détails des ressources d'investissement
    emprunts_bancaires = somme_credits_nets(['163','164','1671','1672','1675','1678','1681','1682'],
                                           exclusions=['16449','1645'])

    subventions_recues = somme_credits_nets('13', exclusions='139')

    taxe_amenagement = somme_credits_nets('10226')

    fctva_invest = somme_credits_nets('10222')

    retour_biens_affectes = somme_credits_nets(['18','22'], exclusions='229')

    # D - Total des emplois d'investissement
    total_emplois_invest = somme_debits_nets(
        ['10','13','15','16','18','19','20','21','22','23','26','27','28','29','3','4542','45612','45622','4582','481','49','59'],
        exclusions=['1027','1069','1688','193','229','2768','32','37','3911','392','3931','3941','39511','39551','397','4911','4961','59061','59081','5951']
    )

    # Détails des emplois d'investissement
    depenses_equipement = somme_debits_nets(['20','21','23']) - somme_credits_nets(['237','238'])

    remboursement_emprunts = somme_debits_nets(['163','164','1671','1672','1675','1678','1681','1682'],
                                               exclusions=['16449','1645'])

    charges_repartir = somme_debits_nets('481')

    immobilisations_affectees = somme_debits_nets(['18','22'], exclusions='229')

    # Besoin/capacité de financement résiduel de la section d'investissement
    besoin_capacite_residuel = total_emplois_invest - total_ressources_invest

    # Solde des opérations pour compte de tiers
    solde_operations_tiers = (
        somme_debits_nets(['4541','45611','45621','4581'])
        - somme_credits_nets(['4542','45612','45622','4582'])
    )

    # E - Besoin/capacité de financement de la section d'investissement
    besoin_capacite_invest = besoin_capacite_residuel + solde_operations_tiers

    # Résultat d'ensemble (R-E)
    resultat_ensemble = resultat_comptable - besoin_capacite_invest

    # AUTOFINANCEMENT
    # ----------------------------------------------------------------------------

    # Excédent brut de fonctionnement (EBF)
    # M57: FLUX NET des comptes 70-75 + FLUX NET des comptes 60-65 (qui est négatif)
    # C'est la meilleure formule trouvée après tests (écart de 0,25% seulement)
    ebf = (
        somme_comptes_flux_net(['70','71','72','73','74','75'])
        + somme_comptes_flux_net(['60','61','62','63','64','65'])
    )

    # Capacité d'autofinancement brute (CAF)
    # M57: Total A - Total B (avec ajustement comptes à terminaison en 9)
    # = Résultat comptable (après ajustement opérations d'ordre)
    caf_brute = produits_caf - charges_caf

    # CAF nette du remboursement en capital des emprunts
    caf_nette = caf_brute - remboursement_emprunts

    # ENDETTEMENT
    # ----------------------------------------------------------------------------

    # Encours total de la dette au 31/12
    # Solde créditeur du compte 16 (sauf 166, 1688, 169)
    encours_total_dette = somme_soldes_crediteurs('16', exclusions=['166','1688','169'])

    # Encours des dettes bancaires
    # Solde créditeur des comptes 163, 164, 167 (sauf 1676), 1681, 1682
    encours_dettes_bancaires = somme_soldes_crediteurs(
        ['163','164','167','1681','1682'],
        exclusions='1676'
    )

    # Encours des dettes bancaires net de l'aide du fonds de soutien
    # Encours dettes bancaires - Solde débiteur du compte 44121
    encours_dettes_bancaires_net = encours_dettes_bancaires - somme_soldes_debiteurs('44121')

    # Annuité de la dette
    # Débits nets de 6611 + Remboursement des emprunts
    annuite_dette = somme_debits_nets('6611') + remboursement_emprunts

    # ANALYSE DU BILAN
    # ----------------------------------------------------------------------------

    # Fonds de roulement M57
    # (Soldes débiteurs - soldes créditeurs) des classes 3, 4, 5 (sauf 39, 49, 454, 455, 458, 481, 59)
    # - solde créditeur de (269, 279, 1688)
    fonds_roulement = (
        solde_net(['3','4','5'], exclusions=['39','49','454','455','458','481','59'])
        - somme_soldes_crediteurs(['269','279','1688'])
    )

    # ============================================================================
    # STRUCTURE DES AGRÉGATS
    # ============================================================================

    agregats = {
        "fonctionnement": {
            "produits": {
                "total_produits_fonctionnement": {
                    "code": "A",
                    "description": "M57: Crédits nets de la classe 7 diminués des débits nets des comptes à terminaison en 9",
                    "montant": total_produits_fonc
                },
                "produits_caf": {
                    "code": "A1",
                    "description": "M57: Crédits nets des comptes 70, 71, 72, 73, 74, 75 (sauf 75882), 76, 77 (sauf 775, 776, 777) et 79",
                    "montant": produits_caf,
                    "details": {
                        "impots_locaux": {
                            "description": "M57: Crédits nets de 7311, 7318, 73221 - Débits nets de 739111, 739115, 739221",
                            "montant": impots_locaux
                        },
                        "fiscalite_reversee_gfp": {
                            "description": "Crédits nets de 73211, 73212 - Débits nets de 739211, 739212",
                            "montant": fiscalite_reversee_gfp
                        },
                        "autres_impots_taxes": {
                            "description": "M57: Crédits nets de 7312, 7313, 7314, 7315, 7317, 732 (sauf 73211, 73212, 73221), 733, 734, 735, 738 - Débits nets de 739 (sauf 739111, 739115, 739211, 739212, 739221)",
                            "montant": autres_impots_taxes
                        },
                        "dotation_globale_fonctionnement": {
                            "description": "Crédits nets du compte 741",
                            "montant": dotation_globale_fonctionnement
                        },
                        "autres_dotations_participations": {
                            "description": "Crédits nets des comptes 74 sauf 741",
                            "montant": autres_dotations_participations,
                            "dont_fctva": {
                                "description": "Crédits nets du compte 744",
                                "montant": fctva_produits
                            }
                        },
                        "produits_services_domaine": {
                            "description": "Crédits nets des comptes 70",
                            "montant": produits_services_domaine
                        }
                    }
                }
            },
            "charges": {
                "total_charges_fonctionnement": {
                    "code": "B",
                    "description": "M57: Débits nets de la classe 6 diminués des crédits nets des comptes à terminaison en 9",
                    "montant": total_charges_fonc
                },
                "charges_caf": {
                    "code": "B1",
                    "description": "M57: Débits nets des comptes 60, 61, 62, 63, 64, 65 (sauf 65882), 66, 67 (sauf 675 et 676)",
                    "montant": charges_caf,
                    "details": {
                        "charges_personnel": {
                            "description": "Débits nets de 621, 631, 633, 64 diminués des crédits nets à terminaison en 9",
                            "montant": charges_personnel
                        },
                        "achats_charges_externes": {
                            "description": "Débits nets de 60, 61, 62 (sauf 621) diminués des crédits nets à terminaison en 9",
                            "montant": achats_charges_externes
                        },
                        "charges_financieres": {
                            "description": "Débits nets du compte 66",
                            "montant": charges_financieres
                        },
                        "contingents": {
                            "description": "Débits nets du compte 655",
                            "montant": contingents
                        },
                        "subventions_versees": {
                            "description": "Débits nets du compte 657",
                            "montant": subventions_versees
                        }
                    }
                }
            },
            "resultat_comptable": {
                "code": "A-B",
                "description": "Total des produits de fonctionnement (A) - Total des charges de fonctionnement (B)",
                "montant": resultat_comptable
            }
        },
        "investissement": {
            "ressources": {
                "total_ressources_investissement": {
                    "code": "C",
                    "description": "M57: Crédits des comptes 10 (sauf 10229, 1027, 1069), 13 (sauf 139), 15, 16 (sauf 1688), 18, 19 (sauf 193), 20, 21, 22 (sauf 229), 23, 26, 27 (sauf 2768), 28, 29, 3 (sauf 32, 37, 3911, 392, 3931, 3941, 39511, 39551, 397), 4541, 45611, 45621, 4581, 481, 49 (sauf 4911, 4961), 59 (sauf 59061, 59081, 5951)",
                    "montant": total_ressources_invest,
                    "details": {
                        "emprunts_bancaires": {
                            "description": "Crédits de 163, 164 (sauf 16449, 1645), 1671, 1672, 1675, 1678, 1681, 1682",
                            "montant": emprunts_bancaires
                        },
                        "subventions_recues": {
                            "description": "Crédits de 13 (sauf 139)",
                            "montant": subventions_recues
                        },
                        "taxe_amenagement": {
                            "description": "Crédits du compte 10226",
                            "montant": taxe_amenagement
                        },
                        "fctva": {
                            "description": "Crédits du compte 10222",
                            "montant": fctva_invest
                        },
                        "retour_biens_affectes": {
                            "description": "Crédits de 18, 22 (sauf 229)",
                            "montant": retour_biens_affectes
                        }
                    }
                },
                "emplois": {
                    "total_emplois_investissement": {
                        "code": "D",
                        "description": "M57: Débits des comptes 10 (sauf 1027, 1069), 13, 15, 16 (sauf 1688), 18, 19 (sauf 193), 20, 21, 22 (sauf 229), 23, 26, 27 (sauf 2768), 28, 29, 3 (sauf 32, 37, 3911, 392, 3931, 3941, 39511, 39551, 397), 4542, 45612, 45622, 4582, 481, 49 (sauf 4911, 4961), 59 (sauf 59061, 59081, 5951)",
                        "montant": total_emplois_invest,
                        "details": {
                            "depenses_equipement": {
                                "description": "Débits de 20, 21, 23 - Crédits de 237, 238",
                                "montant": depenses_equipement
                            },
                            "remboursement_emprunts": {
                                "description": "Débits de 163, 164 (sauf 16449, 1645), 1671, 1672, 1675, 1678, 1681, 1682",
                                "montant": remboursement_emprunts
                            },
                            "charges_repartir": {
                                "description": "Débits du compte 481",
                                "montant": charges_repartir
                            },
                            "immobilisations_affectees": {
                                "description": "Débits de 18, 22 (sauf 229)",
                                "montant": immobilisations_affectees
                            }
                        }
                    }
                },
                "besoin_capacite_financement_residuel": {
                    "code": "D-C",
                    "description": "Total des emplois d'investissement - Total des ressources d'investissement",
                    "montant": besoin_capacite_residuel
                },
                "solde_operations_tiers": {
                    "description": "Débits de 4541, 45611, 45621, 4581 - Crédits de 4542, 45612, 45622, 4582",
                    "montant": solde_operations_tiers
                },
                "besoin_capacite_financement": {
                    "code": "E",
                    "description": "Besoin/capacité de financement résiduel + Solde des opérations pour compte de tiers",
                    "montant": besoin_capacite_invest
                }
            }
        },
        "resultat_ensemble": {
            "code": "R-E",
            "description": "Résultat comptable - Besoin/capacité de financement de la section d'investissement",
            "montant": resultat_ensemble
        },
        "autofinancement": {
            "excedent_brut_fonctionnement": {
                "code": "EBF",
                "description": "M57: Flux net des comptes 70-75 + Flux net des comptes 60-65",
                "montant": ebf
            },
            "capacite_autofinancement_brute": {
                "code": "CAF brute",
                "description": "M57: Total produits fonctionnement (A) - Total charges fonctionnement (B) = Résultat comptable",
                "montant": caf_brute
            },
            "capacite_autofinancement_nette": {
                "code": "CAF nette",
                "description": "CAF brute - Remboursement en capital des emprunts",
                "montant": caf_nette
            }
        },
        "endettement": {
            "encours_total_dette": {
                "description": "Solde créditeur du compte 16 (sauf 166, 1688, 169) au 31/12",
                "montant": encours_total_dette
            },
            "encours_dettes_bancaires": {
                "description": "Solde créditeur de 163, 164, 167 (sauf 1676), 1681, 1682",
                "montant": encours_dettes_bancaires
            },
            "encours_dettes_bancaires_net": {
                "description": "Encours dettes bancaires - Solde débiteur du compte 44121 (aide fonds soutien emprunts toxiques)",
                "montant": encours_dettes_bancaires_net
            },
            "annuite_dette": {
                "description": "Débits nets de 6611 + Remboursement des emprunts",
                "montant": annuite_dette
            }
        },
        "analyse_bilan": {
            "fonds_roulement": {
                "description": "M57: (SD - SC) des classes 3, 4, 5 (sauf 39, 49, 454, 455, 458, 481, 59) - SC de (269, 279, 1688)",
                "montant": fonds_roulement
            }
        }
    }

    return agregats


def charger_plan_comptes():
    """Charge le plan de comptes M57 depuis le JSON"""
    plan_comptes_path = Path(__file__).parent / "docs" / "plan_comptes_m57.json"

    if plan_comptes_path.exists():
        with open(plan_comptes_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("  ATTENTION: Plan de comptes M57 non trouve")
        return {}


def get_libelle_compte(compte, plan_comptes):
    """
    Recherche le libellé d'un compte dans le plan M57

    Args:
        compte: Numéro de compte
        plan_comptes: Dictionnaire du plan de comptes

    Returns:
        Libellé du compte ou None
    """
    # Essai 1: compte exact
    if compte in plan_comptes:
        return plan_comptes[compte]

    # Essai 2: chercher par préfixe (du plus long au plus court)
    for longueur in range(len(compte) - 1, 0, -1):
        prefixe = compte[:longueur]
        if prefixe in plan_comptes:
            return f"{plan_comptes[prefixe]}"

    return None


def clean_balance_data(records):
    """
    Nettoie et structure les données selon la nomenclature M14/M57

    Args:
        records: Liste des enregistrements bruts

    Returns:
        dict: Données nettoyées et structurées
    """
    if not records:
        return None

    # Charger le plan de comptes M57
    print("  Chargement du plan de comptes M57...")
    plan_comptes = charger_plan_comptes()
    print(f"  Plan de comptes charge: {len(plan_comptes)} comptes")

    # FILTRAGE : Ne garder que le BUDGET PRINCIPAL (cbudg="1")
    # Selon la doctrine DGFiP, les budgets annexes doivent être séparés
    # du budget principal pour les agrégats budgétaires réglementaires
    records_budget_principal = [r for r in records if r.get('cbudg') == '1']
    records_budgets_annexes = [r for r in records if r.get('cbudg') != '1']

    print(f"  Filtre budget principal : {len(records_budget_principal)} enregistrements")
    print(f"  Budgets annexes exclus  : {len(records_budgets_annexes)} enregistrements")

    # Extraire les métadonnées du premier enregistrement
    first = records_budget_principal[0] if records_budget_principal else records[0]
    metadata = {
        "commune": first.get('lbudg'),
        "siren": first.get('siren'),
        "exercice": first.get('exer'),
        "population": first.get('population'),
        "note_filtre": "Agrégats calculés sur le budget principal uniquement (cbudg=1), conforme doctrine DGFiP"
    }

    # Calculer les agrégats selon la nomenclature M14/M57
    # UNIQUEMENT sur le budget principal
    agregats = calculer_agregats_m57(records_budget_principal)

    # Nettoyer et structurer les comptes détaillés
    # RÈGLE DGFiP : tous les montants sont en FLUX NET (obnetcre - obnetdeb)
    # Utiliser UNIQUEMENT les records du budget principal
    comptes = []
    comptes_sans_libelle = 0

    for record in records_budget_principal:
        compte = str(record.get('compte', ''))

        credit = record.get('obnetcre', 0) or 0
        debit = record.get('obnetdeb', 0) or 0
        sd = record.get('sd', 0) or 0  # Solde débiteur
        sc = record.get('sc', 0) or 0  # Solde créditeur

        # FLUX NET (règle comptabilité publique)
        flux_net = credit - debit
        solde_net = sd - sc

        if flux_net != 0 or solde_net != 0:  # Ignorer les comptes sans mouvement ni solde
            # Rechercher le libellé officiel dans le plan de comptes
            libelle_officiel = get_libelle_compte(compte, plan_comptes)

            if libelle_officiel is None:
                comptes_sans_libelle += 1
                libelle_officiel = "Compte non trouve dans le plan M57"

            comptes.append({
                "compte": compte,
                "libelle": record.get('lbudg', ''),  # Nom de la commune
                "libelle_compte": libelle_officiel,   # Nom officiel du compte
                "flux_net": flux_net,
                "obnetcre": credit,
                "obnetdeb": debit,
                "sd": sd,  # Solde débiteur
                "sc": sc,  # Solde créditeur
                "solde_net": solde_net,  # SD - SC
                # Champs supplémentaires pour identifier les enregistrements multiples
                "cbudg": record.get('cbudg'),
                "ctype": record.get('ctype'),
                "cstyp": record.get('cstyp'),
                "secteur": record.get('secteur'),
                "finess": record.get('finess'),
                "codbud1": record.get('codbud1')
            })

    if comptes_sans_libelle > 0:
        print(f"  ATTENTION: {comptes_sans_libelle} comptes sans libelle officiel trouve")

    # Trier par numéro de compte
    comptes.sort(key=lambda x: x['compte'])

    return {
        "metadata": metadata,
        "agregats_m57": agregats,
        "total_count": len(comptes),
        "comptes_details": comptes
    }


def save_to_json(data, output_path):
    """Sauvegarde les données en JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Donnees sauvegardees dans {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Récupère les balances comptables M57 d'une commune")
    parser.add_argument("--siren", required=True, help="Code SIREN de la commune")
    parser.add_argument("--annee", required=True, help="Année budgétaire")
    parser.add_argument("--output", default="balance_m57.json", help="Fichier de sortie JSON")
    parser.add_argument("--raw", action="store_true", help="Sauvegarder les données brutes (sans nettoyage)")

    args = parser.parse_args()

    # Récupération des données
    records = fetch_balance_data(args.siren, args.annee)

    if records:
        # Nettoyage des données (sauf si --raw)
        if not args.raw:
            print("\nNettoyage et calcul des agrégats M57...")
            data = clean_balance_data(records)
        else:
            data = {"results": records}

        # Sauvegarde
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / args.output

        save_to_json(data, output_path)

        # Affichage d'un aperçu
        print("\n--- Aperçu des données ---")
        if 'metadata' in data:
            # Données nettoyées
            print(f"Commune: {data['metadata'].get('commune', 'N/A')}")
            print(f"SIREN: {data['metadata'].get('siren', 'N/A')}")
            print(f"Exercice: {data['metadata'].get('exercice', 'N/A')}")
            print(f"Population: {data['metadata'].get('population', 'N/A')}")
            print(f"\nNombre de comptes: {data.get('total_count', 0)}")

            # Afficher les agrégats M57
            if 'agregats_m57' in data:
                print(f"\n--- Agrégats M14/M57 ---")
                fonc = data['agregats_m57']['fonctionnement']
                print(f"Total produits fonctionnement: {fonc['produits']['total_produits_fonctionnement']['montant']:,.2f} €")
                print(f"Total charges fonctionnement: {fonc['charges']['total_charges_fonctionnement']['montant']:,.2f} €")
                print(f"Résultat comptable: {fonc['resultat_comptable']['montant']:,.2f} €")
        else:
            # Données brutes
            print(f"Nombre d'enregistrements: {len(data.get('results', []))}")
    else:
        print("Aucune donnée récupérée")


if __name__ == "__main__":
    main()
