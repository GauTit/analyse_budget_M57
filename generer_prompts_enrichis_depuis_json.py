"""
Script pour générer les prompts enrichis dans l'Excel
à partir des vraies valeurs du JSON et des contextes "L'essentiel"

IMPORTANT : Ce script nécessite que le JSON ait été enrichi avec les ratios financiers.
Exécuter d'abord 'enrichir_json_avec_ratios.py' si ce n'est pas déjà fait.
"""

import pandas as pd
import json
import os

# Fichiers
FICHIER_JSON_MONO = "output/donnees_enrichies.json"
FICHIER_JSON_MULTI = "output/donnees_multi_annees.json"
FICHIER_EXCEL_BASE = "PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx"
FICHIER_EXCEL_SORTIE = "PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx"

# ============================================
# CONTEXTES "L'ESSENTIEL" PAR POSTE
# ============================================

CONTEXTES_ESSENTIELS = {
    "Analyse_globale_intelligente": """
L'ESSENTIEL DE LA SYNTHÈSE GLOBALE :
La synthèse financière globale permet d’apprécier l’ensemble des équilibres budgétaires de la collectivité.
Elle couvre la section de fonctionnement, la capacité d’autofinancement brute et nette, la section d’investissement, l’endettement et le fonds de roulement.
L’analyse met en évidence les articulations comptables entre ces agrégats et repose exclusivement sur la doctrine comptable M14/M57, en utilisant les ratios financiers comme indicateurs de cohérence et de stabilité.

RATIOS ET SEUILS DE RÉFÉRENCE :
- Capacité de désendettement : < 12 ans (seuil prudentiel)
- Taux d’épargne nette : > 10% (seuil prudentiel)

""",

    "Produits_de_fonctionnement": """
L'ESSENTIEL DU POSTE :
Le total des produits de fonctionnement comprend l’ensemble des recettes réelles et d’ordre de la section de fonctionnement.
Le calcul de la CAF repose uniquement sur les flux réels, indépendamment des écritures d’ordre, et constitue un indicateur de capacité d’autofinancement.
""",

    "Impots_locaux": """
L'ESSENTIEL DU POSTE :
Les impôts locaux constituent généralement un poste structurant des recettes réelles de fonctionnement.
Ils regroupent principalement les produits issus de la fiscalité directe locale et économique (TH résiduelle, TFB, TFNB, CFE, CVAE, IFER, TASCOM), y compris les mécanismes de compensation et de neutralisation tels que le FNGIR, nets des reversements.

Les bases prévisionnelles d’imposition sont notifiées chaque année par les services de la Direction Générale des Finances Publiques (DGFIP), généralement au cours du premier trimestre.
Les collectivités votent ensuite les taux applicables à ces bases, déterminant ainsi le produit fiscal attendu.

Depuis 2021, les bases de taxe d’habitation ne concernent plus que les résidences secondaires et les locaux vacants, la taxe d’habitation sur les résidences principales ayant été supprimée.

NOTION CLÉ – Valeur locative cadastrale (VLC) :
La valeur locative cadastrale constitue l’assiette des principaux impôts locaux.
Elle correspond au loyer annuel théorique d’un bien immobilier, déterminé à partir de références de marché anciennes (1970 pour le bâti, 1961 pour le non bâti), et revalorisé annuellement selon des coefficients légaux.
""",

    "DGF": """
L'ESSENTIEL DU POSTE :
La dotation globale de fonctionnement (DGF) constitue l’un des principaux concours financiers de l'État aux collectivités locales.
La DGF comprend :
- La dotation forfaitaire des communes qui est essentiellement basée sur les critères de la population et de la superficie ;
- Les dotations de péréquation communale, destinées à corriger les inégalités de ressources entre collectivités, parmi lesquelles :
  • La dotation de solidarité rurale (DSR), attribuée sous conditions d’éligibilité à certaines communes rurales selon plusieurs fractions et critères réglementaires ;
  • La dotation nationale de péréquation (DNP), visant à réduire les écarts de potentiel fiscal et financier entre communes.
""",

    "Charges_de_fonctionnement": """
L'ESSENTIEL DU POSTE :
Les charges de fonctionnement regroupent l’ensemble des dépenses inscrites en section de fonctionnement, incluant les charges réelles et les charges d’ordre.
Les charges réelles participent à la formation du résultat de fonctionnement, tandis que les charges d’ordre constituent des écritures comptables sans incidence sur les flux financiers.

Le calcul de la capacité d’autofinancement repose exclusivement sur les charges réelles de fonctionnement, à l’exclusion des écritures d’ordre.

""",

    "Charges_de_personnel": """
L'ESSENTIEL DU POSTE :
Les charges de personnel constituent généralement un poste structurant des dépenses réelles de fonctionnement.
Elles regroupent principalement les rémunérations des agents et les charges sociales patronales associées, ainsi que les dépenses liées à la mise à disposition de personnel.

Par leur nature, ces charges présentent un caractère majoritairement rigide à court terme et influencent directement l’équilibre de la section de fonctionnement et la capacité d’autofinancement.
""",

    "Resultat_comptable": """
L'ESSENTIEL DU POSTE :
Le résultat comptable en section de fonctionnement correspond à la différence entre les produits de fonctionnement et les charges de fonctionnement.
Il indique si les recettes réelles couvrent intégralement les dépenses réelles de fonctionnement.
Ce résultat sert de référence pour le calcul de la capacité d’autofinancement et l’appréciation des grands équilibres financiers de la collectivité.

""",

    "CAF_brute": """
L'ESSENTIEL DU POSTE :
La capacité d’autofinancement brute (CAF brute) correspond à l’excédent des produits réels de fonctionnement sur les charges réelles de fonctionnement, avant remboursement du capital de la dette.

Elle intègre les charges financières et n’est pas affectée par les modalités d’amortissement du capital des emprunts.
La CAF brute constitue un indicateur de la capacité de la collectivité à mobiliser des ressources propres issues de son cycle de fonctionnement.
""",

    "CAF_nette": """
L'ESSENTIEL DU POSTE :
La CAF nette est obtenue en retranchant le remboursement en capital des emprunts de la CAF brute.
Elle reflète la capacité de la collectivité à mobiliser des ressources propres après le service du capital de la dette.
La CAF nette est un indicateur de référence pour l’analyse de l’équilibre de fonctionnement et de la capacité d’autofinancement des investissements.

""",

    "Depenses_equipement": """
L'ESSENTIEL DU POSTE :
Il s'agit des investissements réalisés sur l'exercice, par la commune.
On y trouve :
- Les immobilisations incorporelles (dont : frais, documents urbanisme, frais d'études, frais de recherche et développement, frais d'insertion…) ;
- Les immobilisations corporelles (dont : terrains nus, terrains bâtis, bâtiments scolaires, autres bâtiments publics, réseaux de voirie, matériel de bureau et matériel informatique, mobilier…) ;
- Les immobilisations en cours (dont : constructions, installations, matériel et outillage techniques…).

RATIOS D'ANALYSE :
- Ratio de niveau : Dépenses d'équipement / hab. (en €). Ce ratio permet de faire des comparaisons avec la moyenne de la strate ;
- Ratio d'effort d'équipement : Dépenses d'équipement / Produits CAF. Ce ratio permet d'apprécier la part des produits CAF consacrée aux dépenses d'investissement. Mesuré en %, il est à comparer avec les moyennes dégagées de la strate ;
- Taux de couverture de l'investissement : CAF nette / Dépenses d'équipement. Ce ratio mesure la capacité à financer l'investissement par l'autofinancement net disponible après remboursement du capital de la dette.
""",

    "Emprunts_contractes": """
L'ESSENTIEL DU POSTE :
Les emprunts contractés par la collectivité représentent les dettes nouvelles souscrites au cours de l’exercice.
Ils constituent un élément clé pour l’appréciation de l’encours de dette et des charges financières, ainsi que pour l’analyse de la capacité de la collectivité à autofinancer ses investissements.

""",

    "Subventions_recues": """
L'ESSENTIEL DU POSTE :
Les subventions reçues représentent les dotations d’investissement attribuées à la collectivité pour le financement d’opérations déterminées.
Elles peuvent provenir de l’Union européenne, de l’État ou de collectivités territoriales.
Ce poste constitue un indicateur du recours de la collectivité aux financements externes pour ses dépenses d’équipement, distinct des recettes de fonctionnement.

""",

    "Encours_dette": """
L'ESSENTIEL DU POSTE :
L'encours de dette représente le stock des emprunts en capital restant dû au 31 décembre de l'exercice, pour l'ensemble des dettes contractées par la collectivité.
Il reflète le montant que la collectivité doit rembourser à ses prêteurs, qu'il s'agisse d'établissements financiers, de l'État ou d'autres organismes.
L'encours de dette prend en compte :
1. Les emprunts nouveaux souscrits au cours de l'exercice ;
2. Les remboursements effectués sur les emprunts existants au cours de l'exercice.

RATIOS D'ANALYSE :
- Encours total de la dette / hab. (en €) : Il permet de faire des comparaisons avec la moyenne de la strate.
- Ratio d'endettement (Encours de dette / Produits CAF) : Il mesure le "poids de la dette" par rapport aux ressources de fonctionnement de la commune. Si le ratio est supérieur à 100%, cela signifie que l'encours de la dette représente plus d'une année de produits CAF.
- Capacité de désendettement (Encours de dette / CAF brute) : Il s'agit d'un indicateur qui permet de mesurer la capacité d'une commune à rembourser sa dette. Il se mesure en nombre d'années. Le seuil prudentiel est fixé à 12 ans. Pour apprécier le niveau d'endettement, il faut pouvoir mesurer en combien d'années une commune peut amortir la totalité de sa dette en supposant qu'elle y consacre son entière CAF brute.
""",

    "Fonds_roulement": """
L'ESSENTIEL DU POSTE :
Le fonds de roulement représente le cumul des excédents et déficits de fonctionnement et d’investissement arrêtés au 31 décembre de chaque exercice.
Il permet de mesurer la capacité de la collectivité à couvrir son besoin en fonds de roulement (BFR), la trésorerie étant calculée comme la différence entre le FDR et le BFR.
La variation du FDR d’un exercice à l’autre correspond à l’écart comptable entre les ressources et les dépenses d’investissement, incluant les emprunts contractés et les résultats cumulés.
Le fonds de roulement peut être positif ou négatif. Un FDR positif reflète un cumul excédentaire des résultats de fonctionnement et d’investissement, tandis qu’un FDR négatif reflète un cumul déficitaire.

"""
}

# ============================================
# TEXTES PERSONNALISÉS POUR LA SECTION 1
# ============================================
# Vous pouvez écrire ici vos textes personnalisés pour la section "POSITIONNEMENT ET POIDS DU POSTE"
# Laissez vide ("") si vous voulez que l'IA génère automatiquement cette section

TEXTES_PERSONNALISES = {
    "Analyse_globale_intelligente": "",
    "Produits_de_fonctionnement": "Les produits de fonctionnement représentent une ressource essentielle à la couverture des charges courantes de la commune.",
    "Impots_locaux": "",
    "DGF": "",
    "Charges_de_fonctionnement": "",
    "Charges_de_personnel": "",
    "Resultat_comptable": "",
    "CAF_brute": "La CAF brute constitue l’indicateur principal de la capacité de la commune à générer un excédent de ressources issu du fonctionnement avant remboursement du capital de la dette, servant de levier potentiel pour le financement des opérations d’investissement.",
    "CAF_nette": "La CAF nette représente l’autofinancement effectivement disponible pour financer les dépenses d’investissement après remboursement du capital de la dette, constituant un indicateur clé de la marge de manœuvre financière de la commune.",
    "Depenses_equipement": "",
    "Emprunts_contractes": "",
    "Subventions_recues": "",
    "Encours_dette": "",
    "Fonds_roulement": ""
}

# ============================================
# MAPPING POSTES -> CHEMINS JSON
# ============================================

MAPPING_POSTES_JSON = {
    "Analyse_globale_intelligente": "metadata",  # Synthèse globale = toutes les données
    "Produits_de_fonctionnement": "fonctionnement.produits.total",
    "Impots_locaux": "fonctionnement.produits.impots_locaux",
    "DGF": "fonctionnement.produits.dgf",
    "Charges_de_fonctionnement": "fonctionnement.charges.total",
    "Charges_de_personnel": "fonctionnement.charges.charges_personnel",
    "Resultat_comptable": "fonctionnement.resultat",
    "CAF_brute": "autofinancement.caf_brute",
    "CAF_nette": "autofinancement.caf_nette",
    "Depenses_equipement": "investissement.emplois.depenses_equipement",
    "Emprunts_contractes": "investissement.ressources.emprunts",
    "Subventions_recues": "investissement.ressources.subventions_recues",
    "Encours_dette": "endettement.encours_total",
    "Fonds_roulement": "endettement.fonds_roulement"
}


def extraire_valeur_json(data, chemin):
    """Extrait une valeur du JSON en suivant un chemin"""
    keys = chemin.split('.')
    valeur = data
    for key in keys:
        if isinstance(valeur, dict) and key in valeur:
            valeur = valeur[key]
        else:
            return None
    return valeur


def formater_fonds_roulement(data_json):
    """Formate le fonds de roulement en gérant tous les cas (None, 0, positif, négatif)"""
    fdr_data = extraire_valeur_json(data_json, 'endettement.fonds_roulement')

    if not fdr_data or not isinstance(fdr_data, dict):
        return "N/A"

    montant = fdr_data.get('montant_k')
    est_positif = fdr_data.get('est_positif')

    # Cas où la valeur est None ou manquante
    if montant is None:
        return "N/A"

    # Cas où la valeur est 0
    if montant == 0:
        return "0 k€ (équilibré)"

    # Utiliser le booléen est_positif si disponible, sinon déduire du montant
    if est_positif is not None:
        statut = "positif" if est_positif else "négatif"
    else:
        statut = "positif" if montant > 0 else "négatif"

    return f"{abs(montant):.0f} k€ ({statut})"


def generer_donnees_injectees(nom_poste, data_json):
    """Génère la chaîne de données à injecter dans le prompt"""

    # CAS SPÉCIAL : Synthèse globale
    if nom_poste == "Analyse_globale_intelligente":
        # Calculer le fonds de roulement par habitant
        fdr_montant = extraire_valeur_json(data_json, 'endettement.fonds_roulement.montant_k') or 0
        population = extraire_valeur_json(data_json, 'metadata.population') or 1
        fdr_par_hab = fdr_montant / population * 1000 if population > 0 else 0

        # Récupérer les produits CAF pour calculer le ratio d'endettement en pourcentage
        produits_caf = extraire_valeur_json(data_json, 'fonctionnement.produits.produits_caf.montant_k') or 1
        charges_personnel_strate = extraire_valeur_json(data_json, 'fonctionnement.charges.charges_personnel.pct_charges_caf_strate') or 0

        donnees = """SYNTHÈSE DES GRANDS AGRÉGATS FINANCIERS :

SECTION DE FONCTIONNEMENT :
- Produits de fonctionnement : {prod_fonct} k€ ({prod_fonct_hab} €/hab. vs {prod_fonct_strate} €/hab. strate)
  • Impôts locaux : {impots} k€ - Part : {impots_pct}% (strate : {impots_pct_strate}%)
  • DGF : {dgf} k€ - Part : {dgf_pct}% (strate : {dgf_pct_strate}%)
- Charges de fonctionnement : {chg_fonct} k€ ({chg_fonct_hab} €/hab. vs {chg_fonct_strate} €/hab. strate)
  • Charges de personnel : {charges_pers} k€ - Part : {charges_pers_pct}% (strate : {charges_pers_pct_strate}%)
  • Achats et charges externes : {achats} k€ - Part : {achats_pct}% (strate : {achats_pct_strate}%)
- Résultat de fonctionnement : {resultat} k€ ({resultat_hab} €/hab. vs {resultat_strate} €/hab. strate)

AUTOFINANCEMENT :
- CAF brute : {caf_brute} k€ ({caf_brute_hab} €/hab. vs {caf_brute_strate} €/hab. strate) - Taux : {caf_brute_pct}% (strate : {caf_brute_pct_strate}%)
- CAF nette : {caf_nette} k€ ({caf_nette_hab} €/hab. vs {caf_nette_strate} €/hab. strate) - Taux : {caf_nette_pct}% (strate : {caf_nette_pct_strate}%)

INVESTISSEMENT :
- Dépenses d'équipement : {depenses_equip} k€ ({depenses_equip_hab} €/hab. vs {depenses_equip_strate} €/hab. strate)
- Emprunts contractés : {emprunts} k€

ENDETTEMENT :
- Encours de dette : {encours} k€ ({encours_hab} €/hab. vs {encours_strate} €/hab. strate) - Ratio d'endettement (Dette/Produits CAF) : {encours_pct}% (strate : {encours_pct_strate}%)
- Capacité de désendettement (Dette/CAF brute) : {cap_des} années (seuil prudentiel : 12 ans)

RATIOS FINANCIERS CLÉS :
- Taux d'épargne brute (CAF brute/Produits CAF) : {taux_epargne}%
- Taux d'épargne nette (CAF nette/Produits CAF) : {taux_epargne_nette}%
- Part charges de personnel / Charges CAF : {part_personnel}% (strate : {part_personnel_strate}%)
- Ratio d'effort d'équipement (Dépenses équip./Produits CAF) : {ratio_effort}%
- Ratio d'autonomie fiscale (Impôts locaux/Produits CAF) : {ratio_autonomie}%
- Taux de couverture de l'investissement par la CAF nette : {taux_couverture}%

SITUATION NETTE :
- Fonds de roulement : {fdr} ({fdr_par_hab:.0f} €/hab. vs 557 €/hab. strate)
""".format(
            prod_fonct=extraire_valeur_json(data_json, 'fonctionnement.produits.total.montant_k') or 0,
            prod_fonct_hab=extraire_valeur_json(data_json, 'fonctionnement.produits.total.par_hab') or 0,
            prod_fonct_strate=extraire_valeur_json(data_json, 'fonctionnement.produits.total.moyenne_strate_hab') or 0,
            chg_fonct=extraire_valeur_json(data_json, 'fonctionnement.charges.total.montant_k') or 0,
            chg_fonct_hab=extraire_valeur_json(data_json, 'fonctionnement.charges.total.par_hab') or 0,
            chg_fonct_strate=extraire_valeur_json(data_json, 'fonctionnement.charges.total.moyenne_strate_hab') or 0,
            resultat=extraire_valeur_json(data_json, 'fonctionnement.resultat.montant_k') or 0,
            resultat_hab=extraire_valeur_json(data_json, 'fonctionnement.resultat.par_hab') or 0,
            resultat_strate=extraire_valeur_json(data_json, 'fonctionnement.resultat.moyenne_strate_hab') or 0,
            caf_brute=extraire_valeur_json(data_json, 'autofinancement.caf_brute.montant_k') or 0,
            caf_brute_hab=extraire_valeur_json(data_json, 'autofinancement.caf_brute.par_hab') or 0,
            caf_brute_strate=extraire_valeur_json(data_json, 'autofinancement.caf_brute.moyenne_strate_hab') or 0,
            caf_nette=extraire_valeur_json(data_json, 'autofinancement.caf_nette.montant_k') or 0,
            caf_nette_hab=extraire_valeur_json(data_json, 'autofinancement.caf_nette.par_hab') or 0,
            caf_nette_strate=extraire_valeur_json(data_json, 'autofinancement.caf_nette.moyenne_strate_hab') or 0,
            depenses_equip=extraire_valeur_json(data_json, 'investissement.emplois.depenses_equipement.montant_k') or 0,
            depenses_equip_hab=extraire_valeur_json(data_json, 'investissement.emplois.depenses_equipement.par_hab') or 0,
            depenses_equip_strate=extraire_valeur_json(data_json, 'investissement.emplois.depenses_equipement.moyenne_strate_hab') or 0,
            emprunts=extraire_valeur_json(data_json, 'investissement.ressources.emprunts.montant_k') or 0,
            encours=extraire_valeur_json(data_json, 'endettement.encours_total.montant_k') or 0,
            encours_hab=extraire_valeur_json(data_json, 'endettement.encours_total.par_hab') or 0,
            encours_strate=extraire_valeur_json(data_json, 'endettement.encours_total.moyenne_strate_hab') or 0,
            ratio_endettement=extraire_valeur_json(data_json, 'ratios_financiers.ratio_endettement_pct') or 0,
            cap_des=extraire_valeur_json(data_json, 'ratios_financiers.capacite_desendettement_annees') or 0,
            taux_epargne=extraire_valeur_json(data_json, 'ratios_financiers.taux_epargne_brute_pct') or 0,
            taux_epargne_nette=extraire_valeur_json(data_json, 'ratios_financiers.taux_epargne_nette_pct') or 0,
            part_personnel=extraire_valeur_json(data_json, 'ratios_financiers.part_charges_personnel_pct') or 0,
            part_personnel_strate=charges_personnel_strate,
            ratio_effort=extraire_valeur_json(data_json, 'ratios_financiers.ratio_effort_equipement_pct') or 0,
            ratio_autonomie=extraire_valeur_json(data_json, 'ratios_financiers.ratio_autonomie_fiscale_pct') or 0,
            taux_couverture=extraire_valeur_json(data_json, 'ratios_financiers.taux_couverture_investissement_pct') or 0,
            fdr=formater_fonds_roulement(data_json),
            fdr_par_hab=fdr_par_hab
            ,
            impots=extraire_valeur_json(data_json, 'fonctionnement.produits.impots_locaux.montant_k') or 0,
            impots_pct=extraire_valeur_json(data_json, 'fonctionnement.produits.impots_locaux.pct_produits_caf') or 0,
            impots_pct_strate=extraire_valeur_json(data_json, 'fonctionnement.produits.impots_locaux.pct_produits_caf_strate') or 0,
            dgf=extraire_valeur_json(data_json, 'fonctionnement.produits.dgf.montant_k') or 0,
            dgf_pct=extraire_valeur_json(data_json, 'fonctionnement.produits.dgf.pct_produits_caf') or 0,
            dgf_pct_strate=extraire_valeur_json(data_json, 'fonctionnement.produits.dgf.pct_produits_caf_strate') or 0,
            charges_pers=extraire_valeur_json(data_json, 'fonctionnement.charges.charges_personnel.montant_k') or 0,
            charges_pers_pct=extraire_valeur_json(data_json, 'fonctionnement.charges.charges_personnel.pct_charges_caf') or 0,
            charges_pers_pct_strate=extraire_valeur_json(data_json, 'fonctionnement.charges.charges_personnel.pct_charges_caf_strate') or 0,
            achats=extraire_valeur_json(data_json, 'fonctionnement.charges.achats_charges_externes.montant_k') or 0,
            achats_pct=extraire_valeur_json(data_json, 'fonctionnement.charges.achats_charges_externes.pct_charges_caf') or 0,
            achats_pct_strate=extraire_valeur_json(data_json, 'fonctionnement.charges.achats_charges_externes.pct_charges_caf_strate') or 0,
            caf_brute_pct=extraire_valeur_json(data_json, 'autofinancement.caf_brute.pct_produits_caf') or 0,
            caf_brute_pct_strate=extraire_valeur_json(data_json, 'autofinancement.caf_brute.pct_produits_caf_strate') or 0,
            caf_nette_pct=extraire_valeur_json(data_json, 'autofinancement.caf_nette.pct_produits_caf') or 0,
            caf_nette_pct_strate=extraire_valeur_json(data_json, 'autofinancement.caf_nette.pct_produits_caf_strate') or 0,
            encours_pct=extraire_valeur_json(data_json, 'endettement.encours_total.pct_produits_caf') or 0,
            encours_pct_strate=extraire_valeur_json(data_json, 'endettement.encours_total.pct_produits_caf_strate') or 0
        )
        return donnees

    # CAS NORMAL : Poste spécifique
    chemin = MAPPING_POSTES_JSON.get(nom_poste)
    if not chemin:
        return "Données non disponibles"

    poste_data = extraire_valeur_json(data_json, chemin)
    if not poste_data:
        return "Données non disponibles"

    # Extraire les informations pertinentes
    montant_k = poste_data.get('montant_k', 0)
    par_hab = poste_data.get('par_hab', 0)
    moyenne_strate = poste_data.get('moyenne_strate_hab', 0)

    comparaison = poste_data.get('comparaison', {})
    ecart_pct = comparaison.get('ecart_pct', 0)
    niveau = comparaison.get('niveau', '')

    # Formater les données de base
    donnees = f"""DONNÉES DU POSTE :
- Montant : {montant_k} k€
- Par habitant : {par_hab:.0f} €/hab.
- Moyenne de la strate : {moyenne_strate:.0f} €/hab.
"""

    # Ajouter les ratios de structure (% de part) si disponibles
    # Pour les produits de fonctionnement et autofinancement
    if 'pct_produits_caf' in poste_data or 'pct_charges_caf' in poste_data:
        pct_commune = poste_data.get('pct_produits_caf') or poste_data.get('pct_charges_caf')
        pct_strate = poste_data.get('pct_produits_caf_strate') or poste_data.get('pct_charges_caf_strate')

        if pct_commune is not None and pct_strate is not None:
            type_ratio = "produits CAF" if 'pct_produits_caf' in poste_data else "charges CAF"
            ecart_ratio = pct_commune - pct_strate
            donnees += f"- Part dans les {type_ratio} : {pct_commune:.1f}% (commune) vs {pct_strate:.1f}% (strate) [écart : {ecart_ratio:+.1f} pts]\n"

    # Pour les ressources et emplois d'investissement
    if 'pct_ressources' in poste_data:
        pct_commune = poste_data.get('pct_ressources')
        pct_strate = poste_data.get('pct_ressources_strate')

        if pct_commune is not None and pct_strate is not None:
            ecart_ratio = pct_commune - pct_strate
            donnees += f"- Part dans les ressources d'investissement : {pct_commune:.1f}% (commune) vs {pct_strate:.1f}% (strate) [écart : {ecart_ratio:+.1f} pts]\n"

    if 'pct_emplois' in poste_data:
        pct_commune = poste_data.get('pct_emplois')
        pct_strate = poste_data.get('pct_emplois_strate')

        if pct_commune is not None and pct_strate is not None:
            ecart_ratio = pct_commune - pct_strate
            donnees += f"- Part dans les emplois d'investissement : {pct_commune:.1f}% (commune) vs {pct_strate:.1f}% (strate) [écart : {ecart_ratio:+.1f} pts]\n"

    # Ajouter l'écart et le niveau
    donnees += f"- Écart avec la strate (en €/hab) : {ecart_pct:+.1f}%\n"
    donnees += f"- Niveau : {niveau}\n"

    # Ajouter le détail fiscal si impôts locaux
    if nom_poste == "Impots_locaux" and 'detail_fiscalite' in poste_data:
        detail = poste_data['detail_fiscalite']
        donnees += "\n\nDÉTAIL DE LA FISCALITÉ :\n"
        for taxe, info in detail.items():
            taux_vote = info.get('taux_vote_pct', 0)
            taux_strate = info.get('taux_strate_pct', 0)
            produit = info.get('produit_k', 0)
            donnees += f"- {taxe.replace('_', ' ').title()} : Taux voté {taux_vote:.2f}% (strate: {taux_strate:.2f}%), produit {produit} k€\n"

    return donnees


def generer_prompt_enrichi(nom_poste, donnees, data_json, texte_personnalise=""):
    """Génère le prompt enrichi avec contexte + consignes + vraies valeurs

    Args:
        nom_poste: Nom du poste budgétaire
        donnees: Données financières du poste
        data_json: JSON complet des données
        texte_personnalise: Texte personnalisé pour la section 1 (optionnel)
    """

    contexte = CONTEXTES_ESSENTIELS.get(nom_poste, "")

    if not contexte:
        return f"DONNÉES À ANALYSER :\n{donnees}\n\nAnalyser le poste de manière professionnelle."

    # Extraire les vraies valeurs globales du JSON
    metadata = data_json.get('metadata', {})
    commune = metadata.get('commune', 'N/A')
    exercice = metadata.get('exercice', 'N/A')
    population = metadata.get('population', 'N/A')
    strate = metadata.get('strate', {}).get('libelle', 'N/A')

    # Extraire les agrégats financiers
    resultat_fonct = extraire_valeur_json(data_json, 'fonctionnement.resultat.montant_k') or 0
    caf_brute = extraire_valeur_json(data_json, 'autofinancement.caf_brute.montant_k') or 0
    caf_nette = extraire_valeur_json(data_json, 'autofinancement.caf_nette.montant_k') or 0
    encours_dette = extraire_valeur_json(data_json, 'endettement.encours_total.montant_k') or 0
    depenses_equip = extraire_valeur_json(data_json, 'investissement.emplois.depenses_equipement.montant_k') or 0
    fdr_str = formater_fonds_roulement(data_json)

    # Ratios (extraits du JSON pré-calculés)
    ratios = data_json.get('ratios_financiers', {})
    taux_epargne = ratios.get('taux_epargne_brute_pct', 0)
    cap_desendettement = ratios.get('capacite_desendettement_annees', 0)
    part_personnel = ratios.get('part_charges_personnel_pct', 0)

    # Consignes différentes pour synthèse globale vs postes spécifiques
    if nom_poste == 'Analyse_globale_intelligente':
        consignes_analyse = """CONSIGNES D’ANALYSE – SYNTHÈSE FINANCIÈRE GLOBALE :

Rédiger une synthèse financière globale concise, mettant en évidence les articulations comptables entre les principaux agrégats financiers de la commune.

La synthèse ne doit pas dépasser 400 mots et se limiter à l’essentiel.

Elle doit :
- présenter l’équilibre général de la section de fonctionnement,
- indiquer la capacité d’autofinancement (CAF brute et CAF nette),
- décrire le financement de l’investissement sur l’exercice,
- détailler les niveaux d’endettement et leur évolution.

Structurer le propos en paragraphes courts et hiérarchisés.
Ne pas répéter les analyses détaillées par poste.

Identifier les articulations comptables entre :
- fonctionnement, autofinancement, investissement et dette.


"""
    else:
# 1. ANALYSE DES RECETTES (FONCTIONNEMENT)
        if nom_poste == "Impots_locaux":
            angle_specifique = "Mettre en évidence le niveau des impôts locaux par rapport à la strate."
        elif nom_poste == "Fiscalite_reversee":
            angle_specifique = "Mettre en évidence les transferts de fiscalité descendante (FPU) et leur importance relative."
        elif nom_poste == "DGF":
            angle_specifique = "Mettre en évidence le montant des dotations de l'État par habitant et leur variation."
        elif nom_poste in ["Autres_dotations_participations", "FCTVA"]:
            angle_specifique = "Mettre en évidence le montant des financements externes complémentaires reçus."
        elif nom_poste == "Produits_services_domaine":
            angle_specifique = "Mettre en évidence le niveau des recettes propres (redevances, services publics) et leur évolution."

        # 2. ANALYSE DES DÉPENSES (FONCTIONNEMENT)
        elif nom_poste == "Charges_de_personnel":
            # Champagnac : 528 €/hab vs 329 €/hab strate 
            angle_specifique = "Mettre en évidence le niveau des charges de personnel par habitant et leur évolution."
        elif nom_poste == "Achats_charges_externes":
            angle_specifique = "Mettre en évidence le niveau des dépenses courantes (énergie, contrats) et leur évolution."
        elif nom_poste == "Charges_financieres":
            angle_specifique = "Mettre en évidence le montant des charges financières (intérêts de la dette) par rapport aux produits de fonctionnement."
        elif nom_poste in ["Contingents", "Subventions_versees"]:
            angle_specifique = "Mettre en évidence le montant des obligations institutionnelles et des subventions versées."

        # 3. ÉQUILIBRES ET AUTOFINANCEMENT
        elif nom_poste in ["Resultat_comptable", "EBF"]:
            angle_specifique = "Mettre en évidence l’excédent ou déficit du fonctionnement et son évolution."
        elif nom_poste == "CAF_brute":
            angle_specifique = "Mettre en évidence la capacité d’autofinancement brute et sa variation d’un exercice à l’autre."
        elif nom_poste == "CAF_nette":
            angle_specifique = "Mettre en évidence la capacité d’autofinancement nette et sa variation d’un exercice à l’autre."

        # 4. INVESTISSEMENT ET DETTE
        elif nom_poste == "Depenses_equipement":
            angle_specifique = "Mettre en évidence le niveau des dépenses d’équipement par habitant et leur évolution."
        elif nom_poste == "Subventions_recues_invest":
            angle_specifique = "Mettre en évidence le montant des subventions reçues pour investissement et leur évolution."
        elif nom_poste == "Encours_dette":
            angle_specifique = "Mettre en évidence le niveau et la variation de l’encours de dette par habitant."
        elif nom_poste == "Annuite_dette":
            angle_specifique = "Mettre en évidence le montant de l’annuité de la dette et sa proportion par rapport aux produits de fonctionnement."
        elif nom_poste == "Fonds_roulement":
            angle_specifique = "Mettre en évidence le niveau et la variation du fonds de roulement."

        else:
            angle_specifique = "Mettre en évidence la contribution de ce poste à l'équilibre budgétaire général."

        # Section 1 personnalisée ou à générer
        section_1_instruction = ""
        if texte_personnalise and texte_personnalise.strip():
            section_1_instruction = f"""
1. POSITIONNEMENT ET POIDS DU POSTE (TEXTE FOURNI - NE PAS GÉNÉRER) :
   Le texte suivant a déjà été rédigé pour cette section :

   "{texte_personnalise.strip()}"

   ⚠️ NE PAS GÉNÉRER DE TEXTE POUR CETTE SECTION - Elle est déjà fournie.
   ⚠️ PRENDRE EN COMPTE ce contexte pour rédiger les sections suivantes.

2. ANALYSE COMPARATIVE ET DIAGNOSTIC DES ÉCARTS (1 phrase + possibilité d'une 2e phrase factuelle)"""
        else:
            section_1_instruction = """
1. POSITIONNEMENT ET POIDS DU POSTE en une phrase :
   - Situer le poste dans la structure budgétaire de la commune
     (poste majeur, poste secondaire, levier de financement, charge rigide, etc.).

2. ANALYSE COMPARATIVE ET DIAGNOSTIC DES ÉCARTS (1 phrase + possibilité d'une 2e phrase factuelle)"""

        consignes_analyse = f"""
   CONSIGNES D'ANALYSE :

Rédige une note d'analyse financière experte, synthétique et doctrinalement conforme M14/M57.

Adopte le ton d'un analyste DGFiP : factuel, hiérarchisé, sans effet de style, sans commentaire politique.

Structure impérative :

{section_1_instruction}
   - Citer obligatoirement : montant en k€, valeur en €/habitant et écart en % par rapport à la strate
     (utiliser strictement l’écart fourni, sans recalcul).
   - Qualifier l’écart avec un vocabulaire varié et institutionnel
     (niveau supérieur / inférieur à la strate, écart significatif, positionnement atypique, alignement).
   - Ajouter, le cas échéant, une phrase factuelle de mise en perspective sur l’impact du poste dans la structure ou stratégie financière de la collectivité
     (par ex. contribution au financement des investissements, dépendance limitée aux ressources externes, levier d’autofinancement).
   - Adapter le degré de prudence à l’ampleur de l’écart :
     • écart faible → constat affirmé
     • écart marqué → prudence analytique possible
   - Ne jamais invoquer de causes politiques ou conjoncturelles non observables.

   
3. CONTRIBUTION À L'ÉQUILIBRE GLOBAL (Angle spécifique) en une ou deux phrases : 
   - {angle_specifique} mais ne pas donner de chiffres supplémentaires.
   - Indiquer clairement si le poste constitue :
     • un levier,
     • une contrainte,
     • ou un élément neutre.
   - REMARQUE : Si le poste représente moins de 5% du budget total, limiter l’analyse à une phrase factuelle.
   

   """

    prompt = f"""Tu es un analyste financier de la DGFiP (M14/M57).
Tu produis une analyse équivalente à une note DDFIP ou à une analyse transmise au préfet.
Tu n'es PAS un commentateur généraliste.
Tu es soumis à une doctrine comptable STRICTE.

Toute erreur conceptuelle invalide l'analyse.

{contexte}

DONNÉES À ANALYSER :
{donnees}

CONTEXTE FINANCIER GLOBAL DE LA COMMUNE :

Commune: {commune}
Exercice: {exercice}
Population: {population} habitants
Strate démographique: {strate}

ÉQUILIBRES FINANCIERS:
- Résultat de fonctionnement: {resultat_fonct:.0f} k€
- CAF brute: {caf_brute:.0f} k€
- CAF nette: {caf_nette:.0f} k€
- Encours de dette: {encours_dette:.0f} k€
- Dépenses d'équipement: {depenses_equip:.0f} k€
- Fonds de roulement: {fdr_str}

RATIOS CLÉS:
- Taux d'épargne brute: {taux_epargne:.1f}%
- Part des charges de personnel: {part_personnel:.1f}%
- Capacité de désendettement: {cap_desendettement:.1f} années
- Seuil prudentiel de capacité de désendettement: 12 ans

{consignes_analyse}

STYLE ET RIGUEUR :
- Ton neutre, institutionnel, factuel et analytique ("technocratique" au sens noble : précis et rigoureux).
- Utiliser le conditionnel uniquement pour toute interprétation non explicitement portée par les chiffres.
- Prioriser l’affirmation lorsque les constats sont objectivement établis.
- Éviter les répétitions inutiles entre postes : si l’écart est négligeable (<5%), le mentionner très brièvement.
- Aucun commentaire politique, conjoncturel ou recommandation.
- Pas de jugement de gestion.
- Vocabulaire strictement M14/M57, phrases concises et précises, sans effet de style ni jargon excessif.


INTERDICTIONS STRICTES :
❌ Ne pas suggérer que la dette finance des charges de fonctionnement
❌ Ne pas expliquer une CAF brute par la fiscalité seule (la CAF brute dépend aussi des charges)
❌ Ne pas utiliser un ton alarmiste
❌ Ne pas recommander d'action
❌ Ne pas juger la gestion
❌ Ne pas écrire "5-6 phrases" ou un nombre de phrases dans les titres
❌ Ne pas utiliser de vocabulaire managérial ou stratégique (“pilotage”, “optimisation”, “levier d’action”)

IMPORTANT :
- Ne jamais inventer de chiffres
- S’appuyer exclusivement sur les données transmises
- Si une donnée manque, ne pas l'évoquer
"""

    return prompt


def generer_donnees_multi_annees(nom_poste, data_json_multi):
    """Génère les données multi-années à injecter dans le prompt"""

    tendances = data_json_multi.get('tendances_globales', {})
    metadata = data_json_multi.get('metadata', {})

    # Mapping des postes vers les clés du JSON multi-années
    mapping = {
        'Analyse_tendances_globales': None,  # Cas spécial
        'Produits_fonctionnement_evolution': 'produits_fonctionnement',
        'Charges_fonctionnement_evolution': 'charges_fonctionnement',
        'Charges_personnel_evolution': 'charges_personnel',
        'CAF_brute_evolution': 'caf_brute',
        'Encours_dette_evolution': 'encours_dette',
        'Depenses_equipement_evolution': 'depenses_equipement'
    }

    # Cas spécial : Analyse tendances globales
    if nom_poste == 'Analyse_tendances_globales':
        # Extraire les ratios financiers
        ratios_financiers = data_json_multi.get('ratios_financiers', {})
        ratios_par_annee = ratios_financiers.get('ratios_par_annee', {})
        evolutions = ratios_financiers.get('evolutions', {})

        # Préparer les données de ratios
        ratios_section = "\n"
        if ratios_par_annee:
            annees = sorted(ratios_par_annee.keys())
            ratios_section += "RATIOS FINANCIERS PAR ANNÉE :\n"
            for annee in annees:
                ratios_annee = ratios_par_annee[annee]
                ratios_section += f"\nAnnée {annee} :\n"
                ratios_section += f"- Part charges personnel : {ratios_annee.get('part_charges_personnel_pct', 'N/A')}%\n"
                ratios_section += f"- Taux d'épargne brute : {ratios_annee.get('taux_epargne_brute_pct', 'N/A')}%\n"
                ratios_section += f"- Capacité de désendettement : {ratios_annee.get('capacite_desendettement_annees', 'N/A')} années\n"
                ratios_section += f"- Ratio d'effort d'équipement : {ratios_annee.get('ratio_effort_equipement_pct', 'N/A')}%\n"

            ratios_section += "\nÉVOLUTIONS DES RATIOS SUR LA PÉRIODE COMPLÈTE :\n"
            for nom_ratio, evo_data in list(evolutions.items())[:6]:
                debut = evo_data.get('valeur_debut', 0)
                fin = evo_data.get('valeur_fin', 0)
                evo_totale = evo_data.get('evolution_totale', 0)
                if 'annees' in nom_ratio:
                    ratios_section += f"- {nom_ratio} : {debut:.1f} → {fin:.1f} ans ({evo_totale:+.1f} ans)\n"
                else:
                    ratios_section += f"- {nom_ratio} : {debut:.1f}% → {fin:.1f}% ({evo_totale:+.1f} pts)\n"

            # Ajouter les évolutions année par année des principaux postes
            ratios_section += "\nÉVOLUTIONS ANNÉE PAR ANNÉE DES POSTES CLÉS :\n"

            # Produits de fonctionnement
            if 'produits_fonctionnement' in tendances:
                evos = tendances['produits_fonctionnement'].get('evolutions_annuelles', {})
                ratios_section += "\nProduits de fonctionnement :\n"
                for periode, evo in sorted(evos.items()):
                    annee_d, annee_f = periode.split('_')
                    ratios_section += f"  {annee_d}→{annee_f} : {evo.get('evolution_k', 0):+.1f} k€ ({evo.get('evolution_pct', 0):+.1f}%)\n"

            # Charges de fonctionnement
            if 'charges_fonctionnement' in tendances:
                evos = tendances['charges_fonctionnement'].get('evolutions_annuelles', {})
                ratios_section += "\nCharges de fonctionnement :\n"
                for periode, evo in sorted(evos.items()):
                    annee_d, annee_f = periode.split('_')
                    ratios_section += f"  {annee_d}→{annee_f} : {evo.get('evolution_k', 0):+.1f} k€ ({evo.get('evolution_pct', 0):+.1f}%)\n"

            # CAF brute
            if 'caf_brute' in tendances:
                evos = tendances['caf_brute'].get('evolutions_annuelles', {})
                ratios_section += "\nCAF brute :\n"
                for periode, evo in sorted(evos.items()):
                    annee_d, annee_f = periode.split('_')
                    ratios_section += f"  {annee_d}→{annee_f} : {evo.get('evolution_k', 0):+.1f} k€ ({evo.get('evolution_pct', 0):+.1f}%)\n"

        donnees = f"""ÉVOLUTION DES GRANDS AGRÉGATS FINANCIERS
Commune : {metadata.get('commune', 'N/A')}
Période : {metadata.get('periode_debut', 'N/A')} - {metadata.get('periode_fin', 'N/A')}
Nombre d'années : {metadata.get('nb_annees', 'N/A')}
Population : {metadata.get('population_debut', 'N/A')} -> {metadata.get('population_fin', 'N/A')} habitants

PRODUITS DE FONCTIONNEMENT :
- Série (k€) : {tendances.get('produits_fonctionnement', {}).get('serie_k', {})}
- Évolution moyenne annuelle : {tendances.get('produits_fonctionnement', {}).get('evolution_moy_annuelle_pct', 'N/A')}%

CHARGES DE FONCTIONNEMENT :
- Série (k€) : {tendances.get('charges_fonctionnement', {}).get('serie_k', {})}
- Évolution moyenne annuelle : {tendances.get('charges_fonctionnement', {}).get('evolution_moy_annuelle_pct', 'N/A')}%

CHARGES DE PERSONNEL :
- Série (k€) : {tendances.get('charges_personnel', {}).get('serie_k', {})}
- Évolution moyenne annuelle : {tendances.get('charges_personnel', {}).get('evolution_moy_annuelle_pct', 'N/A')}%

CAF BRUTE :
- Série (k€) : {tendances.get('caf_brute', {}).get('serie_k', {})}
- Évolution moyenne annuelle : {tendances.get('caf_brute', {}).get('evolution_moy_annuelle_pct', 'N/A')}%

ENCOURS DE DETTE :
- Série (k€) : {tendances.get('encours_dette', {}).get('serie_k', {})}
- Évolution moyenne annuelle : {tendances.get('encours_dette', {}).get('evolution_moy_annuelle_pct', 'N/A')}%

DÉPENSES D'ÉQUIPEMENT :
- Série (k€) : {tendances.get('depenses_equipement', {}).get('serie_k', {})}
- Évolution moyenne annuelle : {tendances.get('depenses_equipement', {}).get('evolution_moy_annuelle_pct', 'N/A')}%

CAPACITÉ DE DÉSENDETTEMENT :
- Série (années) : {tendances.get('capacite_desendettement', {}).get('serie_annees', {})}
{ratios_section}
"""
        return donnees

    # Cas normal : Poste spécifique
    cle_tendance = mapping.get(nom_poste)
    if not cle_tendance or cle_tendance not in tendances:
        return "Données non disponibles"

    donnees_poste = tendances[cle_tendance]
    serie_k = donnees_poste.get('serie_k', {})
    serie_hab = donnees_poste.get('serie_hab', {})
    evo_moy = donnees_poste.get('evolution_moy_annuelle_pct', 'N/A')
    evolutions_annuelles = donnees_poste.get('evolutions_annuelles', {})

    donnees = f"""ÉVOLUTION DU POSTE SUR LA PÉRIODE {metadata.get('periode_debut', 'N/A')}-{metadata.get('periode_fin', 'N/A')}

Série en k€ :
{serie_k}

Série en €/habitant :
{serie_hab}

Évolution moyenne annuelle : {evo_moy}%

ÉVOLUTIONS ANNÉE PAR ANNÉE :
"""

    # Ajouter les évolutions détaillées année par année
    if evolutions_annuelles:
        for periode, evo in sorted(evolutions_annuelles.items()):
            annee_debut, annee_fin = periode.split('_')
            evo_k = evo.get('evolution_k', 'N/A')
            evo_pct = evo.get('evolution_pct', 'N/A')
            evo_hab = evo.get('evolution_hab', 'N/A')

            donnees += f"\n{annee_debut} → {annee_fin} :"
            donnees += f"\n  - Évolution en k€ : {evo_k:+.1f} k€ ({evo_pct:+.1f}%)" if evo_k != 'N/A' else "\n  - Évolution en k€ : N/A"
            donnees += f"\n  - Évolution par habitant : {evo_hab:+.1f} €/hab." if evo_hab != 'N/A' else "\n  - Évolution par habitant : N/A"
    else:
        donnees += "\nAucune donnée d'évolution disponible"

    return donnees


def generer_prompt_multi_annees(nom_poste, donnees, data_json_multi):
    """Génère le prompt enrichi pour l'analyse multi-années"""

    metadata = data_json_multi.get('metadata', {})
    commune = metadata.get('commune', 'N/A')
    periode_debut = metadata.get('periode_debut', 'N/A')
    periode_fin = metadata.get('periode_fin', 'N/A')

    # Mapping des noms de postes vers leurs libellés clairs
    noms_postes_clairs = {
        'Analyse_tendances_globales': 'SYNTHÈSE GLOBALE DE TOUTES LES ÉVOLUTIONS FINANCIÈRES',
        'Produits_fonctionnement_evolution': 'PRODUITS DE FONCTIONNEMENT',
        'Charges_fonctionnement_evolution': 'CHARGES DE FONCTIONNEMENT',
        'Charges_personnel_evolution': 'CHARGES DE PERSONNEL',
        'CAF_brute_evolution': 'CAPACITÉ D\'AUTOFINANCEMENT BRUTE (CAF BRUTE)',
        'Encours_dette_evolution': 'ENCOURS DE LA DETTE',
        'Depenses_equipement_evolution': 'DÉPENSES D\'ÉQUIPEMENT'
    }

    poste_a_analyser = noms_postes_clairs.get(nom_poste, nom_poste.replace('_', ' ').upper())

    # Consignes spécifiques pour l'analyse multi-années
    if nom_poste == 'Analyse_tendances_globales':
        consignes = f"""POSTE À ANALYSER : {poste_a_analyser}

CONSIGNES D’ANALYSE MULTI‑ANNÉES – SYNTHÈSE GLOBALE HYBRIDE (DGFiP/M14-M57) :

Rédiger une synthèse financière globale sur plusieurs exercices, limitée à 400 mots, en mettant en évidence les articulations comptables entre les principaux agrégats financiers.

1. TENDANCES GLOBALES
- Décrire l’évolution des recettes et des dépenses réelles de fonctionnement.
- Mettre en évidence les variations principales (croissance, stabilité, décroissance) et les éventuelles ruptures.
- Décrire l’effet de ces évolutions sur les soldes intermédiaires et le résultat de fonctionnement, uniquement avec les chiffres disponibles.

2. ANALYSE PAR GRANDE MASSE
- Fonctionnement : évolution des produits et charges, impact sur le résultat.
- Autofinancement : trajectoire de la CAF brute et CAF nette, mise en évidence des montants disponibles.
- Investissement : niveau et régularité des dépenses d’équipement, lien avec la CAF nette.
- Endettement : évolution de l’encours et annuités, capacité de désendettement en années par rapport au seuil prudentiel de 12 ans.
- Charges de personnel : mentionner le pourcentage et comparer avec la moyenne de la strate.

3. ARTICULATIONS ET COHÉRENCE
- Montrer comment la CAF nette finance l’investissement et comment la CAF brute couvre le remboursement du capital.
- Décrire la cohérence globale entre fonctionnement, autofinancement, investissement et endettement.


"""
    else:
        consignes = f"""POSTE BUDGÉTAIRE À ANALYSER : {poste_a_analyser}

CONSIGNES D’ANALYSE MULTI-ANNÉES – DGFiP / M14-M57 :

Rédiger une analyse pluriannuelle du poste "{poste_a_analyser}" sur la période {periode_debut} – {periode_fin}, limitée à 150 mots.

1. TRAJECTOIRE DU POSTE
- Décrire l’évolution du poste année par année, en €/habitant.
- Mettre en évidence les variations significatives : croissance, stabilité, décroissance.
- Repérer les ruptures ou inflexions importantes.
- Utiliser exclusivement les chiffres fournis (k€, €/hab, %) pour quantifier les évolutions.
- Comparer si possible avec la moyenne de la strate.

2. FACTEURS D’ÉVOLUTION
- Identifier les éléments structurels ou conjoncturels liés aux données disponibles qui peuvent expliquer l’évolution.
- Vérifier la cohérence avec les autres postes et la situation financière globale.

"""

    prompt = f"""Tu es un analyste financier de la DGFiP (M14/M57).
Tu produis une analyse équivalente à une note DDFIP ou à une analyse transmise au préfet.
Tu n'es PAS un commentateur généraliste.
Tu es soumis à une doctrine comptable STRICTE.

CONTEXTE MULTI-ANNÉES :
Commune : {commune}
Période d'analyse : {periode_debut} - {periode_fin}

DONNÉES À ANALYSER :
{donnees}

{consignes}

STYLE D'ÉCRITURE :
- Ton professionnel, institutionnel, factuel et analytique.
- Utiliser le conditionnel uniquement pour les hypothèses ("pourrait traduire", "traduirait").
- Phrases concises et précises, vocabulaire strictement M14/M57.
- Pas de recommandations ("devrait", "il faut") ni de jugement de gestion ou d’interprétation politique.
- Prioriser les constats chiffrés significatifs et structurants.
- Éviter le jargon excessif.


INTERDICTIONS STRICTES :
❌ Ne pas suggérer que la dette finance des charges de fonctionnement
❌ Ne pas expliquer une CAF brute par la fiscalité seule (la CAF brute dépend aussi des charges)
❌ Ne pas utiliser un ton alarmiste
❌ Ne pas recommander d'action
❌ Ne pas juger la gestion
❌ Ne pas écrire "5-6 phrases" ou un nombre de phrases dans les titres

IMPORTANT :
- Ne pas inventer de chiffres
- S’appuyer exclusivement sur les données transmises
- Ne jamais extrapoler ni évoquer des données absentes
"""

    return prompt


def main():
    print("\n" + "="*80)
    print("GÉNÉRATION DES PROMPTS ENRICHIS DEPUIS LE JSON")
    print("="*80 + "\n")

    # 1. Charger les JSONs
    print("[1/5] Chargement des JSONs...")

    # Charger JSON mono-année
    with open(FICHIER_JSON_MONO, 'r', encoding='utf-8') as f:
        data_json_mono = json.load(f)
    print(f"  [OK] JSON mono-année chargé : {data_json_mono['metadata']['commune']} - {data_json_mono['metadata']['exercice']}")

    # Charger JSON multi-années si disponible
    data_json_multi = None
    if os.path.exists(FICHIER_JSON_MULTI):
        with open(FICHIER_JSON_MULTI, 'r', encoding='utf-8') as f:
            data_json_multi = json.load(f)
        print(f"  [OK] JSON multi-années chargé : {data_json_multi['metadata']['commune']} - Période {data_json_multi['metadata']['periode_debut']}-{data_json_multi['metadata']['periode_fin']}")
    else:
        print(f"  [WARN] JSON multi-années non trouvé : {FICHIER_JSON_MULTI}")

    # 2. Charger l'Excel de base
    print("\n[2/5] Chargement de l'Excel de base...")
    df = pd.read_excel(FICHIER_EXCEL_BASE)
    print(f"  [OK] {len(df)} lignes chargées")

    # 3. Générer les prompts enrichis
    print("\n[3/5] Génération des prompts enrichis...")
    nb_generes = 0

    for idx, row in df.iterrows():
        # Traiter les postes mono-année
        if row['Type_Rapport'] == 'Mono-annee' and row['Nom_Poste'] in MAPPING_POSTES_JSON:
            # Générer les données injectées
            donnees = generer_donnees_injectees(row['Nom_Poste'], data_json_mono)

            # Récupérer le texte personnalisé (priorité : dictionnaire Python > Excel)
            texte_personnalise = TEXTES_PERSONNALISES.get(row['Nom_Poste'], '')

            # Si vide dans le dictionnaire Python, regarder dans l'Excel
            if not texte_personnalise or texte_personnalise.strip() == '':
                texte_excel = row.get('Texte_Positionnement_Personnalise', '')
                if not pd.isna(texte_excel):
                    texte_personnalise = texte_excel

            # Générer le prompt enrichi avec les vraies valeurs
            prompt_enrichi = generer_prompt_enrichi(row['Nom_Poste'], donnees, data_json_mono, texte_personnalise)

            # Mettre à jour l'Excel
            df.at[idx, 'Donnees_Injectees'] = donnees
            df.at[idx, 'Prompt_Complete'] = prompt_enrichi
            # Sauvegarder le texte personnalisé utilisé dans l'Excel pour la génération du PDF
            if texte_personnalise:
                df.at[idx, 'Texte_Positionnement_Personnalise'] = texte_personnalise

            nb_generes += 1
            print(f"  [OK] {row['Nom_Poste']}")

        # Traiter les postes multi-années
        elif row['Type_Rapport'] == 'Multi-annees' and data_json_multi:
            try:
                # Générer les données et prompt pour le multi-années
                donnees = generer_donnees_multi_annees(row['Nom_Poste'], data_json_multi)
                prompt_enrichi = generer_prompt_multi_annees(row['Nom_Poste'], donnees, data_json_multi)

                # Mettre à jour l'Excel
                df.at[idx, 'Donnees_Injectees'] = donnees
                df.at[idx, 'Prompt_Complete'] = prompt_enrichi

                nb_generes += 1
                print(f"  [OK] {row['Nom_Poste']} (multi-années)")
            except Exception as e:
                print(f"  [WARN] {row['Nom_Poste']} (multi-années) : {e}")

    print(f"\n  Total générés : {nb_generes} prompts")

    # 4. Sauvegarder
    print("\n[4/5] Sauvegarde de l'Excel enrichi...")
    df.to_excel(FICHIER_EXCEL_SORTIE, index=False)
    print(f"  [OK] Fichier sauvegardé : {FICHIER_EXCEL_SORTIE}")

    print("\n" + "="*80)
    print("GÉNÉRATION TERMINÉE")
    print("="*80 + "\n")
    print("Prochaines étapes :")
    print("1. Ouvrir l'Excel : PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx")
    print("2. Copier les prompts de la colonne 'Prompt_Complete'")
    print("3. Les envoyer à un LLM (Claude, Mistral, etc.)")
    print("4. Coller les réponses dans la colonne 'Reponse_Attendue'")
    print("5. Sauvegarder et générer le PDF final")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERREUR] : {e}")
        import traceback
        traceback.print_exc()
