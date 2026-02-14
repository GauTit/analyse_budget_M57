"""
Poste budgétaire : SYNTHÈSE GLOBALE DE TOUTES LES ÉVOLUTIONS FINANCIÈRES
Type : Multi-années (évolution)
"""

from prompts import regles_globales
from prompts.postes.mono_annee import analyse_globale_intelligente

# ============================================
# CONFIGURATION DU POSTE
# ============================================

NOM_POSTE = "Analyse_tendances_globales"
NOM_COMPLET = "SYNTHÈSE GLOBALE DE TOUTES LES ÉVOLUTIONS FINANCIÈRES"
TYPE_RAPPORT = "Multi-annees"
CLE_TENDANCE = None  # None pour Analyse_tendances_globales, sinon clé du JSON tendances

# Utiliser le contexte essentiel du poste mono-année correspondant
CONTEXTE_ESSENTIEL = analyse_globale_intelligente.CONTEXTE_ESSENTIEL

# ============================================
# CONSIGNES D'ANALYSE MULTI-ANNÉES
# ============================================

CONSIGNES_ANALYSE = """POSTE À ANALYSER : SYNTHÈSE GLOBALE DE TOUTES LES ÉVOLUTIONS FINANCIÈRES

L'ESSENTIEL DE LA TRAJECTOIRE PLURIANNUELLE :
L'analyse pluriannuelle (3 à 5 exercices) permet de distinguer les événements exceptionnels des tendances structurelles.
Concepts clés : l'effet de ciseau (charges > produits), la rigidité des charges de personnel et le point d'inflexion (rupture de tendance).
L'objectif est de vérifier si la collectivité dispose d'un modèle économique soutenable.

CONSIGNES D'ANALYSE PLURIANNUELLE – RÉFÉRENTIEL M57 :
Rédiger une synthèse financière pluriannuelle (maximum 400 mots) analysant la trajectoire de la collectivité.

1. DYNAMIQUE DU FONCTIONNEMENT
- Analyser la corrélation entre les recettes et les dépenses réelles.
- Identifier l'existence d'un éventuel "effet de ciseau".
- Préciser si le résultat comptable permet de maintenir une épargne de gestion stable.

2. TRAJECTOIRE DES SOLDES INTERMÉDIAIRES
- Autofinancement : Analyser la pérennité de la CAF brute et de la CAF nette.
- Investissement : Évaluer la régularité de l'effort d'équipement et son mode de financement.
- Solvabilité : Évolution de la capacité de désendettement (seuil : 12 ans).
- Point d'inflexion : Identifier l'exercice charnière s'il existe.

3. ARTICULATIONS ET COHÉRENCE GLOBALE
- Expliquer comment la trajectoire du fonctionnement conditionne la capacité d'investissement.
- Conclure sur la résilience financière au regard de la strate.
"""


# ============================================
# FONCTION DE GÉNÉRATION DU PROMPT
# ============================================

def extraire_donnees(data_json_multi):
    """
    Extrait les données du poste depuis le JSON multi-années

    Args:
        data_json_multi: JSON complet des données multi-années

    Returns:
        dict: Données du poste formatées
    """
    tendances = data_json_multi.get('tendances_globales', {})
    metadata = data_json_multi.get('metadata', {})

    # Cas spécial : Analyse tendances globales
    if CLE_TENDANCE is None:
        return {'tendances': tendances, 'metadata': metadata}

    # Cas normal : Poste spécifique
    if CLE_TENDANCE not in tendances:
        return None

    return tendances[CLE_TENDANCE]


def formater_donnees(donnees_poste, metadata):
    """
    Formate les données du poste pour l'injection dans le prompt

    Args:
        donnees_poste: Données brutes du poste
        metadata: Métadonnées (commune, période, etc.)

    Returns:
        str: Données formatées prêtes à injecter
    """
    # Cas spécial : Analyse tendances globales
    if CLE_TENDANCE is None:
        return formater_donnees_synthese_globale(donnees_poste['tendances'], metadata)

    if not donnees_poste:
        return "Données non disponibles"

    serie_k = donnees_poste.get('serie_k', {})
    serie_hab = donnees_poste.get('serie_hab', {})
    evo_moy = donnees_poste.get('evolution_moy_annuelle_pct', 'N/A')
    evolutions_annuelles = donnees_poste.get('evolutions_annuelles', {})

    periode_debut = metadata.get('periode_debut', 'N/A')
    periode_fin = metadata.get('periode_fin', 'N/A')

    donnees = f"""ÉVOLUTION DU POSTE SUR LA PÉRIODE {periode_debut}-{periode_fin}

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


def formater_donnees_synthese_globale(tendances, metadata):
    """Formate les données pour la synthèse globale multi-années"""

    # Construction d'une section de ratios si disponibles
    ratios_section = ""
    if 'capacite_desendettement' in tendances:
        cap_des = tendances['capacite_desendettement']
        if 'evolutions_annuelles' in cap_des:
            evos = cap_des.get('evolutions_annuelles', {})
            ratios_section += "\nCapacité de désendettement :\n"
            for periode, evo in sorted(evos.items()):
                annee_d, annee_f = periode.split('_')
                ratios_section += f"  {annee_d}→{annee_f} : {evo.get('evolution_annees', 0):+.1f} années\n"

    if 'caf_brute' in tendances:
        caf = tendances['caf_brute']
        if 'evolutions_annuelles' in caf:
            evos = caf.get('evolutions_annuelles', {})
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


def generer_prompt(data_json_multi):
    """
    Génère le prompt complet pour le poste multi-années

    Args:
        data_json_multi: JSON complet des données multi-années

    Returns:
        str: Prompt complet prêt à envoyer au LLM
    """
    # Extraire métadonnées
    metadata = data_json_multi.get('metadata', {})
    commune = metadata.get('commune', 'N/A')
    periode_debut = metadata.get('periode_debut', 'N/A')
    periode_fin = metadata.get('periode_fin', 'N/A')

    # Extraire et formater les données
    donnees_poste = extraire_donnees(data_json_multi)
    donnees_formatees = formater_donnees(donnees_poste, metadata)

    # Construire la section contexte
    section_contexte = ""
    if CONTEXTE_ESSENTIEL:
        section_contexte = f"{CONTEXTE_ESSENTIEL}\n"

    # Construire le prompt
    prompt = f"""{regles_globales.get_intro_role()}

{section_contexte}

CONTEXTE MULTI-ANNÉES :
Commune : {commune}
Période d'analyse : {periode_debut} - {periode_fin}

DONNÉES À ANALYSER :
{donnees_formatees}

{CONSIGNES_ANALYSE}

STYLE D'ÉCRITURE :
- Ton professionnel, institutionnel, factuel et analytique.
- Utiliser le conditionnel uniquement pour les hypothèses ("pourrait traduire").
- Phrases concises, vocabulaire strictement M57.
- Pas de recommandations ("devrait", "il faut") ni de jugement de gestion ou d'interprétation politique.
- Prioriser les constats chiffrés significatifs et structurants.
- Nommer explicitement les agrégats en début de phrase.

{regles_globales.get_interdictions()}

CONCEPTS M57 À RESPECTER :
- Résultat comptable = Produits réels - Charges réelles.
- CAF Brute = Capacité à générer de l'épargne avant service de la dette.
- Trajectoire = Analyse de l'évolution vs Niveau = Constat à l'instant T.

{regles_globales.get_footer_important()}
"""
    return prompt
