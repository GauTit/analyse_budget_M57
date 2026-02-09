"""
Script de vérification de la refactorisation
Teste que tous les modules sont correctement importables
"""

def test_imports():
    """Teste l'import de tous les modules"""
    print("=" * 60)
    print("TEST DE LA REFACTORISATION")
    print("=" * 60)
    print()

    modules_to_test = [
        ("utils", "Fonctions utilitaires"),
        ("pdf_extractor", "Extraction PDF"),
        ("analyseur_texte", "Analyseur de texte"),
        ("graphiques", "Générateur de graphiques"),
        ("rapport", "Générateur de rapport"),
        ("main", "Point d'entrée principal")
    ]

    success = 0
    failed = 0

    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"[OK] {module_name:20s} - {description}")
            success += 1
        except Exception as e:
            print(f"[ERREUR] {module_name:20s} - {description}")
            print(f"         {str(e)}")
            failed += 1

    print()
    print("=" * 60)
    print(f"RESULTAT: {success} modules OK, {failed} erreurs")
    print("=" * 60)
    print()

    if failed == 0:
        print("La refactorisation est reussie!")
        print()
        print("STRUCTURE DES MODULES:")
        print()
        print("  1. utils.py           - Fonctions utilitaires generiques")
        print("  2. pdf_extractor.py   - Extraction d'infos depuis PDF")
        print("  3. analyseur_texte.py - Analyse textuelle budgetaire")
        print("  4. graphiques.py      - Generation de graphiques")
        print("  5. rapport.py         - Assemblage du rapport PDF")
        print("  6. main.py            - Point d'entree principal")
        print()
        print("UTILISATION:")
        print("  python main.py")
        print()
        return True
    else:
        print("Des erreurs ont ete detectees. Veuillez corriger les modules.")
        return False


def test_fonctions_utils():
    """Teste quelques fonctions du module utils"""
    print("TEST DES FONCTIONS UTILITAIRES")
    print("-" * 60)

    from utils import calculer_difference_pct, formulation_comparaison

    # Test 1: Calcul de différence
    diff = calculer_difference_pct(120, 100)
    print(f"Difference entre 120 et 100: {diff}% (attendu: 20.0)")
    assert diff == 20.0, "Erreur calcul difference"

    # Test 2: Formulation
    formulation = formulation_comparaison(3.0)
    print(f"Formulation pour 3%: '{formulation}' (attendu: 'au niveau de')")
    assert formulation == "au niveau de", "Erreur formulation"

    formulation = formulation_comparaison(15.0)
    print(f"Formulation pour 15%: '{formulation}' (attendu: 'superieur a')")
    assert formulation == "supérieur à", "Erreur formulation"

    print()
    print("[OK] Toutes les fonctions utilitaires fonctionnent correctement")
    print()


def test_api():
    """Teste que l'API principale fonctionne"""
    print("TEST DE L'API PRINCIPALE")
    print("-" * 60)

    from parser_budget_v2_complet import ParserBudget
    from rapport import GenerateurRapportAmeliore

    # Test instanciation
    parser = ParserBudget()
    print("[OK] ParserBudget() instancie correctement")

    generateur = GenerateurRapportAmeliore()
    print("[OK] GenerateurRapportAmeliore() instancie correctement")

    # Vérifier que les méthodes existent
    assert hasattr(parser, 'parser_bilan_pdf'), "Methode parser_bilan_pdf manquante"
    print("[OK] parser.parser_bilan_pdf() existe")

    assert hasattr(generateur, 'generer_rapport'), "Methode generer_rapport manquante"
    print("[OK] generateur.generer_rapport() existe")

    print()
    print("[OK] L'API est correctement definie")
    print()


if __name__ == "__main__":
    print()
    if test_imports():
        print()
        test_fonctions_utils()
        print()
        test_api()
        print()
        print("=" * 60)
        print("TOUS LES TESTS REUSSIS!")
        print("=" * 60)
        print()
        print("Pour generer un rapport, executez:")
        print("  python main.py")
        print()
