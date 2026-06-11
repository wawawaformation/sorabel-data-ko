"""Fabrique du modèle Kimi-K2.6 hébergé sur Azure AI Foundry."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def get_llm():
    """Instancie le client de chat Azure AI pour le déploiement Kimi-K2.6."""
    from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel

    return AzureAIChatCompletionsModel(
        endpoint=os.environ["AZURE_AI_INFERENCE_ENDPOINT"],
        credential=os.environ["AZURE_AI_INFERENCE_API_KEY"],
        model=os.environ.get("AZURE_AI_INFERENCE_MODEL", "Kimi-K2.6"),
    )
