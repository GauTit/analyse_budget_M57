"""
Script pour enrichir les fichiers JSON avec les ratios financiers calculés
Détecte automatiquement si le JSON est mono-année ou multi-années
"""

import json
import os
from ratios_financiers import (
    enrichir_json_avec_ratios,
    calculer_tous_les_ratios,
    enrichir_json_multi_annees_avec_ratios,
    calculer_tous_ratios_multi_annees
)


def est_multi_annees(data):
    """Détecte si le JSON est multi-années"""
    return 'bilans_annuels' in data and 'tendances_globales' in data


def enrichir_fichier_json(chemin_fichier):
    """Enrichit un fichier JSON avec les ratios et crée une sauvegarde"""

    if not os.path.exists(chemin_fichier):
        print(f"[ERREUR] Fichier non trouve : {chemin_fichier}")
        return False

    # Charger le JSON
    print(f"\n[1/4] Chargement : {chemin_fichier}")
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Détecter le type de JSON
    is_multi = est_multi_annees(data)

    metadata = data.get('metadata', {})
    commune = metadata.get('commune', 'N/A')

    if is_multi:
        periode_debut = metadata.get('periode_debut', 'N/A')
        periode_fin = metadata.get('periode_fin', 'N/A')
        print(f"  Type : MULTI-ANNEES")
        print(f"  Commune : {commune} - Periode : {periode_debut}-{periode_fin}")
    else:
        exercice = metadata.get('exercice', 'N/A')
        print(f"  Type : MONO-ANNEE")
        print(f"  Commune : {commune} - Exercice : {exercice}")

    # Créer une sauvegarde
    chemin_sauvegarde = chemin_fichier.replace('.json', '_AVANT_RATIOS.json')
    if not os.path.exists(chemin_sauvegarde):
        print(f"\n[2/4] Création de la sauvegarde : {chemin_sauvegarde}")
        with open(chemin_sauvegarde, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("  [OK] Sauvegarde créée")
    else:
        print(f"\n[2/4] Sauvegarde existe déjà : {chemin_sauvegarde}")

    # Calculer les ratios selon le type
    print(f"\n[3/4] Calcul des ratios financiers...")

    if is_multi:
        # Multi-années : calculer pour chaque année
        ratios_multi = calculer_tous_ratios_multi_annees(data)

        if ratios_multi:
            print("\n  Ratios calcules par annee :")
            for annee, ratios in ratios_multi['ratios_par_annee'].items():
                print(f"\n  Annee {annee} :")
                for nom_ratio, valeur in list(ratios.items())[:3]:  # Afficher seulement 3 ratios par année
                    if valeur is not None:
                        if 'annees' in nom_ratio:
                            print(f"    {nom_ratio}: {valeur:.1f} annees")
                        else:
                            print(f"    {nom_ratio}: {valeur:.1f}%")

            print("\n  Evolutions sur la periode :")
            for nom_ratio, evolution_data in list(ratios_multi['evolutions'].items())[:3]:
                debut = evolution_data['valeur_debut']
                fin = evolution_data['valeur_fin']
                evo = evolution_data['evolution_totale']
                if 'annees' in nom_ratio:
                    print(f"    {nom_ratio}: {debut:.1f} -> {fin:.1f} ({evo:+.1f} annees)")
                else:
                    print(f"    {nom_ratio}: {debut:.1f}% -> {fin:.1f}% ({evo:+.1f} pts)")

        # Enrichir le JSON multi-années
        data_enrichie = enrichir_json_multi_annees_avec_ratios(data)

    else:
        # Mono-année : calcul classique
        ratios = calculer_tous_les_ratios(data)

        print("\n  Ratios calcules :")
        for nom_ratio, valeur in ratios.items():
            if valeur is not None:
                if 'annees' in nom_ratio:
                    print(f"    {nom_ratio}: {valeur:.1f} annees")
                else:
                    print(f"    {nom_ratio}: {valeur:.1f}%")
            else:
                print(f"    {nom_ratio}: N/A")

        # Enrichir le JSON mono-année
        data_enrichie = enrichir_json_avec_ratios(data)

    # Sauvegarder le JSON enrichi
    print(f"\n[4/4] Sauvegarde du JSON enrichi : {chemin_fichier}")
    with open(chemin_fichier, 'w', encoding='utf-8') as f:
        json.dump(data_enrichie, f, ensure_ascii=False, indent=2)
    print("  [OK] JSON enrichi sauvegardé")

    return True


def main():
    print("="*80)
    print("ENRICHISSEMENT DES JSON AVEC LES RATIOS FINANCIERS")
    print("="*80)

    # Enrichir le JSON mono-année
    fichier_mono = "output/donnees_enrichies.json"
    if enrichir_fichier_json(fichier_mono):
        print(f"\n[OK] {fichier_mono} enrichi avec succes")
    else:
        print(f"\n[ERREUR] Echec de l'enrichissement de {fichier_mono}")

    # Enrichir le JSON multi-années si disponible
    fichier_multi = "output/donnees_multi_annees.json"
    if os.path.exists(fichier_multi):
        print("\n" + "-"*80)
        if enrichir_fichier_json(fichier_multi):
            print(f"\n[OK] {fichier_multi} enrichi avec succes")
        else:
            print(f"\n[ERREUR] Echec de l'enrichissement de {fichier_multi}")
    else:
        print(f"\n[INFO] Fichier multi-annees non trouve : {fichier_multi}")

    print("\n" + "="*80)
    print("ENRICHISSEMENT TERMINÉ")
    print("="*80)
    print("\nProchaine étape :")
    print("  Mettre à jour 'generer_prompts_enrichis_depuis_json.py' pour utiliser")
    print("  les ratios calculés depuis le JSON au lieu de les recalculer.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERREUR] : {e}")
        import traceback
        traceback.print_exc()
