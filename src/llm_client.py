"""Unified LLM client with adapters for OpenRouter-compatible models and Google Gemini.

此模組封裝：
1. OpenRouterChatClient：透過 OpenRouter 單一端點呼叫多家模型。
2. GeminiChatClient：透過 Google Generative Language API 呼叫 Gemini 2.5 Pro。

當新增模型時，只需新增 adapter 類別並在 get_client() 工廠註冊名稱。
"""
from __future__ import annotations

import os
import time
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "30"))


class LLMError(Exception):
    """Custom exception for LLM related errors"""


class BaseChatClient(ABC):
    """Abstract base class for chat completion clients."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat completion request and return response text."""


class OpenRouterChatClient(BaseChatClient):
    """Client for any model可透過 OpenRouter chat/completions endpoint."""

    ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise LLMError("Missing OPENROUTER_API_KEY.")
        self.session = requests.Session()
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
    """Client for Google Gemini Pro/1.5 Pro.

    Google Generative Language API 目前常用 model:
    - gemini-pro (text-only, **v1**)
    - gemini-1.5-pro-latest (長上下文, **v1beta**)

    依官方文件，endpoint 需包含 model 名稱：
    https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
    """

    def __init__(self, model: str = "gemini-1.5-pro-latest", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise LLMError("Missing GEMINI_API_KEY.")
        self.session = requests.Session()
        self.session.params.update({"key": self.api_key})
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # Gemini expects the entire conversation flattened in "contents"
        # Gemini 不接受 "system" 角色，統一轉為 "user"
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
    # OpenRouter models
    "gpt-4o": (OpenRouterChatClient, "openai/gpt-4o"),
    # Anthropic Claude 3 Sonnet
    "claude-sonnet-3.7": (OpenRouterChatClient, "anthropic/claude-3-sonnet"),
    "claude-3-sonnet-20240229": (OpenRouterChatClient, "anthropic/claude-3-sonnet"),
    # Mistral Large
    "mistral-large": (OpenRouterChatClient, "mistralai/mistral-large"),
    # DeepSeek
    "deepseek-r1": (OpenRouterChatClient, "deepseek-ai/deepseek-llm-r1-chat"),
    "deepseek-chat": (OpenRouterChatClient, "deepseek-ai/deepseek-llm-r1-chat"),
    # Grok
    "grok-3": (OpenRouterChatClient, "xai/grok-3"),
    # Kimi (Moonshot)
    "kimi-k2": (OpenRouterChatClient, "moonshot-ai/moonshot-kimi-k2"),
    "kimi": (OpenRouterChatClient, "moonshot-ai/moonshot-kimi-k2"),
    # Perplexity
    "perplexity": (OpenRouterChatClient, "perplexity/pplx-70b-online"),
    # Gemini (Google)
    "gemini-pro": (GeminiChatClient, None),
    "gemini-1.5-pro-latest": (GeminiChatClient, None),
}


def get_client(name: str) -> BaseChatClient:
    """Return an initialized chat client by simplified name."""
    if name not in _CLIENT_REGISTRY:
        raise ValueError(f"Unknown model name: {name}")
    cls, model_name = _CLIENT_REGISTRY[name]
    if model_name is None:
        return cls()  # type: ignore[arg-type]
    return cls(model=model_name)  # type: ignore[arg-type]


# Simple test runner when executed standalone
if __name__ == "__main__":
    demo_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in one sentence."},
    ]
    for model in ("gpt-4o", "gemini-pro"):
        try:
            client = get_client(model)
            start = time.time()
            reply = client.chat(demo_messages)
            print(f"[{model}] {reply} (took {time.time() - start:.1f}s)")
        except Exception as err:
            print(f"[{model}] error: {err}")
