"""
Test simple de génération de rapport via Ollama
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generators.generer_rapport_llm import generer_rapport_par_sections

# Configuration
FICHIER_PDF = os.path.join(os.path.dirname(__file__), '..', 'docs', 'bilan.pdf')
MODEL = "mistral"  # Excellent pour le français !

# Générer le rapport
rapport = generer_rapport_par_sections(FICHIER_PDF, model=MODEL)

if rapport:
    print("\n" + "=" * 50)
    print("RAPPORT GÉNÉRÉ AVEC SUCCÈS")
    print("=" * 50)
    print("\nPremiers caractères du rapport:")
    print(rapport[:500])
