"""
Script pour visualiser les données budgétaires avec graphiques
et enrichir les comptes avec la table de transposition M14/M57
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def charger_table_transposition(fichier_excel):
    """
    Charge la table de transposition M14/M57 depuis Excel

    Returns:
        dict: Mapping compte -> libellé
    """
    print(f"Chargement de la table de transposition: {fichier_excel}")

    # Lire le fichier Excel sans header
    df = pd.read_excel(fichier_excel, sheet_name='Version_2026', header=None)

    # Colonnes: 0=compte, 1=libelle, 2=notes
    df.columns = ['compte', 'libelle', 'notes']

    # Nettoyer: enlever les lignes vides et convertir les comptes en string
    df = df.dropna(subset=['compte', 'libelle'])
    df['compte'] = df['compte'].astype(str).str.strip()
    df['libelle'] = df['libelle'].astype(str).str.strip()

    # Filtrer les lignes qui ne sont pas des comptes numériques
    df = df[df['compte'].str.match(r'^\d+$', na=False)]

    # Créer le dictionnaire de mapping
    mapping = dict(zip(df['compte'], df['libelle']))

    print(f"Nombre de comptes dans la table: {len(mapping)}")
    print(f"\nExemples de comptes:")
    for compte in list(mapping.keys())[:5]:
        print(f"  {compte}: {mapping[compte]}")

    return mapping


def enrichir_comptes_avec_libelles(comptes_details, mapping_comptes):
    """
    Enrichit les comptes avec leurs libellés officiels

    Note: Depuis la mise à jour, le JSON balance_m57.json contient déjà
    le champ 'libelle_compte' avec le libellé officiel. Cette fonction
    renomme simplement ce champ en 'libelle_officiel' pour compatibilité.

    Args:
        comptes_details: Liste des comptes de balance_m57.json
        mapping_comptes: dict de mapping compte -> libellé (non utilisé)

    Returns:
        Liste enrichie avec libellés officiels
    """
    comptes_enrichis = []

    for compte_data in comptes_details:
        compte_enrichi = compte_data.copy()

        # Utiliser le champ 'libelle_compte' déjà présent dans le JSON
        if 'libelle_compte' in compte_data:
            compte_enrichi['libelle_officiel'] = compte_data['libelle_compte']
        else:
            # Fallback si le JSON n'a pas encore été mis à jour
            compte_enrichi['libelle_officiel'] = compte_data.get('libelle', 'Inconnu')

        comptes_enrichis.append(compte_enrichi)

    return comptes_enrichis


def analyser_principaux_postes(comptes_details, classe, top_n=10):
    """
    Identifie les principaux postes d'une classe de compte

    Args:
        comptes_details: Liste des comptes
        classe: Classe de compte (ex: '7' pour produits, '6' pour charges)
        top_n: Nombre de comptes à afficher

    Returns:
        DataFrame des top comptes
    """
    # Filtrer par classe
    comptes_classe = [c for c in comptes_details if c['compte'].startswith(classe)]

    # Convertir en DataFrame
    df = pd.DataFrame(comptes_classe)

    # Trier par montant absolu
    df['montant_abs'] = df['flux_net'].abs()
    df_top = df.nlargest(top_n, 'montant_abs')

    return df_top


def creer_graphique_barres(df, titre, fichier_sortie):
    """
    Crée un graphique en barres des principaux comptes

    Args:
        df: DataFrame avec colonnes 'compte', 'libelle_officiel', 'flux_net'
        titre: Titre du graphique
        fichier_sortie: Chemin du fichier PNG à créer
    """
    plt.figure(figsize=(14, 8))

    # Préparer les labels (compte + libellé tronqué)
    df_plot = df.copy()
    df_plot['label'] = df_plot.apply(
        lambda row: f"{row['compte']} - {row['libelle_officiel'][:50]}...",
        axis=1
    )

    # Créer le graphique
    colors = ['green' if x > 0 else 'red' for x in df_plot['flux_net']]
    bars = plt.barh(range(len(df_plot)), df_plot['flux_net'], color=colors, alpha=0.7)

    # Ajouter les labels sur l'axe Y
    plt.yticks(range(len(df_plot)), df_plot['label'], fontsize=9)

    # Ajouter les montants sur les barres
    for i, (idx, row) in enumerate(df_plot.iterrows()):
        plt.text(row['flux_net'], i, f" {row['flux_net']:,.0f}€",
                va='center', fontsize=9, fontweight='bold')

    plt.xlabel('Montant (€)', fontsize=11, fontweight='bold')
    plt.title(titre, fontsize=13, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()

    # Sauvegarder
    plt.savefig(fichier_sortie, dpi=150, bbox_inches='tight')
    print(f"Graphique sauvegarde: {fichier_sortie}")
    plt.close()


def creer_graphique_camembert(df, titre, fichier_sortie):
    """
    Crée un graphique en camembert des principaux comptes

    Args:
        df: DataFrame avec colonnes 'compte', 'libelle_officiel', 'flux_net'
        titre: Titre du graphique
        fichier_sortie: Chemin du fichier PNG à créer
    """
    plt.figure(figsize=(12, 10))

    # Prendre les valeurs absolues
    df_plot = df.copy()
    df_plot['montant_abs'] = df_plot['flux_net'].abs()

    # Créer les labels avec libellé tronqué + montant
    labels = [f"{row['libelle_officiel'][:30]}... ({row['montant_abs']:,.0f}€)"
              for idx, row in df_plot.iterrows()]

    plt.pie(df_plot['montant_abs'], labels=labels, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 9})
    plt.title(titre, fontsize=13, fontweight='bold')
    plt.tight_layout()

    # Sauvegarder
    plt.savefig(fichier_sortie, dpi=150, bbox_inches='tight')
    print(f"Graphique sauvegarde: {fichier_sortie}")
    plt.close()


def main():
    # Chemins
    base_dir = Path(__file__).parent
    fichier_plan_comptes = base_dir / "docs" / "plan_comptes_m57.json"
    fichier_balance = base_dir / "output" / "balance_m57.json"
    output_dir = base_dir / "output" / "graphiques"
    output_dir.mkdir(exist_ok=True)

    # 1. Charger le plan de comptes M57 (extrait du PDF)
    print("="*80)
    print("ETAPE 1: Chargement du plan de comptes M57")
    print("="*80)
    print(f"Chargement depuis: {fichier_plan_comptes}")

    with open(fichier_plan_comptes, 'r', encoding='utf-8') as f:
        mapping_comptes = json.load(f)

    print(f"Nombre de comptes dans le plan: {len(mapping_comptes)}")

    # 2. Charger les données budgétaires
    print("\n" + "="*80)
    print("ETAPE 2: Chargement des donnees budgetaires")
    print("="*80)
    with open(fichier_balance, 'r', encoding='utf-8') as f:
        data = json.load(f)

    comptes = data['comptes_details']
    print(f"Nombre de comptes: {len(comptes)}")

    # 2b. Enrichir avec les libellés officiels
    print("\n" + "="*80)
    print("ETAPE 2b: Enrichissement avec les libelles officiels")
    print("="*80)
    comptes = enrichir_comptes_avec_libelles(comptes, mapping_comptes)
    print(f"Comptes enrichis: {len(comptes)}")
    print("\nExemples de comptes enrichis:")
    for c in comptes[:3]:
        print(f"  {c['compte']}: {c['libelle_officiel']}")

    # 3. Analyser les produits (classe 7)
    print("\n" + "="*80)
    print("ETAPE 3: Analyse des PRODUITS (recettes)")
    print("="*80)
    produits_top = analyser_principaux_postes(comptes, '7', top_n=10)
    print("\nTop 10 des produits:")
    print(produits_top[['compte', 'libelle_officiel', 'flux_net']])

    # Créer les graphiques
    creer_graphique_barres(
        produits_top,
        "Top 10 des Produits (Recettes) - Budget Principal",
        output_dir / "produits_barres.png"
    )
    creer_graphique_camembert(
        produits_top,
        "Répartition des Produits (Recettes)",
        output_dir / "produits_camembert.png"
    )

    # 4. Analyser les charges (classe 6)
    print("\n" + "="*80)
    print("ETAPE 4: Analyse des CHARGES (depenses)")
    print("="*80)
    charges_top = analyser_principaux_postes(comptes, '6', top_n=10)
    print("\nTop 10 des charges:")
    print(charges_top[['compte', 'libelle_officiel', 'flux_net']])

    # Créer les graphiques
    creer_graphique_barres(
        charges_top,
        "Top 10 des Charges (Depenses) - Budget Principal",
        output_dir / "charges_barres.png"
    )
    creer_graphique_camembert(
        charges_top,
        "Repartition des Charges (Depenses)",
        output_dir / "charges_camembert.png"
    )

    # 5. Résumé
    print("\n" + "="*80)
    print("RESUME")
    print("="*80)
    total_produits = sum(c['flux_net'] for c in comptes if c['compte'].startswith('7'))
    total_charges = sum(c['flux_net'] for c in comptes if c['compte'].startswith('6'))
    print(f"Total Produits (classe 7): {total_produits:,.2f} €")
    print(f"Total Charges (classe 6): {total_charges:,.2f} €")
    print(f"Resultat: {total_produits - total_charges:,.2f} €")

    print(f"\nGraphiques sauvegardes dans: {output_dir}")


if __name__ == "__main__":
    main()
