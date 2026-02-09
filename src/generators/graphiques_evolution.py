"""
Génération de graphiques d'évolution pour analyses multi-années
Utilise matplotlib pour créer des visualisations claires et professionnelles
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Dict, Optional
import os


def configurer_style_graphique():
    """Configure le style visuel des graphiques"""
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.titlesize'] = 13
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9
    plt.rcParams['figure.titlesize'] = 14


def generer_graphique_evolution_poste(
    bilans: List[Dict],
    chemin_poste: str,
    titre: str,
    unite: str = "k€",
    fichier_sortie: Optional[str] = None,
    par_habitant: bool = False
) -> str:
    """
    Génère un graphique d'évolution pour un poste spécifique

    Args:
        bilans: Liste des bilans avec années
        chemin_poste: Chemin vers la valeur (ex: "fonctionnement.produits.total.montant_k")
        titre: Titre du graphique
        unite: Unité d'affichage
        fichier_sortie: Chemin de sauvegarde (si None, nom auto-généré)
        par_habitant: Si True, normalise les valeurs par la population (k€ -> €/hab)

    Returns:
        Chemin du fichier généré
    """
    configurer_style_graphique()

    # Extraire les données
    annees = [b['annee'] for b in bilans]
    valeurs = []

    for bilan in bilans:
        keys = chemin_poste.split('.')
        valeur = bilan['data']

        for key in keys:
            if isinstance(valeur, dict) and key in valeur:
                valeur = valeur[key]
            else:
                valeur = None
                break

        valeur_finale = valeur if valeur is not None else 0

        # Normaliser par habitant si demandé
        if par_habitant:
            population = bilan['data'].get('metadata', {}).get('population')
            if population and population > 0:
                # Convertir k€ en €/hab (1 k€ = 1000 €)
                valeur_finale = (valeur_finale * 1000) / population
            else:
                valeur_finale = 0

        valeurs.append(valeur_finale)

    # Créer le graphique
    fig, ax = plt.subplots(figsize=(10, 5))

    # Ligne principale
    ax.plot(annees, valeurs, marker='o', linewidth=2.5, markersize=8,
            color='#2c3e50', label=titre)

    # Remplissage sous la courbe
    ax.fill_between(annees, valeurs, alpha=0.2, color='#3498db')

    # Annotations des valeurs
    for i, (annee, valeur) in enumerate(zip(annees, valeurs)):
        # Format différent selon si c'est par habitant ou non
        if par_habitant:
            annotation = f'{valeur:.0f}'
        else:
            annotation = f'{valeur:.0f}'
        ax.annotate(annotation,
                   xy=(annee, valeur),
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   fontweight='bold')

    # Style du graphique
    ax.set_xlabel('Année', fontweight='bold')
    ax.set_ylabel(unite, fontweight='bold')
    ax.set_title(f'Évolution - {titre}', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')

    # Ajuster les limites
    marge = max(valeurs) * 0.15 if max(valeurs) > 0 else 1
    ax.set_ylim(min(valeurs) - marge if min(valeurs) > 0 else 0, max(valeurs) + marge)

    plt.xticks(annees, rotation=0)
    plt.tight_layout()

    # Sauvegarder
    if not fichier_sortie:
        nom_fichier = titre.lower().replace(' ', '_').replace("'", '')
        fichier_sortie = f"output/graphiques/evolution_{nom_fichier}.png"

    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight')
    plt.close()

    return fichier_sortie


def generer_graphique_comparaison_multiple(
    bilans: List[Dict],
    postes_config: List[Dict],
    titre: str,
    fichier_sortie: Optional[str] = None,
    par_habitant: bool = False,
    unite: str = "k€"
) -> str:
    """
    Génère un graphique avec plusieurs courbes pour comparer plusieurs postes

    Args:
        bilans: Liste des bilans
        postes_config: Liste de dicts avec {
            'chemin': str,
            'label': str,
            'couleur': str (optionnel)
        }
        titre: Titre du graphique
        fichier_sortie: Chemin de sauvegarde
        par_habitant: Si True, normalise les valeurs par la population
        unite: Unité d'affichage

    Returns:
        Chemin du fichier généré
    """
    configurer_style_graphique()

    couleurs_defaut = ['#2c3e50', '#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

    annees = [b['annee'] for b in bilans]

    fig, ax = plt.subplots(figsize=(12, 6))

    for idx, config in enumerate(postes_config):
        chemin = config['chemin']
        label = config['label']
        couleur = config.get('couleur', couleurs_defaut[idx % len(couleurs_defaut)])

        valeurs = []
        for bilan in bilans:
            keys = chemin.split('.')
            valeur = bilan['data']

            for key in keys:
                if isinstance(valeur, dict) and key in valeur:
                    valeur = valeur[key]
                else:
                    valeur = None
                    break

            valeur_finale = valeur if valeur is not None else 0

            # Normaliser par habitant si demandé
            if par_habitant:
                population = bilan['data'].get('metadata', {}).get('population')
                if population and population > 0:
                    valeur_finale = (valeur_finale * 1000) / population
                else:
                    valeur_finale = 0

            valeurs.append(valeur_finale)

        ax.plot(annees, valeurs, marker='o', linewidth=2, markersize=6,
               color=couleur, label=label)

    ax.set_xlabel('Année', fontweight='bold')
    ax.set_ylabel(unite, fontweight='bold')
    ax.set_title(titre, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')

    plt.xticks(annees, rotation=0)
    plt.tight_layout()

    if not fichier_sortie:
        fichier_sortie = f"output/graphiques/comparaison_multiple.png"

    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight')
    plt.close()

    return fichier_sortie


def generer_graphique_ratios(
    ratios_par_annee: List[Dict],
    ratio_name: str,
    titre: str,
    unite: str = "%",
    seuil_alerte: Optional[float] = None,
    fichier_sortie: Optional[str] = None
) -> str:
    """
    Génère un graphique d'évolution pour un ratio spécifique

    Args:
        ratios_par_annee: Liste des ratios par année
        ratio_name: Nom du ratio à afficher
        titre: Titre du graphique
        unite: Unité du ratio
        seuil_alerte: Seuil d'alerte (ligne rouge pointillée)
        fichier_sortie: Chemin de sauvegarde

    Returns:
        Chemin du fichier généré
    """
    configurer_style_graphique()

    annees = [r['annee'] for r in ratios_par_annee]
    valeurs = [r.get(ratio_name, 0) if r.get(ratio_name) is not None else 0
              for r in ratios_par_annee]

    fig, ax = plt.subplots(figsize=(10, 5))

    # Ligne principale
    ax.plot(annees, valeurs, marker='o', linewidth=2.5, markersize=8,
            color='#2c3e50', label=titre)

    # Ligne de seuil d'alerte si définie
    if seuil_alerte is not None:
        ax.axhline(y=seuil_alerte, color='#e74c3c', linestyle='--',
                  linewidth=2, label=f'Seuil d\'alerte ({seuil_alerte}{unite})')

    # Remplissage
    if seuil_alerte:
        # Colorer différemment selon le dépassement du seuil
        ax.fill_between(annees, valeurs, seuil_alerte,
                        where=[v > seuil_alerte for v in valeurs],
                        alpha=0.3, color='#e74c3c', label='Zone de vigilance')
        ax.fill_between(annees, valeurs, seuil_alerte,
                        where=[v <= seuil_alerte for v in valeurs],
                        alpha=0.2, color='#2ecc71')
    else:
        ax.fill_between(annees, valeurs, alpha=0.2, color='#3498db')

    # Annotations
    for annee, valeur in zip(annees, valeurs):
        ax.annotate(f'{valeur:.1f}{unite}',
                   xy=(annee, valeur),
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   fontweight='bold')

    ax.set_xlabel('Année', fontweight='bold')
    ax.set_ylabel(unite, fontweight='bold')
    ax.set_title(f'Évolution - {titre}', fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best')

    plt.xticks(annees, rotation=0)
    plt.tight_layout()

    if not fichier_sortie:
        nom_fichier = ratio_name.lower().replace(' ', '_')
        fichier_sortie = f"output/graphiques/ratio_{nom_fichier}.png"

    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight')
    plt.close()

    return fichier_sortie


def generer_graphique_barres_empilees(
    bilans: List[Dict],
    postes: List[Dict],
    titre: str,
    fichier_sortie: Optional[str] = None
) -> str:
    """
    Génère un graphique en barres empilées pour comparer la structure budgétaire

    Args:
        bilans: Liste des bilans
        postes: Liste de dicts avec {'chemin': str, 'label': str, 'couleur': str}
        titre: Titre du graphique
        fichier_sortie: Chemin de sauvegarde

    Returns:
        Chemin du fichier généré
    """
    configurer_style_graphique()

    annees = [b['annee'] for b in bilans]
    donnees_postes = {}

    for config in postes:
        valeurs = []
        for bilan in bilans:
            keys = config['chemin'].split('.')
            valeur = bilan['data']

            for key in keys:
                if isinstance(valeur, dict) and key in valeur:
                    valeur = valeur[key]
                else:
                    valeur = None
                    break

            valeurs.append(valeur if valeur is not None else 0)

        donnees_postes[config['label']] = {
            'valeurs': valeurs,
            'couleur': config.get('couleur', '#3498db')
        }

    fig, ax = plt.subplots(figsize=(12, 6))

    # Créer les barres empilées
    bottom = [0] * len(annees)

    for label, data in donnees_postes.items():
        ax.bar(annees, data['valeurs'], label=label,
              color=data['couleur'], bottom=bottom, width=0.6)
        bottom = [b + v for b, v in zip(bottom, data['valeurs'])]

    ax.set_xlabel('Année', fontweight='bold')
    ax.set_ylabel('Montant (k€)', fontweight='bold')
    ax.set_title(titre, fontweight='bold', pad=20)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')

    plt.xticks(annees, rotation=0)
    plt.tight_layout()

    if not fichier_sortie:
        fichier_sortie = "output/graphiques/barres_empilees.png"

    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight')
    plt.close()

    return fichier_sortie


def generer_tous_graphiques_standard(bilans: List[Dict], ratios_par_annee: List[Dict]) -> Dict[str, str]:
    """
    Génère tous les graphiques standards pour un rapport multi-années

    Returns:
        Dict avec {nom_graphique: chemin_fichier}
    """
    graphiques_generes = {}

    print("\nGénération des graphiques...")

    # 1. Produits et Charges de fonctionnement (par habitant)
    print("  • Produits et Charges de fonctionnement (par habitant)")
    graphiques_generes['produits_charges'] = generer_graphique_comparaison_multiple(
        bilans,
        [
            {'chemin': 'fonctionnement.produits.total.montant_k', 'label': 'Produits', 'couleur': '#2ecc71'},
            {'chemin': 'fonctionnement.charges.total.montant_k', 'label': 'Charges', 'couleur': '#e74c3c'}
        ],
        'Évolution Produits vs Charges de fonctionnement (par habitant)',
        'output/graphiques/produits_charges_fonctionnement.png',
        par_habitant=True,
        unite='€/hab'
    )

    # 2. Résultat de fonctionnement (par habitant)
    print("  • Résultat de fonctionnement (par habitant)")
    graphiques_generes['resultat'] = generer_graphique_evolution_poste(
        bilans,
        'fonctionnement.resultat.montant_k',
        'Résultat de fonctionnement',
        '€/hab',
        'output/graphiques/resultat_fonctionnement.png',
        par_habitant=True
    )

    # 3. CAF brute et nette (par habitant)
    print("  • CAF brute et nette (par habitant)")
    graphiques_generes['caf'] = generer_graphique_comparaison_multiple(
        bilans,
        [
            {'chemin': 'autofinancement.caf_brute.montant_k', 'label': 'CAF brute', 'couleur': '#3498db'},
            {'chemin': 'autofinancement.caf_nette.montant_k', 'label': 'CAF nette', 'couleur': '#9b59b6'}
        ],
        'Évolution de la Capacité d\'Autofinancement (par habitant)',
        'output/graphiques/caf_brute_nette.png',
        par_habitant=True,
        unite='€/hab'
    )

    # 4. Encours de la dette (par habitant)
    print("  • Encours de la dette (par habitant)")
    graphiques_generes['dette'] = generer_graphique_evolution_poste(
        bilans,
        'endettement.encours_total.montant_k',
        'Encours de la dette',
        '€/hab',
        'output/graphiques/encours_dette.png',
        par_habitant=True
    )

    # 5. Capacité de désendettement
    print("  • Capacité de désendettement")
    graphiques_generes['capacite_desendettement'] = generer_graphique_ratios(
        ratios_par_annee,
        'capacite_desendettement',
        'Capacité de désendettement',
        ' ans',
        seuil_alerte=12,
        fichier_sortie='output/graphiques/capacite_desendettement.png'
    )

    # 6. Dépenses d'équipement (par habitant)
    print("  • Dépenses d'équipement (par habitant)")
    graphiques_generes['depenses_equip'] = generer_graphique_evolution_poste(
        bilans,
        'investissement.emplois.depenses_equipement.montant_k',
        'Dépenses d\'équipement',
        '€/hab',
        'output/graphiques/depenses_equipement.png',
        par_habitant=True
    )



    # 8. Taux d'épargne brute
    print("  • Taux d'épargne brute")
    graphiques_generes['epargne'] = generer_graphique_ratios(
        ratios_par_annee,
        'taux_epargne_brute',
        'Taux d\'épargne brute (CAF / Produits)',
        '%',
        fichier_sortie='output/graphiques/taux_epargne_brute.png'
    )

    print(f"\n[OK] {len(graphiques_generes)} graphiques generes avec succes\n")

    return graphiques_generes


def generer_graphique_evolution_structure_100pct(
    bilans: List[Dict],
    postes_chemins: List[Dict],
    titre: str,
    fichier_sortie: Optional[str] = None
) -> str:
    """
    Génère un graphique en barres empilées à 100% pour voir l'évolution de la structure

    Args:
        bilans: Liste des bilans
        postes_chemins: Liste de dicts avec {'chemin': str (ex: 'fonctionnement.produits.impots_locaux.pct_produits_caf'),
                                             'label': str,
                                             'couleur': str}
        titre: Titre du graphique
        fichier_sortie: Chemin de sauvegarde

    Returns:
        Chemin du fichier généré
    """
    configurer_style_graphique()

    annees = [b['annee'] for b in bilans]
    categories = [str(a) for a in annees]

    # Extraire les données pour chaque poste
    data_postes = {}
    for config in postes_chemins:
        valeurs = []
        for bilan in bilans:
            keys = config['chemin'].split('.')
            valeur = bilan['data']

            for key in keys:
                if isinstance(valeur, dict) and key in valeur:
                    valeur = valeur[key]
                else:
                    valeur = None
                    break

            valeurs.append(valeur if valeur is not None else 0)

        data_postes[config['label']] = {
            'valeurs': valeurs,
            'couleur': config.get('couleur', '#3498db')
        }

    # Calculer "Autres" pour chaque année
    autres_valeurs = []
    for i in range(len(annees)):
        total = sum([data['valeurs'][i] for data in data_postes.values()])
        autres = max(0, 100 - total)
        autres_valeurs.append(autres)

    # Ajouter "Autres" aux données
    data_postes['Autres'] = {
        'valeurs': autres_valeurs,
        'couleur': '#95a5a6'
    }

    # Créer le graphique
    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.5

    # Créer les barres empilées
    bottom = [0] * len(annees)
    bars_list = []

    for label, data in data_postes.items():
        bars = ax.bar(categories, data['valeurs'], width, bottom=bottom,
                     label=label, color=data['couleur'], edgecolor='white', linewidth=2)
        bars_list.append((bars, data['valeurs'], bottom.copy()))

        # Ajouter labels sur sections > 5%
        for bar, val, bot in zip(bars, data['valeurs'], bottom):
            if val > 5:
                ax.text(bar.get_x() + bar.get_width()/2., bot + val/2,
                       f'{val:.1f}%', ha='center', va='center',
                       fontsize=8, fontweight='bold', color='white')

        bottom = [b + v for b, v in zip(bottom, data['valeurs'])]

    ax.set_ylabel('Répartition (%)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Année', fontsize=11, fontweight='bold')
    ax.set_title(titre, fontsize=13, fontweight='bold', pad=20)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=True, shadow=True)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()

    if not fichier_sortie:
        fichier_sortie = "output/graphiques/evolution_structure_100pct.png"

    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight')
    plt.close()

    return fichier_sortie


def generer_graphique_ratios_combines(
    ratios_par_annee: List[Dict],
    ratios_config: List[Dict],
    titre: str,
    fichier_sortie: Optional[str] = None
) -> str:
    """
    Génère un graphique avec plusieurs ratios affichés en barres groupées

    Args:
        ratios_par_annee: Liste des ratios par année
        ratios_config: Liste de dicts avec {
            'nom_ratio': str (clé dans ratios_par_annee),
            'label': str (nom affiché),
            'couleur': str,
            'seuil': float (optionnel)
        }
        titre: Titre du graphique
        fichier_sortie: Chemin de sauvegarde

    Returns:
        Chemin du fichier généré
    """
    configurer_style_graphique()

    annees = [r['annee'] for r in ratios_par_annee]
    x = range(len(annees))
    width = 0.8 / len(ratios_config)  # Largeur des barres

    fig, ax = plt.subplots(figsize=(14, 7))

    # Pour chaque ratio, créer un groupe de barres
    for idx, config in enumerate(ratios_config):
        nom_ratio = config['nom_ratio']
        label = config['label']
        couleur = config.get('couleur', '#3498db')
        seuil = config.get('seuil')

        valeurs = [r.get(nom_ratio, 0) if r.get(nom_ratio) is not None else 0
                  for r in ratios_par_annee]

        offset = (idx - len(ratios_config)/2) * width + width/2
        positions = [p + offset for p in x]

        bars = ax.bar(positions, valeurs, width, label=label,
                     color=couleur, alpha=0.85, edgecolor='#2c3e50', linewidth=1)

        # Ajouter les valeurs sur les barres
        for bar, val in zip(bars, valeurs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1f}', ha='center', va='bottom',
                   fontsize=8, fontweight='bold')

        # Ligne de seuil si définie
        if seuil is not None:
            ax.axhline(y=seuil, color=couleur, linestyle='--',
                      linewidth=1.5, alpha=0.5)

    ax.set_xlabel('Année', fontsize=11, fontweight='bold')
    ax.set_ylabel('Valeur', fontsize=11, fontweight='bold')
    ax.set_title(titre, fontsize=13, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels([str(a) for a in annees])
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=True, shadow=True)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()

    if not fichier_sortie:
        fichier_sortie = "output/graphiques/ratios_combines.png"

    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight')
    plt.close()

    return fichier_sortie


if __name__ == "__main__":
    print("Module de génération de graphiques chargé")
    print("Utilisez les fonctions de génération avec vos données de bilans")
