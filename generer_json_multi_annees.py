"""
Génère un JSON consolidé pour l'analyse multi-années
Parse plusieurs bilans PDF et crée un JSON avec évolutions et tendances
"""

import json
import sys
import os

sys.path.insert(0, 'src')

from analysis.analyseur_multi_annees import charger_bilans_multi_annees, detecter_tendances_et_anomalies, calculer_ratios_evolutifs


def calculer_evolution(valeur_annee_n, valeur_annee_n_moins_1):
    """Calcule l'évolution en % entre deux années"""
    if valeur_annee_n_moins_1 is None or valeur_annee_n is None or valeur_annee_n_moins_1 == 0:
        return None
    return round(((valeur_annee_n - valeur_annee_n_moins_1) / abs(valeur_annee_n_moins_1)) * 100, 1)


def calculer_evolution_moyenne(bilans, chemin_donnee):
    """Calcule l'évolution moyenne annuelle sur la période"""
    valeurs = []
    for bilan in bilans:
        keys = chemin_donnee.split('.')
        val = bilan['data']
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                val = None
                break
        if val is not None:
            valeurs.append(val)

    if len(valeurs) < 2:
        return None

    evolutions = []
    for i in range(1, len(valeurs)):
        evo = calculer_evolution(valeurs[i], valeurs[i-1])
        if evo is not None:
            evolutions.append(evo)

    return round(sum(evolutions) / len(evolutions), 1) if evolutions else None


def extraire_serie_temporelle(bilans, chemin_donnee):
    """Extrait une série temporelle pour un poste donné"""
    serie = {}
    for bilan in bilans:
        annee = bilan['annee']
        keys = chemin_donnee.split('.')
        val = bilan['data']
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                val = None
                break
        serie[annee] = val
    return serie


def calculer_evolutions_annuelles(serie_k, serie_hab):
    """
    Calcule les évolutions année par année (N→N+1) en % et en valeur absolue

    Args:
        serie_k: Série temporelle en k€ (dict {annee: valeur})
        serie_hab: Série temporelle en €/hab (dict {annee: valeur})

    Returns:
        dict: Évolutions par paire d'années
    """
    evolutions = {}
    annees = sorted(serie_k.keys())

    for i in range(len(annees) - 1):
        annee_debut = annees[i]
        annee_fin = annees[i + 1]

        val_k_debut = serie_k.get(annee_debut)
        val_k_fin = serie_k.get(annee_fin)
        val_hab_debut = serie_hab.get(annee_debut)
        val_hab_fin = serie_hab.get(annee_fin)

        cle = f"{annee_debut}_{annee_fin}"
        evolutions[cle] = {}

        # Évolution en k€
        if val_k_debut is not None and val_k_fin is not None:
            evolution_k = val_k_fin - val_k_debut
            evolution_pct = calculer_evolution(val_k_fin, val_k_debut)
            evolutions[cle]['evolution_k'] = round(evolution_k, 1)
            evolutions[cle]['evolution_pct'] = evolution_pct if evolution_pct is not None else 0
        else:
            evolutions[cle]['evolution_k'] = None
            evolutions[cle]['evolution_pct'] = None

        # Évolution en €/hab
        if val_hab_debut is not None and val_hab_fin is not None:
            evolution_hab = val_hab_fin - val_hab_debut
            evolutions[cle]['evolution_hab'] = round(evolution_hab, 1)
        else:
            evolutions[cle]['evolution_hab'] = None

    return evolutions


def generer_json_multi_annees_consolide(dossier_bilans, fichier_sortie="output/donnees_multi_annees.json"):
    """
    Génère un JSON consolidé pour l'analyse multi-années

    Args:
        dossier_bilans: Dossier contenant les PDFs multi-années
        fichier_sortie: Fichier JSON de sortie

    Returns:
        dict: JSON consolidé
    """

    print("\n" + "="*80)
    print("GÉNÉRATION JSON MULTI-ANNÉES CONSOLIDÉ")
    print("="*80 + "\n")

    # 1. Charger tous les bilans
    print("[1/3] Chargement des bilans...")
    bilans = charger_bilans_multi_annees(dossier_bilans)

    if len(bilans) < 2:
        raise ValueError(f"Minimum 2 bilans requis (trouvés: {len(bilans)})")

    print(f"  [OK] {len(bilans)} bilans chargés")
    print(f"  Période: {bilans[0]['annee']} -> {bilans[-1]['annee']}")

    # 2. Construire le JSON consolidé
    print("\n[2/3] Construction du JSON consolidé...")

    # Métadonnées globales
    premier_bilan = bilans[0]['data']
    dernier_bilan = bilans[-1]['data']

    json_consolide = {
        "metadata": {
            "commune": premier_bilan['metadata']['commune'],
            "periode_debut": bilans[0]['annee'],
            "periode_fin": bilans[-1]['annee'],
            "nb_annees": len(bilans),
            "population_debut": premier_bilan['metadata']['population'],
            "population_fin": dernier_bilan['metadata']['population'],
            "strate": premier_bilan['metadata']['strate']
        },

        "tendances_globales": {}
    }

    # Définir les postes à analyser avec leurs chemins JSON
    postes_a_analyser = [
        ("produits_fonctionnement", 'fonctionnement.produits.total'),
        ("charges_fonctionnement", 'fonctionnement.charges.total'),
        ("charges_personnel", 'fonctionnement.charges.charges_personnel'),
        ("caf_brute", 'autofinancement.caf_brute'),
        ("caf_nette", 'autofinancement.caf_nette'),
        ("encours_dette", 'endettement.encours_total'),
        ("depenses_equipement", 'investissement.emplois.depenses_equipement'),
        ("emprunts_contractes", 'investissement.ressources.emprunts'),
        ("subventions_recues", 'investissement.ressources.subventions_recues'),
    ]

    # Calculer les tendances pour chaque poste
    for nom_poste, chemin_base in postes_a_analyser:
        serie_k = extraire_serie_temporelle(bilans, f'{chemin_base}.montant_k')
        serie_hab = extraire_serie_temporelle(bilans, f'{chemin_base}.par_hab')
        evolution_moy = calculer_evolution_moyenne(bilans, f'{chemin_base}.montant_k')
        evolutions_annuelles = calculer_evolutions_annuelles(serie_k, serie_hab)

        json_consolide["tendances_globales"][nom_poste] = {
            "serie_k": serie_k,
            "serie_hab": serie_hab,
            "evolution_moy_annuelle_pct": evolution_moy,
            "evolutions_annuelles": evolutions_annuelles
        }

    # Poste spécial : capacité de désendettement (en années, pas en k€)
    serie_cap_des = extraire_serie_temporelle(bilans, 'endettement.ratios.capacite_desendettement_annees')
    evolutions_cap_des = {}
    annees = sorted(serie_cap_des.keys())
    for i in range(len(annees) - 1):
        annee_debut = annees[i]
        annee_fin = annees[i + 1]
        val_debut = serie_cap_des.get(annee_debut)
        val_fin = serie_cap_des.get(annee_fin)
        cle = f"{annee_debut}_{annee_fin}"
        if val_debut is not None and val_fin is not None:
            evolutions_cap_des[cle] = {
                "evolution_annees": round(val_fin - val_debut, 1),
                "evolution_pct": calculer_evolution(val_fin, val_debut)
            }

    json_consolide["tendances_globales"]["capacite_desendettement"] = {
        "serie_annees": serie_cap_des,
        "evolution_moy_annuelle_pct": calculer_evolution_moyenne(bilans, 'endettement.ratios.capacite_desendettement_annees'),
        "evolutions_annuelles": evolutions_cap_des
    }

    # Ajouter les bilans annuels
    json_consolide["bilans_annuels"] = {}

    # Ajouter tous les bilans annuels
    for bilan in bilans:
        json_consolide["bilans_annuels"][str(bilan['annee'])] = bilan['data']

    print(f"  [OK] JSON consolidé créé")
    print(f"  Tendances calculées pour {len(json_consolide['tendances_globales'])} postes")

    # 3. Sauvegarder
    print(f"\n[3/3] Sauvegarde du JSON...")
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        json.dump(json_consolide, f, ensure_ascii=False, indent=2)

    print(f"  [OK] Fichier sauvegardé : {fichier_sortie}")

    print("\n" + "="*80)
    print("GÉNÉRATION TERMINÉE")
    print("="*80 + "\n")

    return json_consolide


def main():
    """Point d'entrée principal pour l'import depuis d'autres scripts"""
    dossier = "docs/bilans_multi_annees"

    if len(sys.argv) > 1:
        dossier = sys.argv[1]

    json_data = generer_json_multi_annees_consolide(dossier)

    print("Prochaine étape :")
    print("  → python generer_prompts_enrichis_depuis_json.py (avec support multi-années)")

    return json_data


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERREUR] : {e}")
        import traceback
        traceback.print_exc()
