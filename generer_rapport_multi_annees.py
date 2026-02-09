# python generer_rapport_multi_annees.py "C:\Users\vagoa\Desktop\cours2IA\3A\ETUDE_TECHNIQUE\CODEBASE\docs\bilans_multi_annees"



"""
Génération de rapport d'analyse comparative multi-années
Compare 4 bilans annuels et génère un rapport PDF complet avec graphiques et analyses LLM
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, 'src')

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                 Image, Table, TableStyle, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor

import pandas as pd

from analysis.analyseur_multi_annees import (
    charger_bilans_multi_annees,
    charger_bilans_depuis_api,
    comparer_bilans_annee_par_annee,
    detecter_tendances_et_anomalies,
    calculer_ratios_evolutifs
)
from generators.graphiques_evolution import generer_tous_graphiques_standard


def creer_styles():
    """Crée les styles PDF pour le rapport"""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='TitrePrincipal',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='TitreSection',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=18,
        spaceBefore=25,
        fontName='Helvetica-Bold',
        borderWidth=1.5,
        borderColor=HexColor('#2c3e50'),
        borderPadding=8,
        backColor=HexColor('#ecf0f1')
    ))

    styles.add(ParagraphStyle(
        name='SousTitre',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=18,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='SousTitreTexte',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        leftIndent=10
    ))

    styles.add(ParagraphStyle(
        name='CorpsTexte',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=14,
        leftIndent=10
    ))

    styles.add(ParagraphStyle(
        name='Metadata',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#555555'),
        alignment=TA_CENTER,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name='MetadataGras',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor('#2c3e50'),
        alignment=TA_CENTER,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='Legende',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#7f8c8d'),
        alignment=TA_CENTER,
        spaceAfter=12,
        spaceBefore=2,
        fontStyle='italic'
    ))

    styles.add(ParagraphStyle(
        name='Encadre',
        parent=styles['BodyText'],
        fontSize=10,
        leftIndent=15,
        rightIndent=15,
        spaceAfter=12,
        spaceBefore=12,
        backColor=HexColor('#f0f8ff'),
        borderColor=HexColor('#3498db'),
        borderWidth=1,
        borderPadding=10,
        leading=14
    ))

    styles.add(ParagraphStyle(
        name='PointCle',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=8,
        bulletText='▸',
        bulletIndent=10,
        leading=14
    ))

    return styles


def convertir_texte_en_paragraphes(texte: str, styles) -> list:
    """Convertit le texte en éléments PDF avec détection intelligente des titres"""
    elements = []
    lignes = texte.split('\n')

    for ligne in lignes:
        ligne = ligne.strip()
        if not ligne:
            elements.append(Spacer(1, 0.2*cm))
            continue

        # Nettoyer les balises HTML/Markdown
        ligne = ligne.replace('<b>', '').replace('</b>', '')
        ligne = ligne.replace('<i>', '').replace('</i>', '')
        ligne = ligne.replace('<strong>', '').replace('</strong>', '')
        ligne = ligne.replace('**', '').replace('__', '')

        # Échapper les caractères spéciaux XML
        ligne_escape = ligne.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # Détecter les titres de différentes façons
        est_titre = False

        # 1. Titres avec flèches (► ou ▶)
        if ligne.startswith('►') or ligne.startswith('▶'):
            ligne_escape = ligne_escape.replace('►', '').replace('▶', '').strip()
            est_titre = True

        # 2. Titres numérotés (ex: "1. Analyse des produits")
        elif len(ligne) > 0 and len(ligne) < 80 and ligne[0].isdigit() and '. ' in ligne[:5]:
            est_titre = True

        # 3. Titres se terminant par ":" et courts
        elif len(ligne) < 100 and ligne.endswith(':'):
            ligne_escape = ligne_escape.rstrip(':')
            est_titre = True

        # 4. Lignes courtes tout en majuscules (ex: "ANALYSE COMPARATIVE")
        elif len(ligne) < 80 and ligne.isupper() and not ligne.startswith('•'):
            est_titre = True

        # Appliquer le style approprié
        if est_titre:
            elements.append(Paragraph(ligne_escape, styles['SousTitreTexte']))
        elif ligne.startswith('•'):
            elements.append(Paragraph(ligne_escape, styles['CorpsTexte']))
        else:
            elements.append(Paragraph(ligne_escape, styles['CorpsTexte']))

    return elements


def creer_encadre_points_cles(titre: str, points: list, styles, couleur_fond='#f0f8ff', couleur_bordure='#3498db') -> list:
    """
    Crée un encadré avec des points clés

    Args:
        titre: Titre de l'encadré
        points: Liste de points à afficher
        styles: Styles PDF
        couleur_fond: Couleur de fond de l'encadré
        couleur_bordure: Couleur de la bordure

    Returns:
        Liste d'éléments PDF
    """
    elements = []

    # Titre de l'encadré
    elements.append(Paragraph(f"<b>{titre}</b>", styles['SousTitre']))
    elements.append(Spacer(1, 0.2*cm))

    # Créer un tableau pour l'encadré
    data = []
    for point in points:
        point_escape = point.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        data.append([Paragraph(f"▸  {point_escape}", styles['CorpsTexte'])])

    table = Table(data, colWidths=[16*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor(couleur_fond)),
        ('BOX', (0, 0), (-1, -1), 1.5, HexColor(couleur_bordure)),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))

    return elements


def creer_tableau_evolution(bilans: list, postes_config: list, styles, par_habitant: bool = True) -> Table:
    """
    Crée un tableau d'évolution pour des postes clés

    Args:
        bilans: Liste des bilans
        postes_config: Liste de tuples (nom_poste, chemin_json)
        styles: Styles PDF
        par_habitant: Si True, affiche les valeurs par habitant (€/hab)

    Returns:
        Table ReportLab
    """
    # En-tête
    annees = [str(b['annee']) for b in bilans]
    header = ['Poste'] + annees + ['Évolution']

    data = [header]

    # Lignes de données
    for nom_poste, chemin in postes_config:
        ligne = [nom_poste]

        valeurs = []
        for bilan in bilans:
            keys = chemin.split('.')
            valeur = bilan['data']

            for key in keys:
                if isinstance(valeur, dict) and key in valeur:
                    valeur = valeur[key]
                else:
                    valeur = None
                    break

            valeur_k = valeur if valeur is not None else 0

            # Convertir en €/hab si demandé
            if par_habitant:
                population = bilan['data'].get('metadata', {}).get('population')
                if population and population > 0:
                    valeur_finale = (valeur_k * 1000) / population
                    valeurs.append(valeur_finale)
                    ligne.append(f"{valeur_finale:.0f} €/hab")
                else:
                    valeurs.append(0)
                    ligne.append("—")
            else:
                valeurs.append(valeur_k)
                ligne.append(f"{valeur_k:.0f} k€")

        # Calcul évolution
        if valeurs[0] != 0:
            evolution_pct = ((valeurs[-1] - valeurs[0]) / valeurs[0]) * 100
            ligne.append(f"{evolution_pct:+.1f}%")
        else:
            ligne.append("—")

        data.append(ligne)

    # Créer le tableau
    table = Table(data, repeatRows=1)

    table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

        # Corps
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f8f9fa')]),

        # Bordures
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdc3c7')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#2c3e50')),

        # Colonne évolution
        ('FONTNAME', (-1, 1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (-1, 1), (-1, -1), HexColor('#ecf0f1')),
    ]))

    return table


def generer_rapport_pdf_multi_annees(
    dossier_bilans: str,
    fichier_sortie: str = "output/rapport_multi_annees.pdf",
    fichier_excel: str = "PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx"
):
    """
    Génère le rapport PDF complet d'analyse multi-années en lisant l'Excel

    Args:
        dossier_bilans: Dossier contenant les PDFs des bilans
        fichier_sortie: Chemin du PDF à générer
        fichier_excel: Fichier Excel contenant les analyses
    """
    print("\n" + "="*80)
    print("GÉNÉRATION RAPPORT D'ANALYSE MULTI-ANNÉES")
    print("="*80 + "\n")

    # 1. Chargement des données
    print("[ÉTAPE 1/5] Chargement des données...")

    # Charger les bilans
    bilans = charger_bilans_multi_annees(dossier_bilans)
    print(f"  [OK] {len(bilans)} bilans chargés")

    # Charger l'Excel avec les analyses
    df_excel = pd.read_excel(fichier_excel)
    df_multi = df_excel[df_excel['Type_Rapport'] == 'Multi-annees'].copy()
    print(f"  [OK] Excel chargé: {len(df_multi)} analyses multi-années")

    # Créer un dictionnaire des analyses par nom de poste
    analyses_excel = {}
    for _, row in df_multi.iterrows():
        nom_poste = row['Nom_Poste']
        reponse = row.get('Reponse_Attendue', '')
        if pd.notna(reponse) and reponse.strip():
            analyses_excel[nom_poste] = reponse
        else:
            analyses_excel[nom_poste] = "Analyse non disponible"

    # Mapping entre les anciens noms et les nouveaux noms de l'Excel
    analyses = {
        'synthese_globale': analyses_excel.get('Analyse_tendances_globales', 'Analyse non disponible'),
        'poste_produits_fonctionnement': analyses_excel.get('Produits_fonctionnement_evolution', 'Analyse non disponible'),
        'poste_charges_fonctionnement': analyses_excel.get('Charges_fonctionnement_evolution', 'Analyse non disponible'),
        'poste_charges_de_personnel': analyses_excel.get('Charges_personnel_evolution', 'Analyse non disponible'),
        'poste_caf_brute': analyses_excel.get('CAF_brute_evolution', 'Analyse non disponible'),
        'poste_depenses_dequipement': analyses_excel.get('Depenses_equipement_evolution', 'Analyse non disponible'),
        'poste_encours_dette': analyses_excel.get('Encours_dette_evolution', 'Analyse non disponible')    }

    print(f"  [OK] {len([v for v in analyses.values() if v != 'Analyse non disponible'])} analyses disponibles")

    # 2. Analyse comparative
    print("\n[ÉTAPE 2/5] Analyse comparative...")
    comparaisons = comparer_bilans_annee_par_annee(bilans)
    tendances = detecter_tendances_et_anomalies(comparaisons)
    ratios = calculer_ratios_evolutifs(bilans)

    # 3. Génération des graphiques
    print("\n[ÉTAPE 3/5] Génération des graphiques...")
    graphiques = generer_tous_graphiques_standard(bilans, ratios['ratios_par_annee'])

    # 4. Construction du PDF
    print("\n[ÉTAPE 4/5] Construction du rapport PDF...")

    os.makedirs(os.path.dirname(fichier_sortie), exist_ok=True)
    doc = SimpleDocTemplate(
        fichier_sortie,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    story = []
    styles = creer_styles()

    metadata = comparaisons['metadata']

    # ============ PAGE DE GARDE ============
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(
        "RAPPORT D'ANALYSE BUDGÉTAIRE<br/>COMPARATIVE MULTI-ANNÉES",
        styles['TitrePrincipal']
    ))
    story.append(Spacer(1, 1.5*cm))

    story.append(Paragraph(f"<b>{metadata['commune']}</b>", styles['MetadataGras']))
    story.append(Paragraph(
        f"Période d'analyse : {metadata['periode_debut']} - {metadata['periode_fin']}",
        styles['Metadata']
    ))
    story.append(Paragraph(
        f"Nombre d'exercices analysés : {metadata['nb_annees']}",
        styles['Metadata']
    ))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        styles['Metadata']
    ))

    story.append(PageBreak())

    # ============ SYNTHÈSE FINANCIÈRE D'ENSEMBLE (EN TÊTE) ============
    story.append(Paragraph("SYNTHÈSE FINANCIÈRE D'ENSEMBLE", styles['TitreSection']))
    story.append(Spacer(1, 0.5*cm))

    # Introduction
    intro_synthese = (
        f"Le présent rapport analyse l'évolution financière de la commune de {metadata['commune']} "
        f"sur la période {metadata['periode_debut']}-{metadata['periode_fin']}. "
        f"Cette analyse comparative porte sur {metadata['nb_annees']} exercices budgétaires et "
        f"examine les principales évolutions des sections de fonctionnement et d'investissement, "
        f"ainsi que la capacité d'autofinancement et la soutenabilité de l'endettement."
    )
    story.append(Paragraph(intro_synthese, styles['CorpsTexte']))
    story.append(Spacer(1, 0.5*cm))

    if 'synthese_globale' in analyses:
        story.extend(convertir_texte_en_paragraphes(analyses['synthese_globale'], styles))

    # Points de situation à signaler (synthèse) - en encadré
    if 'points_attention' in analyses:
        story.append(Spacer(1, 0.5*cm))
        # Extraire les points d'attention depuis le texte
        points_attention_texte = analyses.get('points_attention', '')
        points_liste = [ligne.strip().replace('•', '').strip()
                       for ligne in points_attention_texte.split('\n')
                       if ligne.strip() and ligne.strip().startswith('•')]

        if points_liste:
            story.extend(creer_encadre_points_cles(
                "Points de situation à signaler",
                points_liste,
                styles,
                couleur_fond='#fff3cd',
                couleur_bordure='#f39c12'
            ))

    story.append(PageBreak())

    # ============ SECTION DE FONCTIONNEMENT ============
    story.append(Paragraph("SECTION DE FONCTIONNEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.3*cm))

    # Sous-section Produits
    story.append(Paragraph("Évolution des produits de fonctionnement", styles['SousTitre']))

    # Graphique Produits vs Charges (vue d'ensemble)
    if 'produits_charges' in graphiques and os.path.exists(graphiques['produits_charges']):
        img = Image(graphiques['produits_charges'], width=16*cm, height=8*cm)
        story.append(img)
        story.append(Paragraph(
            "Évolution comparée des produits et charges de fonctionnement (par habitant)",
            styles['Legende']
        ))

    # Tableau évolution avec analyses intégrées
    postes_fonct = [
        ("Produits de fonctionnement", "fonctionnement.produits.total.montant_k"),
        ("Charges de fonctionnement", "fonctionnement.charges.total.montant_k"),
        ("Résultat de fonctionnement", "fonctionnement.resultat.montant_k"),
    ]
    story.append(Spacer(1, 0.5*cm))
    story.append(creer_tableau_evolution(bilans, postes_fonct, styles))

    # Analyse des produits
    story.append(Spacer(1, 0.5*cm))
    if 'poste_produits_fonctionnement' in analyses:
        story.extend(convertir_texte_en_paragraphes(analyses['poste_produits_fonctionnement'], styles))

    # Sous-section Charges
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Évolution des charges de fonctionnement", styles['SousTitre']))

    if 'poste_charges_fonctionnement' in analyses:
        story.extend(convertir_texte_en_paragraphes(analyses['poste_charges_fonctionnement'], styles))

    if 'poste_charges_de_personnel' in analyses:
        story.append(Spacer(1, 0.3*cm))
        story.extend(convertir_texte_en_paragraphes(analyses['poste_charges_de_personnel'], styles))

    # Sous-section Résultat de fonctionnement
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Résultat de fonctionnement", styles['SousTitre']))

    if 'resultat' in graphiques and os.path.exists(graphiques['resultat']):
        img = Image(graphiques['resultat'], width=16*cm, height=8*cm)
        story.append(img)
        story.append(Paragraph("Évolution du résultat de fonctionnement (par habitant)", styles['Legende']))

    # Transition narrative vers CAF
    story.append(Spacer(1, 0.3*cm))
    transition_caf = "L'évolution du résultat de fonctionnement impacte directement la capacité d'autofinancement de la collectivité."
    story.append(Paragraph(transition_caf, styles['CorpsTexte']))

    story.append(PageBreak())

    # ============ CAPACITÉ D'AUTOFINANCEMENT ============
    story.append(Paragraph("CAPACITÉ D'AUTOFINANCEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.3*cm))

    if 'caf' in graphiques and os.path.exists(graphiques['caf']):
        img = Image(graphiques['caf'], width=16*cm, height=8*cm)
        story.append(img)
        story.append(Paragraph("Évolution de la CAF brute et nette (par habitant)", styles['Legende']))

    postes_caf = [
        ("CAF brute", "autofinancement.caf_brute.montant_k"),
        ("CAF nette", "autofinancement.caf_nette.montant_k"),
    ]
    story.append(Spacer(1, 0.5*cm))
    story.append(creer_tableau_evolution(bilans, postes_caf, styles))

    # Analyse CAF
    if 'poste_caf_brute' in analyses:
        story.append(Spacer(1, 0.5*cm))
        story.extend(convertir_texte_en_paragraphes(analyses['poste_caf_brute'], styles))

    # Transition vers investissement
    story.append(Spacer(1, 0.3*cm))
    transition_invest = "La CAF nette constitue la ressource propre disponible pour financer les investissements, après remboursement du capital de la dette."
    story.append(Paragraph(transition_invest, styles['CorpsTexte']))

    story.append(PageBreak())

    # ============ SECTION D'INVESTISSEMENT ============
    story.append(Paragraph("SECTION D'INVESTISSEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.3*cm))

    # Dépenses d'équipement
    story.append(Paragraph("Dépenses d'équipement", styles['SousTitre']))

    if 'depenses_equip' in graphiques and os.path.exists(graphiques['depenses_equip']):
        img = Image(graphiques['depenses_equip'], width=16*cm, height=8*cm)
        story.append(img)
        story.append(Paragraph("Évolution des dépenses d'équipement (par habitant)", styles['Legende']))

    postes_invest = [
        ("Dépenses d'équipement", "investissement.emplois.depenses_equipement.montant_k"),
        ("Emprunts contractés", "investissement.ressources.emprunts.montant_k"),
        ("Subventions reçues", "investissement.ressources.subventions_recues.montant_k"),
    ]
    story.append(Spacer(1, 0.5*cm))
    story.append(creer_tableau_evolution(bilans, postes_invest, styles))

    # Analyse investissement
    if 'poste_depenses_dequipement' in analyses:
        story.append(Spacer(1, 0.5*cm))
        story.extend(convertir_texte_en_paragraphes(analyses['poste_depenses_dequipement'], styles))

    # Articulation financement
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Financement des investissements", styles['SousTitre']))
    articulation_financement = (
        "Le financement des investissements s'articule entre autofinancement (CAF nette), "
        "emprunts contractés et subventions d'investissement reçues. L'équilibre entre ces trois sources "
        "conditionne la soutenabilité financière de la politique d'équipement."
    )
    story.append(Paragraph(articulation_financement, styles['CorpsTexte']))

    # Transition vers endettement
    story.append(Spacer(1, 0.3*cm))
    transition_dette = "Le recours à l'emprunt pour financer les investissements impacte directement l'évolution de l'encours de dette."
    story.append(Paragraph(transition_dette, styles['CorpsTexte']))

    story.append(PageBreak())

    # ============ ENDETTEMENT ============
    story.append(Paragraph("ENDETTEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.3*cm))

    # Encours de dette
    story.append(Paragraph("Évolution de l'encours de dette", styles['SousTitre']))

    if 'dette' in graphiques and os.path.exists(graphiques['dette']):
        img = Image(graphiques['dette'], width=16*cm, height=8*cm)
        story.append(img)
        story.append(Paragraph("Évolution de l'encours de dette (par habitant)", styles['Legende']))

    postes_dette = [
        ("Encours de dette", "endettement.encours_total.montant_k"),
    ]
    story.append(Spacer(1, 0.5*cm))
    story.append(creer_tableau_evolution(bilans, postes_dette, styles))

    # Analyse encours
    if 'poste_encours_dette' in analyses:
        story.append(Spacer(1, 0.5*cm))
        story.extend(convertir_texte_en_paragraphes(analyses['poste_encours_dette'], styles))

    # Capacité de désendettement
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Capacité de désendettement", styles['SousTitre']))

    if 'capacite_desendettement' in graphiques and os.path.exists(graphiques['capacite_desendettement']):
        img = Image(graphiques['capacite_desendettement'], width=16*cm, height=8*cm)
        story.append(img)
        story.append(Paragraph(
            "Capacité de désendettement (en années) - Seuil prudentiel : 12 ans",
            styles['Legende']
        ))

    # Appréciation de la soutenabilité
    story.append(Spacer(1, 0.3*cm))
    soutenabilite = (
        "La capacité de désendettement, ratio entre l'encours de dette et la CAF brute, "
        "constitue l'indicateur central de soutenabilité financière. Un ratio inférieur à 12 ans "
        "traduit une situation d'endettement soutenable."
    )
    story.append(Paragraph(soutenabilite, styles['CorpsTexte']))

    story.append(PageBreak())

    # ============ RATIOS FINANCIERS DE SYNTHÈSE ============
    story.append(Paragraph("RATIOS FINANCIERS DE SYNTHÈSE", styles['TitreSection']))
    story.append(Spacer(1, 0.3*cm))

    # Taux d'épargne brute
    story.append(Paragraph("Taux d'épargne brute", styles['SousTitre']))

    if 'epargne' in graphiques and os.path.exists(graphiques['epargne']):
        img = Image(graphiques['epargne'], width=16*cm, height=8*cm)
        story.append(img)
        story.append(Paragraph("Évolution du taux d'épargne brute (CAF brute / Produits de fonctionnement)", styles['Legende']))

    story.append(Spacer(1, 0.3*cm))
    explication_epargne = (
        "Le taux d'épargne brute mesure la part des produits de fonctionnement dégagée sous forme de CAF brute. "
        "Il traduit la capacité de la collectivité à dégager des marges de manœuvre financières sur son fonctionnement."
    )
    story.append(Paragraph(explication_epargne, styles['CorpsTexte']))


    story.append(PageBreak())



    # ============ CONSTRUCTION DU PDF ============
    doc.build(story)

    taille_kb = os.path.getsize(fichier_sortie) / 1024

    print("\n" + "="*80)
    print(f"[OK] RAPPORT GENERE AVEC SUCCES")
    print(f"  Fichier : {fichier_sortie}")
    print(f"  Taille : {taille_kb:.1f} KB")
    print(f"  Commune : {metadata['commune']}")
    print(f"  Periode : {metadata['periode_debut']}-{metadata['periode_fin']}")
    print(f"  Graphiques : {len(graphiques)}")
    print(f"  Analyses LLM : {len(analyses)}")
    print("="*80 + "\n")


def generer_rapport_pdf():
    """Point d'entrée pour l'import depuis workflow_complet.py"""
    dossier = "docs/bilans_multi_annees"
    fichier_sortie = "output/rapport_analyse_multi_annees.pdf"
    fichier_excel = "PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx"

    generer_rapport_pdf_multi_annees(dossier, fichier_sortie, fichier_excel)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Génère un rapport d'analyse comparative multi-années pour bilans communaux"
    )
    parser.add_argument(
        "dossier_bilans",
        help="Dossier contenant les fichiers PDF des bilans (minimum 2)"
    )
    parser.add_argument(
        "-o", "--output",
        default="output/rapport_multi_annees.pdf",
        help="Fichier PDF de sortie (défaut: output/rapport_multi_annees.pdf)"
    )
    parser.add_argument(
        "-e", "--excel",
        default="PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx",
        help="Fichier Excel contenant les analyses (défaut: PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx)"
    )

    args = parser.parse_args()

    try:
        generer_rapport_pdf_multi_annees(
            args.dossier_bilans,
            args.output,
            args.excel
        )
    except Exception as e:
        print(f"\n[ERREUR] {e}\n")
        sys.exit(1)
