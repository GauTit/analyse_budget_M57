"""
Script pour parser le plan de comptes M57 depuis le PDF
et créer une table de transposition complète
"""

import re
import json
import fitz  # PyMuPDF
from pathlib import Path


def extraire_comptes_du_pdf(fichier_pdf):
    """
    Extrait les comptes et leurs libellés du PDF M57

    Args:
        fichier_pdf: Chemin vers le PDF

    Returns:
        dict: Mapping compte -> libellé
    """
    print(f"Ouverture du PDF: {fichier_pdf}")
    doc = fitz.open(fichier_pdf)

    mapping_comptes = {}
    lignes_totales = 0

    print(f"Nombre de pages: {len(doc)}")
    print("\nExtraction des comptes...")

    for page_num in range(len(doc)):
        page = doc[page_num]
        texte = page.get_text()

        # Chercher les patterns de comptes
        # Format attendu: numéro de compte suivi d'un libellé
        # Ex: "6411 Rémunération du personnel – Personnel titulaire"

        lignes = texte.split('\n')
        lignes_totales += len(lignes)

        for ligne in lignes:
            ligne = ligne.strip()

            # Pattern pour un compte: commence par 1 à 5 chiffres, suivi d'un espace et du libellé
            match = re.match(r'^(\d{1,6})\s+(.+)$', ligne)

            if match:
                compte = match.group(1)
                libelle = match.group(2).strip()

                # Nettoyer le libellé (enlever les caractères spéciaux en fin)
                libelle = re.sub(r'\s+', ' ', libelle)  # Normaliser les espaces

                # Ignorer les lignes trop courtes (probablement pas des vrais comptes)
                if len(libelle) > 3 and not libelle.isdigit():
                    mapping_comptes[compte] = libelle

    doc.close()

    print(f"\nLignes totales analysées: {lignes_totales}")
    print(f"Comptes extraits: {len(mapping_comptes)}")

    return mapping_comptes


def afficher_statistiques(mapping_comptes):
    """Affiche des statistiques sur les comptes extraits"""

    print("\n" + "="*80)
    print("STATISTIQUES")
    print("="*80)

    # Grouper par classe
    classes = {}
    for compte in mapping_comptes.keys():
        classe = compte[0]
        if classe not in classes:
            classes[classe] = 0
        classes[classe] += 1

    print("\nNombre de comptes par classe:")
    for classe in sorted(classes.keys()):
        print(f"  Classe {classe}: {classes[classe]} comptes")

    print("\nExemples de comptes par classe:")
    for classe in sorted(classes.keys()):
        comptes_classe = [c for c in mapping_comptes.keys() if c.startswith(classe)]
        print(f"\n  Classe {classe}:")
        for compte in sorted(comptes_classe)[:3]:
            print(f"    {compte}: {mapping_comptes[compte][:60]}...")


def sauvegarder_mapping(mapping_comptes, fichier_sortie):
    """Sauvegarde le mapping en JSON"""

    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        json.dump(mapping_comptes, f, indent=2, ensure_ascii=False)

    print(f"\nMapping sauvegarde dans: {fichier_sortie}")


def main():
    base_dir = Path(__file__).parent
    fichier_pdf = base_dir / "docs" / "M57D_Plan_de_comptes_01012026_vdef.pdf"
    fichier_sortie = base_dir / "docs" / "plan_comptes_m57.json"

    print("="*80)
    print("EXTRACTION DU PLAN DE COMPTES M57 DEPUIS LE PDF")
    print("="*80)

    # Extraire les comptes
    mapping_comptes = extraire_comptes_du_pdf(fichier_pdf)

    # Afficher les statistiques
    afficher_statistiques(mapping_comptes)

    # Sauvegarder
    sauvegarder_mapping(mapping_comptes, fichier_sortie)

    # Tester avec les comptes de la balance
    print("\n" + "="*80)
    print("TEST AVEC QUELQUES COMPTES DE LA BALANCE")
    print("="*80)

    comptes_test = ['6411', '73111', '7022', '61524', '752', '7478']

    for compte in comptes_test:
        if compte in mapping_comptes:
            print(f"OK {compte}: {mapping_comptes[compte]}")
        else:
            # Chercher par préfixe
            trouve = False
            for longueur in range(len(compte), 0, -1):
                prefixe = compte[:longueur]
                if prefixe in mapping_comptes:
                    print(f"~ {compte}: {mapping_comptes[prefixe]} (via prefixe {prefixe})")
                    trouve = True
                    break
            if not trouve:
                print(f"X {compte}: NON TROUVE")


if __name__ == "__main__":
    main()
