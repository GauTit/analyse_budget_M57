"""
Génère un rapport détaillé au format DGFiP avec analyse LLM
Utilise des templates précis + analyse globale IA
"""

import sys
import os
import json
import requests

sys.path.insert(0, 'src')

from generators.generer_json_enrichi import generer_json_enrichi


def appeler_ollama(prompt, model="mistral", verbose=False):
    """Appelle Ollama"""
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.2  # Bas pour plus de précision
    }

    if verbose:
        print(f"      Envoi requete ({len(prompt)} car)...")

    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        texte = response.json().get("response", "")
        if verbose:
            print(f"      Reponse recue ({len(texte)} car)")
        return texte
    except Exception as e:
        if verbose:
            print(f"      ERREUR: {e}")
        return None


def generer_section_template(titre, donnees, model="mistral", verbose=False):
    """
    Génère une section avec template STRICT format DGFiP

    Le LLM doit juste remplir le template avec les données fournies
    """

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
    """
    Génère une analyse globale ET des recommandations
    Ici le LLM a plus de liberté pour analyser et recommander
    """

    prompt = f"""Tu es un expert en finances publiques locales. Analyse la situation financière GLOBALE de cette commune.

DONNÉES COMPLÈTES:
{json.dumps(json_complet, ensure_ascii=False, indent=2)}

TÂCHE:
1. Fais une analyse TRANSVERSALE de la situation financière
2. Identifie les LIENS entre les différents postes (ex: dette élevée → charges financières → impact sur CAF)
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

Sois franc et factuel. Si la situation est préoccupante, dis-le clairement."""

    return appeler_ollama(prompt, model, verbose)


def generer_rapport_complet(fichier_pdf, model="mistral", fichier_sortie="output/rapport_detaille_llm.txt"):
    """Génère le rapport complet avec templates + analyse globale"""

    print("\n" + "="*70)
    print("GENERATION RAPPORT DETAILLE FORMAT DGFiP + ANALYSE IA")
    print("="*70 + "\n")

    # 1. Générer JSON enrichi
    print("[1/3] Generation du JSON enrichi...")
    json_data = generer_json_enrichi(fichier_pdf)
    print(f"      OK - Toutes donnees et ratios calcules\n")

    # 2. Générer sections avec templates
    print(f"[2/3] Generation des sections avec templates ({model})...")

    rapport = f"""RAPPORT D'ANALYSE BUDGÉTAIRE DÉTAILLÉ
{'='*70}

Commune: {json_data['metadata']['commune']}
Exercice: {json_data['metadata']['exercice']}
Population: {json_data['metadata']['population']} habitants
Strate: {json_data['metadata']['strate']['libelle']}

{'='*70}

FONCTIONNEMENT
"""

    sections = [
        {
            "titre": "Total des produits de fonctionnement",
            "donnees": {
                "total": json_data['fonctionnement']['produits']['total'],
                "produits_caf": json_data['fonctionnement']['produits']['produits_caf']
            }
        },
        {
            "titre": "Impôts locaux",
            "donnees": json_data['fonctionnement']['produits']['impots_locaux']
        },
        {
            "titre": "Autres impôts et taxes",
            "donnees": json_data['fonctionnement']['produits']['autres_impots_taxes']
        },
        {
            "titre": "Dotation globale de fonctionnement",
            "donnees": json_data['fonctionnement']['produits']['dgf']
        },
        {
            "titre": "Produits des services et du domaine",
            "donnees": json_data['fonctionnement']['produits']['produits_services_domaine']
        },
        {
            "titre": "Total des charges de fonctionnement",
            "donnees": {
                "total": json_data['fonctionnement']['charges']['total'],
                "charges_caf": json_data['fonctionnement']['charges']['charges_caf']
            }
        },
        {
            "titre": "Charges de personnel",
            "donnees": json_data['fonctionnement']['charges']['charges_personnel']
        },
        {
            "titre": "Achats et charges externes",
            "donnees": json_data['fonctionnement']['charges']['achats_charges_externes']
        },
        {
            "titre": "Charges financières",
            "donnees": json_data['fonctionnement']['charges']['charges_financieres']
        },
        {
            "titre": "Contingents",
            "donnees": json_data['fonctionnement']['charges']['contingents']
        },
        {
            "titre": "Subventions versées",
            "donnees": json_data['fonctionnement']['charges']['subventions_versees']
        },
        {
            "titre": "Résultat comptable",
            "donnees": json_data['fonctionnement']['resultat']
        }
    ]

    for i, section in enumerate(sections, 1):
        print(f"      [{i}/{len(sections)}] {section['titre']}...", end=" ")
        texte = generer_section_template(section['titre'], section['donnees'], model, verbose=False)
        if texte:
            rapport += f"\n{texte.strip()}\n"
            print("OK")
        else:
            print("ERREUR")

    # Section Investissement
    rapport += f"\n\n{'='*70}\nINVESTISSEMENT\n{'='*70}\n"

    sections_invest = [
        {
            "titre": "Total des ressources d'investissement - Emprunts bancaires",
            "donnees": json_data['investissement']['ressources']['emprunts']
        },
        {
            "titre": "Subventions reçues",
            "donnees": json_data['investissement']['ressources']['subventions_recues']
        },
        {
            "titre": "FCTVA (investissement)",
            "donnees": json_data['investissement']['ressources']['fctva']
        },
        {
            "titre": "Total des emplois d'investissement - Dépenses d'équipement",
            "donnees": json_data['investissement']['emplois']['depenses_equipement']
        },
        {
            "titre": "Remboursement d'emprunts",
            "donnees": json_data['investissement']['emplois']['remboursement_emprunts']
        },
        {
            "titre": "Besoin ou capacité de financement - Résultat d'ensemble",
            "donnees": json_data['investissement']['financement']
        }
    ]

    for i, section in enumerate(sections_invest, 1):
        print(f"      [{len(sections)+i}/{len(sections)+len(sections_invest)}] {section['titre']}...", end=" ")
        texte = generer_section_template(section['titre'], section['donnees'], model, verbose=False)
        if texte:
            rapport += f"\n{texte.strip()}\n"
            print("OK")
        else:
            print("ERREUR")

    # Section Autofinancement
    rapport += f"\n\n{'='*70}\nAUTOFINANCEMENT\n{'='*70}\n"

    sections_autofinancement = [
        {
            "titre": "Excédent brut de fonctionnement",
            "donnees": json_data['autofinancement']['ebf']
        },
        {
            "titre": "Capacité d'autofinancement (CAF)",
            "donnees": json_data['autofinancement']['caf_brute']
        },
        {
            "titre": "CAF nette du remboursement en capital des emprunts",
            "donnees": json_data['autofinancement']['caf_nette']
        }
    ]

    for i, section in enumerate(sections_autofinancement, 1):
        print(f"      [{len(sections)+len(sections_invest)+i}/"
              f"{len(sections)+len(sections_invest)+len(sections_autofinancement)}] "
              f"{section['titre']}...", end=" ")
        texte = generer_section_template(section['titre'], section['donnees'], model, verbose=False)
        if texte:
            rapport += f"\n{texte.strip()}\n"
            print("OK")
        else:
            print("ERREUR")

    # Section Endettement
    rapport += f"\n\n{'='*70}\nENDETTEMENT\n{'='*70}\n"

    sections_endettement = [
        {
            "titre": "Encours total de la dette au 31 décembre N",
            "donnees": {
                **json_data['endettement']['encours_total'],
                "ratios": json_data['endettement']['ratios']
            }
        },
        {
            "titre": "Annuité de la dette",
            "donnees": json_data['endettement']['annuite']
        },
        {
            "titre": "Fonds de roulement",
            "donnees": json_data['endettement']['fonds_roulement']
        }
    ]

    for i, section in enumerate(sections_endettement, 1):
        texte = generer_section_template(section['titre'], section['donnees'], model, verbose=False)
        if texte:
            rapport += f"\n{texte.strip()}\n"

    print(f"      OK - Toutes sections generees\n")

    # 3. Analyse globale IA
    print("[3/3] Generation de l'analyse globale et recommandations IA...")
    analyse_globale = generer_analyse_globale(json_data, model, verbose=True)

    if analyse_globale:
        rapport += f"\n\n{'='*70}\nANALYSE GLOBALE ET RECOMMANDATIONS (IA)\n{'='*70}\n\n"
        rapport += analyse_globale.strip()
        print("      OK\n")
    else:
        print("      ERREUR\n")

    # Sauvegarder
    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        f.write(rapport)

    print("="*70)
    print(f"RAPPORT GENERE: {fichier_sortie}")
    print(f"Taille: {len(rapport)} caracteres")
    print("="*70 + "\n")

    return rapport


if __name__ == "__main__":
    generer_rapport_complet("docs/bilan.pdf", model="mistral")
