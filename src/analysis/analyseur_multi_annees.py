"""
Analyse comparative de bilans communaux sur plusieurs années
Compare les évolutions des postes clés, ratios et détecte les tendances
Supporte à la fois les PDFs et l'API OFGL
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from src.generators.generer_json_enrichi import generer_json_enrichi
from src.parsers.fetcher_api_ofgl import convertir_api_vers_json_enrichi


def extraire_annee_depuis_nom_fichier(nom_fichier: str) -> Optional[int]:
    """
    Extrait l'année depuis le nom de fichier
    Format attendu: "Edition commune DAUPHIN - Alpes-de-Haute-Provence - Exercice 2022"

    Returns:
        Année (int) ou None si non trouvée
    """
    match = re.search(r'Exercice\s*(\d{4})', nom_fichier, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # Fallback: chercher 20XX n'importe où dans le nom
    match = re.search(r'20\d{2}', nom_fichier)
    if match:
        return int(match.group(0))

    return None


def charger_bilans_depuis_api(code_insee: str, annees: List[int]) -> List[Dict]:
    """
    Charge les bilans depuis l'API OFGL

    Args:
        code_insee: Code INSEE de la commune
        annees: Liste des années à récupérer

    Returns:
        Liste de dicts avec structure:
        {
            'annee': int,
            'source': str,
            'data': dict (JSON enrichi)
        }
    """
    bilans = []

    print(f"\nChargement de {len(annees)} bilans depuis l'API OFGL (INSEE: {code_insee})...\n")

    for annee in annees:
        try:
            print(f"  [Année {annee}]")
            print(f"    Récupération depuis l'API OFGL...")

            json_data = convertir_api_vers_json_enrichi(code_insee, annee)

            if not json_data:
                print(f"    [WARN] Aucune donnée disponible pour {annee}")
                continue

            bilans.append({
                'annee': annee,
                'source': 'API',
                'data': json_data
            })

            print(f"    [OK] Année {annee} - {json_data['metadata']['commune']}")

        except Exception as e:
            print(f"    [ERR] ERREUR: {e}")
            continue

    bilans.sort(key=lambda x: x['annee'])

    if len(bilans) < 2:
        raise ValueError(f"Minimum 2 bilans requis pour une analyse comparative (trouvés: {len(bilans)})")

    print(f"\n[OK] {len(bilans)} bilans chargés avec succès depuis l'API")
    print(f"  Période: {bilans[0]['annee']} -> {bilans[-1]['annee']}")

    return bilans


def charger_bilans_multi_annees(dossier_bilans: str) -> List[Dict]:
    """
    Charge tous les bilans PDF d'un dossier et génère les JSONs enrichis

    Args:
        dossier_bilans: Chemin vers le dossier contenant les PDFs

    Returns:
        Liste de dicts avec structure:
        {
            'annee': int,
            'fichier': str,
            'data': dict (JSON enrichi)
        }
    """
    bilans = []

    if not os.path.exists(dossier_bilans):
        raise FileNotFoundError(f"Dossier introuvable: {dossier_bilans}")

    fichiers_pdf = [f for f in os.listdir(dossier_bilans) if f.lower().endswith('.pdf')]

    if not fichiers_pdf:
        raise ValueError(f"Aucun fichier PDF trouvé dans {dossier_bilans}")

    print(f"\nChargement de {len(fichiers_pdf)} bilans depuis {dossier_bilans}...\n")

    for fichier in fichiers_pdf:
        chemin_complet = os.path.join(dossier_bilans, fichier)

        # Extraire l'année depuis le nom de fichier
        annee_fichier = extraire_annee_depuis_nom_fichier(fichier)

        try:
            print(f"  [{fichier}]")
            print(f"    Parsing PDF...")

            # Générer le JSON enrichi
            json_data = generer_json_enrichi(chemin_complet)

            # L'année peut être dans le JSON ou dans le nom de fichier
            annee_exercice = json_data.get('metadata', {}).get('exercice')
            annee_finale = annee_exercice or annee_fichier

            if not annee_finale:
                print(f"    [WARN] ATTENTION: Impossible de determiner l'annee, fichier ignore")
                continue

            bilans.append({
                'annee': annee_finale,
                'source': 'PDF',
                'fichier': fichier,
                'data': json_data
            })

            print(f"    [OK] Annee {annee_finale} - {json_data['metadata']['commune']}")

        except Exception as e:
            print(f"    [ERR] ERREUR: {e}")
            continue

    # Trier par année
    bilans.sort(key=lambda x: x['annee'])

    if len(bilans) < 2:
        raise ValueError(f"Minimum 2 bilans requis pour une analyse comparative (trouves: {len(bilans)})")

    print(f"\n[OK] {len(bilans)} bilans charges avec succes")
    print(f"  Periode: {bilans[0]['annee']} -> {bilans[-1]['annee']}")

    return bilans


def calculer_evolution(valeur_actuelle, valeur_precedente) -> Dict:
    """
    Calcule l'évolution entre deux valeurs

    Returns:
        {
            'evolution_absolue': float,
            'evolution_pct': float,
            'tendance': str ('hausse', 'baisse', 'stable')
        }
    """
    if valeur_precedente is None or valeur_actuelle is None:
        return {'evolution_absolue': None, 'evolution_pct': None, 'tendance': 'inconnu'}

    if valeur_precedente == 0:
        if valeur_actuelle == 0:
            return {'evolution_absolue': 0, 'evolution_pct': 0, 'tendance': 'stable'}
        return {'evolution_absolue': valeur_actuelle, 'evolution_pct': None, 'tendance': 'apparition'}

    evolution_abs = valeur_actuelle - valeur_precedente
    evolution_pct = round((evolution_abs / valeur_precedente) * 100, 2)

    if abs(evolution_pct) < 2:
        tendance = 'stable'
    elif evolution_pct > 0:
        tendance = 'hausse'
    else:
        tendance = 'baisse'

    return {
        'evolution_absolue': round(evolution_abs, 2),
        'evolution_pct': evolution_pct,
        'tendance': tendance
    }


def extraire_valeur_poste(json_data: Dict, chemin: str) -> Optional[float]:
    """
    Extrait une valeur depuis le JSON en suivant un chemin
    Ex: "fonctionnement.produits.total.montant_k"

    Returns:
        Valeur ou None si introuvable
    """
    keys = chemin.split('.')
    valeur = json_data

    for key in keys:
        if isinstance(valeur, dict) and key in valeur:
            valeur = valeur[key]
        else:
            return None

    return valeur


def comparer_bilans_annee_par_annee(bilans: List[Dict]) -> Dict:
    """
    Compare les bilans année par année

    Returns:
        Structure avec évolutions pour chaque poste clé
    """
    comparaisons = {
        'metadata': {
            'commune': bilans[0]['data']['metadata']['commune'],
            'periode_debut': bilans[0]['annee'],
            'periode_fin': bilans[-1]['annee'],
            'nb_annees': len(bilans)
        },
        'evolutions_annuelles': [],
        'synthese_globale': {}
    }

    # Définir les postes clés à suivre
    postes_cles = {
        'Produits de fonctionnement': 'fonctionnement.produits.total.montant_k',
        'Charges de fonctionnement': 'fonctionnement.charges.total.montant_k',
        'Résultat de fonctionnement': 'fonctionnement.resultat.montant_k',
        'Impôts locaux': 'fonctionnement.produits.impots_locaux.montant_k',
        'DGF': 'fonctionnement.produits.dgf.montant_k',
        'Charges de personnel': 'fonctionnement.charges.charges_personnel.montant_k',
        'Dépenses d\'équipement': 'investissement.emplois.depenses_equipement.montant_k',
        'Emprunts contractés': 'investissement.ressources.emprunts.montant_k',
        'Subventions reçues': 'investissement.ressources.subventions_recues.montant_k',
        'CAF brute': 'autofinancement.caf_brute.montant_k',
        'CAF nette': 'autofinancement.caf_nette.montant_k',
        'Encours dette': 'endettement.encours_total.montant_k',
        'Capacité désendettement': 'endettement.ratios.capacite_desendettement_annees'
    }

    # Comparaison année par année
    for i in range(1, len(bilans)):
        bilan_precedent = bilans[i-1]
        bilan_actuel = bilans[i]

        evolutions = {
            'annee_precedente': bilan_precedent['annee'],
            'annee_actuelle': bilan_actuel['annee'],
            'postes': {}
        }

        for nom_poste, chemin in postes_cles.items():
            val_prec = extraire_valeur_poste(bilan_precedent['data'], chemin)
            val_act = extraire_valeur_poste(bilan_actuel['data'], chemin)

            evolution = calculer_evolution(val_act, val_prec)
            evolutions['postes'][nom_poste] = {
                'valeur_precedente': val_prec,
                'valeur_actuelle': val_act,
                **evolution
            }

        comparaisons['evolutions_annuelles'].append(evolutions)

    # Synthèse globale (première année vs dernière année)
    if len(bilans) >= 2:
        premier_bilan = bilans[0]
        dernier_bilan = bilans[-1]

        synthese = {
            'periode': f"{premier_bilan['annee']}-{dernier_bilan['annee']}",
            'postes': {}
        }

        for nom_poste, chemin in postes_cles.items():
            val_debut = extraire_valeur_poste(premier_bilan['data'], chemin)
            val_fin = extraire_valeur_poste(dernier_bilan['data'], chemin)

            evolution = calculer_evolution(val_fin, val_debut)
            synthese['postes'][nom_poste] = {
                'valeur_debut': val_debut,
                'valeur_fin': val_fin,
                **evolution
            }

        comparaisons['synthese_globale'] = synthese

    return comparaisons


def detecter_tendances_et_anomalies(comparaisons: Dict) -> Dict:
    """
    Détecte les tendances significatives et anomalies

    Returns:
        {
            'tendances_fortes': [...],
            'anomalies': [...],
            'points_attention': [...]
        }
    """
    resultats = {
        'tendances_fortes': [],
        'anomalies': [],
        'points_attention': []
    }

    synthese = comparaisons.get('synthese_globale', {})
    postes = synthese.get('postes', {})

    for nom_poste, donnees in postes.items():
        evolution_pct = donnees.get('evolution_pct')

        if evolution_pct is None:
            continue

        # Tendances fortes (évolution > 20%)
        if abs(evolution_pct) > 20:
            resultats['tendances_fortes'].append({
                'poste': nom_poste,
                'evolution_pct': evolution_pct,
                'type': 'hausse' if evolution_pct > 0 else 'baisse',
                'valeur_debut': donnees['valeur_debut'],
                'valeur_fin': donnees['valeur_fin']
            })

        # Anomalies (évolution > 50% ou < -30%)
        if evolution_pct > 50 or evolution_pct < -30:
            resultats['anomalies'].append({
                'poste': nom_poste,
                'evolution_pct': evolution_pct,
                'message': f"Évolution très importante ({evolution_pct:+.1f}%)"
            })

    # Points d'attention spécifiques

    # Dette qui augmente fortement
    if 'Encours dette' in postes:
        evol_dette = postes['Encours dette'].get('evolution_pct', 0)
        if evol_dette and evol_dette > 15:
            resultats['points_attention'].append({
                'type': 'endettement',
                'message': f"Hausse significative de l'endettement: +{evol_dette:.1f}%"
            })

    # Capacité d'autofinancement qui baisse
    if 'CAF brute' in postes:
        evol_caf = postes['CAF brute'].get('evolution_pct', 0)
        if evol_caf and evol_caf < -10:
            resultats['points_attention'].append({
                'type': 'autofinancement',
                'message': f"Baisse de la CAF brute: {evol_caf:.1f}%"
            })

    # Charges de personnel qui augmentent plus vite que les produits
    if 'Charges de personnel' in postes and 'Produits de fonctionnement' in postes:
        evol_personnel = postes['Charges de personnel'].get('evolution_pct', 0)
        evol_produits = postes['Produits de fonctionnement'].get('evolution_pct', 0)

        if evol_personnel and evol_produits and evol_personnel > evol_produits + 5:
            resultats['points_attention'].append({
                'type': 'rigidite',
                'message': f"Charges de personnel en hausse ({evol_personnel:+.1f}%) plus rapide que les produits ({evol_produits:+.1f}%)"
            })

    return resultats


def calculer_ratios_evolutifs(bilans: List[Dict]) -> Dict:
    """
    Calcule les ratios financiers clés et leur évolution dans le temps

    Returns:
        Structure avec ratios par année et évolutions
    """
    ratios_par_annee = []

    for bilan in bilans:
        data = bilan['data']

        # Extraire les valeurs de base
        produits_fonct = extraire_valeur_poste(data, 'fonctionnement.produits.total.montant_k') or 0
        charges_fonct = extraire_valeur_poste(data, 'fonctionnement.charges.total.montant_k') or 0
        charges_personnel = extraire_valeur_poste(data, 'fonctionnement.charges.charges_personnel.montant_k') or 0
        caf_brute = extraire_valeur_poste(data, 'autofinancement.caf_brute.montant_k') or 0
        dette = extraire_valeur_poste(data, 'endettement.encours_total.montant_k') or 0
        depenses_equip = extraire_valeur_poste(data, 'investissement.emplois.depenses_equipement.montant_k') or 0

        # Calcul des ratios
        ratios = {
            'annee': bilan['annee'],
            'taux_epargne_brute': round((caf_brute / produits_fonct * 100), 2) if produits_fonct else 0,
            'rigidite_structurelle': round((charges_personnel / charges_fonct * 100), 2) if charges_fonct else 0,
            'taux_endettement': round((dette / produits_fonct * 100), 2) if produits_fonct else 0,
            'capacite_desendettement': round(dette / caf_brute, 2) if caf_brute else None,
            'taux_equipement': round((depenses_equip / produits_fonct * 100), 2) if produits_fonct else 0,
            'ratio_caf_depenses_equip': round((caf_brute / depenses_equip * 100), 2) if depenses_equip else None
        }

        ratios_par_annee.append(ratios)

    # Calculer les évolutions
    evolutions_ratios = {}
    if len(ratios_par_annee) >= 2:
        premier = ratios_par_annee[0]
        dernier = ratios_par_annee[-1]

        for key in ['taux_epargne_brute', 'rigidite_structurelle', 'taux_endettement',
                    'capacite_desendettement', 'taux_equipement']:
            val_debut = premier.get(key)
            val_fin = dernier.get(key)

            if val_debut is not None and val_fin is not None:
                evolutions_ratios[key] = calculer_evolution(val_fin, val_debut)

    return {
        'ratios_par_annee': ratios_par_annee,
        'evolutions': evolutions_ratios
    }


if __name__ == "__main__":
    # Test du module
    dossier_test = "docs/bilans_multi_annees"

    try:
        bilans = charger_bilans_multi_annees(dossier_test)
        comparaisons = comparer_bilans_annee_par_annee(bilans)
        tendances = detecter_tendances_et_anomalies(comparaisons)
        ratios = calculer_ratios_evolutifs(bilans)

        print("\n=== SYNTHÈSE DES ÉVOLUTIONS ===")
        print(f"\nPeriode: {comparaisons['metadata']['periode_debut']} -> {comparaisons['metadata']['periode_fin']}")
        print(f"Commune: {comparaisons['metadata']['commune']}")

        print("\n--- Tendances fortes ---")
        for t in tendances['tendances_fortes']:
            print(f"  - {t['poste']}: {t['evolution_pct']:+.1f}%")

        print("\n--- Points d'attention ---")
        for p in tendances['points_attention']:
            print(f"  [!] {p['message']}")

    except Exception as e:
        print(f"Erreur: {e}")
