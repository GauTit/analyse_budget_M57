"""
Poste budgétaire : Emprunts Contractes
Type : Mono-année
"""

from prompts import regles_globales

# ============================================
# CONTEXTE ESSENTIEL DU POSTE
# ============================================

CONTEXTE_ESSENTIEL = """L'ESSENTIEL DU POSTE :
Les emprunts contractés correspondent aux nouveaux flux de dette souscrits par la collectivité au cours de l'exercice. Contrairement aux recettes de fonctionnement, l'emprunt est une ressource non définitive qui génère une obligation de remboursement futur (service de la dette).

DOCTRINE D'EMPLOI :
- Équilibre budgétaire : L'emprunt constitue la variable d'ajustement de la section d'investissement. Il vient compléter l'autofinancement (CAF nette) et les subventions pour couvrir le besoin de financement des dépenses d'équipement.
- Principe d'exclusion : En vertu des règles de la comptabilité publique, l'emprunt est strictement interdit pour le financement des dépenses de fonctionnement (principe de l'équilibre réel).
- Si l'emprunt est nul ET que le FDR est négatif, qualifier la situation comme un point d'attention et non comme neutre.

LOGIQUE D'ANALYSE :
Le recours à l'emprunt impacte directement l'encours de dette au bilan et détermine la charge financière (intérêts) ainsi que l'annuité future. Son niveau s'apprécie au regard de la capacité de désendettement et de la stratégie de conservation du patrimoine."""

# ============================================
# TEXTE PERSONNALISÉ (PHRASE D'INSPIRATION)
# ============================================

TEXTE_PERSONNALISE = """Les emprunts contractés par la commune représentent les dettes nouvelles souscrites au cours de l'exercice, constituant un élément déterminant pour l'appréciation du niveau de l'encours de dette, des charges financières futures et du mode de financement des dépenses d'équipement."""

# ============================================
# CONFIGURATION DU POSTE
# ============================================

CHEMIN_JSON = "investissement.ressources.emprunts"
NOM_POSTE = "Emprunts_contractes"
TYPE_RAPPORT = "Mono-annee"

# Inclure le contexte financier global complet ?
# - True : Inclut CAF brute, encours dette, ratios clés (+ de tokens)
# - False : Inclut uniquement commune, exercice, population, strate (économie de tokens)
INCLURE_CONTEXTE_FINANCIER = False

# ============================================
# ANGLE SPÉCIFIQUE D'ANALYSE
# ============================================

ANGLE_SPECIFIQUE = """Évaluer le niveau de recours à l'emprunt pour le financement des investissements de l'exercice."""


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
    # Cas spécial : Analyse globale intelligente
    if CHEMIN_JSON == "metadata":
        return data_json  # Retourner tout le JSON

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
        data_json: JSON complet (pour analyse globale uniquement)

    Returns:
        str: Données formatées prêtes à injecter
    """
    # Cas spécial : Analyse globale intelligente
    if CHEMIN_JSON == "metadata":
        return formater_donnees_synthese_globale(poste_data)

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
    if 'pct_produits_caf' in poste_data or 'pct_charges_caf' in poste_data:
        pct_commune = poste_data.get('pct_produits_caf') or poste_data.get('pct_charges_caf')
        pct_strate = poste_data.get('pct_produits_caf_strate') or poste_data.get('pct_charges_caf_strate')

        if pct_commune is not None and pct_strate is not None:
            type_pct = "recettes réelles de fonctionnement" if 'pct_produits_caf' in poste_data else "dépenses réelles de fonctionnement"
            donnees += f"\nPOIDS DANS LA STRUCTURE :\n"
            donnees += f"- Part dans les {type_pct} : {pct_commune:.1f}% (commune) vs {pct_strate:.1f}% (strate)\n"

    # Cas spécial pour les impôts locaux : détail de la fiscalité
    if 'detail_fiscalite' in poste_data:
        detail = poste_data['detail_fiscalite']
        donnees += "\nDÉTAIL DE LA FISCALITÉ :\n"

        for taxe_nom, taxe_data in detail.items():
            if isinstance(taxe_data, dict):
                taux_commune = taxe_data.get('taux_vote_pct', 0)
                taux_strate = taxe_data.get('taux_strate_pct', 0)
                base_k = taxe_data.get('base_k', 0)
                produit_k = taxe_data.get('produit_k', 0)

                nom_affiche = taxe_nom.replace('_', ' ').title()
                donnees += f"  • {nom_affiche} :\n"
                donnees += f"    - Base : {base_k} k€\n"
                donnees += f"    - Taux voté : {taux_commune:.2f}% (strate : {taux_strate:.2f}%)\n"
                donnees += f"    - Produit : {produit_k} k€\n"

    return donnees


def formater_donnees_synthese_globale(data_json):
    """Formate les données pour la synthèse globale"""
    metadata = data_json.get('metadata', {})

    # Extraire tous les agrégats clés
    donnees = f"""SYNTHÈSE GLOBALE DES ÉQUILIBRES FINANCIERS

Commune : {metadata.get('commune', 'N/A')}
Exercice : {metadata.get('exercice', 'N/A')}
Population : {metadata.get('population', 'N/A')} habitants
Strate : {metadata.get('strate', {}).get('libelle', 'N/A')}

FONCTIONNEMENT :
- Produits de fonctionnement : {data_json.get('fonctionnement', {}).get('produits', {}).get('total', {}).get('montant_k', 0)} k€
- Charges de fonctionnement : {data_json.get('fonctionnement', {}).get('charges', {}).get('total', {}).get('montant_k', 0)} k€
- Résultat de fonctionnement : {data_json.get('fonctionnement', {}).get('resultat', {}).get('montant_k', 0)} k€

AUTOFINANCEMENT :
- CAF brute : {data_json.get('autofinancement', {}).get('caf_brute', {}).get('montant_k', 0)} k€
- CAF nette : {data_json.get('autofinancement', {}).get('caf_nette', {}).get('montant_k', 0)} k€

INVESTISSEMENT :
- Dépenses d'équipement : {data_json.get('investissement', {}).get('emplois', {}).get('depenses_equipement', {}).get('montant_k', 0)} k€
- Emprunts contractés : {data_json.get('investissement', {}).get('ressources', {}).get('emprunts', {}).get('montant_k', 0)} k€

ENDETTEMENT :
- Encours de dette : {data_json.get('endettement', {}).get('encours_total', {}).get('montant_k', 0)} k€
- Fonds de roulement : {data_json.get('endettement', {}).get('fonds_roulement', {}).get('montant_k', 0)} k€
- Capacité de désendettement : {data_json.get('endettement', {}).get('ratios', {}).get('capacite_desendettement_annees', 0):.1f} années

RATIOS FINANCIERS :
- Taux d'épargne brute : {data_json.get('ratios_financiers', {}).get('taux_epargne_brute_pct', 0):.1f}%
- Part des charges de personnel : {data_json.get('ratios_financiers', {}).get('part_charges_personnel_pct', 0):.1f}%
"""
    return donnees


def generer_consignes_analyse(texte_personnalise=""):
    """
    Génère les consignes d'analyse spécifiques au poste

    Args:
        texte_personnalise: Phrase d'inspiration pour la section 1 (optionnel)

    Returns:
        str: Consignes d'analyse formatées
    """
    # Cas spécial : Analyse globale intelligente
    if CHEMIN_JSON == "metadata":
        return generer_consignes_synthese_globale()

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


def generer_consignes_synthese_globale():
    """Consignes spécifiques pour la synthèse globale"""
    return """CONSIGNES D'ANALYSE – SYNTHÈSE FINANCIÈRE GLOBALE :

Rédiger une synthèse financière globale concise, mettant en évidence les articulations comptables entre les principaux agrégats financiers de la commune.

La synthèse ne doit pas dépasser 400 mots et se limiter à l'essentiel.

DIRECTIVES DE RÉDACTION IMPÉRATIVES :
- DÉBUT : Commencer obligatoirement par la formulation : "Le résultat comptable de la commune de [NOM_COMMUNE] présente un [excédent/déficit] de [VALEUR] k€."
- DISTINCTION RÉSULTAT : Si les données permettent d'isoler le résultat de fonctionnement du résultat d'investissement, les distinguer explicitement. Sinon, préciser qu'il s'agit du résultat global (fonctionnement + investissement).
- POSITIONNEMENT : Analyser les montants par rapport à la moyenne de la strate (données disponibles) plutôt que par rapport au passé.
- VOCABULAIRE : Ne jamais utiliser le mot "évolution" ou "variation" (puisque nous analysons un exercice unique), mais utiliser "niveau", "poids", "positionnement" ou "part".
- TERMINOLOGIE : Utiliser exclusivement "recettes réelles de fonctionnement" (RRF) et "dépenses réelles de fonctionnement" (DRF). Ne jamais écrire "produits de capacité d'autofinancement", "produits CAF", ou "charges CAF".

CONTENU :
- Présenter l'équilibre du résultat comptable (RRF vs DRF).
- Indiquer la capacité d'autofinancement (CAF brute et CAF nette), avec le taux d'épargne brute. Si la CAF brute et le résultat de fonctionnement sont quasi identiques (écart < 5 k€), signaler que les charges d'ordre nettes sont négligeables et interroger la politique d'amortissement.
- Décrire le financement de l'équipement sur l'exercice :
  • Si le taux de couverture (CAF nette / dépenses d'équipement) est ≥ 100% : indiquer que l'investissement est intégralement autofinancé.
  • Si le taux de couverture est < 100% : indiquer la part financée par la CAF nette et préciser que le solde provient d'autres ressources (subventions, fonds de roulement, résultats antérieurs reportés), SANS qualifier l'investissement d'"autofinancé".
  • Préciser si un emprunt a été contracté ou non.
- Détailler le niveau d'endettement et la capacité de désendettement.
- Qualifier le fonds de roulement :
  • FDR positif ET proche de la strate (écart < -30%) → facteur favorable.
  • FDR positif MAIS nettement inférieur à la strate (écart > -30%) → point de vigilance, à croiser avec le niveau d'encours de dette par habitant.
  • FDR négatif → facteur défavorable.

STRUCTURE :
Paragraphes courts. Identifier les articulations comptables entre :
- fonctionnement, autofinancement, investissement et dette.

Structurer le propos en paragraphes courts et hiérarchisés.
Ne pas répéter les analyses détaillées par poste.
"""


def generer_prompt(data_json, texte_personnalise=None):
    """
    Génère le prompt complet pour le poste Emprunts_contractes

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
    donnees_formatees = formater_donnees(poste_data, data_json)

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
        consignes=consignes
    )

    return prompt
