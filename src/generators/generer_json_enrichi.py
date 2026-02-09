"""
Génère un JSON ULTRA-ENRICHI pour rapport détaillé type DGFiP
Inclut TOUS les ratios et comparaisons nécessaires
"""

import json
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parsers.parser_budget_v2_complet import ParserBudget


def calculer_ecart_absolu_et_pct(valeur_commune, valeur_strate):
    """Calcule écart absolu et en %"""
    if valeur_commune is None or valeur_strate is None or valeur_strate == 0:
        return None, None

    ecart_absolu = valeur_commune - valeur_strate
    ecart_pct = round((ecart_absolu / valeur_strate * 100), 1)

    return ecart_absolu, ecart_pct


def formater_comparaison_texte(valeur_commune, valeur_strate, unite="€/hab"):
    """Génère le texte de comparaison formaté"""
    if valeur_commune is None or valeur_strate is None:
        return None

    ecart_abs, ecart_pct = calculer_ecart_absolu_et_pct(valeur_commune, valeur_strate)

    if ecart_abs is None:
        return None

    if abs(ecart_pct) < 5:
        niveau = "au niveau de"
    elif ecart_pct > 15:
        niveau = "nettement supérieur à"
    elif ecart_pct > 5:
        niveau = "supérieur à"
    elif ecart_pct < -15:
        niveau = "nettement inférieur à"
    else:
        niveau = "inférieur à"

    return {
        "texte": f"{valeur_commune}{unite} commune – {valeur_strate}{unite} Moyenne de la strate",
        "ecart_absolu": ecart_abs,
        "ecart_pct": ecart_pct,
        "niveau": niveau
    }


def generer_json_enrichi(fichier_pdf):
    """Génère JSON enrichi avec TOUS les ratios et comparaisons"""

    # Parser les données avec le nouveau parser
    parser = ParserBudget()
    budget = parser.parser_bilan_pdf(fichier_pdf)

    # Extraire les infos de base depuis budget
    nom_commune = budget.get('commune', 'CHAMPAGNAC')
    exercice = budget.get('exercice', 2024)
    population = budget.get('population', 1048)
    strate_min = 500
    strate_max = 2000

    # Calculs de ratios clés
    produits_caf_k = budget.get('produits_fonct_caf_k', 0)
    charges_caf_k = budget.get('charges_fonct_caf_k', 0)
    caf_brute_k = budget.get('caf_brute_k', 0)
    dette_k = budget.get('dette_totale_k', 0)
    depenses_equip_k = budget.get('depenses_equipement_k', 0)
    remb_emprunts_k = budget.get('remboursement_emprunts_k', 0)
    charges_financieres_k = budget.get('charges_financieres_k', 0)

    # Ratios calculés
    ratio_endettement = round((dette_k / produits_caf_k * 100), 2) if produits_caf_k else None
    ratio_capacite_desendettement = round(dette_k / caf_brute_k, 2) if caf_brute_k else None
    caf_nette_k = budget.get('caf_nette_k', caf_brute_k - remb_emprunts_k)  # Priorité à la valeur extraite du PDF
    ratio_effort_equipement = round((depenses_equip_k / produits_caf_k * 100), 1) if produits_caf_k else None
    annuite_dette_k = charges_financieres_k + remb_emprunts_k

    # Structure JSON ultra-enrichie
    json_data = {
        "metadata": {
            "commune": nom_commune,
            "exercice": exercice,
            "population": population,
            "strate": {
                "min": strate_min,
                "max": strate_max,
                "libelle": f"{strate_min} à {strate_max} habitants"
            }
        },

        "fonctionnement": {
            "produits": {
                "total": {
                    "montant_k": budget.get('produits_fonctionnement_k'),
                    "par_hab": budget.get('produits_fonctionnement_hab'),
                    "moyenne_strate_hab": budget.get('produits_fonctionnement_moy_strate'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('produits_fonctionnement_hab'),
                        budget.get('produits_fonctionnement_moy_strate')
                    )
                },

                "produits_caf": {
                    "montant_k": budget.get('produits_fonct_caf_k'),
                    "par_hab": budget.get('produits_fonct_caf_hab'),
                    "moyenne_strate_hab": budget.get('produits_fonct_caf_moy_strate'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('produits_fonct_caf_hab'),
                        budget.get('produits_fonct_caf_moy_strate')
                    )
                },

                "impots_locaux": {
                    "montant_k": budget.get('impots_locaux_k'),
                    "par_hab": budget.get('impots_locaux_hab'),
                    "moyenne_strate_hab": budget.get('impots_locaux_moy_strate'),
                    "pct_produits_caf": budget.get('impots_locaux_ratio'),
                    "pct_produits_caf_strate": budget.get('impots_locaux_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('impots_locaux_hab'),
                        budget.get('impots_locaux_moy_strate')
                    ),
                    "detail_fiscalite": {
                        "taxe_habitation": {
                            "base_k": budget.get('base_th_secondaires_k'),
                            "taux_vote_pct": budget.get('produit_th_secondaires_taux_secondaires'),
                            "taux_strate_pct": budget.get('produit_th_secondaires_taux_moy'),
                            "produit_k": budget.get('produit_th_secondaires_k')
                        },
                        "taxe_fonciere_bati": {
                            "base_k": budget.get('base_tfpb_k'),
                            "taux_vote_pct": budget.get('produit_tfpb_taux'),
                            "taux_strate_pct": budget.get('produit_tfpb_taux_moy'),
                            "produit_k": budget.get('produit_tfpb_apres_k'),
                            "produit_par_hab": budget.get('produit_tfpb_apres_k', 0) / population if population else None
                        },
                        "taxe_fonciere_non_bati": {
                            "base_k": budget.get('base_tfpnb_k'),
                            "taux_vote_pct": budget.get('produit_taux_tfpnb'),
                            "taux_strate_pct": budget.get('produit_taux_tfpnb_moy'),
                            "produit_k": budget.get('produit_tfpnb_k')
                        }
                    }
                },

                "autres_impots_taxes": {
                    "montant_k": budget.get('autres_impots_k'),
                    "par_hab": budget.get('autres_impots_hab'),
                    "moyenne_strate_hab": budget.get('autres_impots_moy_strate'),
                    "pct_produits_caf": budget.get('autres_impots_ratio'),
                    "pct_produits_caf_strate": budget.get('autres_impots_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('autres_impots_hab'),
                        budget.get('autres_impots_moy_strate')
                    )
                },

                "dgf": {
                    "montant_k": budget.get('dgf_k'),
                    "par_hab": budget.get('dgf_hab'),
                    "moyenne_strate_hab": budget.get('dgf_moy_strate'),
                    "pct_produits_caf": budget.get('dgf_ratio'),
                    "pct_produits_caf_strate": budget.get('dgf_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('dgf_hab'),
                        budget.get('dgf_moy_strate')
                    )
                },

                "produits_services_domaine": {
                    "montant_k": budget.get('produits_services_k'),
                    "par_hab": budget.get('produits_services_hab'),
                    "moyenne_strate_hab": budget.get('produits_services_moy_strate'),
                    "pct_produits_caf": budget.get('produits_services_ratio'),
                    "pct_produits_caf_strate": budget.get('produits_services_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('produits_services_hab'),
                        budget.get('produits_services_moy_strate')
                    )
                }
            },

            "charges": {
                "total": {
                    "montant_k": budget.get('charges_fonctionnement_k'),
                    "par_hab": budget.get('charges_fonctionnement_hab'),
                    "moyenne_strate_hab": budget.get('charges_fonctionnement_moy_strate'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('charges_fonctionnement_hab'),
                        budget.get('charges_fonctionnement_moy_strate')
                    )
                },

                "charges_caf": {
                    "montant_k": budget.get('charges_fonct_caf_k'),
                    "par_hab": budget.get('charges_fonct_caf_hab'),
                    "moyenne_strate_hab": budget.get('charges_fonct_caf_moy_strate'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('charges_fonct_caf_hab'),
                        budget.get('charges_fonct_caf_moy_strate')
                    )
                },

                "charges_personnel": {
                    "montant_k": budget.get('charges_personnel_k'),
                    "par_hab": budget.get('charges_personnel_hab'),
                    "moyenne_strate_hab": budget.get('charges_personnel_moy_strate'),
                    "pct_charges_caf": budget.get('charges_personnel_ratio'),
                    "pct_charges_caf_strate": budget.get('charges_personnel_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('charges_personnel_hab'),
                        budget.get('charges_personnel_moy_strate')
                    )
                },

                "achats_charges_externes": {
                    "montant_k": budget.get('achats_charges_ext_k'),
                    "par_hab": budget.get('achats_charges_ext_hab'),
                    "moyenne_strate_hab": budget.get('achats_charges_ext_moy_strate'),
                    "pct_charges_caf": budget.get('achats_charges_ext_ratio'),
                    "pct_charges_caf_strate": budget.get('achats_charges_ext_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('achats_charges_ext_hab'),
                        budget.get('achats_charges_ext_moy_strate')
                    )
                },

                "charges_financieres": {
                    "montant_k": budget.get('charges_financieres_k'),
                    "par_hab": budget.get('charges_financieres_hab'),
                    "moyenne_strate_hab": budget.get('charges_financieres_moy_strate'),
                    "pct_charges_caf": budget.get('charges_financieres_ratio'),
                    "pct_charges_caf_strate": budget.get('charges_financieres_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('charges_financieres_hab'),
                        budget.get('charges_financieres_moy_strate')
                    )
                },

                "contingents": {
                    "montant_k": budget.get('contingents_k'),
                    "par_hab": budget.get('contingents_hab'),
                    "moyenne_strate_hab": budget.get('contingents_moy_strate'),
                    "pct_charges_caf": budget.get('contingents_ratio'),
                    "pct_charges_caf_strate": budget.get('contingents_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('contingents_hab'),
                        budget.get('contingents_moy_strate')
                    )
                },

                "subventions_versees": {
                    "montant_k": budget.get('subventions_versees_k'),
                    "par_hab": budget.get('subventions_versees_hab'),
                    "moyenne_strate_hab": budget.get('subventions_versees_moy_strate'),
                    "pct_charges_caf": budget.get('subventions_versees_ratio'),
                    "pct_charges_caf_strate": budget.get('subventions_versees_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('subventions_versees_hab'),
                        budget.get('subventions_versees_moy_strate')
                    )
                }
            },

            "resultat": {
                "montant_k": budget.get('resultat_fonctionnement_k'),
                "par_hab": budget.get('resultat_fonctionnement_hab'),
                "moyenne_strate_hab": budget.get('resultat_fonctionnement_moy_strate'),
                "comparaison": formater_comparaison_texte(
                    budget.get('resultat_fonctionnement_hab'),
                    budget.get('resultat_fonctionnement_moy_strate')
                )
            }
        },

        "investissement": {
            "ressources": {
                "total_k": budget.get('ressources_investissement_k'),
                "emprunts": {
                    "montant_k": budget.get('emprunts_k'),
                    "par_hab": budget.get('emprunts_hab'),
                    "moyenne_strate_hab": budget.get('emprunts_moy_strate'),
                    "pct_ressources": budget.get('emprunts_ratio'),
                    "pct_ressources_strate": budget.get('emprunts_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('emprunts_hab'),
                        budget.get('emprunts_moy_strate')
                    )
                },
                "subventions_recues": {
                    "montant_k": budget.get('subventions_recues_k'),
                    "par_hab": budget.get('subventions_recues_hab'),
                    "moyenne_strate_hab": budget.get('subventions_recues_moy_strate'),
                    "pct_ressources": budget.get('subventions_recues_ratio'),
                    "pct_ressources_strate": budget.get('subventions_recues_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('subventions_recues_hab'),
                        budget.get('subventions_recues_moy_strate')
                    )
                },
                "fctva": {
                    "montant_k": budget.get('fctva_invest_k'),
                    "par_hab": budget.get('fctva_invest_hab'),
                    "moyenne_strate_hab": budget.get('fctva_invest_moy_strate'),
                    "pct_ressources": budget.get('fctva_invest_ratio'),
                    "pct_ressources_strate": budget.get('fctva_invest_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('fctva_invest_hab'),
                        budget.get('fctva_invest_moy_strate')
                    )
                }
            },

            "emplois": {
                "total_k": budget.get('emplois_investissement_k'),
                "depenses_equipement": {
                    "montant_k": depenses_equip_k,
                    "par_hab": budget.get('depenses_equipement_hab'),
                    "moyenne_strate_hab": budget.get('depenses_equipement_moy_strate'),
                    "pct_emplois": budget.get('depenses_equipement_ratio'),
                    "pct_emplois_strate": budget.get('depenses_equipement_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('depenses_equipement_hab'),
                        budget.get('depenses_equipement_moy_strate')
                    )
                },
                "remboursement_emprunts": {
                    "montant_k": remb_emprunts_k,
                    "par_hab": budget.get('remboursement_emprunts_hab'),
                    "moyenne_strate_hab": budget.get('remboursement_emprunts_moy_strate'),
                    "pct_emplois": budget.get('remboursement_emprunts_ratio'),
                    "pct_emplois_strate": budget.get('remboursement_emprunts_ratio_moy'),
                    "comparaison": formater_comparaison_texte(
                        budget.get('remboursement_emprunts_hab'),
                        budget.get('remboursement_emprunts_moy_strate')
                    )
                }
            },

            "financement": {
                "besoin_financement_residuel_k": budget.get('besoin_financement_residuel_k'),
                "besoin_financement_residuel_par_hab": budget.get('besoin_financement_residuel_hab'),
                "resultat_ensemble_k": budget.get('resultat_ensemble_k'),
                "resultat_ensemble_par_hab": budget.get('resultat_ensemble_hab'),
                "comparaison_resultat": formater_comparaison_texte(
                    budget.get('resultat_ensemble_hab'),
                    budget.get('resultat_ensemble_moy_strate')
                )
            }
        },

        "autofinancement": {
            "ebf": {
                "montant_k": budget.get('ebf_k'),
                "par_hab": budget.get('ebf_hab'),
                "moyenne_strate_hab": budget.get('ebf_moy_strate'),
                "pct_produits_caf": budget.get('ebf_ratio'),
                "pct_produits_caf_strate": budget.get('ebf_ratio_moy'),
                "comparaison": formater_comparaison_texte(
                    budget.get('ebf_hab'),
                    budget.get('ebf_moy_strate')
                )
            },
            "caf_brute": {
                "montant_k": caf_brute_k,
                "par_hab": budget.get('caf_brute_hab'),
                "moyenne_strate_hab": budget.get('caf_brute_moy_strate'),
                "pct_produits_caf": budget.get('caf_brute_ratio'),
                "pct_produits_caf_strate": budget.get('caf_brute_ratio_moy'),
                "comparaison": formater_comparaison_texte(
                    budget.get('caf_brute_hab'),
                    budget.get('caf_brute_moy_strate')
                )
            },
            "caf_nette": {
                "montant_k": caf_nette_k,
                "par_hab": budget.get('caf_nette_hab', round(caf_nette_k * 1000 / population, 0) if population else None),
                "moyenne_strate_hab": budget.get('caf_nette_moy_strate'),
                "pct_produits_caf": budget.get('caf_nette_ratio'),
                "pct_produits_caf_strate": budget.get('caf_nette_ratio_moy'),
                "est_positive": caf_nette_k > 0,
                "comparaison": formater_comparaison_texte(
                    budget.get('caf_nette_hab', round(caf_nette_k * 1000 / population, 0) if population else None),
                    budget.get('caf_nette_moy_strate')
                )
            }
        },

        "endettement": {
            "encours_total": {
                "montant_k": dette_k,
                "par_hab": budget.get('dette_totale_hab'),
                "moyenne_strate_hab": budget.get('dette_totale_moy_strate'),
                "pct_produits_caf": budget.get('dette_totale_ratio'),
                "pct_produits_caf_strate": budget.get('dette_totale_ratio_moy'),
                "comparaison": formater_comparaison_texte(
                    budget.get('dette_totale_hab'),
                    budget.get('dette_totale_moy_strate')
                )
            },
            "ratios": {
                "ratio_endettement": ratio_endettement,
                "ratio_endettement_strate": round((budget.get('dette_totale_moy_strate', 0) * population / budget.get('produits_fonct_caf_moy_strate', 1) / population * 100), 2) if budget.get('produits_fonct_caf_moy_strate') else None,
                "capacite_desendettement_annees": ratio_capacite_desendettement,
                "capacite_desendettement_strate_annees": round(budget.get('dette_totale_moy_strate', 0) * population / (budget.get('caf_brute_moy_strate', 1) * population), 2) if budget.get('caf_brute_moy_strate') else None,
                "seuil_alerte_annees": 12,
                "est_en_alerte": ratio_capacite_desendettement and ratio_capacite_desendettement > 12
            },
            "annuite": {
                "montant_k": annuite_dette_k,
                "par_hab": round(annuite_dette_k * 1000 / population, 0) if population else None,
                "moyenne_strate_hab": (budget.get('charges_financieres_moy_strate', 0) + budget.get('remboursement_emprunts_moy_strate', 0)),
                "pct_produits_caf": budget.get('annuite_dette_ratio'),
                "pct_produits_caf_strate": budget.get('annuite_dette_ratio_moy'),
                "detail": {
                    "charges_financieres_hab": budget.get('charges_financieres_hab'),
                    "remboursement_capital_hab": budget.get('remboursement_emprunts_hab')
                },
                "comparaison": formater_comparaison_texte(
                    round(annuite_dette_k * 1000 / population, 0) if population else None,
                    (budget.get('charges_financieres_moy_strate', 0) + budget.get('remboursement_emprunts_moy_strate', 0))
                )
            },
            "fonds_roulement": {
                "montant_k": budget.get('fonds_roulement_k'),
                "par_hab": budget.get('fonds_roulement_hab'),
                "moyenne_strate_hab": budget.get('fonds_roulement_moy_strate'),
                "est_positif": budget.get('fonds_roulement_k', 0) > 0,
                "comparaison": formater_comparaison_texte(
                    budget.get('fonds_roulement_hab'),
                    budget.get('fonds_roulement_moy_strate')
                )
            }
        }
    }

    return json_data


def sauvegarder_json_enrichi(json_data, fichier_sortie="output/donnees_enrichies.json"):
    """Sauvegarde le JSON enrichi"""
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    return fichier_sortie


if __name__ == "__main__":
    print("=== GENERATION JSON ENRICHI ===\n")
    json_data = generer_json_enrichi('docs/bilan.pdf')
    fichier = sauvegarder_json_enrichi(json_data)
    print(f"JSON enrichi sauvegarde : {fichier}")
    print(f"Taille : {len(json.dumps(json_data))} caracteres")
