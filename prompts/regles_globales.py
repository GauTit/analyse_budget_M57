"""
Règles globales M57 et contraintes rédactionnelles
Applicables à tous les postes budgétaires

Ce module centralise toutes les règles doctrinales, le style d'écriture,
les interdictions et les concepts M57 utilisés pour la génération des prompts.
"""

# ============================================
# STYLE D'ÉCRITURE ET RIGUEUR
# ============================================

STYLE_ECRITURE = """STYLE ET RIGUEUR :
- Ton neutre, institutionnel, factuel et analytique.
- Utiliser le conditionnel uniquement pour toute interprétation non explicitement portée par les chiffres.
- Prioriser l'affirmation lorsque les constats sont objectivement établis.
- Éviter les répétitions inutiles entre postes : si l'écart est négligeable (< 5%), le mentionner très brièvement.
- Aucun commentaire politique, conjoncturel ou recommandation.
- Pas de jugement de gestion.
- Vocabulaire strictement M57, phrases concises et précises."""

# ============================================
# INTERDICTIONS STRICTES
# ============================================

INTERDICTIONS = """INTERDICTIONS STRICTES :
❌ Ne pas suggérer que la dette finance des charges de fonctionnement.
❌ Ne pas expliquer une CAF brute par les recettes seules (la CAF brute résulte du solde produits réels – charges réelles, y compris charges financières).
❌ Ne pas utiliser un ton alarmiste.
❌ Ne pas qualifier de 'neutre' un poste dont l'écart avec la strate dépasse -50 % sans justification explicite.
❌ Ne pas recommander d'action ni juger la gestion.
❌ Ne pas parler de produits de capacité d'autofinancement mais de Recettes Réelles de Fonctionnement.
❌ Ne pas écrire un nombre de phrases dans les titres de section.
❌ Exclus formellement le vocabulaire managérial (« pilotage », « optimisation », « levier d'action », « marge de manœuvre », « marge de sécurité », « marge de manoeuvre »).
❌ Ne pas extrapoler de tendance temporelle (« stabilité », « progression », « dégradation ») sans comparaison chiffrée avec l'exercice précédent.
❌ Ne pas qualifier un investissement d'« autofinancé » sauf si le taux de couverture (CAF nette / dépenses d'équipement) est ≥ 100%.
❌ Ne pas inventer de chiffres. S'appuyer exclusivement sur les données transmises. Si une donnée manque, ne pas l'évoquer.
❌ Ne pas qualifier de 'neutre', 'favorable' ou 'compatible' un poste dont l'écart avec la strate dépasse -50% ou +80% sans justification explicite par un indicateur croisé.
❌ Ne pas utiliser de formulations managériales conditionnelles du type 'sous réserve de la maîtrise de...', 'sous réserve d'un pilotage de...', 'à condition de maintenir...'. Se limiter au constat factuel.
❌ Ne pas confondre le taux d'épargne brute (CAF brute / RRF) avec un ratio rapporté au résultat de fonctionnement. Le dénominateur du taux d'épargne brute est exclusivement les RRF.
❌ Ne pas utiliser le mot "évolution" ni "variation". Utiliser exclusivement "niveau", "poids", "positionnement" ou "part".
❌ INTERDICTION d'utiliser des pronoms démonstratifs en début de phrase ("Ce poste", "Cette évolution").
❌ Ne jamais utiliser l'adjectif "autofinancé" pour qualifier un investissement."""

# ============================================
# CONCEPTS M57
# ============================================

CONCEPTS_M57 = """CONCEPTS M57 À RESPECTER :
- Résultat comptable = Produits réels - Charges réelles.
- CAF Brute = Capacité à générer de l'épargne avant service de la dette.
- Trajectoire = Analyse de l'évolution vs Niveau = Constat à l'instant T.
- RRF (Recettes Réelles de Fonctionnement) = produits de fonctionnement HORS opérations d'ordre. C'est le dénominateur du taux d'épargne brute.
- Total des produits de fonctionnement = RRF + opérations d'ordre. Ce montant est supérieur ou égal aux RRF.
- Résultat de fonctionnement = produits de fonctionnement (réels + ordre) – charges de fonctionnement (réels + ordre). C'est un résultat comptable de la SEULE section de fonctionnement.
- Résultat comptable global = résultat de fonctionnement + résultat d'investissement. Ne jamais confondre les deux."""

# ============================================
# RATIOS ET SEUILS PRUDENTIELS
# ============================================

RATIOS_SEUILS = """RATIOS ET SEUILS PRUDENTIELS :
- Capacité de désendettement (Encours / CAF brute) : > 12 ans (Alerte), > 15 ans (Zone critique). En pratique, une capacité inférieur à 10 ans est généralement considéré comme confortable par les analystes financiers.
- Taux d'épargne brute (CAF brute / RRF) : > 15% (Confort). Un taux < 8% est généralement considéré par les analystes financiers comme un signe d'incapacité probable à renouveler le patrimoine (seuil usuel, non réglementaire).
- Taux de rigidité de la dette (Remboursement du capital / CAF brute) : Mesure quelle part de l'épargne brute est absorbée par le service de la dette en capital avant de pouvoir investir. Plus ce ratio est élevé, moins la collectivité dispose de ressources propres pour financer ses équipements."""

# ============================================
# INTRODUCTION PROMPT (RÔLE ANALYSTE)
# ============================================

INTRO_ROLE_ANALYSTE = """Tu es un analyste financier de la DGFiP (M57).
Tu produis une analyse équivalente à une note DDFIP ou à une analyse transmise au préfet.
Tu n'es PAS un commentateur généraliste.
Tu es soumis à une doctrine comptable STRICTE.

Toute erreur conceptuelle invalide l'analyse."""

# ============================================
# FOOTER PROMPT (RAPPEL IMPORTANT)
# ============================================

FOOTER_IMPORTANT = """IMPORTANT :
- Ne jamais inventer de chiffres
- S'appuyer exclusivement sur les données transmises
- Si une donnée manque, ne pas l'évoquer"""


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def get_intro_role():
    """Retourne l'introduction du rôle de l'analyste"""
    return INTRO_ROLE_ANALYSTE


def get_style_ecriture():
    """Retourne les consignes de style d'écriture"""
    return STYLE_ECRITURE


def get_interdictions():
    """Retourne la liste des interdictions strictes"""
    return INTERDICTIONS


def get_concepts_m57():
    """Retourne les concepts M57 à respecter"""
    return CONCEPTS_M57


def get_ratios_seuils():
    """Retourne les ratios et seuils prudentiels"""
    return RATIOS_SEUILS


def get_footer_important():
    """Retourne le rappel important en fin de prompt"""
    return FOOTER_IMPORTANT


def construire_contexte_financier_global(metadata, agregats_financiers, ratios):
    """
    Construit la section "CONTEXTE FINANCIER GLOBAL DE LA COMMUNE"

    Args:
        metadata: Dictionnaire contenant commune, exercice, population, strate
        agregats_financiers: Dictionnaire avec resultat_fonct, caf_brute, caf_nette, encours_dette, depenses_equip, fdr_str
        ratios: Dictionnaire avec taux_epargne, part_personnel, cap_desendettement

    Returns:
        str: Section formatée du contexte financier global
    """
    return f"""CONTEXTE FINANCIER GLOBAL DE LA COMMUNE :

Commune: {metadata.get('commune', 'N/A')}
Exercice: {metadata.get('exercice', 'N/A')}
Population: {metadata.get('population', 'N/A')} habitants
Strate démographique: {metadata.get('strate', 'N/A')}

ÉQUILIBRES FINANCIERS:
- Résultat de fonctionnement: {agregats_financiers.get('resultat_fonct', 0):.0f} k€
- CAF brute: {agregats_financiers.get('caf_brute', 0):.0f} k€
- CAF nette: {agregats_financiers.get('caf_nette', 0):.0f} k€
- Encours de dette: {agregats_financiers.get('encours_dette', 0):.0f} k€
- Dépenses d'équipement: {agregats_financiers.get('depenses_equip', 0):.0f} k€
- Fonds de roulement: {agregats_financiers.get('fdr_str', 'N/A')}

RATIOS CLÉS:
- Taux d'épargne brute (CAF brute / RRF): {ratios.get('taux_epargne', 0):.1f}% (seuil de confort: > 15% ; seuil d'alerte usuel: < 8%)
- Part des charges de personnel dans les DRF: {ratios.get('part_personnel', 0):.1f}%
- Capacité de désendettement (encours / CAF brute): {ratios.get('cap_desendettement', 0):.1f} années (alerte: > 12 ans ; zone critique: > 15 ans)
"""


def construire_contexte_minimal(metadata):
    """
    Construit un contexte minimal optimisé (sans agrégats financiers redondants)

    Philosophie :
    - Commune, exercice, population, strate = ESSENTIELS pour situer l'analyse
    - Toutes les autres données (CAF, dette, ratios) sont déjà dans "DONNÉES À ANALYSER"
    - Éviter la redondance = économie de tokens + meilleure focalisation du LLM

    Args:
        metadata: Dictionnaire contenant commune, exercice, population, strate

    Returns:
        str: Section formatée du contexte minimal (~40 tokens au lieu de ~200)
    """
    return f"""CONTEXTE :

Commune: {metadata.get('commune', 'N/A')}
Exercice: {metadata.get('exercice', 'N/A')}
Population: {metadata.get('population', 'N/A')} habitants
Strate démographique: {metadata.get('strate', 'N/A')}
"""


def construire_prompt_complet(intro, contexte_essentiel, donnees, contexte_financier, consignes, inclure_contexte_financier=True):
    """
    Assemble toutes les parties pour construire le prompt complet

    Args:
        intro: Introduction du rôle analyste
        contexte_essentiel: Contexte spécifique du poste (L'ESSENTIEL)
        donnees: Données formatées du poste à analyser
        contexte_financier: Contexte financier global de la commune (ou contexte minimal)
        consignes: Consignes d'analyse spécifiques au poste
        inclure_contexte_financier: Si False, ne pas inclure le contexte financier (défaut: True)

    Returns:
        str: Prompt complet prêt à envoyer au LLM
    """
    # Section contexte (optionnelle)
    section_contexte = f"\n{contexte_financier}\n" if inclure_contexte_financier and contexte_financier else ""

    return f"""{intro}

{contexte_essentiel}

DONNÉES À ANALYSER :
{donnees}
{section_contexte}
{consignes}

{get_style_ecriture()}

{get_interdictions()}

{get_footer_important()}
"""
