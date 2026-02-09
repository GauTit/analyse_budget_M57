"""
VERSION CORRIGÉE - Génère rapport PDF avec prompts ULTRA-STRICTS
Évite toutes les erreurs du LLM (placeholders, mauvaises interprétations, etc.)
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
        "temperature": 0.1  # TRÈS BAS pour éviter l'invention
    }

    if verbose:
        print(f"      Envoi requete...", end=" ")

    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        texte = response.json().get("response", "")
        if verbose:
            print(f"OK")
        return texte
    except Exception as e:
        if verbose:
            print(f"ERREUR: {e}")
        return None


def generer_section_ultra_strict(titre, donnees, model="mistral", verbose=False):
    """
    Génère une section avec prompt ULTRA-STRICT
    Fournit un EXEMPLE CONCRET pour éviter toute confusion
    """

    # Extraire les données clés pour l'exemple
    montant_k = donnees.get('montant_k', donnees.get('total', {}).get('montant_k', 0))
    par_hab = donnees.get('par_hab', donnees.get('total', {}).get('par_hab', 0))
    moyenne_strate = donnees.get('moyenne_strate_hab', donnees.get('total', {}).get('moyenne_strate_hab', 0))

    comparaison = donnees.get('comparaison', donnees.get('total', {}).get('comparaison', {}))
    if comparaison:
        texte_comparaison = comparaison.get('texte', f"{par_hab}€/hab commune – {moyenne_strate}€/hab Moyenne de la strate")
        ecart_pct = comparaison.get('ecart_pct', 0)
        niveau = comparaison.get('niveau', 'au niveau de')
    else:
        texte_comparaison = f"{par_hab}€/hab commune – {moyenne_strate}€/hab Moyenne de la strate"
        ecart_pct = round((par_hab - moyenne_strate) / moyenne_strate * 100, 1) if moyenne_strate else 0
        niveau = "supérieur à" if ecart_pct > 5 else "au niveau de"

    prompt = f"""Tu es un rédacteur de rapports budgétaires DGFiP.

INTERDICTIONS ABSOLUES:
❌ N'utilise JAMAIS de placeholders comme XXX, YYY, [...]
❌ N'utilise JAMAIS le mot "café" (CAF = Capacité d'Autofinancement)
❌ N'invente AUCUN chiffre, utilise UNIQUEMENT ceux fournis ci-dessous
❌ Ne laisse AUCUNE variable non remplacée comme {{variable}}

RÈGLES OBLIGATOIRES:
✅ Commence TOUJOURS par "► " (bullet point)
✅ Utilise le format exact: "(XXX€/hab. commune – YYY€/hab. Moyenne de la strate)" AVEC LES VRAIS CHIFFRES
✅ Mentionne l'écart en % si significatif (>5%)
✅ Sois factuel, précis, professionnel

EXEMPLE CONCRET À SUIVRE:
► Charges de personnel
Les charges de personnel représentent 420 k€ pour la commune, soit 917€/hab. (917€/hab. commune – 797€/hab. Moyenne de la strate).
Ce montant est nettement supérieur à la moyenne de strate (+15%), représentant 54,9% des charges totales.

DONNÉES POUR CETTE SECTION:
{json.dumps(donnees, ensure_ascii=False, indent=2)}

SECTION À GÉNÉRER: {titre}

INFORMATIONS CLÉS:
- Montant: {montant_k} k€
- Par habitant: {par_hab}€/hab
- Moyenne strate: {moyenne_strate}€/hab
- Comparaison: {texte_comparaison}
- Écart: {ecart_pct:+.1f}%
- Niveau: {niveau} la moyenne de strate

Génère MAINTENANT la section en suivant l'exemple. Utilise UNIQUEMENT les chiffres fournis ci-dessus."""

    return appeler_ollama(prompt, model, verbose)


def generer_analyse_globale_stricte(json_complet, model="mistral", verbose=False):
    """Génère analyse globale avec consignes strictes"""

    # Extraire les chiffres clés
    commune = json_complet['metadata']['commune']
    resultat_k = json_complet['fonctionnement']['resultat']['montant_k']
    caf_brute_k = json_complet['autofinancement']['caf_brute']['montant_k']
    caf_nette_k = json_complet['autofinancement']['caf_nette']['montant_k']
    dette_k = json_complet['endettement']['encours_total']['montant_k']
    ratio_dette_caf = json_complet['endettement']['ratios']['capacite_desendettement_annees']

    prompt = f"""Tu es un expert en finances publiques locales.

INTERDICTIONS:
❌ N'invente AUCUN chiffre
❌ Ne calcule rien toi-même
❌ Utilise UNIQUEMENT les données fournies

DONNÉES CLÉS DE LA COMMUNE {commune}:
- Résultat de fonctionnement: {resultat_k} k€
- CAF brute: {caf_brute_k} k€
- CAF nette: {caf_nette_k} k€
- Dette totale: {dette_k} k€
- Capacité de désendettement: {ratio_dette_caf:.1f} années

DONNÉES COMPLÈTES:
{json.dumps(json_complet, ensure_ascii=False, indent=2)}

TÂCHE:
Rédige une analyse SYNTHÉTIQUE et FACTUELLE avec:

1. SITUATION GLOBALE (2 paragraphes max)
   - Utilise les chiffres clés ci-dessus
   - Qualifie la situation (bonne/moyenne/préoccupante)

2. POINTS D'ALERTE (liste à puces)
   - Identifie 2-3 problèmes majeurs avec chiffres précis

3. POINTS FORTS (liste à puces)
   - Identifie 2-3 points positifs avec chiffres précis

4. RECOMMANDATIONS (3 recommandations max)
   - Concrètes et actionnables
   - Liées aux données observées

FORMAT OBLIGATOIRE:
► SITUATION FINANCIÈRE GLOBALE
[Texte]

► POINTS D'ALERTE
• [Point 1]
• [Point 2]

► POINTS FORTS
• [Point 1]
• [Point 2]

► RECOMMANDATIONS
1. [Recommandation 1]
2. [Recommandation 2]
3. [Recommandation 3]

Génère MAINTENANT."""

    return appeler_ollama(prompt, model, verbose)


def creer_styles():
    """Crée les styles pour le PDF"""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='TitrePrincipal',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

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

    styles.add(ParagraphStyle(
        name='CorpsTexte',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=14,
        leftIndent=10
    ))

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
    """Convertit texte en éléments PDF"""
    elements = []
    lignes = texte.split('\n')

    for ligne in lignes:
        ligne = ligne.strip()

        if not ligne:
            elements.append(Spacer(1, 0.3*cm))
            continue

        if ligne.startswith('►') or ligne.startswith('▶'):
            ligne_clean = ligne.replace('►', '▶').strip()
            elements.append(Paragraph(ligne_clean, styles['SousTitre']))
        else:
            ligne_escape = ligne.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(ligne_escape, styles['CorpsTexte']))

    return elements


def generer_rapport_pdf_corrige(fichier_pdf, model="mistral", fichier_sortie="output/rapport_detaille_corrige.pdf"):
    """Génère le rapport PDF CORRIGÉ avec prompts ultra-stricts"""

    print("\n" + "="*70)
    print("GENERATION RAPPORT PDF CORRIGE - PROMPTS ULTRA-STRICTS")
    print("="*70 + "\n")

    # 1. JSON enrichi
    print("[1/3] Generation du JSON enrichi...")
    json_data = generer_json_enrichi(fichier_pdf)
    print(f"      OK\n")

    # 2. Créer PDF
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
    story.append(Paragraph("<i>Analyse assistée par IA - Version corrigée</i>", styles['Metadata']))
    story.append(PageBreak())

    # 3. Générer sections
    print(f"[2/3] Generation des sections (prompts ultra-stricts)...\n")

    # FONCTIONNEMENT
    story.append(Paragraph("FONCTIONNEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.5*cm))

    sections_fonctionnement = [
        ("Total des produits de fonctionnement", json_data['fonctionnement']['produits']['total']),
        ("Impôts locaux", json_data['fonctionnement']['produits']['impots_locaux']),
        ("Dotation globale de fonctionnement", json_data['fonctionnement']['produits']['dgf']),
        ("Total des charges de fonctionnement", json_data['fonctionnement']['charges']['total']),
        ("Charges de personnel", json_data['fonctionnement']['charges']['charges_personnel']),
        ("Résultat comptable", json_data['fonctionnement']['resultat'])
    ]

    for i, (titre, donnees) in enumerate(sections_fonctionnement, 1):
        print(f"      [{i}/15] {titre}...", end=" ")
        texte = generer_section_ultra_strict(titre, donnees, model, verbose=False)
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
        ("Dépenses d'équipement", json_data['investissement']['emplois']['depenses_equipement']),
        ("Subventions reçues", json_data['investissement']['ressources']['subventions_recues']),
        ("Emprunts", json_data['investissement']['ressources']['emprunts'])
    ]

    for i, (titre, donnees) in enumerate(sections_invest, 7):
        print(f"      [{i}/15] {titre}...", end=" ")
        texte = generer_section_ultra_strict(titre, donnees, model, verbose=False)
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
        ("Capacité d'autofinancement", json_data['autofinancement']['caf_brute']),
        ("CAF nette", json_data['autofinancement']['caf_nette'])
    ]

    for i, (titre, donnees) in enumerate(sections_autofinancement, 10):
        print(f"      [{i}/15] {titre}...", end=" ")
        texte = generer_section_ultra_strict(titre, donnees, model, verbose=False)
        if texte:
            story.extend(convertir_texte_en_paragraphes(texte, styles))
            story.append(Spacer(1, 0.5*cm))
            print("OK")
        else:
            print("ERREUR")

    story.append(PageBreak())

    # ENDETTEMENT
    story.append(Paragraph("ENDETTEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.5*cm))

    sections_endettement = [
        ("Encours de la dette", json_data['endettement']['encours_total']),
        ("Fonds de roulement", json_data['endettement']['fonds_roulement'])
    ]

    for i, (titre, donnees) in enumerate(sections_endettement, 13):
        print(f"      [{i}/15] {titre}...", end=" ")
        texte = generer_section_ultra_strict(titre, donnees, model, verbose=False)
        if texte:
            story.extend(convertir_texte_en_paragraphes(texte, styles))
            story.append(Spacer(1, 0.5*cm))
            print("OK")
        else:
            print("ERREUR")

    print(f"\n")

    # ANALYSE GLOBALE
    story.append(PageBreak())
    story.append(Paragraph("ANALYSE GLOBALE ET RECOMMANDATIONS", styles['TitreSection']))
    story.append(Spacer(1, 0.5*cm))

    print("[3/3] Generation analyse globale...")
    analyse = generer_analyse_globale_stricte(json_data, model, verbose=True)

    if analyse:
        story.extend(convertir_texte_en_paragraphes(analyse, styles))
        print("      OK\n")
    else:
        print("      ERREUR\n")

    # Générer PDF
    print("Creation du PDF...", end=" ")
    doc.build(story)
    print("OK\n")

    print("="*70)
    print(f"PDF GENERE: {fichier_sortie}")
    taille = os.path.getsize(fichier_sortie) / 1024
    print(f"Taille: {taille:.1f} KB")
    print("="*70 + "\n")

    return fichier_sortie


if __name__ == "__main__":
    generer_rapport_pdf_corrige("docs/bilan.pdf", model="mistral")
