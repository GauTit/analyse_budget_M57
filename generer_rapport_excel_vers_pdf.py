"""
Génération de rapport d'analyse budgétaire mono-année
à partir des réponses de l'Excel et des données du JSON enrichi

Usage:
    python generer_rapport_excel_vers_pdf.py
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime
from reportlab.pdfgen import canvas

matplotlib.use('Agg')  # Backend non-interactif

# ============================================
# CONFIGURATION
# ============================================

FICHIER_EXCEL = "PROMPTS_RAPPORT_COMPLET_ENRICHIS.xlsx"
FICHIER_JSON = "output/donnees_enrichies.json"
DOSSIER_GRAPHIQUES = "output/graphiques_mono_annee"
FICHIER_SORTIE = "output/rapport_analyse_mono_annee.pdf"


# ============================================
# EN-TÊTES ET PIEDS DE PAGE
# ============================================

class EnTetePiedPage(canvas.Canvas):
    """Classe pour gérer les en-têtes et pieds de page"""

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.commune = ""
        self.exercice = ""

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page_dict in self.pages:
            self.__dict__.update(page_dict)
            if self._pageNumber > 1:  # Pas d'en-tête sur la page de garde
                self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        # En-tête
        self.saveState()
        self.setFont('Helvetica', 9)
        self.setFillColorRGB(0.4, 0.4, 0.4)
        self.drawString(2*cm, A4[1] - 1.5*cm, f"{self.commune} - Exercice {self.exercice}")

        # Pied de page
        self.setFont('Helvetica', 9)
        self.drawRightString(A4[0] - 2*cm, 1.2*cm, f"Page {self._pageNumber - 1} / {page_count - 1}")
        self.restoreState()


# ============================================
# CRÉATION DES STYLES PDF
# ============================================

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
        leftIndent=0
    ))

    styles.add(ParagraphStyle(
        name='CorpsTexte',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8,
        leading=15,
        leftIndent=0,
        rightIndent=0,
        fontName='Times-Roman'
    ))

    styles.add(ParagraphStyle(
        name='Liste',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_LEFT,
        spaceAfter=6,
        leading=14,
        leftIndent=15,
        bulletIndent=5,
        fontName='Times-Roman'
    ))

    styles.add(ParagraphStyle(
        name='Metadata',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#000000'),
        alignment=TA_CENTER,
        spaceAfter=5,
        fontName='Times-Roman'
    ))

    styles.add(ParagraphStyle(
        name='MetadataGras',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor('#000000'),
        alignment=TA_CENTER,
        spaceAfter=8,
        fontName='Times-Bold'
    ))

    styles.add(ParagraphStyle(
        name='Legende',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#000000'),
        alignment=TA_CENTER,
        spaceAfter=12,
        spaceBefore=2,
        fontName='Times-Italic'
    ))

    return styles


# ============================================
# GÉNÉRATION DES GRAPHIQUES
# ============================================

def generer_graphique_repartition_produits(data, fichier_sortie):
    """Génère un camembert de répartition des recettes réelles de fonctionnement (en % des produits CAF)"""
    produits = data['fonctionnement']['produits']

    labels = []
    values = []
    montants = []

    # Extraire les principaux postes de produits avec leurs % du PDF
    if 'impots_locaux' in produits and 'pct_produits_caf' in produits['impots_locaux']:
        pct = produits['impots_locaux'].get('pct_produits_caf')
        montant = produits['impots_locaux'].get('montant_k', 0)
        if pct is not None and pct > 0:
            labels.append('Impôts locaux')
            values.append(pct)
            montants.append(montant)

    if 'dgf' in produits and 'pct_produits_caf' in produits['dgf']:
        pct = produits['dgf'].get('pct_produits_caf')
        montant = produits['dgf'].get('montant_k', 0)
        if pct is not None and pct > 0:
            labels.append('DGF')
            values.append(pct)
            montants.append(montant)

    if 'autres_impots_taxes' in produits and 'pct_produits_caf' in produits['autres_impots_taxes']:
        pct = produits['autres_impots_taxes'].get('pct_produits_caf')
        montant = produits['autres_impots_taxes'].get('montant_k', 0)
        if pct is not None and pct > 0:
            labels.append('Autres impôts et taxes')
            values.append(pct)
            montants.append(montant)

    if 'produits_services_domaine' in produits and 'pct_produits_caf' in produits['produits_services_domaine']:
        pct = produits['produits_services_domaine'].get('pct_produits_caf')
        montant = produits['produits_services_domaine'].get('montant_k', 0)
        if pct is not None and pct > 0:
            labels.append('Services et domaine')
            values.append(pct)
            montants.append(montant)

    # Calculer la part "Autres" pour atteindre 100%
    total_pct = sum(values)
    if total_pct < 100:
        autres_pct = 100 - total_pct
        labels.append('Autres produits')
        values.append(autres_pct)
        # Calculer le montant correspondant
        produits_caf_total = produits.get('produits_caf', {}).get('montant_k', 0)
        autres_montant = produits_caf_total * (autres_pct / 100) if produits_caf_total else 0
        montants.append(autres_montant)

    # Graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#95a5a6']

    def make_autopct(montants_list):
        def autopct_format(pct):
            # matplotlib appelle cette fonction pour chaque tranche dans l'ordre
            idx = autopct_format.counter
            autopct_format.counter += 1
            if idx < len(montants_list):
                montant = int(montants_list[idx])
                return f'{pct:.1f}%\n({montant}k€)'
            return f'{pct:.1f}%'
        autopct_format.counter = 0
        return autopct_format

    wedges, texts, autotexts = ax.pie(values, labels=labels,
                                        autopct=make_autopct(montants),
                                        colors=colors[:len(values)], startangle=90,
                                        textprops={'fontsize': 10})

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
        autotext.set_weight('bold')

    for text in texts:
        text.set_fontsize(11)
        text.set_weight('bold')

    ax.set_title('Répartition des recettes réelles de fonctionnement',
                 fontsize=13, fontweight='bold', pad=15)

    plt.tight_layout()
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    return fichier_sortie


def generer_graphique_repartition_charges(data, fichier_sortie):
    """Génère un camembert de répartition des dépenses réelles de fonctionnement (en % des charges CAF)"""
    charges = data['fonctionnement']['charges']

    labels = []
    values = []
    montants = []

    # Extraire les principaux postes de charges avec leurs % du PDF
    if 'charges_personnel' in charges and 'pct_charges_caf' in charges['charges_personnel']:
        pct = charges['charges_personnel'].get('pct_charges_caf')
        montant = charges['charges_personnel'].get('montant_k', 0)
        if pct is not None and pct > 0:
            labels.append('Personnel')
            values.append(pct)
            montants.append(montant)

    if 'achats_charges_externes' in charges and 'pct_charges_caf' in charges['achats_charges_externes']:
        pct = charges['achats_charges_externes'].get('pct_charges_caf')
        montant = charges['achats_charges_externes'].get('montant_k', 0)
        if pct is not None and pct > 0:
            labels.append('Achats et charges externes')
            values.append(pct)
            montants.append(montant)

    if 'charges_financieres' in charges and 'pct_charges_caf' in charges['charges_financieres']:
        pct = charges['charges_financieres'].get('pct_charges_caf')
        montant = charges['charges_financieres'].get('montant_k', 0)
        if pct is not None and pct > 0:
            labels.append('Charges financières')
            values.append(pct)
            montants.append(montant)

    if 'contingents' in charges and 'pct_charges_caf' in charges['contingents']:
        pct = charges['contingents'].get('pct_charges_caf')
        montant = charges['contingents'].get('montant_k', 0)
        if pct is not None and pct > 0:
            labels.append('Contingents')
            values.append(pct)
            montants.append(montant)

    if 'subventions_versees' in charges and 'pct_charges_caf' in charges['subventions_versees']:
        pct = charges['subventions_versees'].get('pct_charges_caf')
        montant = charges['subventions_versees'].get('montant_k', 0)
        if pct is not None and pct > 0:
            labels.append('Subventions versées')
            values.append(pct)
            montants.append(montant)

    # Calculer la part "Autres" pour atteindre 100%
    total_pct = sum(values)
    if total_pct < 100:
        autres_pct = 100 - total_pct
        labels.append('Autres charges')
        values.append(autres_pct)
        # Calculer le montant correspondant
        charges_caf_total = charges.get('charges_caf', {}).get('montant_k', 0)
        autres_montant = charges_caf_total * (autres_pct / 100) if charges_caf_total else 0
        montants.append(autres_montant)

    # Graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#e74c3c', '#f39c12', '#3498db', '#9b59b6', '#1abc9c', '#95a5a6']

    def make_autopct(montants_list):
        def autopct_format(pct):
            # matplotlib appelle cette fonction pour chaque tranche dans l'ordre
            idx = autopct_format.counter
            autopct_format.counter += 1
            if idx < len(montants_list):
                montant = int(montants_list[idx])
                return f'{pct:.1f}%\n({montant}k€)'
            return f'{pct:.1f}%'
        autopct_format.counter = 0
        return autopct_format

    wedges, texts, autotexts = ax.pie(values, labels=labels,
                                        autopct=make_autopct(montants),
                                        colors=colors[:len(values)], startangle=90,
                                        textprops={'fontsize': 10})

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
        autotext.set_weight('bold')

    for text in texts:
        text.set_fontsize(11)
        text.set_weight('bold')

    ax.set_title('Répartition des dépenses réelles de fonctionnement',
                 fontsize=13, fontweight='bold', pad=15)

    plt.tight_layout()
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    return fichier_sortie


def generer_graphique_comparaison_strate(data, fichier_sortie):
    """Génère un graphique comparatif avec la moyenne de strate"""

    # Données à comparer
    categories = []
    commune_values = []
    strate_values = []

    # Produits de fonctionnement
    if 'produits' in data['fonctionnement']:
        produits = data['fonctionnement']['produits']['total']
        categories.append('Produits\nFonctionnement')
        commune_values.append(produits['par_hab'])
        strate_values.append(produits['moyenne_strate_hab'])

    # Charges de fonctionnement
    if 'charges' in data['fonctionnement']:
        charges = data['fonctionnement']['charges']['total']
        categories.append('Charges\nFonctionnement')
        commune_values.append(charges['par_hab'])
        strate_values.append(charges['moyenne_strate_hab'])

    # CAF brute
    if 'autofinancement' in data and 'caf_brute' in data['autofinancement']:
        caf = data['autofinancement']['caf_brute']
        categories.append('CAF\nBrute')
        commune_values.append(caf['par_hab'])
        strate_values.append(caf['moyenne_strate_hab'])

    # Graphique
    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(categories))
    width = 0.35

    bars1 = ax.bar([i - width/2 for i in x], commune_values, width,
                    label='Commune', color='#3498db', alpha=0.85, edgecolor='#2c3e50', linewidth=1.2)
    bars2 = ax.bar([i + width/2 for i in x], strate_values, width,
                    label='Moyenne strate', color='#95a5a6', alpha=0.85, edgecolor='#7f8c8d', linewidth=1.2)

    ax.set_xlabel('Indicateurs', fontsize=11, fontweight='bold')
    ax.set_ylabel('€ par habitant', fontsize=11, fontweight='bold')
    ax.set_title('Comparaison avec la moyenne de strate',
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10)
    ax.legend(fontsize=10, loc='upper left', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Ajouter les valeurs sur les barres
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}€',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    return fichier_sortie


def generer_graphique_fiscalite(data, fichier_sortie):
    """Génère un graphique comparatif des taux de fiscalité"""

    if 'impots_locaux' not in data['fonctionnement']['produits']:
        return None

    detail_fiscalite = data['fonctionnement']['produits']['impots_locaux'].get('detail_fiscalite', {})

    if not detail_fiscalite:
        return None

    labels = []
    taux_commune = []
    taux_strate = []

    for taxe_nom, taxe_data in detail_fiscalite.items():
        if 'taux_vote_pct' in taxe_data and 'taux_strate_pct' in taxe_data:
            nom_court = taxe_nom.replace('taxe_', '').replace('_', ' ').title()
            labels.append(nom_court)
            taux_commune.append(taxe_data['taux_vote_pct'])
            taux_strate.append(taxe_data['taux_strate_pct'])

    if not labels:
        return None

    # Graphique
    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(labels))
    width = 0.35

    bars1 = ax.bar([i - width/2 for i in x], taux_commune, width,
                    label='Taux commune', color='#e74c3c', alpha=0.85, edgecolor='#c0392b', linewidth=1.2)
    bars2 = ax.bar([i + width/2 for i in x], taux_strate, width,
                    label='Taux moyen strate', color='#95a5a6', alpha=0.85, edgecolor='#7f8c8d', linewidth=1.2)

    ax.set_xlabel('Taxes', fontsize=11, fontweight='bold')
    ax.set_ylabel('Taux (%)', fontsize=11, fontweight='bold')
    ax.set_title('Comparaison des taux de fiscalité locale',
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(fontsize=10, loc='upper left', framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Ajouter les valeurs sur les barres
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    return fichier_sortie


def generer_graphique_ratios_financiers(data, fichier_sortie):
    """Génère un graphique des principaux ratios financiers"""

    ratios_noms = []
    ratios_valeurs = []
    ratios_seuils = []

    # Capacité de désendettement
    if 'endettement' in data and 'ratios' in data['endettement']:
        cap_des = data['endettement']['ratios'].get('capacite_desendettement_annees')
        if cap_des is not None:
            ratios_noms.append('Capacité\ndésendettement\n(années)')
            ratios_valeurs.append(cap_des)
            ratios_seuils.append(12)  # Seuil prudentiel

    # Taux d'épargne (CAF nette / Produits CAF * 100)
    if 'autofinancement' in data and 'fonctionnement' in data:
        caf_nette = data['autofinancement'].get('caf_nette', {}).get('montant_k')
        produits_caf = data['fonctionnement'].get('produits', {}).get('produits_caf', {}).get('montant_k')
        if caf_nette is not None and produits_caf and produits_caf > 0:
            taux_epargne = (caf_nette / produits_caf) * 100
            ratios_noms.append('Taux épargne\nnette (%)')
            ratios_valeurs.append(taux_epargne)
            ratios_seuils.append(10)  # Seuil indicatif



    if not ratios_noms:
        return None

    # Graphique
    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(ratios_noms))

    bars = ax.bar(x, ratios_valeurs, color=['#3498db', '#2ecc71', '#f39c12'],
                  alpha=0.85, edgecolor=['#2c3e50', '#27ae60', '#e67e22'], linewidth=1.5)

    # Ajouter les seuils
    for i, seuil in enumerate(ratios_seuils):
        ax.axhline(y=seuil, xmin=(i)/len(ratios_noms), xmax=(i+1)/len(ratios_noms),
                   color='#e74c3c', linestyle='--', linewidth=2.5, alpha=0.8)
        ax.text(i, seuil * 1.05, f'Seuil: {seuil}',
                ha='center', fontsize=9, color='#c0392b', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='#e74c3c'))

    ax.set_ylabel('Valeur', fontsize=11, fontweight='bold')
    ax.set_title('Principaux ratios financiers',
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(ratios_noms, fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    # Ajouter les valeurs sur les barres
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.1f}',
               ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    return fichier_sortie


def generer_graphique_cascade_fonctionnement(data, fichier_sortie):
    """Génère un graphique en cascade (waterfall) du fonctionnement"""

    # Extraire les données
    produits_k = data['fonctionnement']['produits']['total'].get('montant_k', 0)
    charges_k = data['fonctionnement']['charges']['total'].get('montant_k', 0)
    resultat_k = data['fonctionnement']['resultat'].get('montant_k', 0)

    # Calcul des opérations d'ordre (différence entre résultat comptable et CAF brute)
    caf_brute_k = data['autofinancement']['caf_brute'].get('montant_k', 0)
    operations_ordre_k = caf_brute_k - resultat_k

    remb_emprunts_k = data['investissement']['emplois']['remboursement_emprunts'].get('montant_k', 0)
    caf_nette_k = data['autofinancement']['caf_nette'].get('montant_k', 0)

    # Préparation des données pour le graphique
    categories = ['Produits\nfonct.', 'Charges\nfonct.', 'Résultat', 'Opérations\nd\'ordre',
                  'CAF\nbrute', 'Remb.\nemprunts', 'CAF\nnette']

    valeurs = [produits_k, -charges_k, resultat_k, operations_ordre_k, caf_brute_k, -remb_emprunts_k, caf_nette_k]

    # Créer le graphique
    fig, ax = plt.subplots(figsize=(13, 7))

    # Calculer les positions
    cumul = 0
    positions_y = []
    hauteurs = []
    couleurs = []

    for i, val in enumerate(valeurs):
        if i == 0:  # Produits (barre complète)
            positions_y.append(0)
            hauteurs.append(val)
            couleurs.append('#2ecc71')
        elif i in [2, 4, 6]:  # Résultat, CAF brute, CAF nette (barres complètes)
            positions_y.append(0)
            hauteurs.append(valeurs[i])
            couleurs.append('#3498db' if i == 2 else '#2ecc71' if valeurs[i] > 0 else '#e74c3c')
        else:  # Variations
            positions_y.append(cumul if val < 0 else cumul)
            hauteurs.append(abs(val))
            couleurs.append('#e74c3c' if val < 0 else '#f39c12')

        if i < len(valeurs) - 1:
            cumul = valeurs[i] if i in [0, 2, 4] else cumul + val

    # Dessiner les barres
    bars = ax.bar(range(len(categories)), hauteurs, bottom=positions_y,
                   color=couleurs, alpha=0.85, edgecolor='#2c3e50', linewidth=1.2, width=0.6)

    # Ajouter les connecteurs
    for i in range(len(categories) - 1):
        if i not in [1, 3, 5]:  # Pas de connecteur après les variations
            y1 = positions_y[i] + hauteurs[i]
            y2 = positions_y[i+1] if i+1 in [2, 4, 6] else positions_y[i+1]
            ax.plot([i + 0.3, i + 0.7], [y1, y2], 'k--', alpha=0.3, linewidth=1)

    # Ajouter les valeurs sur les barres
    for i, (bar, val) in enumerate(zip(bars, valeurs)):
        height = bar.get_height() + bar.get_y()
        label = f'{abs(val):.0f}k€'
        ax.text(bar.get_x() + bar.get_width()/2., height,
               label, ha='center', va='bottom' if val >= 0 else 'top',
               fontsize=10, fontweight='bold')

    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylabel('Montant (k€)', fontsize=11, fontweight='bold')
    ax.set_title('Cascade du fonctionnement : de la section de fonctionnement à la CAF nette',
                 fontsize=13, fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.axhline(y=0, color='black', linewidth=0.8)

    plt.tight_layout()
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    return fichier_sortie


def generer_graphique_financement_investissement(data, fichier_sortie):
    """Génère un camembert du financement de l'investissement"""

    labels = []
    values = []

    # Ressources d'investissement
    caf_nette_k = data['autofinancement']['caf_nette'].get('montant_k', 0)
    if caf_nette_k > 0:
        labels.append('CAF nette')
        values.append(caf_nette_k)

    emprunts_k = data['investissement']['ressources']['emprunts'].get('montant_k', 0)
    if emprunts_k > 0:
        labels.append('Emprunts contractés')
        values.append(emprunts_k)

    subventions_k = data['investissement']['ressources']['subventions_recues'].get('montant_k', 0)
    if subventions_k > 0:
        labels.append('Subventions reçues')
        values.append(subventions_k)

    fctva_k = data['investissement']['ressources']['fctva'].get('montant_k', 0)
    if fctva_k > 0:
        labels.append('FCTVA')
        values.append(fctva_k)

    # Calculer "Autres ressources"
    total_ressources_k = data['investissement']['ressources'].get('total_k', 0)
    total_calcule = sum(values)
    if total_ressources_k > total_calcule:
        autres_k = total_ressources_k - total_calcule
        labels.append('Autres ressources')
        values.append(autres_k)

    if not values or sum(values) == 0:
        return None

    # Graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#2ecc71', '#3498db', '#f39c12', '#9b59b6', '#95a5a6']

    def make_autopct(values_list):
        def autopct_format(pct):
            idx = autopct_format.counter
            autopct_format.counter += 1
            if idx < len(values_list):
                montant = int(values_list[idx])
                return f'{pct:.1f}%\n({montant}k€)'
            return f'{pct:.1f}%'
        autopct_format.counter = 0
        return autopct_format

    _, texts, autotexts = ax.pie(values, labels=labels,
                                   autopct=make_autopct(values),
                                   colors=colors[:len(values)], startangle=90,
                                   textprops={'fontsize': 10})

    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
        autotext.set_weight('bold')

    for text in texts:
        text.set_fontsize(11)
        text.set_weight('bold')

    ax.set_title('Financement de l\'investissement',
                 fontsize=13, fontweight='bold', pad=15)

    plt.tight_layout()
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    return fichier_sortie


def generer_graphique_structure_comparee(data, fichier_sortie):
    """Génère un graphique en barres empilées à 100% pour comparer structure commune vs strate"""

    produits = data['fonctionnement']['produits']

    # Extraire les données pour la commune
    commune_impots = produits['impots_locaux'].get('pct_produits_caf', 0)
    commune_dgf = produits['dgf'].get('pct_produits_caf', 0)
    commune_autres_impots = produits.get('autres_impots_taxes', {}).get('pct_produits_caf', 0)
    commune_services = produits.get('produits_services_domaine', {}).get('pct_produits_caf', 0)
    commune_autres = 100 - (commune_impots + commune_dgf + commune_autres_impots + commune_services)

    # Extraire les données pour la strate
    strate_impots = produits['impots_locaux'].get('pct_produits_caf_strate', 0)
    strate_dgf = produits['dgf'].get('pct_produits_caf_strate', 0)
    strate_autres_impots = produits.get('autres_impots_taxes', {}).get('pct_produits_caf_strate', 0)
    strate_services = produits.get('produits_services_domaine', {}).get('pct_produits_caf_strate', 0)
    strate_autres = 100 - (strate_impots + strate_dgf + strate_autres_impots + strate_services)

    # Données pour le graphique
    categories = ['Commune', 'Strate']
    impots = [commune_impots, strate_impots]
    dgf = [commune_dgf, strate_dgf]
    autres_impots = [commune_autres_impots, strate_autres_impots]
    services = [commune_services, strate_services]
    autres = [commune_autres, strate_autres]

    # Créer le graphique
    fig, ax = plt.subplots(figsize=(10, 6))
    width = 0.5

    # Barres empilées
    p1 = ax.bar(categories, impots, width, label='Impôts locaux', color='#3498db', edgecolor='white', linewidth=2)
    p2 = ax.bar(categories, dgf, width, bottom=impots, label='DGF', color='#2ecc71', edgecolor='white', linewidth=2)

    bottom2 = [i + d for i, d in zip(impots, dgf)]
    p3 = ax.bar(categories, autres_impots, width, bottom=bottom2, label='Autres impôts', color='#f39c12', edgecolor='white', linewidth=2)

    bottom3 = [b + a for b, a in zip(bottom2, autres_impots)]
    p4 = ax.bar(categories, services, width, bottom=bottom3, label='Services', color='#e74c3c', edgecolor='white', linewidth=2)

    bottom4 = [b + s for b, s in zip(bottom3, services)]
    p5 = ax.bar(categories, autres, width, bottom=bottom4, label='Autres produits', color='#95a5a6', edgecolor='white', linewidth=2)

    # Ajouter les pourcentages sur les sections
    def add_labels(bars, values, bottoms):
        for bar, val, bottom in zip(bars, values, bottoms):
            if val > 5:  # Afficher seulement si > 5%
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., bottom + height/2,
                       f'{val:.1f}%', ha='center', va='center',
                       fontsize=9, fontweight='bold', color='white')

    add_labels(p1, impots, [0, 0])
    add_labels(p2, dgf, impots)
    add_labels(p3, autres_impots, bottom2)
    add_labels(p4, services, bottom3)
    add_labels(p5, autres, bottom4)

    ax.set_ylabel('Répartition (%)', fontsize=11, fontweight='bold')
    ax.set_title('Structure comparée des produits de fonctionnement CAF (Commune vs Strate)',
                 fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=True, shadow=True)
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig(fichier_sortie, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    return fichier_sortie


def generer_tous_graphiques(data_json):
    """Génère tous les graphiques à partir du JSON"""

    os.makedirs(DOSSIER_GRAPHIQUES, exist_ok=True)

    graphiques = {}

    print("\n[GRAPHIQUES] Génération en cours...")

    # Graphique 1: Répartition des produits
    fichier = os.path.join(DOSSIER_GRAPHIQUES, "repartition_produits.png")
    generer_graphique_repartition_produits(data_json, fichier)
    graphiques['repartition_produits'] = fichier
    print(f"  [OK] Repartition des produits")

    # Graphique 2: Répartition des charges
    fichier = os.path.join(DOSSIER_GRAPHIQUES, "repartition_charges.png")
    generer_graphique_repartition_charges(data_json, fichier)
    graphiques['repartition_charges'] = fichier
    print(f"  [OK] Repartition des charges")

    # Graphique 3: Comparaison strate
    fichier = os.path.join(DOSSIER_GRAPHIQUES, "comparaison_strate.png")
    generer_graphique_comparaison_strate(data_json, fichier)
    graphiques['comparaison_strate'] = fichier
    print(f"  [OK] Comparaison avec strate")

    # Graphique 4: Fiscalité
    fichier = os.path.join(DOSSIER_GRAPHIQUES, "fiscalite.png")
    result = generer_graphique_fiscalite(data_json, fichier)
    if result:
        graphiques['fiscalite'] = fichier
        print(f"  [OK] Comparaison fiscalite")

    # Graphique 5: Ratios financiers
    fichier = os.path.join(DOSSIER_GRAPHIQUES, "ratios_financiers.png")
    result = generer_graphique_ratios_financiers(data_json, fichier)
    if result:
        graphiques['ratios_financiers'] = fichier
        print(f"  [OK] Ratios financiers")

    # Graphique 6: Cascade du fonctionnement (NOUVEAU)
    fichier = os.path.join(DOSSIER_GRAPHIQUES, "cascade_fonctionnement.png")
    result = generer_graphique_cascade_fonctionnement(data_json, fichier)
    if result:
        graphiques['cascade_fonctionnement'] = fichier
        print(f"  [OK] Cascade du fonctionnement")

    # Graphique 7: Financement de l'investissement (NOUVEAU)
    fichier = os.path.join(DOSSIER_GRAPHIQUES, "financement_investissement.png")
    result = generer_graphique_financement_investissement(data_json, fichier)
    if result:
        graphiques['financement_investissement'] = fichier
        print(f"  [OK] Financement de l'investissement")

    # Graphique 8: Structure comparée (NOUVEAU)
    fichier = os.path.join(DOSSIER_GRAPHIQUES, "structure_comparee.png")
    result = generer_graphique_structure_comparee(data_json, fichier)
    if result:
        graphiques['structure_comparee'] = fichier
        print(f"  [OK] Structure comparee commune vs strate")

    print(f"\n  Total: {len(graphiques)} graphiques générés\n")

    return graphiques


# ============================================
# CONVERSION TEXTE EN ÉLÉMENTS PDF
# ============================================

def formater_titre_poste(nom_poste):
    """Formate un nom de poste pour affichage professionnel"""
    if not nom_poste or pd.isna(nom_poste):
        return ""

    # Remplacer les underscores par des espaces
    nom = str(nom_poste).replace('_', ' ')

    # Mettre en majuscule la première lettre de chaque mot
    nom = nom.title()

    # Corrections spécifiques
    corrections = {
        'Caf': 'CAF',
        'Dgf': 'DGF',
        'Fctva': 'FCTVA',
        'De La': 'de la',
        'Du': 'du',
        'Des': 'des',
        'Et': 'et',
        'D\'': 'd\'',
        'Dequipement': 'd\'équipement'
    }

    for old, new in corrections.items():
        nom = nom.replace(old, new)

    return nom


def generer_contenu_analyse(row, styles):
    """Génère le contenu complet d'une analyse à partir de la réponse de l'IA

    L'IA génère les 3 sections en s'inspirant éventuellement des phrases d'exemple
    fournies dans le code Python (TEXTES_PERSONNALISES).

    Args:
        row: Ligne du DataFrame contenant l'analyse
        styles: Styles PDF

    Returns:
        Liste d'éléments PDF à ajouter au document
    """
    elements = []

    # Récupérer le texte généré par l'IA (contient les 3 sections générées)
    texte_ia = row.get('Reponse_Attendue', '')
    if pd.isna(texte_ia):
        texte_ia = ''

    # Afficher le texte de l'IA
    if texte_ia:
        elements.extend(convertir_texte_en_paragraphes(texte_ia, styles))

    return elements


def convertir_texte_en_paragraphes(texte, styles):
    """Convertit le texte en éléments PDF avec gestion des puces et sous-titres"""
    if not texte or pd.isna(texte):
        return []

    elements = []
    lignes = str(texte).split('\n')

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
            elements.append(Paragraph(ligne_escape, styles['Liste']))
        else:
            elements.append(Paragraph(ligne_escape, styles['CorpsTexte']))

    return elements


# ============================================
# GÉNÉRATION DU PDF
# ============================================

def generer_rapport_pdf():
    """Génère le rapport PDF complet"""

    print("\n" + "="*80)
    print("GÉNÉRATION RAPPORT D'ANALYSE BUDGÉTAIRE MONO-ANNÉE")
    print("="*80 + "\n")

    # 1. Chargement des données
    print("[ÉTAPE 1/4] Chargement des données...")

    # Charger l'Excel
    df_excel = pd.read_excel(FICHIER_EXCEL)
    df_mono = df_excel[df_excel['Type_Rapport'] == 'Mono-annee'].copy()
    print(f"  [OK] Excel charge: {len(df_mono)} analyses mono-annee")

    # Charger le JSON
    with open(FICHIER_JSON, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    print(f"  [OK] JSON charge: {data_json['metadata']['commune']} - {data_json['metadata']['exercice']}")

    # 2. Génération des graphiques
    print("\n[ÉTAPE 2/4] Génération des graphiques...")
    graphiques = generer_tous_graphiques(data_json)

    # 3. Construction du PDF
    print("[ÉTAPE 3/4] Construction du rapport PDF...")

    os.makedirs(os.path.dirname(FICHIER_SORTIE), exist_ok=True)

    metadata = data_json['metadata']

    # Créer le document avec en-têtes et pieds de page
    def create_canvas(filename):
        c = EnTetePiedPage(filename, pagesize=A4)
        c.commune = metadata['commune']
        c.exercice = str(metadata['exercice'])
        return c

    doc = SimpleDocTemplate(
        FICHIER_SORTIE,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm,
        canvasmaker=create_canvas
    )

    story = []
    styles = creer_styles()

    # ============ PAGE DE GARDE ============
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph(
        "RAPPORT D'ANALYSE BUDGÉTAIRE<br/>MONO-ANNÉE",
        styles['TitrePrincipal']
    ))
    story.append(Spacer(1, 1.5*cm))

    story.append(Paragraph(f"<b>{metadata['commune']}</b>", styles['MetadataGras']))
    story.append(Paragraph(f"Exercice {metadata['exercice']}", styles['Metadata']))
    story.append(Paragraph(
        f"Population : {metadata['population']} habitants",
        styles['Metadata']
    ))
    story.append(Paragraph(
        f"Strate démographique : {metadata['strate']['libelle']}",
        styles['Metadata']
    ))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f"Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        styles['Metadata']
    ))

    story.append(PageBreak())

    # ============ PRÉSENTATION DE LA COLLECTIVITÉ ============
    story.append(Paragraph("PRÉSENTATION DE LA COLLECTIVITÉ", styles['TitreSection']))
    story.append(Spacer(1, 0.4*cm))

    # Informations générales
    story.append(Paragraph("Identification", styles['SousTitre']))
    story.append(Spacer(1, 0.2*cm))

    texte_identification = (
        f"La commune de {metadata['commune']} compte {metadata['population']} habitants "
        f"au titre de l'exercice {metadata['exercice']}. "
        f"Elle se situe dans la strate démographique des communes de {metadata['strate']['libelle']}."
    )
    story.append(Paragraph(texte_identification, styles['CorpsTexte']))
    story.append(Spacer(1, 0.4*cm))

    # Contexte de l'analyse
    story.append(Paragraph("Objet de l'analyse", styles['SousTitre']))
    story.append(Spacer(1, 0.2*cm))

    texte_objet = (
        "Le présent rapport d'analyse budgétaire a pour objet d'apprécier la situation financière "
        "de la collectivité au titre de l'exercice budgétaire considéré. L'analyse porte sur les "
        "opérations de fonctionnement et d'investissement, la capacité d'autofinancement, l'endettement "
        "et les principaux ratios financiers. Les données sont systématiquement comparées à la moyenne "
        "de la strate démographique de référence."
    )
    story.append(Paragraph(texte_objet, styles['CorpsTexte']))
    story.append(Spacer(1, 0.4*cm))

    # Méthodologie
    story.append(Paragraph("Méthodologie", styles['SousTitre']))
    story.append(Spacer(1, 0.2*cm))

    texte_methodo = (
        "L'analyse financière s'appuie sur les données des budgets exécutés par les communes "
        "dont la source provient de la Direction Générale des Finances Publiques (DGFiP)."
        " Elle respecte la nomenclature comptable M57. Les comparaisons avec la strate démographique permettent "
        "de situer la collectivité par rapport aux communes de taille comparable. Les ratios de niveau "
        "sont exprimés en euros par habitant. Les ratios de structure sont exprimés en %."
    )
    story.append(Paragraph(texte_methodo, styles['CorpsTexte']))

    story.append(PageBreak())

    # ============ SYNTHÈSE GLOBALE ============
    synthese = df_mono[df_mono['Section'] == 'Synthese_globale']
    if not synthese.empty:
        story.append(Paragraph("SYNTHÈSE FINANCIÈRE GLOBALE", styles['TitreSection']))
        story.append(Spacer(1, 0.4*cm))

        for _, row in synthese.iterrows():
            # Ajouter le titre du poste budgétaire
            story.append(Paragraph(formater_titre_poste(row['Nom_Poste']), styles['SousTitreTexte']))
            story.append(Spacer(1, 0.2*cm))
            story.extend(generer_contenu_analyse(row, styles))
            story.append(Spacer(1, 0.3*cm))

        story.append(PageBreak())

    # ============ SECTION DE FONCTIONNEMENT ============
    story.append(Paragraph("I. SECTION DE FONCTIONNEMENT", styles['TitreSection']))
    story.append(Spacer(1, 0.4*cm))

    # Introduction générale au fonctionnement
    intro_fonct = (
        "La section de fonctionnement retrace l'ensemble des opérations courantes de la collectivité. "
        "Elle se caractérise par les produits (recettes) et les charges (dépenses) nécessaires au "
        "fonctionnement des services publics locaux."
    )
    story.append(Paragraph(intro_fonct, styles['CorpsTexte']))
    story.append(Spacer(1, 0.5*cm))

    # 1.1 Produits de fonctionnement
    story.append(Paragraph("1.1. Produits de fonctionnement", styles['SousTitre']))
    story.append(Spacer(1, 0.3*cm))

    # Analyses produits
    fonctionnement = df_mono[df_mono['Section'] == 'Fonctionnement']
    produits_analyses = fonctionnement[fonctionnement['Nom_Poste'].str.contains('produit|Produit', case=False, na=False)]

    for _, row in produits_analyses.iterrows():
        # Ajouter le titre du poste budgétaire
        story.append(Paragraph(formater_titre_poste(row['Nom_Poste']), styles['SousTitreTexte']))
        story.append(Spacer(1, 0.2*cm))
        story.extend(generer_contenu_analyse(row, styles))
        story.append(Spacer(1, 0.3*cm))

    # Graphique répartition produits
    story.append(Spacer(1, 0.2*cm))
    if 'repartition_produits' in graphiques:
        # Ratio 10:6 = 1.67, donc pour 14cm de largeur : 14/1.67 = 8.4cm
        img = Image(graphiques['repartition_produits'], width=13*cm, height=7.8*cm)
        story.append(img)
        story.append(Paragraph("Graphique 1 – Répartition des recettes réelles de fonctionnement", styles['Legende']))
        story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # 1.2 Charges de fonctionnement
    story.append(Paragraph("1.2. Charges de fonctionnement", styles['SousTitre']))
    story.append(Spacer(1, 0.3*cm))

    # Analyses charges
    charges_analyses = fonctionnement[fonctionnement['Nom_Poste'].str.contains('charge|Charge', case=False, na=False)]

    for _, row in charges_analyses.iterrows():
        # Ajouter le titre du poste budgétaire
        story.append(Paragraph(formater_titre_poste(row['Nom_Poste']), styles['SousTitreTexte']))
        story.append(Spacer(1, 0.2*cm))
        story.extend(generer_contenu_analyse(row, styles))
        story.append(Spacer(1, 0.3*cm))

    # Graphique répartition charges
    story.append(Spacer(1, 0.2*cm))
    if 'repartition_charges' in graphiques:
        # Ratio 10:6 = 1.67
        img = Image(graphiques['repartition_charges'], width=13*cm, height=7.8*cm)
        story.append(img)
        story.append(Paragraph("Graphique 2 – Répartition des dépenses réelles de fonctionnement", styles['Legende']))
        story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # 1.3 Analyse comparative
    story.append(Paragraph("1.3. Analyse comparative", styles['SousTitre']))
    story.append(Spacer(1, 0.3*cm))

    # Texte d'analyse comparative
    texte_comparatif = (
        "Le positionnement de la commune par rapport à la moyenne de sa strate démographique "
        "permet d'apprécier le niveau relatif de ses produits et charges de fonctionnement. "
        "Cette comparaison constitue un élément d'appréciation de la structure financière communale."
    )
    story.append(Paragraph(texte_comparatif, styles['CorpsTexte']))
    story.append(Spacer(1, 0.4*cm))

    # Graphique comparaison strate
    if 'comparaison_strate' in graphiques:
        # Ratio 11:6 = 1.83
        img = Image(graphiques['comparaison_strate'], width=13*cm, height=7.1*cm)
        story.append(img)
        story.append(Paragraph(
            "Graphique 3 – Comparaison avec la moyenne de strate",
            styles['Legende']
        ))
        story.append(Spacer(1, 0.5*cm))

    # Graphique fiscalité
    if 'fiscalite' in graphiques:
        story.append(Spacer(1, 0.3*cm))
        texte_fiscalite = (
            "L'analyse de la pression fiscale locale s'effectue par comparaison des taux communaux "
            "avec les taux moyens constatés dans la strate."
        )
        story.append(Paragraph(texte_fiscalite, styles['CorpsTexte']))
        story.append(Spacer(1, 0.4*cm))

        # Ratio 11:6 = 1.83
        img = Image(graphiques['fiscalite'], width=13*cm, height=7.1*cm)
        story.append(img)
        story.append(Paragraph(
            "Graphique 4 – Comparaison des taux de fiscalité locale",
            styles['Legende']
        ))

    story.append(PageBreak())

    # ============ AUTOFINANCEMENT ============
    autofinancement = df_mono[df_mono['Section'] == 'Autofinancement']
    if not autofinancement.empty:
        story.append(Paragraph("II. CAPACITÉ D'AUTOFINANCEMENT", styles['TitreSection']))
        story.append(Spacer(1, 0.4*cm))

        intro_caf = (
            "La capacité d'autofinancement constitue l'excédent dégagé par la section de fonctionnement "
            "permettant de financer les investissements et de rembourser la dette."
        )
        story.append(Paragraph(intro_caf, styles['CorpsTexte']))
        story.append(Spacer(1, 0.4*cm))

        for _, row in autofinancement.iterrows():
            # Ajouter le titre du poste budgétaire
            story.append(Paragraph(formater_titre_poste(row['Nom_Poste']), styles['SousTitreTexte']))
            story.append(Spacer(1, 0.2*cm))
            story.extend(generer_contenu_analyse(row, styles))
            story.append(Spacer(1, 0.3*cm))

        story.append(PageBreak())

    # ============ INVESTISSEMENT ============
    investissement = df_mono[df_mono['Section'] == 'Investissement']
    if not investissement.empty:
        story.append(Paragraph("III. SECTION D'INVESTISSEMENT", styles['TitreSection']))
        story.append(Spacer(1, 0.4*cm))

        intro_invest = (
            "La section d'investissement retrace les opérations affectant le patrimoine de la collectivité. "
            "Elle comprend les dépenses d'équipement et leurs financements."
        )
        story.append(Paragraph(intro_invest, styles['CorpsTexte']))
        story.append(Spacer(1, 0.4*cm))

        for _, row in investissement.iterrows():
            # Ajouter le titre du poste budgétaire
            story.append(Paragraph(formater_titre_poste(row['Nom_Poste']), styles['SousTitreTexte']))
            story.append(Spacer(1, 0.2*cm))
            story.extend(generer_contenu_analyse(row, styles))
            story.append(Spacer(1, 0.3*cm))

        story.append(PageBreak())

    # ============ ENDETTEMENT ============
    endettement = df_mono[df_mono['Section'] == 'Endettement']
    if not endettement.empty:
        story.append(Paragraph("IV. ENDETTEMENT", styles['TitreSection']))
        story.append(Spacer(1, 0.4*cm))

        intro_dette = (
            "L'analyse de l'endettement porte sur l'encours de dette au 31 décembre et sur "
            "la capacité de la collectivité à le rembourser dans des conditions soutenables."
        )
        story.append(Paragraph(intro_dette, styles['CorpsTexte']))
        story.append(Spacer(1, 0.4*cm))

        for _, row in endettement.iterrows():
            # Ajouter le titre du poste budgétaire
            story.append(Paragraph(formater_titre_poste(row['Nom_Poste']), styles['SousTitreTexte']))
            story.append(Spacer(1, 0.2*cm))
            story.extend(generer_contenu_analyse(row, styles))
            story.append(Spacer(1, 0.3*cm))

        story.append(PageBreak())



    # ============ CONSTRUCTION FINALE ============
    print("  [OK] Assemblage du document...")
    doc.build(story)

    # 4. Statistiques finales
    print("\n[ETAPE 4/4] Generation terminee")

    taille_kb = os.path.getsize(FICHIER_SORTIE) / 1024

    print("\n" + "="*80)
    print(f"[OK] RAPPORT GENERE AVEC SUCCES")
    print(f"  Fichier : {FICHIER_SORTIE}")
    print(f"  Taille : {taille_kb:.1f} KB")
    print(f"  Commune : {metadata['commune']}")
    print(f"  Exercice : {metadata['exercice']}")
    print(f"  Analyses : {len(df_mono)}")
    print(f"  Graphiques : {len(graphiques)}")
    print("="*80 + "\n")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    try:
        generer_rapport_pdf()
    except Exception as e:
        print(f"\n[ERREUR]: {e}\n")
        import traceback
        traceback.print_exc()
