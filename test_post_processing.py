"""
Script de test pour le post-processing des termes interdits
"""

from llm_client import nettoyer_termes_interdits


# Exemples de textes avec des termes interdits
TEXTES_TEST = [
    # Test 1 : Expressions LLM typiques
    """Il faut noter que les charges de personnel représentent 45% des DRF.
Nous constatons que la CAF brute est en baisse.
On observe que le FDR est positif.""",

    # Test 2 : Vocabulaire managérial
    """L'optimisation de la masse salariale passe par un pilotage rigoureux.
La marge de manœuvre budgétaire reste limitée.
Ce levier d'action permet de préserver la marge de sécurité.""",

    # Test 3 : Pronoms démonstratifs
    """Ce poste représente 30% des recettes.
Cette évolution traduit une hausse de la fiscalité.
Cet agrégat montre une dégradation.""",

    # Test 4 : Termes interdits (évolution/variation)
    """L'évolution des charges de personnel est de +5%.
La variation de la DGF est de -3%.
Cette évolution structurelle impacte le FDR.""",

    # Test 5 : Recommandations et ton alarmiste
    """Il faut maîtriser les dépenses de fonctionnement.
La situation est préoccupante et devrait être corrigée.
Cette évolution inquiétante nécessite un pilotage renforcé.""",

    # Test 6 : Formulations conditionnelles
    """La CAF reste positive sous réserve de la maîtrise de la masse salariale.
L'équilibre est maintenu sous réserve d'un pilotage des charges.
La situation est stable à condition de maintenir les recettes.""",

    # Test 7 : Mélange de tout
    """Il faut noter que Ce poste montre une évolution importante.
Nous constatons que l'optimisation est nécessaire sous réserve de la maîtrise de la dette.
Cette variation inquiétante devrait être corrigée par un pilotage adapté.""",
]


def test_post_processing():
    """Teste le post-processing sur différents exemples"""
    print("\n" + "="*80)
    print("TEST DU POST-PROCESSING DES TERMES INTERDITS")
    print("="*80 + "\n")

    for i, texte_original in enumerate(TEXTES_TEST, 1):
        print(f"\n{'-'*80}")
        print(f"TEST {i}/{len(TEXTES_TEST)}")
        print(f"{'-'*80}")
        print("\nTEXTE ORIGINAL :")
        print(texte_original)

        # Nettoyer le texte
        texte_nettoye, warnings = nettoyer_termes_interdits(texte_original, verbose=True)

        print("\nTEXTE NETTOYE :")
        print(texte_nettoye)

        if not warnings:
            print("\nAucun terme interdit detecte")

        print()

    print("\n" + "="*80)
    print("FIN DES TESTS")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_post_processing()
