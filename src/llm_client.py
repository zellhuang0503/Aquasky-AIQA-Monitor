"""Unified LLM client with adapters for OpenRouter-compatible models and Google Gemini.

此模組封裝：
1. OpenRouterChatClient：透過 OpenRouter 單一端點呼叫多家模型。
2. GeminiChatClient：透過 Google Generative Language API 呼叫 Gemini 2.5 Pro。

當新增模型時，只需新增 adapter 類別並在 get_client() 工廠註冊名稱。
"""
from __future__ import annotations

import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import configparser
from pathlib import Path
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

# --- Configuration Loading ---
# Build a robust path to the config.ini file and load it.
config = configparser.ConfigParser()
config_path = Path(__file__).parent.parent / 'config.ini'
config.read(config_path)

HTTP_TIMEOUT = config.getint('settings', 'HTTP_TIMEOUT', fallback=60) # Increased timeout for more stability


class LLMError(Exception):
    """Custom exception for LLM related errors"""


class BaseChatClient(ABC):
    """Abstract base class for chat completion clients."""

    def _create_session_with_retries(self) -> requests.Session:
        """Creates a requests session with a retry mechanism."""
        session = requests.Session()
        retries = Retry(
            total=3,  # Total number of retries
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[500, 502, 503, 504],  # Retry on these server errors
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat completion request and return response text."""


class OpenRouterChatClient(BaseChatClient):
    """Client for any model可透過 OpenRouter chat/completions endpoint."""

    ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or config.get('api_keys', 'OPENROUTER_API_KEY', fallback=None)
        if not self.api_key:
            raise LLMError("Missing OPENROUTER_API_KEY.")
        self.session = self._create_session_with_retries()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": "Aquasky-AIQA-Monitor"
        })

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": False,
        }
        resp = self.session.post(self.ENDPOINT, json=payload, timeout=HTTP_TIMEOUT)
        if resp.status_code != 200:
            raise LLMError(f"OpenRouter API error: {resp.status_code} {resp.text}")
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            raise LLMError(f"Unexpected response format: {data}")


class GeminiChatClient(BaseChatClient):
    """Client for Google Gemini Pro/1.5 Pro."""

    def __init__(self, model: str = "gemini-1.5-pro-latest", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or config.get('api_keys', 'GEMINI_API_KEY', fallback=None)
        if not self.api_key:
            raise LLMError("Missing GEMINI_API_KEY.")
        self.session = self._create_session_with_retries()
        self.session.params.update({"key": self.api_key})
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        contents = []
        for m in messages:
            role = "user" if m["role"] == "system" else m["role"]
            contents.append({"role": role, "parts": [{"text": m["content"]}]})
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 1024),
            },
        }
        resp = self.session.post(self.endpoint, json=payload, timeout=HTTP_TIMEOUT)
        if resp.status_code != 200:
            raise LLMError(f"Gemini API error: {resp.status_code} {resp.text}")
        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError):
            raise LLMError(f"Unexpected response format: {data}")


# Factory mapping
_CLIENT_REGISTRY = {
    # --- User Specified Models for Final Run ---
    "kimi-k2-free": (OpenRouterChatClient, "moonshotai/kimi-k2:free"),
    "devstral-medium": (OpenRouterChatClient, "mistralai/devstral-medium"),
    "deepseek-chimera-free": (OpenRouterChatClient, "tngtech/deepseek-r1t2-chimera:free"),
    "gemini-2.5-flash-lite": (OpenRouterChatClient, "google/gemini-2.5-flash-lite-preview-06-17"),
    "grok-3": (OpenRouterChatClient, "x-ai/grok-3"),
    "claude-sonnet-4": (OpenRouterChatClient, "anthropic/claude-sonnet-4"),
    "gpt-4o-mini-high": (OpenRouterChatClient, "openai/o4-mini-high"),
    "perplexity-sonar-pro": (OpenRouterChatClient, "perplexity/sonar-pro"),
}


def get_client(name: str) -> BaseChatClient:
    """Return an initialized chat client by simplified name."""
    if name not in _CLIENT_REGISTRY:
        raise ValueError(f"Unknown model name: {name}")
    
    client_class, model_name = _CLIENT_REGISTRY[name]
    
    # Pass the specific model name if it exists, otherwise the client uses its default
    if model_name:
        return client_class(model=model_name)
    else:
        return client_class()