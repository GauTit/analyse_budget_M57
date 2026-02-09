"""
Module pour récupérer les données financières depuis l'API OFGL
Alternative au parsing PDF, utilise l'API publique data.ofgl.fr
"""

import requests
from typing import Dict, List, Optional


def construire_url_api(code_insee: str, annee: int, budget_type: str = "Budget principal") -> str:
    """
    Construit l'URL de l'API OFGL pour une commune et une année données

    Args:
        code_insee: Code INSEE de la commune (ex: "07154")
        annee: Année de l'exercice (ex: 2024)
        budget_type: Type de budget (défaut: "Budget principal")

    Returns:
        URL complète de l'API
    """
    base_url = "https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/ofgl-base-communes/records"
    where_clause = f'insee="{code_insee}" AND year(exer)={annee} AND type_de_budget="{budget_type}"'

    return f"{base_url}?where={where_clause}&limit=100"


def recuperer_donnees_ofgl(code_insee: str, annee: int, budget_type: str = "Budget principal") -> Optional[Dict]:
    """
    Récupère les données financières d'une commune depuis l'API OFGL

    Args:
        code_insee: Code INSEE de la commune
        annee: Année de l'exercice
        budget_type: Type de budget

    Returns:
        Dict contenant les données brutes de l'API ou None en cas d'erreur
    """
    url = construire_url_api(code_insee, annee, budget_type)

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()

        if 'results' not in data or not data['results']:
            return None

        return data['results']

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération des données: {e}")
        return None


def extraire_valeur_agregat(records: List[Dict], agregat: str) -> Optional[float]:
    """
    Extrait la valeur d'un agrégat spécifique depuis les enregistrements OFGL

    Args:
        records: Liste des enregistrements retournés par l'API
        agregat: Nom de l'agrégat (ex: "Recettes de fonctionnement", "Dépenses d'équipement")

    Returns:
        Valeur en k€ ou None si non trouvée
    """
    for record in records:
        if record.get('agregat') == agregat:
            montant = record.get('montant')
            if montant is not None:
                return float(montant) / 1000  # Conversion en k€
    return None


def convertir_api_vers_json_enrichi(code_insee: str, annee: int) -> Optional[Dict]:
    """
    Récupère les données de l'API et les convertit au format JSON enrichi
    Compatible avec la structure existante du projet

    Args:
        code_insee: Code INSEE de la commune
        annee: Année de l'exercice

    Returns:
        Dict au format JSON enrichi ou None en cas d'erreur
    """
    records = recuperer_donnees_ofgl(code_insee, annee)

    if not records:
        return None

    # Extraire les métadonnées
    premier_record = records[0]
    nom_commune = premier_record.get('lbudg', 'Commune inconnue')

    # Extraction des valeurs depuis les agrégats
    recettes_fonct = extraire_valeur_agregat(records, "Recettes de fonctionnement") or 0
    depenses_fonct = extraire_valeur_agregat(records, "Dépenses de fonctionnement") or 0
    impots_locaux = extraire_valeur_agregat(records, "Impôts locaux") or 0
    dgf = extraire_valeur_agregat(records, "Dotation globale de fonctionnement") or 0
    autres_dotations = extraire_valeur_agregat(records, "Autres dotations de fonctionnement") or 0
    frais_personnel = extraire_valeur_agregat(records, "Frais de personnel") or 0
    achats_charges = extraire_valeur_agregat(records, "Achats et charges externes") or 0
    charges_financieres = extraire_valeur_agregat(records, "Charges financières") or 0
    depenses_equipement = extraire_valeur_agregat(records, "Dépenses d'équipement") or 0
    remb_emprunts = extraire_valeur_agregat(records, "Remboursements d'emprunts hors GAD") or 0
    emprunts = extraire_valeur_agregat(records, "Emprunts hors GAD") or 0
    subventions = extraire_valeur_agregat(records, "Subventions re�ues et participations") or 0
    fctva = extraire_valeur_agregat(records, "FCTVA") or 0
    encours_dette = extraire_valeur_agregat(records, "Encours de dette") or 0
    annuite_dette = extraire_valeur_agregat(records, "Annuité de la dette") or 0
    epargne_brute = extraire_valeur_agregat(records, "Epargne brute") or 0
    epargne_nette = extraire_valeur_agregat(records, "Epargne nette") or 0

    # Structure JSON enrichie
    json_enrichi = {
        "metadata": {
            "commune": nom_commune,
            "exercice": annee,
            "code_insee": code_insee,
            "source": "API OFGL",
            "type_budget": "Budget principal"
        },
        "fonctionnement": {
            "produits": {
                "total": {
                    "montant_k": recettes_fonct,
                    "label": "Total des produits de fonctionnement"
                },
                "impots_locaux": {
                    "montant_k": impots_locaux,
                    "label": "Impôts locaux"
                },
                "dgf": {
                    "montant_k": dgf,
                    "label": "Dotation globale de fonctionnement"
                },
                "autres_dotations": {
                    "montant_k": autres_dotations,
                    "label": "Autres dotations et participations"
                }
            },
            "charges": {
                "total": {
                    "montant_k": depenses_fonct,
                    "label": "Total des charges de fonctionnement"
                },
                "charges_personnel": {
                    "montant_k": frais_personnel,
                    "label": "Charges de personnel"
                },
                "achats_charges_externes": {
                    "montant_k": achats_charges,
                    "label": "Achats et charges externes"
                },
                "charges_financieres": {
                    "montant_k": charges_financieres,
                    "label": "Charges financières"
                }
            },
            "resultat": {
                "montant_k": recettes_fonct - depenses_fonct,
                "label": "Résultat de fonctionnement"
            }
        },
        "investissement": {
            "emplois": {
                "depenses_equipement": {
                    "montant_k": depenses_equipement,
                    "label": "Dépenses d'équipement"
                },
                "remboursement_emprunts": {
                    "montant_k": remb_emprunts,
                    "label": "Remboursement des emprunts"
                }
            },
            "ressources": {
                "emprunts": {
                    "montant_k": emprunts,
                    "label": "Emprunts contractés"
                },
                "subventions_recues": {
                    "montant_k": subventions,
                    "label": "Subventions d'investissement reçues"
                },
                "fctva": {
                    "montant_k": fctva,
                    "label": "FCTVA"
                }
            }
        },
        "autofinancement": {},
        "endettement": {
            "encours_total": {
                "montant_k": encours_dette,
                "label": "Encours total de dette"
            },
            "annuite_dette": {
                "montant_k": annuite_dette,
                "label": "Annuité de la dette"
            }
        }
    }

    # Utiliser directement l'épargne brute et nette de l'API si disponible
    # Sinon calculer à partir du résultat de fonctionnement
    if epargne_brute > 0:
        caf_brute = epargne_brute
    else:
        caf_brute = recettes_fonct - depenses_fonct

    if epargne_nette > 0:
        caf_nette = epargne_nette
    else:
        caf_nette = caf_brute - remb_emprunts

    json_enrichi["autofinancement"] = {
        "caf_brute": {
            "montant_k": caf_brute,
            "label": "Capacité d'autofinancement brute"
        },
        "caf_nette": {
            "montant_k": caf_nette,
            "label": "Capacité d'autofinancement nette"
        }
    }

    # Calcul des ratios d'endettement
    if caf_brute > 0:
        capacite_desendettement = encours_dette / caf_brute
    else:
        capacite_desendettement = None

    json_enrichi["endettement"]["ratios"] = {
        "capacite_desendettement_annees": capacite_desendettement
    }

    return json_enrichi


def recuperer_donnees_multi_annees(code_insee: str, annees: List[int]) -> List[Dict]:
    """
    Récupère les données pour plusieurs années

    Args:
        code_insee: Code INSEE de la commune
        annees: Liste des années à récupérer

    Returns:
        Liste de dicts avec structure:
        {
            'annee': int,
            'source': 'API',
            'data': dict (JSON enrichi)
        }
    """
    bilans = []

    for annee in annees:
        print(f"  Récupération des données {annee} depuis l'API OFGL...")

        json_data = convertir_api_vers_json_enrichi(code_insee, annee)

        if json_data:
            bilans.append({
                'annee': annee,
                'source': 'API',
                'data': json_data
            })
            print(f"    [OK] Année {annee} - {json_data['metadata']['commune']}")
        else:
            print(f"    [WARN] Aucune donnée disponible pour {annee}")

    return bilans


if __name__ == "__main__":
    # Test du module
    code_insee = "07154"  # Dauphin
    annee = 2024

    print(f"Test de récupération des données pour {code_insee} - {annee}")
    print("=" * 60)

    json_data = convertir_api_vers_json_enrichi(code_insee, annee)

    if json_data:
        print(f"\n✓ Données récupérées avec succès")
        print(f"  Commune: {json_data['metadata']['commune']}")
        print(f"  Exercice: {json_data['metadata']['exercice']}")
        print(f"\n  Produits de fonctionnement: {json_data['fonctionnement']['produits']['total']['montant_k']:.0f} k€")
        print(f"  Charges de fonctionnement: {json_data['fonctionnement']['charges']['total']['montant_k']:.0f} k€")
        print(f"  Résultat de fonctionnement: {json_data['fonctionnement']['resultat']['montant_k']:.0f} k€")
        print(f"  CAF brute: {json_data['autofinancement']['caf_brute']['montant_k']:.0f} k€")
        print(f"  Encours de dette: {json_data['endettement']['encours_total']['montant_k']:.0f} k€")

        if json_data['endettement']['ratios']['capacite_desendettement_annees']:
            print(f"  Capacité de désendettement: {json_data['endettement']['ratios']['capacite_desendettement_annees']:.2f} ans")
    else:
        print("\n✗ Échec de la récupération des données")

    # Test multi-années
    print("\n" + "=" * 60)
    print("Test récupération multi-années (2020-2024)")
    print("=" * 60)

    bilans = recuperer_donnees_multi_annees(code_insee, [2020, 2021, 2022, 2023, 2024])

    print(f"\n✓ {len(bilans)} années récupérées avec succès")
