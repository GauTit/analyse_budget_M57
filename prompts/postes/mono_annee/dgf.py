"""
Poste budgétaire : Dotation Globale de Fonctionnement (DGF)
Type : Mono-année
"""

from prompts import regles_globales

# ============================================
# CONTEXTE ESSENTIEL DU POSTE
# ============================================

CONTEXTE_ESSENTIEL = """L'ESSENTIEL DU POSTE :
La dotation globale de fonctionnement (DGF) est le principal concours financier de l'État. C'est une recette de fonctionnement libre d'emploi (non affectée).

COMPOSITION DOCTRINALE :
- La Dotation forfaitaire : part historique liée à la population et à la superficie.
- Les Dotations de péréquation : visant à corriger les disparités de ressources. Elles incluent :
  • La DSR (Solidarité Rurale) pour les communes rurales éligibles.
  • La DSU (Solidarité Urbaine) pour les communes urbaines.
  • La DNP (Dotation Nationale de Péréquation) pour compenser les écarts de potentiel fiscal.

LOGIQUE D'ANALYSE :
La DGF est inversement proportionnelle à la richesse de la collectivité (mesurée par le potentiel financier). Une baisse de la dotation forfaitaire peut traduire une augmentation du potentiel fiscal de la commune (phénomène d'écrêtement de la dotation forfaitaire). Cette baisse peut toutefois être compensée par une hausse des dotations de péréquation (DSR, DSU, DNP) si la commune reste éligible, de sorte que l'évolution de la DGF globale doit s'analyser composante par composante."""

# ============================================
# TEXTE PERSONNALISÉ (PHRASE D'INSPIRATION)
# ============================================

TEXTE_PERSONNALISE = "La dotation globale de fonctionnement (DGF) constitue le concours financier principal de l'Etat aux collectivités locales."

# ============================================
# CONFIGURATION DU POSTE
# ============================================

CHEMIN_JSON = "fonctionnement.produits.dgf"
NOM_POSTE = "DGF"
TYPE_RAPPORT = "Mono-annee"

# Inclure le contexte financier global complet ?
# - True : Inclut CAF brute, encours dette, ratios clés (+ de tokens)
# - False : Inclut uniquement commune, exercice, population, strate (économie de tokens)
INCLURE_CONTEXTE_FINANCIER = False

# ============================================
# ANGLE SPÉCIFIQUE D'ANALYSE
# ============================================

ANGLE_SPECIFIQUE = "Situer le montant de la dotation globale de fonctionnement par habitant au regard de la strate et évaluer le poids de la DGF dans les recettes réelles de fonctionnement."


# ============================================
# FONCTION DE GÉNÉRATION DU PROMPT
# ============================================

def extraire_donnees(data_json):
    """
    Extrait les données du poste depuis le JSON

    Args:
        data_json: JSON complet des données enrichies

    Returns:
        dict: Données du poste formatées
    """
    # Naviguer dans le JSON pour extraire les données du poste
    keys = CHEMIN_JSON.split('.')
    poste_data = data_json
    for key in keys:
        poste_data = poste_data.get(key, {})

    return poste_data


def formater_donnees(poste_data, data_json=None):
    """
    Formate les données du poste pour l'injection dans le prompt

    Args:
        poste_data: Données brutes du poste
        data_json: JSON complet (non utilisé pour ce poste, mais nécessaire pour la compatibilité)

    Returns:
        str: Données formatées prêtes à injecter
    """
    if not poste_data or not isinstance(poste_data, dict):
        return "Données non disponibles"

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
- Écart avec la strate : {ecart_pct:+.1f}% ({niveau})
"""

    # Ajouter les ratios de structure si disponibles
    if 'pct_produits_caf' in poste_data:
        pct_commune = poste_data.get('pct_produits_caf')
        pct_strate = poste_data.get('pct_produits_caf_strate')

        if pct_commune is not None and pct_strate is not None:
            donnees += f"\nPOIDS DANS LA STRUCTURE :\n"
            donnees += f"- Part dans les recettes réelles de fonctionnement : {pct_commune:.1f}% (commune) vs {pct_strate:.1f}% (strate)\n"

    return donnees


def generer_consignes_analyse(texte_personnalise=""):
    """
    Génère les consignes d'analyse spécifiques au poste

    Args:
        texte_personnalise: Phrase d'inspiration pour la section 1 (optionnel)

    Returns:
        str: Consignes d'analyse formatées
    """
    # Section 1 avec phrase d'inspiration si fournie
    if texte_personnalise and texte_personnalise.strip():
        section_1 = f"""
1. POSITIONNEMENT ET POIDS DU POSTE en une phrase :

   PHRASE D'INSPIRATION (à utiliser comme guide pour la rédaction) :
   "{texte_personnalise.strip()}"

   → S'inspirer de cette phrase tout en l'adaptant au contexte financier.
   → Conserver le ton institutionnel et factuel.

2. ANALYSE COMPARATIVE ET DIAGNOSTIC DES ÉCARTS (1 phrase + possibilité d'une 2e phrase factuelle)"""
    else:
        section_1 = """
1. POSITIONNEMENT ET POIDS DU POSTE en une phrase :
   - Situer le poste dans la structure budgétaire de la commune
     (poste majeur, poste secondaire, charge structurelle, ressource principale, etc.).

2. ANALYSE COMPARATIVE ET DIAGNOSTIC DES ÉCARTS (1 phrase + possibilité d'une 2e phrase factuelle)"""

    return f"""CONSIGNES D'ANALYSE :

Rédige une note d'analyse financière experte, synthétique et doctrinalement conforme M57.

Adopte le ton d'un analyste DGFiP : factuel, hiérarchisé, sans effet de style, sans commentaire politique.

Structure impérative :

{section_1}
   - Citer obligatoirement : montant en k€, valeur en €/habitant et écart en % par rapport à la strate
     (utiliser strictement l'écart fourni, sans recalcul).
   - Qualifier l'écart avec un vocabulaire varié et institutionnel
     (niveau supérieur / inférieur à la strate, écart significatif, positionnement atypique, alignement).
   - Ajouter, le cas échéant, une phrase factuelle de mise en perspective sur l'impact du poste
     dans la structure financière de la collectivité
     (par ex. contribution à la formation de l'épargne, poids dans les recettes réelles, incidence sur la solvabilité).
   - Adapter le degré de prudence à l'ampleur de l'écart :
     • écart faible (< 10%) → constat affirmé
     • écart marqué (> 20%) → prudence analytique, conditionnel admis
   - Ne jamais invoquer de causes politiques ou conjoncturelles non observables dans les données.

3. CONTRIBUTION À L'ÉQUILIBRE GLOBAL (Angle spécifique) en une ou deux phrases :
   - {ANGLE_SPECIFIQUE}
   - Ne pas introduire de chiffres supplémentaires non fournis dans les données.
   - Indiquer clairement si le poste constitue :
     • un facteur favorable à l'équilibre,
     • une contrainte sur l'équilibre,
     • un point de vigilance (si les signaux sont mixtes),
     • ou un élément neutre.
   - La qualification de la section 3 DOIT ÊTRE COHÉRENTE avec le diagnostic de la section 2.
     Un poste dont l'écart avec la strate est défavorable ne peut pas être qualifié de "facteur favorable"
     sans explication explicite.
   - REMARQUE : Si le poste représente moins de 5% du budget total, limiter l'analyse à une phrase factuelle.
   INTERDICTION : Ne pas qualifier l'évolution temporelle (stable, en hausse, en baisse) sans données de l'exercice précédent.
"""


def generer_prompt(data_json, texte_personnalise=None):
    """
    Génère le prompt complet pour le poste DGF

    Args:
        data_json: JSON complet des données enrichies
        texte_personnalise: Texte d'inspiration personnalisé (optionnel)

    Returns:
        str: Prompt complet prêt à envoyer au LLM
    """
    # Utiliser le texte personnalisé par défaut si non fourni
    if texte_personnalise is None:
        texte_personnalise = TEXTE_PERSONNALISE

    # Extraire les métadonnées
    metadata = data_json.get('metadata', {})
    commune = metadata.get('commune', 'N/A')
    exercice = metadata.get('exercice', 'N/A')
    population = metadata.get('population', 'N/A')
    strate = metadata.get('strate', {}).get('libelle', 'N/A')

    # Extraire les agrégats financiers pour le contexte global
    def extraire_valeur(chemin):
        keys = chemin.split('.')
        valeur = data_json
        for key in keys:
            valeur = valeur.get(key, {})
        return valeur.get('montant_k', 0) if isinstance(valeur, dict) else 0

    resultat_fonct = extraire_valeur('fonctionnement.resultat')
    caf_brute = extraire_valeur('autofinancement.caf_brute')
    caf_nette = extraire_valeur('autofinancement.caf_nette')
    encours_dette = extraire_valeur('endettement.encours_total')
    depenses_equip = extraire_valeur('investissement.emplois.depenses_equipement')

    # Fonds de roulement
    fdr_data = data_json.get('endettement', {}).get('fonds_roulement', {})
    fdr_montant = fdr_data.get('montant_k', 0)
    fdr_str = f"{fdr_montant:.0f} k€" if fdr_montant >= 0 else f"{fdr_montant:.0f} k€ (négatif)"

    # Ratios clés
    ratios = data_json.get('ratios_financiers', {})
    taux_epargne = ratios.get('taux_epargne_brute_pct', 0)
    part_personnel = ratios.get('part_charges_personnel_pct', 0)
    cap_desendettement = ratios.get('capacite_desendettement_annees', 0)

    # Extraire et formater les données du poste
    poste_data = extraire_donnees(data_json)
    donnees_formatees = formater_donnees(poste_data)

    # Construire le contexte financier global
    agregats = {
        'resultat_fonct': resultat_fonct,
        'caf_brute': caf_brute,
        'caf_nette': caf_nette,
        'encours_dette': encours_dette,
        'depenses_equip': depenses_equip,
        'fdr_str': fdr_str
    }

    ratios_dict = {
        'taux_epargne': taux_epargne,
        'part_personnel': part_personnel,
        'cap_desendettement': cap_desendettement
    }

    metadata_dict = {
        'commune': commune,
        'exercice': exercice,
        'population': population,
        'strate': strate
    }

    # Choisir le type de contexte selon la configuration du poste
    if INCLURE_CONTEXTE_FINANCIER:
        # Contexte complet avec tous les agrégats financiers
        contexte_financier = regles_globales.construire_contexte_financier_global(
            metadata_dict, agregats, ratios_dict
        )
    else:
        # Contexte minimal (seulement commune, exercice, population, strate)
        contexte_financier = regles_globales.construire_contexte_minimal(metadata_dict)

    # Générer les consignes
    consignes = generer_consignes_analyse(texte_personnalise)

    # Assembler le prompt complet
    prompt = regles_globales.construire_prompt_complet(
        intro=regles_globales.get_intro_role(),
        contexte_essentiel=CONTEXTE_ESSENTIEL,
        donnees=donnees_formatees,
        contexte_financier=contexte_financier,
        consignes=consignes,
        inclure_contexte_financier=True  # On inclut toujours le contexte (complet ou minimal selon config)
    )

    return prompt
