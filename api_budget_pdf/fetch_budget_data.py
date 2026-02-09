"""
Script pour récupérer les données budgétaires via l'API OpenDataSoft
Usage: python fetch_budget_data.py --insee CODE_INSEE --annee ANNEE
"""

import requests
import json
import argparse
from pathlib import Path


API_BASE_URL = "https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/ofgl-base-communes-consolidee/records"


def fetch_budget_data(code_insee, annee, limit=100):
    """
    Récupère les données budgétaires pour une commune et une année données

    Args:
        code_insee: Code INSEE de la commune (str)
        annee: Année budgétaire (int ou str)
        limit: Nombre maximum de résultats (int)

    Returns:
        dict: Données JSON de l'API
    """
    # Construction des paramètres selon la doc OpenDataSoft
    # Utiliser une liste de tuples pour avoir plusieurs paramètres "refine"
    params = [
        ("limit", str(limit)),
        ("refine", f"exer:\"{annee}\""),
        ("refine", f"insee:\"{code_insee}\"")
    ]

    print(f"Requête API pour commune {code_insee}, exercice {annee}...")
    print(f"URL: {API_BASE_URL}")

    try:
        response = requests.get(API_BASE_URL, params=params)
        print(f"URL complète: {response.url}")
        response.raise_for_status()

        data = response.json()
        print(f"✓ Requête réussie - {data.get('total_count', 0)} résultats trouvés")

        return data

    except requests.exceptions.RequestException as e:
        print(f"✗ Erreur lors de la requête API: {e}")
        return None


def clean_data(data):
    """
    Nettoie les données pour ne garder que les champs essentiels

    Args:
        data: Données brutes de l'API

    Returns:
        dict: Données nettoyées avec métadonnées et résultats simplifiés
    """
    if not data or not data.get('results'):
        return data

    # Extraire les métadonnées du premier résultat
    first_result = data['results'][0]
    metadata = {
        "commune": first_result.get('com_name'),
        "code_insee": first_result.get('insee'),
        "exercice": first_result.get('exer'),
        "population": first_result.get('ptot'),
        "departement": first_result.get('dep_name'),
        "tranche_population": first_result.get('tranche_population')
    }

    # Nettoyer chaque résultat pour ne garder que les champs essentiels
    cleaned_results = []
    for result in data['results']:
        cleaned = {
            "agregat": result.get('agregat'),
            "montant": result.get('montant'),
            "euros_par_habitant": result.get('euros_par_habitant')
        }
        cleaned_results.append(cleaned)

    return {
        "metadata": metadata,
        "total_count": len(cleaned_results),
        "agregats": cleaned_results
    }


def save_to_json(data, output_path):
    """Sauvegarde les données en JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Données sauvegardées dans {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Récupère les données budgétaires d'une commune")
    parser.add_argument("--insee", required=True, help="Code INSEE de la commune")
    parser.add_argument("--annee", required=True, help="Année budgétaire")
    parser.add_argument("--output", default="output_api.json", help="Fichier de sortie JSON")
    parser.add_argument("--raw", action="store_true", help="Sauvegarder les données brutes (sans nettoyage)")

    args = parser.parse_args()

    # Récupération des données
    data = fetch_budget_data(args.insee, args.annee)

    if data:
        # Nettoyage des données (sauf si --raw)
        if not args.raw:
            print("\nNettoyage des données...")
            data = clean_data(data)

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
            print(f"Code INSEE: {data['metadata'].get('code_insee', 'N/A')}")
            print(f"Exercice: {data['metadata'].get('exercice', 'N/A')}")
            print(f"Population: {data['metadata'].get('population', 'N/A')}")
            print(f"Nombre d'agrégats: {data.get('total_count', 0)}")
            if data.get('agregats'):
                print(f"\nPremier agrégat:")
                first = data['agregats'][0]
                print(f"  - {first.get('agregat')}: {first.get('montant')}€ ({first.get('euros_par_habitant'):.2f}€/hab)")
        elif data.get('results'):
            # Données brutes
            first_record = data['results'][0]
            if 'lbudg' in first_record:
                print(f"Commune: {first_record.get('lbudg', 'N/A')}")
            if 'exer' in first_record:
                print(f"Exercice: {first_record.get('exer', 'N/A')}")
            if 'ptot' in first_record:
                print(f"Population: {first_record.get('ptot', 'N/A')}")
            print(f"Nombre de résultats: {data.get('total_count', 0)}")
    else:
        print("Aucune donnée récupérée")


if __name__ == "__main__":
    main()
