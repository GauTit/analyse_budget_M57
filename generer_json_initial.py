"""
Génère le JSON initial depuis le PDF bilan.pdf
Ce script doit être exécuté en premier dans le workflow mono-année
"""

import sys
sys.path.insert(0, 'src')

from generators.generer_json_enrichi import generer_json_enrichi, sauvegarder_json_enrichi


def main():
    """Point d'entrée pour l'import depuis workflow_complet.py"""
    print("\n=== GÉNÉRATION JSON INITIAL DEPUIS PDF ===\n")

    fichier_pdf = 'docs/bilan.pdf'
    print(f"[1/2] Parsing du PDF : {fichier_pdf}")

    json_data = generer_json_enrichi(fichier_pdf)

    print(f"[2/2] Sauvegarde du JSON...")
    fichier = sauvegarder_json_enrichi(json_data)

    print(f"\n[OK] JSON initial généré : {fichier}")
    print(f"  Commune : {json_data['metadata']['commune']}")
    print(f"  Exercice : {json_data['metadata']['exercice']}")
    print(f"  Population : {json_data['metadata']['population']}")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
