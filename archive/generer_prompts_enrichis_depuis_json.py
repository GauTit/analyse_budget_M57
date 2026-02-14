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
# (Corrigés selon doctrine stricte M57 DGFIP)
# ============================================

CONTEXTES_ESSENTIELS = {
"Analyse_globale_intelligente": """
L'ESSENTIEL DE LA SYNTHÈSE GLOBALE :
Le diagnostic consiste à évaluer la robustesse de la structure financière au 31 décembre. Il s'agit de vérifier si l'exploitation (fonctionnement) génère suffisamment de ressources pour honorer les obligations financières et sécuriser le patrimoine sans mettre en péril la liquidité.

LOGIQUE D'ARTICULATION (PHOTO À L'INSTANT T) :
1. Équilibre d'exploitation : Vérifier que les recettes réelles de fonctionnement (RRF) couvrent non seulement les dépenses réelles de fonctionnement (DRF), mais dégagent un excédent suffisant (CAF brute) pour assurer le service de la dette passée.
2. Couverture de la dette : L'annuité en capital doit être intégralement couverte par l'épargne de l'année. Une CAF nette positive est le gage qu'aucun 'emprunt toxique' (emprunter pour rembourser du capital) n'est nécessaire.
3. Soutenabilité du stock : Le ratio de désendettement est ici interprété comme un indice de vulnérabilité. Plus il est proche de 12 ans, moins la collectivité dispose de capacité à absorber un futur choc de recettes ou de dépenses.
4. Sécurité du Bilan : Le FDR doit permettre de couvrir le besoin en fonds de roulement (BFR) pour éviter les ruptures de liquidité en cours d'année. Un FDR positif mais nettement inférieur à la moyenne de la strate (écart > -30%) constitue un point de vigilance, surtout s'il est combiné à un encours de dette par habitant supérieur à la strate.

DISTINCTIONS DOCTRINALES IMPÉRATIVES :
- Résultat de fonctionnement = produits de fonctionnement (réels + ordre) – charges de fonctionnement (réels + ordre). C'est un résultat comptable de la SEULE section de fonctionnement.
- Résultat comptable global = résultat de fonctionnement + résultat d'investissement. Ne jamais confondre les deux.
- RRF (Recettes Réelles de Fonctionnement) = produits de fonctionnement HORS opérations d'ordre. C'est le dénominateur du taux d'épargne brute.
- Total des produits de fonctionnement = RRF + opérations d'ordre. Ce montant est supérieur ou égal aux RRF.

RATIOS ET SEUILS PRUDENTIELS :
- Capacité de désendettement (Encours / CAF brute) : > 12 ans (Alerte), > 15 ans (Zone critique). En pratique, une capacité inférieur à 10 ans est généralement considéré comme confortable par les analystes financiers.
- Taux d'épargne brute (CAF brute / RRF) : > 15% (Confort). Un taux < 8% est généralement considéré par les analystes financiers comme un signe d'incapacité probable à renouveler le patrimoine (seuil usuel, non réglementaire).
- Taux de rigidité de la dette (Remboursement du capital / CAF brute) : Mesure quelle part de l'épargne brute est absorbée par le service de la dette en capital avant de pouvoir investir. Plus ce ratio est élevé, moins la collectivité dispose de ressources propres pour financer ses équipements.
""",

"Produits_de_fonctionnement": """
L'ESSENTIEL DU POSTE :
Le total des produits de fonctionnement regroupe l'ensemble des ressources de la section, divisées en recettes réelles (fiscalité, dotations, ventes de services) et recettes d'ordre (neutralisations comptables).

COMPOSITION DOCTRINALE :
- Recettes réelles : Elles constituent le flux de trésorerie entrant et se décomposent en trois grands blocs : la fiscalité (impôts locaux), les dotations de l'État (DGF) et les produits des services (cantines, parkings, etc.).
- Recettes d'ordre : Elles incluent notamment les 'travaux en régie', qui correspondent à la valorisation du travail des services techniques communaux pour des chantiers d'investissement.

LOGIQUE D'ANALYSE :
Le calcul de la capacité d'autofinancement (CAF) repose exclusivement sur les produits réels de fonctionnement. L'analyse doit isoler la part des recettes 'volatiles' (redevances) des recettes 'garanties' (dotations et fiscalité) pour évaluer la sécurité financière de la collectivité.
""",

"Impots_locaux": """
L'ESSENTIEL DU POSTE :
Les impôts locaux constituent le principal levier d'autonomie financière de la collectivité et son poste de recettes le plus structurant.
Ils regroupent :
- La fiscalité directe : Taxe Foncière sur les Propriétés Bâties (TFB), Taxe Foncière sur les Propriétés Non Bâties (TFNB) et Taxe d'Habitation sur les Résidences Secondaires et locaux vacants (THRS). Note : la TH sur les résidences principales est supprimée depuis 2021.
- La fiscalité économique : Cotisation Foncière des Entreprises (CFE), IFER et TASCOM. (Note doctrinale : Les collectivités ne perçoivent plus la CVAE depuis 2023 (LFI 2023, art. 55). L'intégralité du produit est désormais affectée à l'État. En compensation, les communes, EPCI et départements reçoivent une fraction de TVA, composée d'une part fixe (moyenne des recettes de CVAE 2020-2023) et d'une part dynamique affectée au FNAET. La suppression définitive de la CVAE côté entreprises, initialement prévue pour 2024, a été reportée à 2030 par la LFI 2025).
- Les mécanismes de lissage : Le FNGIR (prélèvement ou reversement fixe) et les dotations de compensation fiscale nettes des reversements.

LOGIQUE DE FORMATION DU PRODUIT :
Le produit fiscal dépend de deux variables que l'analyse doit distinguer :
1. L'effet 'Base' : La valeur locative cadastrale (VLC) constitue l'assiette. Elle est revalorisée chaque année par la Loi de Finances selon l'inflation (ex: +7,1% en 2023) et par l'évolution physique du territoire (constructions nouvelles).
2. L'effet 'Taux' : Seul levier décisionnel de la collectivité. Les taux sont votés annuellement par le conseil municipal sur la base des notifications de la DGFIP (État).

NOTION CLÉ – Valeur locative cadastrale (VLC) :
Elle correspond au loyer annuel théorique d'un bien immobilier (références 1970 pour le bâti, 1961 pour le non bâti). Une augmentation du produit fiscal n'indique pas nécessairement une hausse de la pression fiscale décidée par la commune, mais peut résulter de la seule revalorisation forfaitaire nationale.
""",

"DGF": """
L'ESSENTIEL DU POSTE :
La dotation globale de fonctionnement (DGF) est le principal concours financier de l'État. C'est une recette de fonctionnement libre d'emploi (non affectée).

COMPOSITION DOCTRINALE :
- La Dotation forfaitaire : part historique liée à la population et à la superficie.
- Les Dotations de péréquation : visant à corriger les disparités de ressources. Elles incluent :
  • La DSR (Solidarité Rurale) pour les communes rurales éligibles.
  • La DSU (Solidarité Urbaine) pour les communes urbaines.
  • La DNP (Dotation Nationale de Péréquation) pour compenser les écarts de potentiel fiscal.

LOGIQUE D'ANALYSE :
La DGF est inversement proportionnelle à la richesse de la collectivité (mesurée par le potentiel financier). Une baisse de la dotation forfaitaire peut traduire une augmentation du potentiel fiscal de la commune (phénomène d'écrêtement de la dotation forfaitaire). Cette baisse peut toutefois être compensée par une hausse des dotations de péréquation (DSR, DSU, DNP) si la commune reste éligible, de sorte que l'évolution de la DGF globale doit s'analyser composante par composante.
""",

"Charges_de_fonctionnement": """
L'ESSENTIEL DU POSTE :
Les charges de fonctionnement regroupent l'ensemble des dépenses nécessaires à la gestion courante de la collectivité. Elles se divisent en charges réelles (sorties de trésorerie) et charges d'ordre (amortissements et provisions).

COMPOSITION DOCTRINALE :
- Charges réelles : Elles incluent principalement les charges à caractère général (achats, fluides, contrats), les charges de personnel, et les charges financières (intérêts de la dette).
- Charges d'ordre : Écritures comptables destinées à constater l'usure du patrimoine (amortissements). Elles n'ont pas d'incidence sur la trésorerie mais impactent le résultat comptable.

INTERDICTIONS STRICTES : ne jamais utiliser le terme "marge de manœuvre"

LOGIQUE D'ANALYSE :
Le calcul de la capacité d'autofinancement (CAF) repose exclusivement sur les charges réelles de fonctionnement. Une attention particulière est portée à la maîtrise des charges réelles pour préserver l'épargne de la collectivité face à l'inflation (notamment l'énergie et les contrats de prestation).
""",

"Charges_de_personnel": """
L'ESSENTIEL DU POSTE :
Les charges de personnel constituent le premier poste de dépenses réelles de fonctionnement. Elles regroupent les rémunérations (traitement de base, indemnités), les charges sociales patronales et les dépenses liées aux personnels mis à disposition.

FACTEURS D'ÉVOLUTION (LOGIQUE DOCTRINALE) :
- Le GVT positif (Glissement Vieillesse Technicité) : Hausse mécanique liée à l'avancement d'échelon et d'ancienneté des agents à effectifs constants.
- Le GVT négatif (effet de noria) : Baisse mécanique liée au remplacement de départs en retraite (agents en haut de grille) par des recrutements en bas de grille. L'analyse doit porter sur le solde net du GVT (positif – négatif) pour évaluer la dynamique réelle de la masse salariale à effectifs constants.
- Mesures réglementaires nationales : Revalorisations du point d'indice (ex: 2022/2023) ou du SMIC, qui s'imposent à la collectivité.
- Rigidité structurelle : Ce poste est peu modulable à court terme et impacte directement la capacité d'autofinancement (CAF).

ANALYSE :
L'analyse doit distinguer les hausses liées à une politique de recrutement volontariste des hausses subies liées aux décisions de l'État, à la pyramide des âges et au solde net du GVT.
""",

"Resultat_comptable": """
L'ESSENTIEL DU POSTE :
Le résultat comptable de l'exercice en section de fonctionnement correspond à la différence entre l'ensemble des produits et des charges de la section (incluant les flux réels et les écritures d'ordre).

DISTINCTION DOCTRINALE :
- Résultat global : Il intègre les opérations d'ordre (comme les dotations aux amortissements), reflétant ainsi le résultat comptable "net" au sens patrimonial.
- Équilibre réel : Si le résultat est positif, il contribue à la formation de l'excédent de fonctionnement qui sera, après affectation, utilisé pour financer la section d'investissement ou renforcer les réserves.

Ce résultat est le point de départ de l'analyse, mais doit être retraité des écritures d'ordre pour déterminer la Capacité d'Autofinancement (CAF).
""",

"CAF_brute": """
L'ESSENTIEL DU POSTE :
L'épargne brute (ou capacité d'autofinancement - CAF) mesure l'excédent de ressources dégagé par la gestion courante de la collectivité au cours de l'exercice. Elle représente la richesse réelle disponible, après couverture des charges de fonctionnement et des intérêts de la dette, pour financer les investissements. Elle correspond à la différence entre les recettes réelles de fonctionnement et les dépenses réelles de fonctionnement.

DÉTERMINATION DOCTRINALE :
- Périmètre : Conformément à la doctrine M57, l'épargne brute repose exclusivement sur les opérations réelles (flux monétaires). Elle exclut les opérations d'ordre (amortissements, provisions, transferts entre sections) qui n'impactent pas la trésorerie.
- Distinction avec l'épargne de gestion : L'épargne de gestion mesure la performance opérationnelle brute des services. L'épargne brute (CAF) est un indicateur plus complet car elle intègre le coût de la structure de financement (intérêts de la dette - chapitre 66) ainsi que le solde des produits et charges exceptionnels (chapitres 67 et 77). 
- Neutralité de la dette : Elle est calculée avant le remboursement du capital des emprunts. Elle permet donc d'évaluer la capacité intrinsèque de la collectivité à honorer ses engagements financiers, indépendamment de la structure de son profil d'extinction de dette.
- Ne pas écrire que la CAF brute 'contribue à la formation de l'épargne' car elle EST l'épargne brute.

RÔLE STRATÉGIQUE :
Pivot de l'analyse financière publique, l'épargne brute doit impérativement couvrir le remboursement annuel du capital de la dette (annuité en capital). Le solde disponible après ce remboursement (épargne nette) constitue la ressource propre prioritaire pour financer les dépenses d'équipement (investissements) et limiter le recours à l'emprunt nouveau. C'est l'indicateur central de la solvabilité de la collectivité.
""",

"CAF_nette": """
L'ESSENTIEL DU POSTE :
La CAF nette (ou épargne nette, terme officiel DGFIP) est obtenue en retranchant le remboursement en capital des emprunts de la CAF brute.
Elle reflète la ressource propre réellement disponible pour financer l'équipement après avoir honoré l'intégralité du service de la dette.

LOGIQUE DOCTRINALE :
- Indicateur de santé : Une CAF nette positive indique que la collectivité autofinance son renouvellement de dette et dégage un surplus pour ses investissements.
- Seuil d'alerte : Une CAF nette négative signifie que la section de fonctionnement ne couvre pas le remboursement du capital de la dette, contraignant la collectivité à financer sa dette passée par de l'emprunt nouveau ou par ses réserves (situation structurellement déséquilibrée).
""",

"Depenses_equipement": """
L'ESSENTIEL DU POSTE :
Les dépenses d'équipement (ou investissements directs) mesurent l'effort de création, de renouvellement ou d'extension du patrimoine communal au cours de l'exercice. Elles se composent exclusivement de flux réels en section d'investissement.

TYPOLOGIE M57 :
- Immobilisations incorporelles : Dépenses immatérielles (études, documents d'urbanisme, logiciels, frais d'insertion).
- Immobilisations corporelles : Biens concrets (terrains, bâtiments scolaires et publics, réseaux de voirie, matériel et mobilier).
- Immobilisations en cours : Travaux engagés mais non réceptionnés à la clôture de l'exercice (comptes 23).

RATIOS DOCTRINAUX :
- Ratio de niveau (Dépenses d'équipement / hab.) : Mesure l'intensité physique de l'investissement par habitant, à comparer aux moyennes de strate.
- Ratio d'effort d'équipement (Dépenses d'équipement / Recettes Réelles de Fonctionnement) : Indique quelle part de la richesse annuelle générée par le fonctionnement est convertie en investissement.
- Taux de couverture (CAF nette / Dépenses d'équipement) : Détermine la part de l'investissement financée par l'autofinancement propre après remboursement de la dette. Un taux élevé traduit une faible dépendance à l'emprunt pour la réalisation des travaux.
""",

"Emprunts_contractes": """
L'ESSENTIEL DU POSTE :
Les emprunts contractés correspondent aux nouveaux flux de dette souscrits par la collectivité au cours de l'exercice. Contrairement aux recettes de fonctionnement, l'emprunt est une ressource non définitive qui génère une obligation de remboursement futur (service de la dette).

DOCTRINE D'EMPLOI :
- Équilibre budgétaire : L'emprunt constitue la variable d'ajustement de la section d'investissement. Il vient compléter l'autofinancement (CAF nette) et les subventions pour couvrir le besoin de financement des dépenses d'équipement.
- Principe d'exclusion : En vertu des règles de la comptabilité publique, l'emprunt est strictement interdit pour le financement des dépenses de fonctionnement (principe de l'équilibre réel).
- Si l'emprunt est nul ET que le FDR est négatif, qualifier la situation comme un point d'attention et non comme neutre.

LOGIQUE D'ANALYSE :
Le recours à l'emprunt impacte directement l'encours de dette au bilan et détermine la charge financière (intérêts) ainsi que l'annuité future. Son niveau s'apprécie au regard de la capacité de désendettement et de la stratégie de conservation du patrimoine.
""",

"Subventions_recues": """
L'ESSENTIEL DU POSTE :
Les subventions reçues constituent des ressources d'équipement non remboursables, affectées au financement d'opérations d'investissement spécifiques. Elles proviennent principalement de l'État (DETR, DSIL), de l'Union européenne, ou d'autres collectivités territoriales (Département, Région).
   - Les subventions d'investissement n'ont aucun lien avec la formation de l'épargne (concept de fonctionnement). Qualifier leur contribution exclusivement au regard du financement de la section d'investissement.
   - Un niveau de subventions nettement inférieur à la strate (écart > -50%) augmente le reste à charge de la collectivité et constitue un facteur défavorable au financement de l'investissement, jamais un élément 'neutre'.
   - Ne pas spéculer sur les causes (absence de demande, inéligibilité) sans donnée factuelle.
   
COMPOSITION DOCTRINALE :
- Subventions d'équipement : Concours financiers directs liés à la réalisation d'immobilisations.
- FCTVA (Fonds de Compensation de la TVA) : Recette d'investissement automatique versée par l'État pour compenser la TVA acquittée sur les dépenses d'équipement.
- Taxe d'aménagement : Ressource liée aux autorisations d'urbanisme, affectée par nature au financement des équipements publics.

LOGIQUE DE FINANCEMENT :
Ces recettes permettent de réduire le "reste à charge" de la collectivité sur ses projets d'équipement. Le taux de subventionnement (Subventions + FCTVA / Dépenses d'équipement) mesure le degré d'accompagnement extérieur dans la réalisation du patrimoine communal et conditionne le recours à l'emprunt.
""",

"Encours_dette": """
L'ESSENTIEL DU POSTE :
L'encours de dette représente le stock de capital restant dû au 31 décembre. Il correspond à la dette financière de long terme contractée pour financer l'investissement.
Il reflète l'exigibilité future des remboursements envers les prêteurs (établissements bancaires, État, ou organismes spécialisés).

DÉTERMINATION DU STOCK :
L'encours de fin d'exercice résulte de l'encours au 1er janvier, majoré des nouveaux emprunts mobilisés (tirages) et minoré des remboursements de capital effectués (amortissements financiers) durant l'année.

CROISEMENT DOCTRINAL :
- Un encours par habitant nettement supérieur à la strate, combiné à un fonds de roulement nettement inférieur à la strate, traduit un profil de commune ayant investi fortement à crédit en consommant ses réserves. Ce croisement doit être explicité s'il est constaté.

RATIOS DOCTRINAUX (SOLVABILITÉ ET STRUCTURE) :
- Encours de la dette par habitant (en €) : Indicateur de comparaison avec la moyenne de la strate pour mesurer la pression de l'endettement par administré.
- Poids de la dette par rapport aux recettes réelles de fonctionnement : Mesure la part du stock de dette dans les ressources annuelles de gestion (en nombre d’années, non en pourcentage).
- Capacité de désendettement (Encours de dette / CAF brute) : Exprimée en années. Mesure le temps nécessaire pour rembourser l'intégralité du stock de dette en y consacrant toute l'épargne brute annuelle.
Seuils de référence : > 12 ans = alerte ; > 15 ans = zone critique ; < 10 ans = confortable.
""",

"Fonds_roulement": """
L'ESSENTIEL DU POSTE :
Le fonds de roulement net global (FRNG) représente l'excédent des ressources stables (capitaux propres, emprunts à long terme, subventions d'investissement) sur les emplois stables (immobilisations et actifs de long terme). Il constitue la réserve de sécurité financière de la collectivité.

MÉCANIQUE FINANCIÈRE :
- Équilibre de bilan : Le fonds de roulement permet de couvrir le besoin en fonds de roulement (BFR) lié aux décalages de trésorerie entre les encaissements et les décaissements.
- Besoin en fonds de roulement (BFR) : En comptabilité publique locale, le BFR correspond à la différence entre les créances à court terme (restes à recouvrer, charges constatées d'avance) et les dettes à court terme (restes à payer, produits constatés d'avance). Un BFR positif signifie que la collectivité doit avancer de la trésorerie en attendant les encaissements.
- Calcul de la liquidité : La trésorerie nette est le solde disponible après couverture du BFR (Trésorerie = FDR - BFR).

INTERPRÉTATION DOCTRINALE :
- FDR Positif : La collectivité dispose de ressources pérennes suffisantes pour financer ses investissements et dégager un excédent de liquidité, mais s'il est nettement inférieur à la moyenne de la strate (écart > -30%) doit être qualifié de 'point de vigilance' et non de 'facteur favorable'.
- FDR Négatif : Les emplois de long terme sont financés par des ressources de court terme, ce qui caractérise une situation de fragilité financière et un recours potentiel aux lignes de trésorerie.
"""
}

# ============================================
# PHRASES D'INSPIRATION POUR LA SECTION 1
# ============================================
# Ces phrases servent d'EXEMPLES et d'INSPIRATION pour guider l'IA dans la rédaction de la section 1.
# L'IA s'inspirera de ces phrases pour générer la section "POSITIONNEMENT ET POIDS DU POSTE"
# tout en respectant le contexte et les données du poste.
# Laissez vide ("") si vous voulez que l'IA génère sans inspiration particulière.

TEXTES_PERSONNALISES = {
    "Analyse_globale_intelligente": "",
    "Produits_de_fonctionnement": "Le total des produits de fonctionnement comprend toutes les recettes concernant le fonctionnement de la commune. Cela regroupe l’ensemble des opérations réelles et d’ordre, c’est-à-dire toutes les opérations qui entrainent ou pas des flux de trésorerie (encaissements ou non).",
    "Impots_locaux": "Les impots locaux constituent un poste de recettes important. On y trouve, principalement, les produits issus de la fiscalité directe locale.",
    "DGF": "La dotation globale de fonctionnement (DGF) constitue le concours financier principal de l’Etat aux collectivités locales.",
    "Charges_de_fonctionnement": "Le total des charges de fonctionnement comprend toutes les dépenses concernant le fonctionnement de la commune. Cela regroupe l’ensemble des opérations réelles et d’ordre, c’est-à-dire toutes les opérations qui entrainent ou pas des flux de trésorerie (décaissements ou non).",
    "Charges_de_personnel": "Les charges de personnel constituent la principale dépense de fonctionnement. On y trouve, principalement, les rémunérations des agents et les charges sociales patronales associées.",
    "Resultat_comptable": "Le résultat comptable est la différence entre le total des produits de fonctionnement et le total des charges de fonctionnement. Il traduit la couverture (ou non, s’il est négatif) des charges de fonctionnement (dépenses) par les produits de fonctionnement (recettes).",
    "CAF_brute": "La CAF brute constitue l'indicateur principal de la capacité de la commune à générer un excédent de ressources issu du fonctionnement avant remboursement du capital de la dette, servant de levier potentiel pour le financement de la section d'investissement.",
    "CAF_nette": "La CAF nette représente l'autofinancement effectivement disponible pour financer la section d'investissement après remboursement en capital de la dette, constituant un indicateur clé de la capacité financière de la commune.",
    "Depenses_equipement": "Les dépenses d’équipement constituent les investissements réalisés par la commune sur l’exercice, principalement dans les immobilisations corporelles et incorporelles, ainsi que les immobilisations en cours. Les dépenses d’équipement peuvent être traduites « en opération d’équipement ».",
    "Emprunts_contractes": "Les emprunts contractés par la commune représentent les dettes nouvelles souscrites au cours de l'exercice, constituant un élément déterminant pour l'appréciation du niveau de l'encours de dette, des charges financières futures et du mode de financement des dépenses d'équipement.",
    "Subventions_recues": "Les subventions reçues constituent une ressource d'investissement non remboursable, dont le niveau conditionne le reste à charge de la collectivité sur ses opérations d'équipement.",
    "Encours_dette": "L’encours de dette constitue un poste majeur du passif financier de la commune, représentant un levier important de financement des investissements.",
    "Fonds_roulement": "Le fonds de roulement constitue un poste majeur dans la structure financière de la commune, traduisant la capacité cumulée à couvrir le besoin en fonds de roulement et la trésorerie."
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

# ============================================
# MAPPING POSTES MULTI-ANNÉES -> CONTEXTES
# ============================================
# Associe chaque poste multi-années à son contexte "L'essentiel" correspondant

MAPPING_MULTI_VERS_CONTEXTE = {
    "Analyse_tendances_globales": "Analyse_globale_intelligente",
    "Produits_fonctionnement_evolution": "Produits_de_fonctionnement",
    "Charges_fonctionnement_evolution": "Charges_de_fonctionnement",
    "Charges_personnel_evolution": "Charges_de_personnel",
    "CAF_brute_evolution": "CAF_brute",
    "Encours_dette_evolution": "Encours_dette",
    "Depenses_equipement_evolution": "Depenses_equipement"
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
- Encours de dette : {encours} k€ ({encours_hab} €/hab. vs {encours_strate} €/hab. strate)
- Capacité de désendettement (encours / CAF brute) : {cap_des} années.
  Cette donnée s'exprime exclusivement en années.
  Seuil d’alerte usuel : > 12 ans ; zone critique : > 15 ans.

RATIOS FINANCIERS CLÉS :
- Taux d'épargne brute (CAF brute/RRF) : {taux_epargne}%
- Taux d'épargne nette (CAF nette/RRF) : {taux_epargne_nette}%
- Coefficient de mobilisation de la CAF (Remboursement dette/CAF brute) : {coeff_mobilisation}%
- Part charges de personnel / DRF : {part_personnel}% (strate : {part_personnel_strate}%)
- Ratio d'effort d'équipement (Dépenses équip./RFF) : {ratio_effort}%
- Ratio d'autonomie fiscale (Impôts locaux/RFF) : {ratio_autonomie}%
- Taux de couverture des dépenses d'équipement par la CAF nette : {taux_couverture}%

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
            coeff_mobilisation=extraire_valeur_json(data_json, 'ratios_financiers.coefficient_mobilisation_caf_pct') or 0,
            part_personnel=extraire_valeur_json(data_json, 'ratios_financiers.part_charges_personnel_pct') or 0,
            part_personnel_strate=charges_personnel_strate,
            ratio_effort=extraire_valeur_json(data_json, 'ratios_financiers.ratio_effort_equipement_pct') or 0,
            ratio_autonomie=extraire_valeur_json(data_json, 'ratios_financiers.ratio_autonomie_fiscale_pct') or 0,
            # Utilisation du nouveau ratio conforme M57 (avec fallback sur l'ancien nom pour rétrocompatibilité)
            taux_couverture=extraire_valeur_json(data_json, 'ratios_financiers.taux_couverture_depenses_equipement_pct') or extraire_valeur_json(data_json, 'ratios_financiers.taux_couverture_investissement_pct') or 0,
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
            type_ratio = "RRF" if 'pct_produits_caf' in poste_data else "DRF"
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
    else:
        # 1. ANALYSE DES RECETTES (FONCTIONNEMENT)
        if nom_poste == "Produits_fonctionnement":
            angle_specifique = "Situer la contribution des produits de fonctionnement à la formation de l'épargne brute de l'exercice."
        elif nom_poste == "Impots_locaux":
            angle_specifique = "Situer le niveau des taux d'imposition communaux au regard de la moyenne de la strate."
        elif nom_poste == "Fiscalite_reversee":
            angle_specifique = "Situer la part des attributions de compensation et de la fiscalité reversée (FPU) dans les recettes réelles de fonctionnement."
        elif nom_poste == "DGF":
            angle_specifique = "Situer le montant de la dotation globale de fonctionnement par habitant au regard de la strate et évaluer le poids de la DGF dans les recettes réelles de fonctionnement."
        elif nom_poste == "Autres_dotations_participations":
            angle_specifique = "Situer le poids des concours financiers externes dans la structure des recettes réelles de fonctionnement."
        elif nom_poste == "FCTVA":
            angle_specifique = "Situer le poids des concours financiers externes dans la structure des recettes réelles de fonctionnement."
        elif nom_poste == "Produits_services_domaine":
            angle_specifique = "Situer le niveau de mobilisation des recettes tarifaires issues des services publics locaux."

        # 2. ANALYSE DES DÉPENSES (FONCTIONNEMENT)
        elif nom_poste == "Charges_de_fonctionnement":
            angle_specifique = "Évaluer le poids structurel des charges réelles de fonctionnement et leur incidence sur la formation de l'épargne brute."
        elif nom_poste == "Charges_de_personnel":
            angle_specifique = """Évaluer le poids des charges de personnel par habitant et leur part dans les dépenses réelles de fonctionnement.
            - DISTINGUER obligatoirement deux situations :
                • Si l'écart en €/hab est élevé MAIS que le ratio de structure (part dans les DRF) est proche de la strate (écart < 3 points) : l'écart traduit un effet de VOLUME global (le budget par habitant est élevé sur tous les postes), pas une surreprésentation spécifique du personnel. Le qualifier explicitement.
                • Si l'écart en €/hab est faible MAIS que le ratio de structure est significativement supérieur à la strate (écart > 3 points) : le personnel est spécifiquement surreprésenté dans la structure des charges malgré un budget global modéré. Le qualifier explicitement comme effet de STRUCTURE.
                • Si les deux écarts sont élevés : cumul effet volume + structure, à distinguer.
            - Conclure explicitement sur la nature de l'écart (volume, structure, ou les deux).""" 
            
        elif nom_poste == "Achats_charges_externes":
            angle_specifique = "Évaluer le poids des charges à caractère général (énergie, contrats, fournitures) dans les dépenses réelles de fonctionnement."
        elif nom_poste == "Charges_financieres":
            angle_specifique = "Évaluer le poids des intérêts de la dette dans les charges réelles de fonctionnement et leur incidence sur le passage de l'épargne de gestion à l'épargne brute."
        elif nom_poste == "Contingents":
            angle_specifique = "Situer le poids des contributions obligatoires dans les charges de fonctionnement."
        elif nom_poste == "Subventions_versees":
            angle_specifique = "Situer le poids des subventions versées dans les charges de fonctionnement."

        # 3. ÉQUILIBRES ET AUTOFINANCEMENT
        elif nom_poste == "Resultat_comptable":
            angle_specifique = "Situer le résultat de l'exercice dans la formation de l'excédent de fonctionnement reporté."
        elif nom_poste == "EBF":
            angle_specifique = "Situer l'excédent brut de fonctionnement dans la chaîne de formation de l'épargne (avant charges financières)."
        elif nom_poste == "CAF_brute":
            angle_specifique = "Évaluer le niveau de l'épargne brute au regard du seuil de confort (taux d'épargne brute > 15%) et sa capacité à couvrir le remboursement du capital de la dette."
        elif nom_poste == "CAF_nette":
            angle_specifique = "Évaluer le niveau de l'épargne nette disponible pour le financement de la section d'investissement après service de la dette en capital."

        # 4. INVESTISSEMENT ET DETTE
        elif nom_poste == "Depenses_equipement":
            angle_specifique = """Situer l'effort d'équipement par habitant au regard de la moyenne de la strate.
   - Un niveau inférieur à la strate allège la pression sur le financement de l'investissement (facteur favorable à l'équilibre budgétaire à court terme), mais peut traduire un risque de sous-investissement et d'insuffisance de renouvellement du patrimoine à moyen terme.
   - Un niveau supérieur à la strate constitue une pression sur le besoin de financement (contrainte relative), mais traduit un effort patrimonial soutenu.
   - Ne pas confondre contrainte budgétaire (besoin de financement) et risque patrimonial (sous-investissement)."""
        elif nom_poste == "Subventions_recues":
            angle_specifique = "Situer le taux de financement externe des dépenses d'équipement (subventions + FCTVA / dépenses d'équipement). Croiser systématiquement avec le niveau effectif d'emprunt de l'exercice. Ne pas spéculer sur un recours futur à l'emprunt si l'exercice courant ne le confirme pas."
        elif nom_poste == "Encours_dette":
            angle_specifique = """Évaluer le niveau d'endettement par habitant et la capacité de désendettement au regard des seuils de référence (alerte : > 12 ans ; zone critique : > 15 ans).
   - Croiser systématiquement le ratio encours/RRF avec le taux d'épargne brute :
     • Si encours/RRF > 80% ET taux d'épargne brute < 15% : qualifier de point d'attention, même si la capacité de désendettement reste sous le seuil d'alerte.
     • Si encours/RRF > 80% ET taux d'épargne brute > 15% : la capacité d'épargne compense le poids de la dette, qualifier de facteur neutre à favorable.
   - Ne pas qualifier un encours de 'compatible avec l'équilibre financier' sans justifier par au moins un indicateur croisé."""        
        elif nom_poste == "Annuite_dette":
            angle_specifique = "Évaluer le poids de l'annuité (capital + intérêts) dans les recettes réelles de fonctionnement."
        elif nom_poste == "Fonds_roulement":
            angle_specifique = "Situer le niveau du fonds de roulement et sa capacité à couvrir le besoin en fonds de roulement pour sécuriser la trésorerie."

        else:
            angle_specifique = "Situer la contribution de ce poste à l'équilibre budgétaire de l'exercice."
        # Section 1 avec phrase d'inspiration si fournie
        section_1_instruction = ""
        if texte_personnalise and texte_personnalise.strip():
            section_1_instruction = f"""
1. POSITIONNEMENT ET POIDS DU POSTE en une phrase :

   PHRASE D'INSPIRATION (à utiliser comme guide pour la rédaction) :
   "{texte_personnalise.strip()}"

   → S'inspirer de cette phrase tout en l'adaptant au contexte financier.
   → Conserver le ton institutionnel et factuel.

2. ANALYSE COMPARATIVE ET DIAGNOSTIC DES ÉCARTS (1 phrase + possibilité d'une 2e phrase factuelle)"""
        else:
            section_1_instruction = """
1. POSITIONNEMENT ET POIDS DU POSTE en une phrase :
   - Situer le poste dans la structure budgétaire de la commune
     (poste majeur, poste secondaire, charge structurelle, ressource principale, etc.).

2. ANALYSE COMPARATIVE ET DIAGNOSTIC DES ÉCARTS (1 phrase + possibilité d'une 2e phrase factuelle)"""

        consignes_analyse = f"""
   CONSIGNES D'ANALYSE :

Rédige une note d'analyse financière experte, synthétique et doctrinalement conforme M57.

Adopte le ton d'un analyste DGFiP : factuel, hiérarchisé, sans effet de style, sans commentaire politique.

Structure impérative :

{section_1_instruction}
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
   - {angle_specifique}
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
   INTERDICTION d'utiliser des pronoms démonstratifs en début de phrase ("Ce poste", "Cette évolution").

   """

    prompt = f"""Tu es un analyste financier de la DGFiP (M57).
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
- Taux d'épargne brute (CAF brute / RRF): {taux_epargne:.1f}% (seuil de confort: > 15% ; seuil d'alerte usuel: < 8%)
- Part des charges de personnel dans les DRF: {part_personnel:.1f}%
- Capacité de désendettement (encours / CAF brute): {cap_desendettement:.1f} années (alerte: > 12 ans ; zone critique: > 15 ans)


{consignes_analyse}

STYLE ET RIGUEUR :
- Ton neutre, institutionnel, factuel et analytique.
- Utiliser le conditionnel uniquement pour toute interprétation non explicitement portée par les chiffres.
- Prioriser l'affirmation lorsque les constats sont objectivement établis.
- Éviter les répétitions inutiles entre postes : si l'écart est négligeable (< 5%), le mentionner très brièvement.
- Aucun commentaire politique, conjoncturel ou recommandation.
- Pas de jugement de gestion.
- Vocabulaire strictement M57, phrases concises et précises.

INTERDICTIONS STRICTES :
❌ Ne pas suggérer que la dette finance des charges de fonctionnement.
❌ Ne pas expliquer une CAF brute par les recettes seules (la CAF brute résulte du solde produits réels – charges réelles, y compris charges financières).
❌ Ne pas utiliser un ton alarmiste.
❌ Ne pas qualifier de 'neutre' un poste dont l'écart avec la strate dépasse -50 % sans justification explicite.
❌ Ne pas recommander d'action ni juger la gestion.
❌ Ne pas parler de produits de capacité d’autofinancement mais de Recettes Réelles de Fonctionnement.
❌ Ne pas écrire un nombre de phrases dans les titres de section.
❌ Exclus formellement le vocabulaire managérial (« pilotage », « optimisation », « levier d'action », « marge de manœuvre », « marge de sécurité », « marge de manoeuvre »).
❌ Ne pas extrapoler de tendance temporelle (« stabilité », « progression », « dégradation ») sans comparaison chiffrée avec l'exercice précédent.
❌ Ne pas qualifier un investissement d'« autofinancé » sauf si le taux de couverture (CAF nette / dépenses d'équipement) est ≥ 100%.
❌ Ne pas inventer de chiffres. S'appuyer exclusivement sur les données transmises. Si une donnée manque, ne pas l'évoquer.
❌ Ne pas qualifier de 'neutre', 'favorable' ou 'compatible' un poste dont l'écart avec la strate dépasse -50% ou +80% sans justification explicite par un indicateur croisé.
❌ Ne pas utiliser de formulations managériales conditionnelles du type 'sous réserve de la maîtrise de...', 'sous réserve d'un pilotage de...', 'à condition de maintenir...'. Se limiter au constat factuel.
❌ Ne pas confondre le taux d'épargne brute (CAF brute / RRF) avec un ratio rapporté au résultat de fonctionnement. Le dénominateur du taux d'épargne brute est exclusivement les RRF.
❌ Ne pas utiliser le mot "évolution" ni "variation". Utiliser exclusivement "niveau", "poids", "positionnement" ou "part".



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

    # Récupérer le contexte "L'essentiel" correspondant
    nom_poste_contexte = MAPPING_MULTI_VERS_CONTEXTE.get(nom_poste)
    contexte = CONTEXTES_ESSENTIELS.get(nom_poste_contexte, "") if nom_poste_contexte else ""

    # Consignes spécifiques pour l'analyse multi-années
    if nom_poste == 'Analyse_tendances_globales':
        consignes = f"""POSTE À ANALYSER : {poste_a_analyser}

L'ESSENTIEL DE LA TRAJECTOIRE PLURIANNUELLE :
L'analyse pluriannuelle (3 à 5 exercices) permet de distinguer les événements exceptionnels des tendances structurelles. 
Concepts clés : l'effet de ciseau (charges > produits), la rigidité des charges de personnel et le point d'inflexion (rupture de tendance).
L'objectif est de vérifier si la collectivité dispose d'un modèle économique soutenable.

CONSIGNES D’ANALYSE PLURIANNUELLE – RÉFÉRENTIEL M57 :
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
    else:
        consignes = f"""POSTE BUDGÉTAIRE À ANALYSER : {poste_a_analyser}

CONSIGNES D’ANALYSE PLURIANNUELLE – RÉFÉRENTIEL M57 :

Rédiger une analyse pluriannuelle synthétique du poste "{poste_a_analyser}" (max 150 mots).

1. TRAJECTOIRE ET QUANTIFICATION
- Décrire la dynamique du poste en combinant montants globaux (k€) et ratios par habitant (€/hab.).
- Identifier les **points d’inflexion** ou ruptures de tendance sur la période.
- Qualifier l'évolution par rapport à la moyenne de la strate pour situer la collectivité.

2. DIAGNOSTIC ET COHÉRENCE
- Identifier si l'évolution est **structurelle** (tendance de fond) ou **conjoncturelle** (événement isolé sur un exercice).
- Pour les dépenses : préciser si l'évolution pèse sur l'autofinancement.
- Pour les recettes : préciser si l'évolution renforce l'autonomie financière.
- Assurer la cohérence avec les autres agrégats (ex: lien entre investissement et subventions reçues).
"""

    # Construire la section contexte si disponible
    section_contexte = ""
    if contexte:
        section_contexte = f"{contexte}\n"

    prompt = f"""Tu es un analyste financier de la DGFiP (M57).
Tu produis une analyse équivalente à une note DDFIP ou à une analyse transmise au préfet.
Tu n'es PAS un commentateur généraliste.
Tu es soumis à une doctrine comptable STRICTE.

{section_contexte}

CONTEXTE MULTI-ANNÉES :
Commune : {commune}
Période d'analyse : {periode_debut} - {periode_fin}

DONNÉES À ANALYSER :
{donnees}

{consignes}

STYLE D'ÉCRITURE :
- Ton professionnel, institutionnel, factuel et analytique.
- Utiliser le conditionnel uniquement pour les hypothèses ("pourrait traduire").
- Phrases concises, vocabulaire strictement M57.
- Pas de recommandations ("devrait", "il faut") ni de jugement de gestion ou d’interprétation politique.
- Prioriser les constats chiffrés significatifs et structurants.
- Nommer explicitement les agrégats en début de phrase.


INTERDICTIONS STRICTES :
❌ Ne pas suggérer que la dette finance des charges de fonctionnement.
❌ Ne pas expliquer une CAF brute par la fiscalité seule.
❌ Ne pas utiliser un ton alarmiste, ne pas recommander d'action ni juger la gestion.
❌ Ne jamais utiliser l'adjectif "autofinancé" pour qualifier un investissement.
❌ INTERDICTION d'utiliser des pronoms démonstratifs en début de phrase ("Ce poste", "Cette évolution").
❌ Ne pas utiliser "5-6 phrases" dans les titres.

CONCEPTS M57 À RESPECTER :
- Résultat comptable = Produits réels - Charges réelles.
- CAF Brute = Capacité à générer de l'épargne avant service de la dette.
- Trajectoire = Analyse de l'évolution vs Niveau = Constat à l'instant T.

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
