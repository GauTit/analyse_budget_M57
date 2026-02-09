"""
Exemples de ratios financiers supplémentaires à implémenter dans le futur

Ces ratios peuvent enrichir l'analyse financière des collectivités territoriales.
Ils ne sont pas encore intégrés mais peuvent être ajoutés au module ratios_financiers.py
"""


# =============================================================================
# RATIOS DE FONCTIONNEMENT
# =============================================================================

def calculer_ratio_dependance_dotations(dgf_k, produits_caf_k):
    """
    Ratio de dépendance aux dotations de l'État
    Ratio : DGF / produits CAF * 100
    Mesure la dépendance aux dotations de l'État
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((dgf_k / produits_caf_k) * 100, 1)


def calculer_ratio_pression_fiscale(impots_locaux_k, population):
    """
    Ratio de pression fiscale locale
    Ratio : impôts locaux / population (en €/hab)
    Mesure la pression fiscale exercée sur les habitants
    """
    if not population or population == 0:
        return None
    return round((impots_locaux_k * 1000) / population, 0)


def calculer_ratio_productivite_personnel(charges_personnel_k, population):
    """
    Ratio de productivité du personnel
    Ratio : charges de personnel / population (en €/hab)
    Mesure le coût moyen du personnel par habitant
    """
    if not population or population == 0:
        return None
    return round((charges_personnel_k * 1000) / population, 0)


def calculer_ratio_charges_gestion(achats_charges_externes_k, produits_caf_k):
    """
    Ratio des charges de gestion
    Ratio : achats et charges externes / produits CAF * 100
    Mesure la part des dépenses de gestion courante
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((achats_charges_externes_k / produits_caf_k) * 100, 1)


# =============================================================================
# RATIOS D'INVESTISSEMENT
# =============================================================================

def calculer_taux_subventionnement_investissement(subventions_recues_k, depenses_equipement_k):
    """
    Taux de subventionnement de l'investissement
    Ratio : subventions reçues / dépenses d'équipement * 100
    Mesure l'effet levier des subventions sur l'investissement
    """
    if not depenses_equipement_k or depenses_equipement_k == 0:
        return None
    return round((subventions_recues_k / depenses_equipement_k) * 100, 1)


def calculer_ratio_investissement_par_habitant(depenses_equipement_k, population):
    """
    Ratio d'investissement par habitant
    Ratio : dépenses d'équipement / population (en €/hab)
    Mesure le niveau d'investissement par habitant
    """
    if not population or population == 0:
        return None
    return round((depenses_equipement_k * 1000) / population, 0)


def calculer_ratio_financement_externe_investissement(emprunts_k, subventions_k, depenses_equipement_k):
    """
    Ratio de financement externe de l'investissement
    Ratio : (emprunts + subventions) / dépenses d'équipement * 100
    Mesure la part des ressources externes dans le financement de l'investissement
    """
    if not depenses_equipement_k or depenses_equipement_k == 0:
        return None
    ressources_externes_k = (emprunts_k or 0) + (subventions_k or 0)
    return round((ressources_externes_k / depenses_equipement_k) * 100, 1)


# =============================================================================
# RATIOS D'ENDETTEMENT
# =============================================================================

def calculer_taux_interet_moyen_dette(charges_financieres_k, encours_dette_k):
    """
    Taux d'intérêt moyen de la dette
    Ratio : charges financières / encours de dette * 100
    Mesure le coût moyen de la dette
    """
    if not encours_dette_k or encours_dette_k == 0:
        return None
    return round((charges_financieres_k / encours_dette_k) * 100, 2)


def calculer_ratio_annuite_dette(annuite_k, produits_caf_k):
    """
    Ratio d'annuité de la dette
    Ratio : annuité (capital + intérêts) / produits CAF * 100
    Mesure le poids du service de la dette sur les recettes
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((annuite_k / produits_caf_k) * 100, 1)


def calculer_duree_moyenne_vie_dette(encours_dette_k, remboursement_capital_annuel_k):
    """
    Durée moyenne de vie de la dette
    Ratio : encours de dette / remboursement de capital annuel moyen (en années)
    Mesure la durée moyenne restante de remboursement de la dette
    """
    if not remboursement_capital_annuel_k or remboursement_capital_annuel_k == 0:
        return None
    return round(encours_dette_k / remboursement_capital_annuel_k, 1)


# =============================================================================
# RATIOS DE TRÉSORERIE ET LIQUIDITÉ
# =============================================================================

def calculer_ratio_liquidite(tresorerie_k, charges_caf_k):
    """
    Ratio de liquidité
    Ratio : trésorerie / charges CAF * 100
    Mesure la capacité à couvrir les dépenses courantes avec la trésorerie disponible
    Si > 20%, la trésorerie est confortable
    """
    if not charges_caf_k or charges_caf_k == 0:
        return None
    return round((tresorerie_k / charges_caf_k) * 100, 1)


def calculer_ratio_fonds_roulement(fdr_k, charges_caf_k):
    """
    Ratio de fonds de roulement
    Ratio : fonds de roulement / charges CAF * 100
    Mesure le niveau de réserves par rapport aux dépenses annuelles
    """
    if not charges_caf_k or charges_caf_k == 0:
        return None
    return round((fdr_k / charges_caf_k) * 100, 1)


# =============================================================================
# RATIOS DE PERFORMANCE
# =============================================================================

def calculer_marge_autofinancement_brute(caf_brute_k, produits_caf_k):
    """
    Marge d'autofinancement brute
    Ratio : CAF brute / produits CAF * 100
    Identique au taux d'épargne brute - mesure la rentabilité du fonctionnement
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((caf_brute_k / produits_caf_k) * 100, 1)


def calculer_ratio_resultat_fonctionnement(resultat_k, produits_caf_k):
    """
    Ratio de résultat de fonctionnement
    Ratio : résultat de fonctionnement / produits CAF * 100
    Mesure la performance d'exploitation
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((resultat_k / produits_caf_k) * 100, 1)


# =============================================================================
# RATIOS INTERCOMMUNAUX (SI DONNÉES DISPONIBLES)
# =============================================================================

def calculer_ratio_reversement_intercommunalite(fiscalite_reversee_k, impots_locaux_k):
    """
    Ratio de reversement à l'intercommunalité
    Ratio : fiscalité reversée / impôts locaux * 100
    Mesure le poids des reversements fiscaux à l'EPCI
    """
    if not impots_locaux_k or impots_locaux_k == 0:
        return None
    return round((fiscalite_reversee_k / impots_locaux_k) * 100, 1)


def calculer_ratio_integration_fiscale(fiscalite_reversee_k, produits_caf_k):
    """
    Ratio d'intégration fiscale
    Ratio : fiscalité reversée / produits CAF * 100
    Mesure le niveau d'intégration intercommunale
    """
    if not produits_caf_k or produits_caf_k == 0:
        return None
    return round((fiscalite_reversee_k / produits_caf_k) * 100, 1)


# =============================================================================
# EXEMPLE D'UTILISATION
# =============================================================================

if __name__ == "__main__":
    print("="*80)
    print("RATIOS FINANCIERS SUPPLÉMENTAIRES - EXEMPLES")
    print("="*80)
    print("\nCe fichier contient des exemples de ratios financiers supplémentaires")
    print("qui peuvent être ajoutés au module ratios_financiers.py")
    print("\nPour les intégrer :")
    print("1. Copier les fonctions nécessaires dans ratios_financiers.py")
    print("2. Les ajouter à la fonction calculer_tous_les_ratios()")
    print("3. Mettre à jour generer_prompts_enrichis_depuis_json.py pour les utiliser")
    print("\nCatégories de ratios disponibles :")
    print("- Ratios de fonctionnement (4 ratios)")
    print("- Ratios d'investissement (3 ratios)")
    print("- Ratios d'endettement (3 ratios)")
    print("- Ratios de trésorerie et liquidité (2 ratios)")
    print("- Ratios de performance (2 ratios)")
    print("- Ratios intercommunaux (2 ratios)")
    print("\nTotal : 16 ratios supplémentaires disponibles")
    print("="*80)
