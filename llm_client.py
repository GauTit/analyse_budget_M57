"""
Module d'abstraction pour les APIs LLM
Permet de changer facilement entre OpenAI, Anthropic (Claude), DeepSeek, Gemini, etc.

Configuration via variables d'environnement (.env) :
    LLM_PROVIDER=openai|anthropic|deepseek|gemini

    OPENAI_API_KEY=votre-cle-openai
    OPENAI_MODEL=gpt-4.1-mini

    ANTHROPIC_API_KEY=votre-cle-anthropic
    ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

    DEEPSEEK_API_KEY=votre-cle-deepseek
    DEEPSEEK_MODEL=deepseek-chat

    GEMINI_API_KEY=votre-cle-gemini
    GEMINI_MODEL=gemini-2.0-flash-exp

    LLM_TEMPERATURE=0.0
    LLM_MAX_TOKENS=2000

Usage:
    from llm_client import creer_client_llm

    client = creer_client_llm()
    reponse = client.generer_reponse("Votre prompt ici")
"""

import os
import re
from abc import ABC, abstractmethod


# =============================================================================
# POST-PROCESSING : VALIDATION DES TERMES INTERDITS
# =============================================================================

# Termes à nettoyer automatiquement (safe à supprimer)
TERMES_A_NETTOYER = {
    # Expressions typiques des LLMs (à nettoyer en début de phrase)
    r'^Il faut noter que\s+': '',
    r'^Nous constatons que\s+': '',
    r'^On observe que\s+': '',
    r'^On peut noter que\s+': '',
    r'^Nous pouvons constater que\s+': '',
    r'^Il est important de noter que\s+': '',
    r'^Notons que\s+': '',
    r'^Il convient de noter que\s+': '',
    r'^Force est de constater que\s+': '',
    r'^Il apparait que\s+': '',
    r'^Il ressort que\s+': '',

    # Pronoms démonstratifs en début de phrase (remplacement safe)
    r'^Ce poste\s+': 'Le poste ',
    r"^Cette situation\s+": "La situation ",
    r"^Ces postes\s+": "Les postes ",
}

# Patterns d'alerte (détection sans remplacement automatique)
PATTERNS_ALERTE = {
    'vocabulaire_managerial': [
        r'\bpilotage\b', r'\boptimisation\b',
        r"\blevier d['']action\b", r'\bmarge de man[oœ]uvre\b',
        r'\bmarge de sécurité\b'
    ],
    'termes_temporels_interdits': [
        r'\bévolution\b', r'\bvariation\b',
        r'\bprogressi(on|f)\b', r'\bdégradation\b',
        r'\bstabilité\b'
    ],
    'pronoms_demonstratifs': [
        r'^Ce poste\b', r'^Cette évolution\b',
        r'^Cet agrégat\b', r'^Cette situation\b'
    ],
    'formulations_conditionnelles': [
        r'sous réserve de', r'à condition de',
        r"sous réserve d['']un"
    ],
    'ton_alarmiste': [
        r'\balarmant\b', r'\binquiétant\b', r'\bpréoccupant\b',
        r'\bgrave\b', r'\bcritique\b(?! du)', r'\bdramatique\b'
    ],
    'recommandations': [
        r'\bdevrait\b', r'\bil faut\b', r'\bil faudrait\b',
        r'\brecommandons\b', r'\bsuggérons\b',
        r'\bconseillons\b', r'\bpréconisons\b'
    ],
    'autofinance': [
        r'\bautofinancé\b'
    ]
}


def nettoyer_termes_interdits(texte, verbose=True):
    """
    Nettoie les termes interdits dans la réponse du LLM

    Args:
        texte (str): Texte à nettoyer
        verbose (bool): Si True, affiche les warnings

    Returns:
        tuple: (texte_nettoyé, liste_warnings)
    """
    if not texte:
        return texte, []

    texte_original = texte
    warnings = []

    # 1. Nettoyage automatique des formulations LLM (phrase par phrase pour gérer les débuts de phrase)
    lignes = texte.split('\n')
    lignes_nettoyees = []

    for ligne in lignes:
        ligne_nettoyee = ligne

        # Appliquer les remplacements automatiques (safe)
        for pattern, remplacement in TERMES_A_NETTOYER.items():
            matches = re.findall(pattern, ligne_nettoyee, re.IGNORECASE)
            if matches:
                warnings.append(f"[NETTOYE] Formulation LLM supprimee : '{matches[0]}'")
                ligne_nettoyee = re.sub(pattern, remplacement, ligne_nettoyee, flags=re.IGNORECASE)

        # Nettoyer les espaces multiples et les débuts de phrase vides
        ligne_nettoyee = re.sub(r'\s+', ' ', ligne_nettoyee).strip()

        lignes_nettoyees.append(ligne_nettoyee)

    texte_nettoye = '\n'.join(lignes_nettoyees)

    # 2. Détection des patterns d'alerte (sans remplacement automatique)
    for categorie, patterns in PATTERNS_ALERTE.items():
        for pattern in patterns:
            matches = re.findall(pattern, texte_nettoye, re.IGNORECASE)
            if matches:
                warnings.append(f"[ALERTE {categorie.upper()}] Terme suspect detecte : '{matches[0]}'")

    # 3. Afficher les warnings si verbose
    if verbose and warnings:
        print(f"\n[!] POST-PROCESSING : {len(warnings)} terme(s) interdit(s) detecte(s)")
        for w in warnings[:5]:  # Limiter à 5 pour ne pas polluer
            print(f"  - {w}")
        if len(warnings) > 5:
            print(f"  ... et {len(warnings) - 5} autre(s)")

    return texte_nettoye, warnings


class ClientLLMBase(ABC):
    """Classe de base pour tous les clients LLM"""

    def __init__(self, model, temperature=0.0, max_tokens=2000):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def generer_reponse(self, prompt):
        """Génère une réponse à partir d'un prompt"""
        pass

    @abstractmethod
    def get_provider_name(self):
        """Retourne le nom du provider"""
        pass


class ClientOpenAI(ClientLLMBase):
    """Client pour l'API OpenAI (GPT)"""

    def __init__(self, api_key, model, temperature=0.0, max_tokens=2000):
        super().__init__(model, temperature, max_tokens)

        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "La bibliothèque 'openai' n'est pas installée. "
                "Installez-la avec : pip install openai"
            )

        if not api_key:
            raise ValueError(
                "La clé API OpenAI n'est pas configurée. "
                "Veuillez définir la variable d'environnement OPENAI_API_KEY."
            )

        self.client = OpenAI(api_key=api_key)

    def generer_reponse(self, prompt):
        """Génère une réponse en utilisant l'API OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            reponse_brute = response.choices[0].message.content

            # Post-processing : nettoyage des termes interdits
            reponse_nettoyee, warnings = nettoyer_termes_interdits(reponse_brute)
            return reponse_nettoyee
        except Exception as e:
            raise Exception(f"Erreur lors de l'appel API OpenAI : {e}")

    def get_provider_name(self):
        return f"OpenAI ({self.model})"


class ClientAnthropic(ClientLLMBase):
    """Client pour l'API Anthropic (Claude)"""

    def __init__(self, api_key, model, temperature=0.0, max_tokens=2000):
        super().__init__(model, temperature, max_tokens)

        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError(
                "La bibliothèque 'anthropic' n'est pas installée. "
                "Installez-la avec : pip install anthropic"
            )

        if not api_key:
            raise ValueError(
                "La clé API Anthropic n'est pas configurée. "
                "Veuillez définir la variable d'environnement ANTHROPIC_API_KEY."
            )

        self.client = Anthropic(api_key=api_key)

    def generer_reponse(self, prompt):
        """Génère une réponse en utilisant l'API Anthropic"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            reponse_brute = response.content[0].text

            # Post-processing : nettoyage des termes interdits
            reponse_nettoyee, warnings = nettoyer_termes_interdits(reponse_brute)
            return reponse_nettoyee
        except Exception as e:
            raise Exception(f"Erreur lors de l'appel API Anthropic : {e}")

    def get_provider_name(self):
        return f"Anthropic Claude ({self.model})"


class ClientDeepSeek(ClientLLMBase):
    """Client pour l'API DeepSeek (compatible OpenAI)"""

    def __init__(self, api_key, model, temperature=0.0, max_tokens=2000):
        super().__init__(model, temperature, max_tokens)

        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "La bibliothèque 'openai' n'est pas installée. "
                "Installez-la avec : pip install openai"
            )

        if not api_key:
            raise ValueError(
                "La clé API DeepSeek n'est pas configurée. "
                "Veuillez définir la variable d'environnement DEEPSEEK_API_KEY."
            )

        # DeepSeek utilise une API compatible OpenAI
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def generer_reponse(self, prompt):
        """Génère une réponse en utilisant l'API DeepSeek"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            reponse_brute = response.choices[0].message.content

            # Post-processing : nettoyage des termes interdits
            reponse_nettoyee, warnings = nettoyer_termes_interdits(reponse_brute)
            return reponse_nettoyee
        except Exception as e:
            raise Exception(f"Erreur lors de l'appel API DeepSeek : {e}")

    def get_provider_name(self):
        return f"DeepSeek ({self.model})"


class ClientGemini(ClientLLMBase):
    """Client pour l'API Google Gemini"""

    def __init__(self, api_key, model, temperature=0.0, max_tokens=2000):
        super().__init__(model, temperature, max_tokens)

        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "La bibliothèque 'google-generativeai' n'est pas installée. "
                "Installez-la avec : pip install google-generativeai"
            )

        if not api_key:
            raise ValueError(
                "La clé API Gemini n'est pas configurée. "
                "Veuillez définir la variable d'environnement GEMINI_API_KEY."
            )

        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    def generer_reponse(self, prompt):
        """Génère une réponse en utilisant l'API Gemini"""
        try:
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
            )
            reponse_brute = response.text

            # Post-processing : nettoyage des termes interdits
            reponse_nettoyee, warnings = nettoyer_termes_interdits(reponse_brute)
            return reponse_nettoyee
        except Exception as e:
            raise Exception(f"Erreur lors de l'appel API Gemini : {e}")

    def get_provider_name(self):
        return f"Google Gemini ({self.model})"


def creer_client_llm(provider=None, model=None, temperature=None, max_tokens=None):
    """
    Crée et retourne un client LLM selon la configuration

    Args:
        provider (str): Provider à utiliser ('openai', 'anthropic').
                       Si None, utilise LLM_PROVIDER du .env
        model (str): Modèle à utiliser. Si None, utilise la config du .env
        temperature (float): Température. Si None, utilise LLM_TEMPERATURE du .env
        max_tokens (int): Tokens max. Si None, utilise LLM_MAX_TOKENS du .env

    Returns:
        ClientLLMBase: Instance du client LLM configuré

    Raises:
        ValueError: Si le provider est invalide ou mal configuré
    """

    # Récupérer la configuration depuis l'environnement
    provider = provider or os.getenv("LLM_PROVIDER", "openai").lower()
    temperature = temperature if temperature is not None else float(os.getenv("LLM_TEMPERATURE", "0.0"))
    max_tokens = max_tokens if max_tokens is not None else int(os.getenv("LLM_MAX_TOKENS", "2000"))

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        return ClientOpenAI(api_key, model, temperature, max_tokens)

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
        return ClientAnthropic(api_key, model, temperature, max_tokens)

    elif provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        return ClientDeepSeek(api_key, model, temperature, max_tokens)

    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        return ClientGemini(api_key, model, temperature, max_tokens)

    else:
        raise ValueError(
            f"Provider LLM invalide : '{provider}'. "
            f"Providers supportés : 'openai', 'anthropic', 'deepseek', 'gemini'"
        )


def afficher_configuration():
    """Affiche la configuration LLM actuelle (utile pour debug)"""
    provider = os.getenv("LLM_PROVIDER", "openai")

    print("Configuration LLM actuelle :")
    print(f"  Provider : {provider}")

    if provider == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        api_key = os.getenv("OPENAI_API_KEY", "")
        print(f"  Modèle : {model}")
        print(f"  API Key : {'✓ configurée' if api_key else '✗ manquante'}")

    elif provider == "anthropic":
        model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        print(f"  Modèle : {model}")
        print(f"  API Key : {'✓ configurée' if api_key else '✗ manquante'}")

    elif provider == "deepseek":
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        print(f"  Modèle : {model}")
        print(f"  API Key : {'✓ configurée' if api_key else '✗ manquante'}")

    elif provider == "gemini":
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        api_key = os.getenv("GEMINI_API_KEY", "")
        print(f"  Modèle : {model}")
        print(f"  API Key : {'✓ configurée' if api_key else '✗ manquante'}")

    temperature = os.getenv("LLM_TEMPERATURE", "0.0")
    max_tokens = os.getenv("LLM_MAX_TOKENS", "2000")
    print(f"  Temperature : {temperature}")
    print(f"  Max tokens : {max_tokens}")


if __name__ == "__main__":
    # Test rapide
    try:
        afficher_configuration()
        print("\nTest de création du client...")
        client = creer_client_llm()
        print(f"✓ Client créé avec succès : {client.get_provider_name()}")
    except Exception as e:
        print(f"✗ Erreur : {e}")
