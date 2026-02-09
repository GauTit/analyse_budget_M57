"""
Génère un rapport PDF détaillé au format DGFiP avec analyse LLM
Version PDF professionnelle avec mise en forme
"""

import sys
import os
import json
import requests

sys.path.insert(0, 'src')

from generators.generer_json_enrichi import generer_json_enrichi
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor
from datetime import datetime


def appeler_ollama(prompt, model="mistral", verbose=False):
    """Appelle Ollama"""
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.2
    }

    if verbose:
        print(f"      Envoi requete ({len(prompt)} car)...", end=" ")

    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        texte = response.json().get("response", "")
        if verbose:
            print(f"OK ({len(texte)} car)")
        return texte
    except Exception as e:
        if verbose:
            print(f"ERREUR: {e}")
        return None


def generer_section_template(titre, donnees, model="mistral", verbose=False):
    """Génère une section avec template STRICT format DGFiP"""

    prompt = f"""Tu es un assistant qui génère des sections de rapport budgétaire au format DGFiP.

RÈGLES STRICTES:
- Utilise le format: "► Titre" pour chaque sous-section
- Compare TOUJOURS avec la Moyenne de la strate au format: "(XXX€/hab. commune – YYY€/hab. Moyenne de la strate)"
- Utilise les chiffres EXACTS fournis
- Mentionne les écarts en % quand ils sont significatifs
- Sois factuel et précis
- Rédige en français professionnel

DONNÉES FOURNIES:
{json.dumps(donnees, ensure_ascii=False, indent=2)}

SECTION À GÉNÉRER: {titre}

Génère la section au format DGFiP avec bullets (►) et comparaisons systématiques à la strate."""

    return appeler_ollama(prompt, model, verbose)


def generer_analyse_globale(json_complet, model="mistral", verbose=False):
    """Génère analyse globale avec liberté pour le LLM"""

    prompt = f"""Tu es un expert en finances publiques locales. Analyse la situation financière GLOBALE de cette commune.

DONNÉES COMPLÈTES:
{json.dumps(json_complet, ensure_ascii=False, indent=2)}

TÂCHE:
1. Fais une analyse TRANSVERSALE de la situation financière
2. Identifie les LIENS entre les différents postes
3. Identifie les POINTS D'ALERTE et les POINTS FORTS
4. Propose des RECOMMANDATIONS concrètes et priorisées

FORMAT ATTENDU:
► SITUATION FINANCIÈRE GLOBALE
[Ton analyse globale en 2-3 paragraphes]

► POINTS D'ALERTE
[Liste les problèmes identifiés]

► POINTS FORTS
[Liste les points positifs]

► RECOMMANDATIONS
[3-5 recommandations concrètes et actionnables]

Sois franc et factuel."""

    return appeler_ollama(prompt, model, verbose)


def creer_styles():
    """Crée les styles pour le PDF"""
    styles = getSampleStyleSheet()

    # Style titre principal
    styles.add(ParagraphStyle(
        name='TitrePrincipal',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    # Style titre de section
    styles.add(ParagraphStyle(
        name='TitreSection',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=HexColor('#2c3e50'),
        spaceAfter=15,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=HexColor('#2c3e50'),
        borderPadding=5
    ))

    # Style sous-titre (pour les ►)
    styles.add(ParagraphStyle(
        name='SousTitre',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        leftIndent=0
    ))

    # Style corps de texte
    styles.add(ParagraphStyle(
        name='CorpsTexte',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14,
        leftIndent=10
    ))

    # Style métadonnées
    styles.add(ParagraphStyle(
        name='Metadata',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#555555'),
        alignment=TA_CENTER,
        spaceAfter=5
    ))

    return styles


def convertir_texte_en_paragraphes(texte, styles):
    """Convertit le texte brut en éléments PDF avec styles appropriés"""
    elements = []

    lignes = texte.split('\n')

    for ligne in lignes:
        ligne = ligne.strip()

        if not ligne:
            elements.append(Spacer(1, 0.3*cm))
            continue

        # Détecter les bullets ►
        if ligne.startswith('►'):
            # Nettoyer et formater
            ligne_clean = ligne.replace('►', '▶').strip()
            elements.append(Paragraph(ligne_clean, styles['SousTitre']))

        # Lignes normales
        else:
            # Échapper les caractères spéciaux pour ReportLab
            ligne_escape = ligne.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(ligne_escape, styles['CorpsTexte']))

    return elements


def generer_rapport_pdf_complet(fichier_pdf, model="mistral", fichier_sortie="output/rapport_detaille_llm.pdf"):
    """Génère le rapport PDF complet"""

    print("\n" + "="*70)
    print("GENERATION RAPPORT PDF DETAILLE FORMAT DGFiP + ANALYSE IA")
    print("="*70 + "\n")

    # 1. JSON enrichi
    print("[1/3] Generation du JSON enrichi...")
    json_data = generer_json_enrichi(fichier_pdf)
    print(f"      OK\n")

    # 2. Créer le document PDF
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

    # Page de garde
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("RAPPORT D'ANALYSE BUDGÉTAIRE DÉTAILLÉ", styles['TitrePrincipal']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"<b>{json_data['metadata']['commune']}</b>", styles['Metadata']))
    story.append(Paragraph(f"Exercice {json_data['metadata']['exercice']}", styles['Metadata']))
    story.append(Paragraph(f"Population : {json_data['metadata']['population']} habitants", styles['Metadata']))
    story.append(Paragraph(f"Strate : {json_data['metadata']['strate']['libelle']}", styles['Metadata']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Metadata']))
    story.append(Paragraph("<i>Analyse assistée par Intelligence Artificielle (Mistral 7B)</i>", styles['Metadata']))
    story.append(PageBreak())

    # 3. Générer les sections avec LLM
    print(f"[2/3] Generation des sections avec LLM ({model})...\n")

    # FONCTIONNEMENT
    story.append(Paragraph("FONCTIONNEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.5*cm))

    sections_fonctionnement = [
        ("Total des produits de fonctionnement", {
            "total": json_data['fonctionnement']['produits']['total'],
            "produits_caf": json_data['fonctionnement']['produits']['produits_caf']
        }),
        ("Impôts locaux", json_data['fonctionnement']['produits']['impots_locaux']),
        ("Autres impôts et taxes", json_data['fonctionnement']['produits']['autres_impots_taxes']),
        ("Dotation globale de fonctionnement", json_data['fonctionnement']['produits']['dgf']),
        ("Produits des services et du domaine", json_data['fonctionnement']['produits']['produits_services_domaine']),
        ("Total des charges de fonctionnement", {
            "total": json_data['fonctionnement']['charges']['total'],
            "charges_caf": json_data['fonctionnement']['charges']['charges_caf']
        }),
        ("Charges de personnel", json_data['fonctionnement']['charges']['charges_personnel']),
        ("Achats et charges externes", json_data['fonctionnement']['charges']['achats_charges_externes']),
        ("Charges financières", json_data['fonctionnement']['charges']['charges_financieres']),
        ("Contingents", json_data['fonctionnement']['charges']['contingents']),
        ("Subventions versées", json_data['fonctionnement']['charges']['subventions_versees']),
        ("Résultat comptable", json_data['fonctionnement']['resultat'])
    ]

    for i, (titre, donnees) in enumerate(sections_fonctionnement, 1):
        print(f"      [{i}/{len(sections_fonctionnement)}] {titre}...", end=" ")
        texte = generer_section_template(titre, donnees, model, verbose=False)
        if texte:
            story.extend(convertir_texte_en_paragraphes(texte, styles))
            story.append(Spacer(1, 0.5*cm))
            print("OK")
        else:
            print("ERREUR")

    story.append(PageBreak())

    # INVESTISSEMENT
    story.append(Paragraph("INVESTISSEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.5*cm))

    sections_invest = [
        ("Emprunts bancaires", json_data['investissement']['ressources']['emprunts']),
        ("Subventions reçues", json_data['investissement']['ressources']['subventions_recues']),
        ("FCTVA", json_data['investissement']['ressources']['fctva']),
        ("Dépenses d'équipement", json_data['investissement']['emplois']['depenses_equipement']),
        ("Remboursement d'emprunts", json_data['investissement']['emplois']['remboursement_emprunts']),
        ("Résultat d'ensemble", json_data['investissement']['financement'])
    ]

    for i, (titre, donnees) in enumerate(sections_invest, 1):
        print(f"      [{len(sections_fonctionnement)+i}/"
              f"{len(sections_fonctionnement)+len(sections_invest)}] {titre}...", end=" ")
        texte = generer_section_template(titre, donnees, model, verbose=False)
        if texte:
            story.extend(convertir_texte_en_paragraphes(texte, styles))
            story.append(Spacer(1, 0.5*cm))
            print("OK")
        else:
            print("ERREUR")

    story.append(PageBreak())

    # AUTOFINANCEMENT
    story.append(Paragraph("AUTOFINANCEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.5*cm))

    sections_autofinancement = [
        ("Excédent brut de fonctionnement", json_data['autofinancement']['ebf']),
        ("Capacité d'autofinancement (CAF)", json_data['autofinancement']['caf_brute']),
        ("CAF nette", json_data['autofinancement']['caf_nette'])
    ]

    for i, (titre, donnees) in enumerate(sections_autofinancement, 1):
        texte = generer_section_template(titre, donnees, model, verbose=False)
        if texte:
            story.extend(convertir_texte_en_paragraphes(texte, styles))
            story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # ENDETTEMENT
    story.append(Paragraph("ENDETTEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.5*cm))

    sections_endettement = [
        ("Encours total de la dette", {
            **json_data['endettement']['encours_total'],
            "ratios": json_data['endettement']['ratios']
        }),
        ("Annuité de la dette", json_data['endettement']['annuite']),
        ("Fonds de roulement", json_data['endettement']['fonds_roulement'])
    ]

    for i, (titre, donnees) in enumerate(sections_endettement, 1):
        texte = generer_section_template(titre, donnees, model, verbose=False)
        if texte:
            story.extend(convertir_texte_en_paragraphes(texte, styles))
            story.append(Spacer(1, 0.5*cm))

    print(f"\n      OK - Toutes sections generees\n")

    # ANALYSE GLOBALE IA
    story.append(PageBreak())
    story.append(Paragraph("ANALYSE GLOBALE ET RECOMMANDATIONS", styles['TitreSection']))
    story.append(Spacer(1, 0.5*cm))

    print("[3/3] Generation de l'analyse globale IA...")
    analyse = generer_analyse_globale(json_data, model, verbose=True)

    if analyse:
        story.extend(convertir_texte_en_paragraphes(analyse, styles))
        print("      OK\n")
    else:
        print("      ERREUR\n")

    # Générer le PDF
    print("Creation du fichier PDF...", end=" ")
    doc.build(story)
    print("OK\n")

    print("="*70)
    print(f"PDF GENERE: {fichier_sortie}")
    taille = os.path.getsize(fichier_sortie) / 1024
    print(f"Taille: {taille:.1f} KB")
    print("="*70 + "\n")

    return fichier_sortie


if __name__ == "__main__":
    generer_rapport_pdf_complet("docs/bilan.pdf", model="mistral")
