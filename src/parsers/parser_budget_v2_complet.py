import pdfplumber
import re
from fpdf import FPDF
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# ===============================
# ARCHITECTURE CONFIG-DRIVEN V2
# ===============================

@dataclass
class ChampConfig:
    """Configuration pour extraire un champ du PDF"""
    nom: str
    pattern: str
    cles_sortie: List[str]
    types: List[type]
    traitement_special: Optional[str] = None
    occurrence: int = 0  # 0 = première, 1 = deuxième, -1 = dernière
    flags_regex: int = 0  # Flags pour re.search (ex: re.MULTILINE)

class ConfigurationBudget:
    """Configuration centralisée de tous les champs à extraire"""

    @staticmethod
    def obtenir_configuration() -> List[ChampConfig]:
        """
        Configuration COMPLETE de tous les champs du PDF budget.
        Facile à maintenir : 1 ligne par champ au lieu de 5-10 lignes de code répétitif.
        """
        return [
            # ====== INFORMATIONS GENERALES ======

            ChampConfig(
                nom="Nom de la commune et département",
                pattern=r'([A-Z][A-Z-]+(?:\s+[A-Z][A-Z-]+)*)\s+-\s+([A-Za-zéèê]+)',
                cles_sortie=['commune', 'departement'],
                types=[str, str]
            ),

            ChampConfig(
                nom="Année exercice",
                pattern=r'Exercice\s+(\d{4})',
                cles_sortie=['exercice'],
                types=[int]
            ),

            ChampConfig(
                nom="Population",
                pattern=r'Population l[ée]gale en vigueur au 1er janvier de l\'exercice\s*:\s*(\d{1,3}(?: \d{3})*) +habitants',
                cles_sortie=['population'],
                types=[int]
            ),

            # ====== SECTION FONCTIONNEMENT ======

            ChampConfig(
                nom="Total produits de fonctionnement",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +TOTAL DES PRODUITS DE FONCTIONNEMENT = A',
                cles_sortie=['produits_fonctionnement_k', 'produits_fonctionnement_hab', 'produits_fonctionnement_moy_strate'],
                types=[int, int, int]
            ),

            ChampConfig(
                nom="Produits de fonctionnement CAF",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +PRODUITS\s+DE FONCTIONNEMENT CAF',
                cles_sortie=['produits_fonct_caf_k', 'produits_fonct_caf_hab', 'produits_fonct_caf_moy_strate'],
                types=[int, int, int]
            ),

            ChampConfig(
                nom="Impôts locaux",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +dont : Imp[ôo]ts Locaux\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['impots_locaux_k', 'impots_locaux_hab', 'impots_locaux_moy_strate', 'impots_locaux_ratio', 'impots_locaux_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Fiscalité reversée",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Fiscalit[ée] revers[ée]e par les groupements [àa] fiscalit[ée] propre\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['fiscalite_reversee_k', 'fiscalite_reversee_hab', 'fiscalite_reversee_moy_strate', 'fiscalite_reversee_ratio', 'fiscalite_reversee_ratio_moy'],
                types=[int, int, int, float, float],
                traitement_special='gerer_tiret'
            ),

            ChampConfig(
                nom="Autres impôts et taxes",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Autres imp[ôo]ts et taxes\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['autres_impots_k', 'autres_impots_hab', 'autres_impots_moy_strate', 'autres_impots_ratio', 'autres_impots_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="DGF",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Dotation globale de fonctionnement\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['dgf_k', 'dgf_hab', 'dgf_moy_strate', 'dgf_ratio', 'dgf_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Autres dotations et participations",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Autres dotations et participations\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['autres_dotations_k', 'autres_dotations_hab', 'autres_dotations_moy_strate', 'autres_dotations_ratio', 'autres_dotations_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="FCTVA produits",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +dont : FCTVA\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['fctva_produits_k', 'fctva_produits_hab', 'fctva_produits_moy_strate', 'fctva_produits_ratio', 'fctva_produits_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Produits des services et du domaine",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Produits des services et du domaine\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['produits_services_k', 'produits_services_hab', 'produits_services_moy_strate', 'produits_services_ratio', 'produits_services_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Total charges de fonctionnement",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +TOTAL DES CHARGES DE FONCTIONNEMENT = B',
                cles_sortie=['charges_fonctionnement_k', 'charges_fonctionnement_hab', 'charges_fonctionnement_moy_strate'],
                types=[int, int, int]
            ),

            ChampConfig(
                nom="Charges de fonctionnement CAF",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +CHARGES DE FONCTIONNEMENT CAF',
                cles_sortie=['charges_fonct_caf_k', 'charges_fonct_caf_hab', 'charges_fonct_caf_moy_strate'],
                types=[int, int, int]
            ),

            ChampConfig(
                nom="Charges de personnel",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +dont : Charges de personnel\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['charges_personnel_k', 'charges_personnel_hab', 'charges_personnel_moy_strate', 'charges_personnel_ratio', 'charges_personnel_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Achats et charges externes",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Achats et charges externes\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['achats_charges_ext_k', 'achats_charges_ext_hab', 'achats_charges_ext_moy_strate', 'achats_charges_ext_ratio', 'achats_charges_ext_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Charges financières",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Charges financi[èe]res\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['charges_financieres_k', 'charges_financieres_hab', 'charges_financieres_moy_strate', 'charges_financieres_ratio', 'charges_financieres_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Contingents",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Contingents\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['contingents_k', 'contingents_hab', 'contingents_moy_strate', 'contingents_ratio', 'contingents_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Subventions versées",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Subventions vers[ée]es\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['subventions_versees_k', 'subventions_versees_hab', 'subventions_versees_moy_strate', 'subventions_versees_ratio', 'subventions_versees_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Résultat comptable",
                pattern=r'(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +RESULTAT COMPTABLE = A - B = R',
                cles_sortie=['resultat_fonctionnement_k', 'resultat_fonctionnement_hab', 'resultat_fonctionnement_moy_strate'],
                types=[int, int, int]
            ),

            # ====== SECTION INVESTISSEMENT ======

            ChampConfig(
                nom="Total ressources d'investissement",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +TOTAL DES RESSOURCES D\'INVESTISSEMENT = C',
                cles_sortie=['ressources_investissement_k', 'ressources_investissement_hab', 'ressources_investissement_moy_strate'],
                types=[int, int, int]
            ),

            ChampConfig(
                nom="Emprunts bancaires",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +dont : Emprunts bancaires et dettes assimil[ée]es\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['emprunts_k', 'emprunts_hab', 'emprunts_moy_strate', 'emprunts_ratio', 'emprunts_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Subventions reçues",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Subventions re[çc]ues\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['subventions_recues_k', 'subventions_recues_hab', 'subventions_recues_moy_strate', 'subventions_recues_ratio', 'subventions_recues_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Taxe d'aménagement",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe d\'am[ée]nagement\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['taxe_amenagement_k', 'taxe_amenagement_hab', 'taxe_amenagement_moy_strate', 'taxe_amenagement_ratio', 'taxe_amenagement_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="FCTVA investissement",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +FCTVA\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['fctva_invest_k', 'fctva_invest_hab', 'fctva_invest_moy_strate', 'fctva_invest_ratio', 'fctva_invest_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Retour de biens affectés",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Retour de biens affect[ée]s, conc[ée]d[ée]s,?\s*(?:vendus|\.\.\.)?\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['retour_biens_k', 'retour_biens_hab', 'retour_biens_moy_strate', 'retour_biens_ratio', 'retour_biens_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Total emplois d'investissement",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +TOTAL DES EMPLOIS D\'INVESTISSEMENT = D',
                cles_sortie=['emplois_investissement_k', 'emplois_investissement_hab', 'emplois_investissement_moy_strate'],
                types=[int, int, int]
            ),

            ChampConfig(
                nom="Dépenses d'équipement",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +dont : D[ée]penses d\'[ée]quipement\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['depenses_equipement_k', 'depenses_equipement_hab', 'depenses_equipement_moy_strate', 'depenses_equipement_ratio', 'depenses_equipement_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Remboursement d'emprunts",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Remboursement d\'emprunts et dettes assimil[ée]es\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['remboursement_emprunts_k', 'remboursement_emprunts_hab', 'remboursement_emprunts_moy_strate', 'remboursement_emprunts_ratio', 'remboursement_emprunts_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Charges à répartir",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Charges [àa] r[ée]partir\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['charges_a_repartir_k', 'charges_a_repartir_hab', 'charges_a_repartir_moy_strate', 'charges_a_repartir_ratio', 'charges_a_repartir_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Immobilisations affectées",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Immobilisations affect[ée]es, conc[ée]d[ée]es,?\s*(?:vendues|\.\.\.)?\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['immobilisations_affectees_k', 'immobilisations_affectees_hab', 'immobilisations_affectees_moy_strate', 'immobilisations_affectees_ratio', 'immobilisations_affectees_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Besoin financement résiduel",
                pattern=r'(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +Besoin ou capacit[ée] de financement r[ée]siduel de la section d\'investissement = D - C',
                cles_sortie=['besoin_financement_residuel_k', 'besoin_financement_residuel_hab', 'besoin_financement_residuel_moy_strate'],
                types=[int, int, int]
            ),

            ChampConfig(
                nom="Solde opérations tiers",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +\+\s+Solde des op[ée]rations pour le compte de tiers',
                cles_sortie=['solde_operations_tiers_k', 'solde_operations_tiers_hab', 'solde_operations_tiers_moy_strate'],
                types=[int, int, int]
            ),

            ChampConfig(
                nom="Besoin financement total",
                pattern=r'(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +=\s+Besoin ou capacit[ée] de financement de la section d\'investissement = E',
                cles_sortie=['besoin_financement_total_k', 'besoin_financement_total_hab', 'besoin_financement_total_moy_strate'],
                types=[int, int, int]
            ),

            ChampConfig(
                nom="Résultat d'ensemble",
                pattern=r'(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +R[ée]sultat d\'ensemble = R - E',
                cles_sortie=['resultat_ensemble_k', 'resultat_ensemble_hab', 'resultat_ensemble_moy_strate'],
                types=[int, int, int]
            ),

            # ====== SECTION AUTOFINANCEMENT ======

            ChampConfig(
                nom="EBF",
                pattern=r'(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +Exc[ée]dent brut de fonctionnement\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['ebf_k', 'ebf_hab', 'ebf_moy_strate', 'ebf_ratio', 'ebf_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="CAF brute",
                pattern=r'(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +Capacit[ée] d\'autofinancement = CAF\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['caf_brute_k', 'caf_brute_hab', 'caf_brute_moy_strate', 'caf_brute_ratio', 'caf_brute_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="CAF nette",
                pattern=r'(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +CAF nette du remboursement.*?([\d,]+)\s+([\d,]+)',
                cles_sortie=['caf_nette_k', 'caf_nette_hab', 'caf_nette_moy_strate', 'caf_nette_ratio', 'caf_nette_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            # ====== SECTION ENDETTEMENT ======

            ChampConfig(
                nom="Encours total dette",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Encours total de la dette au 31 d[ée]cembre N\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['dette_totale_k', 'dette_totale_hab', 'dette_totale_moy_strate', 'dette_totale_ratio', 'dette_totale_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Encours dettes bancaires",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Encours des dettes bancaires et assimil[ée]es\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['dette_bancaire_k', 'dette_bancaire_hab', 'dette_bancaire_moy_strate', 'dette_bancaire_ratio', 'dette_bancaire_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Encours dettes bancaires net fonds",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Encours des dettes bancaires net de l\'aide du fonds de soutien pour la sortie des emprunts\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['dette_bancaire_net_fonds_k', 'dette_bancaire_net_fonds_hab', 'dette_bancaire_net_fonds_moy_strate', 'dette_bancaire_net_fonds_ratio', 'dette_bancaire_net_fonds_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Annuité de la dette",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Annuit[ée] de la dette\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['annuite_dette_k', 'annuite_dette_hab', 'annuite_dette_moy_strate', 'annuite_dette_ratio', 'annuite_dette_ratio_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Fonds de roulement",
                pattern=r'(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +(-?\d{1,3}(?: \d{3})*) +FONDS DE ROULEMENT',
                cles_sortie=['fonds_roulement_k', 'fonds_roulement_hab', 'fonds_roulement_moy_strate'],
                types=[int, int, int]
            ),

            # ====== SECTION FISCALITE DIRECTE LOCALE - BASES ======

            ChampConfig(
                nom="Base TH secondaires",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe d\'habitation \(r[ée]sidences secondaires et logements vacants\)\s+(\d+|-)\s*$',
                cles_sortie=['base_th_secondaires_k', 'base_th_secondaires_hab', 'base_th_secondaires_moy_strate', 'base_th_secondaires_info'],
                types=[int, int, int, int],
                traitement_special='gerer_tiret',
                flags_regex=re.MULTILINE
            ),

            ChampConfig(
                nom="Base TFPB",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe fonci[èe]re sur les propri[ée]t[ée]s b[âa]ties\s+(\d+|-)\s+(\d+|-)\s+(\d+|-)',
                cles_sortie=['base_tfpb_k', 'base_tfpb_hab', 'base_tfpb_moy_strate', 'base_tfpb_reduite_k', 'base_tfpb_reduite_hab', 'base_tfpb_reduite_moy_strate'],
                types=[int, int, int, int, int, int],
                traitement_special='gerer_tiret'
            ),

            ChampConfig(
                nom="Base TFPNB",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe fonci[èe]re sur les propri[ée]t[ée]s non b[âa]ties\s+(\d+|-)\s+(\d+|-)\s+(\d+|-)',
                cles_sortie=['base_tfpnb_k', 'base_tfpnb_hab', 'base_tfpnb_moy_strate', 'base_tfpnb_reduite_k', 'base_tfpnb_reduite_hab', 'base_tfpnb_reduite_moy_strate'],
                types=[int, int, int, int, int, int],
                traitement_special='gerer_tiret'
            ),

            ChampConfig(
                nom="Base Taxe additionnelle TFPNB",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe additionnelle [àa] la taxe fonci[èe]re sur les propri[ée]t[ée]s non b[âa]ties\s+([\d,]+|-)\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['base_ta_tfpnb_k', 'base_ta_tfpnb_hab', 'base_ta_tfpnb_moy_strate', 'base_ta_tfpnb_val1', 'base_ta_tfpnb_val2', 'base_ta_tfpnb_val3'],
                types=[int, int, int, float, float, float],
                traitement_special='gerer_tiret',
                occurrence=0
            ),

            ChampConfig(
                nom="Base CFE",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Cotisation fonci[èe]re des entreprises\s+(\d+|-)\s+(\d+|-)\s+(\d+|-)',
                cles_sortie=['base_cfe_k', 'base_cfe_hab', 'base_cfe_moy_strate', 'base_cfe_reduite_k', 'base_cfe_reduite_hab', 'base_cfe_reduite_moy_strate'],
                types=[int, int, int, int, int, int],
                traitement_special='gerer_tiret'
            ),

            # ====== SECTION FISCALITE DIRECTE LOCALE - TAUX/PRODUITS ======

            ChampConfig(
                nom="Produit TH secondaires",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe d\'habitation \(r[ée]sidences secondaires[^)]+\)\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['produit_th_secondaires_k', 'produit_th_secondaires_hab', 'produit_th_secondaires_moy_strate', 'produit_th_secondaires_taux_secondaires', 'produit_th_secondaires_taux_moy'],
                types=[int, int, int, float, float],
                occurrence=1  # 2ème occurrence
            ),

            ChampConfig(
                nom="Produit TFPB avant coefficient",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe fonci[èe]re sur les propri[ée]t[ée]s b[âa]ties \(avant application du coefficient correcteur\)\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['produit_tfpb_avant_k', 'produit_tfpb_avant_hab', 'produit_tfpb_avant_moy_strate', 'produit_tfpb_taux', 'produit_tfpb_taux_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Effet coefficient correcteur TFPB",
                pattern=r'Effet du coefficient correcteur\s*:?\s*\n?\s*(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['effet_coeff_tfpb_k', 'effet_coeff_tfpb_hab', 'effet_coeff_tfpb_moy_strate', 'effet_coeff_tfpb_taux_vote', 'effet_coeff_tfpb_taux_moy_strate'],
                types=[int, int, int, float, float],
                traitement_special='gerer_tiret'
            ),

            ChampConfig(
                nom="Produit TFPB après coefficient",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe fonci[èe]re sur les propri[ée]t[ée]s b[âa]ties \(apr[èe]s application du coefficient correcteur\)\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['produit_tfpb_apres_k', 'produit_tfpb_apres_hab', 'produit_tfpb_apres_moy_strate', 'produit_tfpb_apres_taux_vote', 'produit_tfpb_apres_taux_moy_strate'],
                types=[int, int, int, float, float],
                traitement_special='gerer_tiret'
            ),

            ChampConfig(
                nom="Allocation compensatrice foncier bâti",
                pattern=r'Allocation compensatrice de foncier b[âa]ti - r[ée]duction 50% valeur locative des.*?\n\s*(\d+)\s+(\d+)\s+(\d+)\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['alloc_comp_tfpb_k', 'alloc_comp_tfpb_hab', 'alloc_comp_tfpb_moy_strate', 'alloc_comp_tfpb_taux_vote', 'alloc_comp_tfpb_taux_moy_strate'],
                types=[int, int, int, float, float],
                traitement_special='gerer_tiret'
            ),

            ChampConfig(
                nom="Produit TFPNB",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe fonci[èe]re sur les propri[ée]t[ée]s non b[âa]ties\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['produit_tfpnb_k', 'produit_tfpnb_hab', 'produit_tfpnb_moy_strate', 'produit_taux_tfpnb', 'produit_taux_tfpnb_moy'],
                types=[int, int, int, float, float],
                occurrence=-1  # Dernière occurrence
            ),

            ChampConfig(
                nom="Produit Taxe additionnelle TFPNB",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe additionnelle [àa] la taxe fonci[èe]re sur les propri[ée]t[ée]s non b[âa]ties\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['produit_ta_tfpnb_k', 'produit_ta_tfpnb_hab', 'produit_ta_tfpnb_moy_strate', 'produit_ta_tfpnb_taux', 'produit_ta_tfpnb_taux_moy'],
                types=[int, int, int, float, float],
                traitement_special='gerer_tiret',
                occurrence=1  # 2ème occurrence
            ),

            ChampConfig(
                nom="Produit CFE",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Cotisation fonci[èe]re des entreprises\s+([\d,]+)\s+([\d,]+)',
                cles_sortie=['produit_cfe_k', 'produit_cfe_hab', 'produit_cfe_moy_strate', 'produit_cfe_taux', 'produit_cfe_taux_moy'],
                types=[int, int, int, float, float]
            ),

            ChampConfig(
                nom="Allocation compensatrice CFE",
                pattern=r'Allocation compensatrice de cotisation fonci[èe]re des entreprises - r[ée]duction de 50%.*?\n\s*(\d+)\s+(\d+)\s+(\d+)\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['alloc_comp_cfe_k', 'alloc_comp_cfe_hab', 'alloc_comp_cfe_moy_strate', 'alloc_comp_cfe_taux_vote', 'alloc_comp_cfe_taux_moy_strate'],
                types=[int, int, int, float, float],
                traitement_special='gerer_tiret'
            ),

            # ====== IMPOTS DE REPARTITION ======

            ChampConfig(
                nom="IFER",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Imposition forfaitaire sur les entreprises de r[ée]seau\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['ifer_k', 'ifer_hab', 'ifer_moy_strate', 'ifer_taux_vote', 'ifer_taux_moy_strate'],
                types=[int, int, int, float, float],
                traitement_special='gerer_tiret'
            ),

            ChampConfig(
                nom="TASCOM",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Taxe sur les surfaces commerciales\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['tascom_k', 'tascom_hab', 'tascom_moy_strate', 'tascom_taux_vote', 'tascom_taux_moy_strate'],
                types=[int, int, int, float, float],
                traitement_special='gerer_tiret'
            ),

            ChampConfig(
                nom="Fractions de TVA",
                pattern=r'(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +(\d{1,3}(?: \d{3})*) +Fractions de TVA \(montant net N\)\s+([\d,]+|-)\s+([\d,]+|-)',
                cles_sortie=['tva_k', 'tva_hab', 'tva_moy_strate', 'tva_taux_vote', 'tva_taux_moy_strate'],
                types=[int, int, int, float, float],
                traitement_special='gerer_tiret'
            ),
        ]


class ParserBudget:
    """Parser de budget configurable et maintenable - Version 2 COMPLETE"""

    def __init__(self):
        self.config = ConfigurationBudget.obtenir_configuration()

    def extraire_texte_pdf(self, fichier_pdf: str) -> str:
        """Extrait le texte complet du PDF"""
        texte_complet = []
        with pdfplumber.open(fichier_pdf) as pdf:
            for page in pdf.pages:
                texte = page.extract_text()
                if texte:
                    texte_complet.append(texte)
        return '\n'.join(texte_complet)

    def _convertir_valeur(self, valeur: str, type_cible: type, gerer_tiret: bool = False) -> Any:
        """Convertit une valeur extraite dans le type approprié"""
        # Gérer les tirets
        if gerer_tiret and valeur.strip() == '-':
            return None

        # Nettoyage
        valeur_nettoyee = valeur.replace(' ', '').replace(',', '.')

        # Conversion
        try:
            if type_cible == int:
                return int(valeur_nettoyee)
            elif type_cible == float:
                return float(valeur_nettoyee)
            else:
                return valeur_nettoyee
        except ValueError:
            logger.warning(f"Impossible de convertir '{valeur}' en {type_cible.__name__}")
            return None

    def extraire_champ(self, texte: str, config: ChampConfig) -> Dict[str, Any]:
        """Extrait un champ selon sa configuration"""
        resultat = {}

        try:
            # Recherche du pattern
            if config.occurrence != 0:
                # Plusieurs occurrences possibles
                matches = re.findall(config.pattern, texte, flags=config.flags_regex)
                if not matches:
                    logger.warning(f"❌ '{config.nom}' : pattern non trouvé")
                    return resultat

                # Sélectionner l'occurrence souhaitée
                if config.occurrence == -1:
                    match = matches[-1]  # Dernière
                elif config.occurrence < len(matches):
                    match = matches[config.occurrence]
                else:
                    logger.warning(f"❌ '{config.nom}' : occurrence {config.occurrence} non trouvée (trouvé {len(matches)} occurrences)")
                    return resultat

                groupes = match if isinstance(match, tuple) else (match,)
            else:
                # Première occurrence
                match_obj = re.search(config.pattern, texte, flags=config.flags_regex)
                if not match_obj:
                    logger.warning(f"❌ '{config.nom}' : pattern non trouvé")
                    return resultat
                groupes = match_obj.groups()

            # Conversion des valeurs
            gerer_tiret = config.traitement_special == 'gerer_tiret'

            for i, (cle, type_val) in enumerate(zip(config.cles_sortie, config.types)):
                if i < len(groupes):
                    valeur_brute = groupes[i]
                    resultat[cle] = self._convertir_valeur(valeur_brute, type_val, gerer_tiret)

            logger.info(f"✅ '{config.nom}' : {len(resultat)} valeurs extraites")

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction de '{config.nom}' : {e}")

        return resultat

    def parser_bilan_pdf(self, fichier_pdf: str) -> Dict[str, Any]:
        """
        Parse le PDF et extrait toutes les données selon la configuration
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"📄 DEBUT DU PARSING DE {fichier_pdf}")
        logger.info(f"{'='*60}\n")

        # Extraction du texte
        texte = self.extraire_texte_pdf(fichier_pdf)

        # Extraction de tous les champs
        budget = {}
        champs_ok = 0
        champs_ko = 0

        for config_champ in self.config:
            donnees = self.extraire_champ(texte, config_champ)
            budget.update(donnees)

            if donnees:
                champs_ok += 1
            else:
                champs_ko += 1

        logger.info(f"\n{'='*60}")
        logger.info(f"📊 RESUME : {champs_ok} champs OK ✅, {champs_ko} champs KO ❌")
        logger.info(f"📦 TOTAL : {len(budget)} valeurs extraites")
        logger.info(f"{'='*60}\n")

        return budget

    def valider_budget(self, budget: Dict[str, Any]) -> bool:
        """Valide la cohérence des données extraites"""
        logger.info(f"\n{'='*60}")
        logger.info("VALIDATION DES DONNEES")
        logger.info(f"{'='*60}\n")

        tests_ok = True

        # Test 1: CAF brute >= CAF nette
        if 'caf_brute_k' in budget and 'caf_nette_k' in budget:
            if budget['caf_brute_k'] >= budget['caf_nette_k']:
                logger.info("✅ Test 1 : CAF brute >= CAF nette")
            else:
                logger.error("❌ Test 1 : CAF brute < CAF nette")
                tests_ok = False
        else:
            logger.warning("⚠️  Test 1 : Données CAF manquantes")

        # Test 2: Résultat = Produits - Charges
        if all(k in budget for k in ['resultat_fonctionnement_k', 'produits_fonctionnement_k', 'charges_fonctionnement_k']):
            resultat_calcule = budget['produits_fonctionnement_k'] - budget['charges_fonctionnement_k']
            if abs(resultat_calcule - budget['resultat_fonctionnement_k']) <= 1:
                logger.info(f"✅ Test 2 : Résultat cohérent ({resultat_calcule} = {budget['resultat_fonctionnement_k']})")
            else:
                logger.error(f"❌ Test 2 : Résultat incohérent ({resultat_calcule} != {budget['resultat_fonctionnement_k']})")
                tests_ok = False
        else:
            logger.warning("⚠️  Test 2 : Données résultat manquantes")

        # Test 3: Valeurs positives (sauf résultat, besoin, caf, ebf, fonds_roulement et effet coefficient)
        valeurs_negatives = []
        for cle, valeur in budget.items():
            if valeur is not None and isinstance(valeur, (int, float)):
                if ('resultat' not in cle and 'besoin' not in cle and 'caf' not in cle and
                    'ebf' not in cle and 'fonds_roulement' not in cle and 'effet_coeff' not in cle and valeur < 0):
                    valeurs_negatives.append(f"{cle}: {valeur}")

        if valeurs_negatives:
            logger.error(f"❌ Test 3 : Valeurs négatives trouvées : {', '.join(valeurs_negatives)}")
            tests_ok = False
        else:
            logger.info("✅ Test 3 : Toutes les valeurs sont positives (hors résultats/financement)")

        logger.info(f"\n{'='*60}")
        if tests_ok:
            logger.info("✅ TOUS LES TESTS DE VALIDATION SONT PASSES")
        else:
            logger.error("❌ CERTAINS TESTS ONT ECHOUE")
        logger.info(f"{'='*60}\n")

        return tests_ok

    def generer_rapport_pdf(self, budget: Dict[str, Any], nom_fichier: str = "rapport_v2.pdf"):
        """Génère un rapport PDF à partir des données extraites"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Titre
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(0, 10, "RAPPORT D'ANALYSE BUDGETAIRE - V2", ln=True, align='C')
        pdf.ln(5)

        # Date
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", ln=True, align='C')
        pdf.ln(10)

        # Données extraites
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(0, 10, "DONNEES EXTRAITES", ln=True)
        pdf.ln(5)
        pdf.set_font("Courier", size=9)

        for cle, valeur in sorted(budget.items()):
            pdf.cell(0, 6, f"{cle}: {valeur}", ln=True)

        # Sauvegarder
        pdf.output(nom_fichier)
        logger.info(f"✅ Rapport PDF généré : {nom_fichier}")


# ===============================
# EXECUTION PRINCIPALE
# ===============================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("PARSER BUDGET V2 - ARCHITECTURE CONFIG-DRIVEN")
    print("="*60 + "\n")

    # Créer le parser
    parser = ParserBudget()

    # Parser le PDF
    budget = parser.parser_bilan_pdf('docs/bilan.pdf')

    # Validation
    parser.valider_budget(budget)

    # Génération du rapport PDF
    parser.generer_rapport_pdf(budget)

    # Affichage des données (optionnel)
    print("\n" + "="*60)
    print("DONNEES EXTRAITES (triées)")
    print("="*60)
    for cle, valeur in sorted(budget.items()):
        print(f"{cle}: {valeur}")

    print("\n✅ TRAITEMENT TERMINE AVEC SUCCES\n")
