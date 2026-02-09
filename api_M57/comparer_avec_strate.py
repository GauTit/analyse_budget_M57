"""
Script pour comparer les comptes comptables d'une commune avec la moyenne de sa strate
Usage: python comparer_avec_strate.py --siren SIREN --annee ANNEE
"""

import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
from collections import defaultdict
import time


API_OFGL = "https://data.ofgl.fr/api/explore/v2.1/catalog/datasets/ofgl-base-communes-consolidee/records"


def fetch_commune_info(siren, annee):
    """
    Récupère les informations de la commune (population, strate) via l'API OFGL

    Args:
        siren: Code SIREN de la commune
        annee: Année budgétaire

    Returns:
        dict: Informations de la commune (population, tranche_population, etc.)
    """
    print(f"\n{'='*80}")
    print(f"ETAPE 1: Récupération des informations de la commune (SIREN: {siren})")
    print(f"{'='*80}")

    # Utiliser refine au lieu de where (format OpenDataSoft)
    params = [
        ("limit", "1"),
        ("refine", f"siren:{siren}"),
        ("refine", f"exer:{annee}")
    ]

    try:
        response = requests.get(API_OFGL, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get('results'):
            print(f"ERREUR: Aucune donnée trouvée pour SIREN {siren}, année {annee}")
            return None

        result = data['results'][0]
        info = {
            "commune": result.get('com_name'),
            "siren": siren,
            "code_insee": result.get('insee'),
            "population": result.get('ptot'),
            "tranche_population": result.get('tranche_population'),
            "departement": result.get('dep_name'),
            "region": result.get('reg_name')
        }

        print(f"Commune: {info['commune']}")
        print(f"Population: {info['population']} habitants")
        print(f"Strate: {info['tranche_population']}")
        print(f"Département: {info['departement']}")

        return info

    except requests.exceptions.RequestException as e:
        print(f"ERREUR API OFGL: {e}")
        return None


def fetch_communes_strate(tranche_population, annee, limit=100):
    """
    Récupère toutes les communes d'une strate

    Args:
        tranche_population: Code de la tranche de population
        annee: Année budgétaire
        limit: Nombre de résultats par page

    Returns:
        list: Liste des communes (siren, nom, population)
    """
    print(f"\n{'='*80}")
    print(f"ETAPE 2: Récupération des communes de la strate {tranche_population}")
    print(f"{'='*80}")

    communes = []
    offset = 0
    sirens_vus = set()

    while True:
        # Utiliser refine pour les filtres (format OpenDataSoft)
        params = [
            ("select", "siren,com_name,ptot"),
            ("refine", f"tranche_population:{tranche_population}"),
            ("refine", f"exer:{annee}"),
            ("limit", str(limit)),
            ("offset", str(offset)),
            ("group_by", "siren,com_name,ptot")
        ]

        try:
            response = requests.get(API_OFGL, params=params)
            response.raise_for_status()
            data = response.json()

            results = data.get('results', [])
            if not results:
                break

            for result in results:
                siren = result.get('siren')
                if siren and siren not in sirens_vus:
                    communes.append({
                        "siren": siren,
                        "nom": result.get('com_name'),
                        "population": result.get('ptot')
                    })
                    sirens_vus.add(siren)

            print(f"  Récupéré {len(results)} enregistrements (total communes: {len(communes)})")

            if len(results) < limit:
                break

            offset += limit
            time.sleep(0.1)  # Pause pour ne pas surcharger l'API

        except requests.exceptions.RequestException as e:
            print(f"ERREUR lors de la récupération des communes: {e}")
            break

    print(f"\nTotal: {len(communes)} communes dans la strate {tranche_population}")
    return communes


def fetch_balance_m57(siren, annee, limit=100):
    """
    Récupère la balance M57 complète d'une commune

    Args:
        siren: Code SIREN
        annee: Année budgétaire
        limit: Nombre de résultats par page

    Returns:
        list: Liste des comptes avec flux nets
    """
    base_url = f"https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/balances-comptables-des-communes-en-{annee}/records"

    all_records = []
    offset = 0

    while True:
        params = {
            "where": f"siren={siren} AND cbudg='1'",  # Budget principal uniquement
            "limit": limit,
            "offset": offset
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()

            records = data.get('results', [])
            if not records:
                break

            all_records.extend(records)

            if len(records) < limit:
                break

            offset += limit

        except requests.exceptions.RequestException as e:
            print(f"  ERREUR balance M57 pour SIREN {siren}: {e}")
            return []

    return all_records


def calculer_flux_nets_par_compte(records):
    """
    Calcule les flux nets par compte depuis les records de balance

    Args:
        records: Liste des enregistrements bruts

    Returns:
        dict: {compte: flux_net}
    """
    comptes_dict = defaultdict(float)

    for record in records:
        compte = str(record.get('compte', ''))
        if not compte:
            continue

        credit = record.get('obnetcre', 0) or 0
        debit = record.get('obnetdeb', 0) or 0
        flux_net = credit - debit

        comptes_dict[compte] += flux_net

    return dict(comptes_dict)


def calculer_moyennes_strate(communes, annee, max_communes=None):
    """
    Calcule les moyennes des comptes pour toutes les communes de la strate

    Args:
        communes: Liste des communes de la strate
        annee: Année budgétaire
        max_communes: Limite le nombre de communes à traiter (pour tests)

    Returns:
        dict: Statistiques par compte (moyenne, médiane, etc.)
    """
    print(f"\n{'='*80}")
    print(f"ETAPE 3: Calcul des moyennes de la strate")
    print(f"{'='*80}")

    # Limiter pour les tests
    if max_communes:
        communes = communes[:max_communes]
        print(f"MODE TEST: Limité à {max_communes} communes")

    # Collecter les flux nets de toutes les communes
    comptes_par_commune = []
    communes_ok = 0

    for i, commune in enumerate(communes, 1):
        print(f"  [{i}/{len(communes)}] Récupération {commune['nom']} (SIREN: {commune['siren']})...")

        records = fetch_balance_m57(commune['siren'], annee)
        if records:
            flux_nets = calculer_flux_nets_par_compte(records)
            if flux_nets:
                comptes_par_commune.append({
                    "siren": commune['siren'],
                    "population": commune['population'],
                    "flux_nets": flux_nets
                })
                communes_ok += 1

        time.sleep(0.2)  # Pause entre chaque requête

    print(f"\nCommunes traitées avec succès: {communes_ok}/{len(communes)}")

    if not comptes_par_commune:
        print("ERREUR: Aucune donnée récupérée")
        return {}

    # Calculer les statistiques par compte
    tous_comptes = set()
    for data in comptes_par_commune:
        tous_comptes.update(data['flux_nets'].keys())

    print(f"Nombre de comptes distincts: {len(tous_comptes)}")

    stats_comptes = {}
    for compte in tous_comptes:
        valeurs = []
        valeurs_par_hab = []

        for data in comptes_par_commune:
            flux = data['flux_nets'].get(compte, 0)
            pop = data['population']

            if flux != 0:
                valeurs.append(flux)
                if pop and pop > 0:
                    valeurs_par_hab.append(flux / pop)

        if valeurs:
            stats_comptes[compte] = {
                "moyenne": sum(valeurs) / len(valeurs),
                "mediane": sorted(valeurs)[len(valeurs) // 2] if valeurs else 0,
                "nb_communes": len(valeurs),
                "moyenne_par_hab": sum(valeurs_par_hab) / len(valeurs_par_hab) if valeurs_par_hab else 0
            }

    return stats_comptes


def charger_balance_locale(fichier_balance):
    """Charge le fichier balance_m57.json local"""
    print(f"\n{'='*80}")
    print(f"ETAPE 0: Chargement de la balance locale")
    print(f"{'='*80}")

    with open(fichier_balance, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Commune: {data['metadata']['commune']}")
    print(f"Exercice: {data['metadata']['exercice']}")
    print(f"Nombre de comptes: {len(data['comptes_details'])}")

    return data


def creer_tableau_comparatif(balance_locale, stats_strate, info_commune, output_path):
    """
    Crée un tableau Excel comparant chaque compte avec la moyenne de la strate

    Args:
        balance_locale: Données de la balance locale
        stats_strate: Statistiques de la strate
        info_commune: Informations de la commune
        output_path: Chemin du fichier Excel à créer
    """
    print(f"\n{'='*80}")
    print(f"ETAPE 4: Création du tableau comparatif")
    print(f"{'='*80}")

    # Préparer les données
    rows = []
    population = info_commune['population']

    for compte_data in balance_locale['comptes_details']:
        compte = compte_data['compte']
        flux_net = compte_data['flux_net']
        libelle = compte_data.get('libelle_compte', compte_data.get('libelle_officiel', ''))

        # Récupérer les stats de la strate
        stats = stats_strate.get(compte, {})
        moyenne_strate = stats.get('moyenne', 0)
        moyenne_par_hab_strate = stats.get('moyenne_par_hab', 0)
        nb_communes = stats.get('nb_communes', 0)

        # Calculer les indicateurs
        flux_par_hab = flux_net / population if population else 0
        ecart_absolu = flux_net - moyenne_strate
        ecart_pourcent = (ecart_absolu / moyenne_strate * 100) if moyenne_strate != 0 else 0

        ecart_par_hab = flux_par_hab - moyenne_par_hab_strate
        ecart_pourcent_par_hab = (ecart_par_hab / moyenne_par_hab_strate * 100) if moyenne_par_hab_strate != 0 else 0

        rows.append({
            "Compte": compte,
            "Libellé": libelle,
            "Commune - Montant": flux_net,
            "Commune - €/hab": flux_par_hab,
            "Strate - Moyenne": moyenne_strate,
            "Strate - €/hab": moyenne_par_hab_strate,
            "Écart absolu": ecart_absolu,
            "Écart %": ecart_pourcent,
            "Écart €/hab": ecart_par_hab,
            "Écart % par hab": ecart_pourcent_par_hab,
            "Nb communes strate": nb_communes
        })

    # Créer le DataFrame
    df = pd.DataFrame(rows)

    # Trier par valeur absolue de l'écart
    df['ecart_abs_abs'] = df['Écart absolu'].abs()
    df = df.sort_values('ecart_abs_abs', ascending=False)
    df = df.drop('ecart_abs_abs', axis=1)

    # Sauvegarder en Excel avec formatage
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Comparaison comptes', index=False)

        # Formater les colonnes
        workbook = writer.book
        worksheet = writer.sheets['Comparaison comptes']

        # Largeur des colonnes
        worksheet.column_dimensions['A'].width = 12
        worksheet.column_dimensions['B'].width = 50
        worksheet.column_dimensions['C'].width = 18
        worksheet.column_dimensions['D'].width = 15
        worksheet.column_dimensions['E'].width = 18
        worksheet.column_dimensions['F'].width = 15
        worksheet.column_dimensions['G'].width = 18
        worksheet.column_dimensions['H'].width = 12
        worksheet.column_dimensions['I'].width = 15
        worksheet.column_dimensions['J'].width = 15
        worksheet.column_dimensions['K'].width = 15

    print(f"Tableau sauvegardé: {output_path}")
    print(f"Nombre de comptes comparés: {len(df)}")

    return df


def creer_graphiques_top_ecarts(df, info_commune, output_dir, top_n=15):
    """
    Crée des graphiques des plus grands écarts avec la strate

    Args:
        df: DataFrame du tableau comparatif
        info_commune: Informations de la commune
        output_dir: Dossier de sortie
        top_n: Nombre de comptes à afficher
    """
    print(f"\n{'='*80}")
    print(f"ETAPE 5: Création des graphiques")
    print(f"{'='*80}")

    # Filtrer les comptes avec écarts significatifs
    df_ecarts = df[df['Strate - Moyenne'] != 0].copy()
    df_ecarts['ecart_abs'] = df_ecarts['Écart absolu'].abs()

    # Top écarts positifs et négatifs
    df_top = df_ecarts.nlargest(top_n, 'ecart_abs')

    # Graphique 1: Comparaison montants (commune vs strate)
    fig, ax = plt.subplots(figsize=(14, 10))

    x = range(len(df_top))
    width = 0.35

    labels = [f"{row['Compte']}\n{row['Libellé'][:30]}..." for _, row in df_top.iterrows()]

    ax.barh([i - width/2 for i in x], df_top['Commune - Montant'], width,
            label=info_commune['commune'], color='steelblue', alpha=0.8)
    ax.barh([i + width/2 for i in x], df_top['Strate - Moyenne'], width,
            label=f"Moyenne strate {info_commune['tranche_population']}", color='orange', alpha=0.8)

    ax.set_yticks(x)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel('Montant (€)', fontsize=11, fontweight='bold')
    ax.set_title(f"Top {top_n} des écarts avec la strate - Montants absolus",
                fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()

    fichier = output_dir / "comparaison_strate_montants.png"
    plt.savefig(fichier, dpi=150, bbox_inches='tight')
    print(f"Graphique sauvegardé: {fichier}")
    plt.close()

    # Graphique 2: Comparaison par habitant
    fig, ax = plt.subplots(figsize=(14, 10))

    ax.barh([i - width/2 for i in x], df_top['Commune - €/hab'], width,
            label=info_commune['commune'], color='green', alpha=0.8)
    ax.barh([i + width/2 for i in x], df_top['Strate - €/hab'], width,
            label=f"Moyenne strate {info_commune['tranche_population']}", color='red', alpha=0.8)

    ax.set_yticks(x)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel('Montant par habitant (€/hab)', fontsize=11, fontweight='bold')
    ax.set_title(f"Top {top_n} des écarts avec la strate - Par habitant",
                fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()

    fichier = output_dir / "comparaison_strate_par_habitant.png"
    plt.savefig(fichier, dpi=150, bbox_inches='tight')
    print(f"Graphique sauvegardé: {fichier}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Compare les comptes d'une commune avec sa strate")
    parser.add_argument("--siren", required=True, help="Code SIREN de la commune")
    parser.add_argument("--annee", required=True, help="Année budgétaire")
    parser.add_argument("--balance", default="balance_m57.json", help="Fichier balance local")
    parser.add_argument("--test", action="store_true", help="Mode test: limite à 10 communes")

    args = parser.parse_args()

    # Chemins
    base_dir = Path(__file__).parent
    fichier_balance = base_dir / "output" / args.balance
    output_dir = base_dir / "output" / "comparaison_strate"
    output_dir.mkdir(exist_ok=True)

    # Étape 0: Charger la balance locale
    balance_locale = charger_balance_locale(fichier_balance)

    # Étape 1: Récupérer les infos de la commune
    info_commune = fetch_commune_info(args.siren, args.annee)
    if not info_commune:
        return

    # Étape 2: Récupérer les communes de la strate
    communes_strate = fetch_communes_strate(info_commune['tranche_population'], args.annee)
    if not communes_strate:
        return

    # Étape 3: Calculer les moyennes de la strate
    max_communes = 10 if args.test else None
    stats_strate = calculer_moyennes_strate(communes_strate, args.annee, max_communes)
    if not stats_strate:
        return

    # Sauvegarder les stats de la strate
    fichier_stats = output_dir / "stats_strate.json"
    with open(fichier_stats, 'w', encoding='utf-8') as f:
        json.dump({
            "info_commune": info_commune,
            "nb_communes_strate": len(communes_strate),
            "statistiques": stats_strate
        }, f, indent=2, ensure_ascii=False)
    print(f"\nStatistiques de la strate sauvegardées: {fichier_stats}")

    # Étape 4: Créer le tableau comparatif
    fichier_excel = output_dir / "comparaison_comptes_strate.xlsx"
    df_comparaison = creer_tableau_comparatif(balance_locale, stats_strate, info_commune, fichier_excel)

    # Étape 5: Créer les graphiques
    creer_graphiques_top_ecarts(df_comparaison, info_commune, output_dir)

    print(f"\n{'='*80}")
    print(f"TERMINÉ")
    print(f"{'='*80}")
    print(f"Résultats dans: {output_dir}")
    print(f"  - Tableau Excel: comparaison_comptes_strate.xlsx")
    print(f"  - Graphiques: comparaison_strate_*.png")
    print(f"  - Statistiques: stats_strate.json")


if __name__ == "__main__":
    main()
