from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Any

from openai import OpenAI

# Load .env automatically when python-dotenv is installed.
# This lets Kimi/Moonshot API keys be stored in a local .env file.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # Environment variables still work without python-dotenv.
    pass


@dataclass
class ModelResponse:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    raw_model: str = ""


class OpenAICompatibleClient:
    """Generic OpenAI-compatible chat client for Ollama, Kimi/Moonshot, etc."""

    def __init__(
        self,
        model_name: str,
        base_url: str,
        api_key: str,
        timeout: int = 900,
        temperature: float = 0.0,
        max_tokens: Optional[int] = 8192,
        num_ctx: Optional[int] = None,
        extra_body: Optional[dict[str, Any]] = None,
        disable_thinking: bool = False,
    ):
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.num_ctx = num_ctx
        self.disable_thinking = disable_thinking
        self.default_extra_body = extra_body or {}
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)

    def _usage(self, response) -> tuple[int, int, int]:
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
        total_tokens = getattr(usage, "total_tokens", 0) if usage else (input_tokens + output_tokens)
        return input_tokens or 0, output_tokens or 0, total_tokens or 0

    def _extra_body(self, extra: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        body: dict[str, Any] = dict(self.default_extra_body)

        # Ollama OpenAI-compatible endpoint accepts options.num_ctx.
        if self.num_ctx is not None:
            options = dict(body.get("options", {}))
            options["num_ctx"] = int(self.num_ctx)
            body["options"] = options

        # Kimi K2.6 supports disabling thinking using this field.
        if self.disable_thinking:
            body["thinking"] = {"type": "disabled"}

        if extra:
            for k, v in extra.items():
                if isinstance(v, dict) and isinstance(body.get(k), dict):
                    merged = dict(body[k])
                    merged.update(v)
                    body[k] = merged
                else:
                    body[k] = v
        return body

    def complete(self, prompt: str) -> ModelResponse:
        kwargs = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a precise web data extraction engine. Return valid JSON only. "
                        "No markdown. No explanation. No comments. The first character must be { "
                        "and the last character must be }."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
            "stream": False,
            "extra_body": self._extra_body(),
        }
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens

        response = self.client.chat.completions.create(**kwargs)
        text = response.choices[0].message.content or ""
        input_tokens, output_tokens, total_tokens = self._usage(response)
        return ModelResponse(text=text, input_tokens=input_tokens, output_tokens=output_tokens, total_tokens=total_tokens, raw_model=self.model_name)

    def complete_with_image(self, prompt: str, image_data_url: str) -> ModelResponse:
        return self.complete_with_images(prompt=prompt, image_data_urls=[image_data_url])

    def complete_with_images(self, prompt: str, image_data_urls: list[str]) -> ModelResponse:
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for idx, image_data_url in enumerate(image_data_urls, start=1):
            content.append({"type": "text", "text": f"Screenshot tile {idx}, ordered from top to bottom:"})
            content.append({"type": "image_url", "image_url": {"url": image_data_url}})

        kwargs = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a precise visual web data extraction engine. Use only the provided "
                        "screenshot tiles. Return valid JSON only. No markdown. No explanation. "
                        "The first character must be { and the last character must be }."
                    ),
                },
                {"role": "user", "content": content},
            ],
            "temperature": self.temperature,
            "stream": False,
            "extra_body": self._extra_body(),
        }
        if self.max_tokens is not None:
            kwargs["max_tokens"] = self.max_tokens

        response = self.client.chat.completions.create(**kwargs)
        text = response.choices[0].message.content or ""
        input_tokens, output_tokens, total_tokens = self._usage(response)
        return ModelResponse(text=text, input_tokens=input_tokens, output_tokens=output_tokens, total_tokens=total_tokens, raw_model=self.model_name)


class OllamaOpenAIClient(OpenAICompatibleClient):
    def __init__(
        self,
        model_name: str = "gemma4:e4b",
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "ollama",
        timeout: int = 900,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        num_ctx: Optional[int] = 131072,
    ):
        super().__init__(
            model_name=model_name,
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
            num_ctx=num_ctx,
        )

    def _extra_body(self, extra: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        body = super()._extra_body(extra)
        # Ollama uses num_predict (in options) to cap generation.
        # When max_tokens is None we want truly unlimited output, so set num_predict=-1.
        options = dict(body.get("options", {}))
        options["num_predict"] = self.max_tokens if self.max_tokens is not None else -1
        body["options"] = options
        return body


class KimiK26Client(OpenAICompatibleClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.moonshot.ai/v1",
        model_name: str = "kimi-k2.6",
        timeout: int = 1200,
        temperature: float = 0.0,
        max_tokens: Optional[int] = 8192,
        disable_thinking: bool = True,
    ):
        key = api_key or os.environ.get("MOONSHOT_API_KEY") or os.environ.get("KIMI_API_KEY")
        if not key:
            raise ValueError("Missing Kimi API key. Set MOONSHOT_API_KEY or KIMI_API_KEY.")
        super().__init__(
            model_name=model_name,
            base_url=base_url,
            api_key=key,
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens,
            num_ctx=None,
            disable_thinking=disable_thinking,
        )


def create_model_client(
    model: str,
    *,
    num_ctx: Optional[int] = None,
    max_tokens: Optional[int] = 8192,
    temperature: float = 0.0,
):
    """Model registry for WADE-Bench.

    Supported local Ollama models:
      - gemma4:e4b / gemma4_e4b
      - gemma4-131k:latest / gemma4_131k
      - qwen3-vl:8b / qwen3_vl_8b

    Supported API model:
      - kimi-k2.6 / kimi26 / kimi_2_6
    """
    key = model.strip()
    normalized = key.lower().replace("_", "-")

    if normalized in {"gemma4:e4b", "gemma4-e4b", "ollama-gemma4-e4b"}:
        return OllamaOpenAIClient(
            model_name="gemma4:e4b",
            timeout=3600,
            max_tokens=max_tokens,
            temperature=temperature,
            num_ctx=num_ctx or 131072,
        )

    if normalized in {"gemma4-131k", "gemma4-131k:latest", "ollama-gemma4-131k"}:
        return OllamaOpenAIClient(
            model_name="gemma4-131k:latest",
            timeout=3600,
            max_tokens=max_tokens,
            temperature=temperature,
            num_ctx=num_ctx or 131072,
        )

    if normalized in {"qwen3-vl:8b", "qwen3-vl-8b", "qwen3vl:8b", "qwen3vl-8b", "ollama-qwen3-vl-8b"}:
        return OllamaOpenAIClient(
            model_name="qwen3-vl:8b",
            timeout=3600,
            max_tokens=max_tokens,
            temperature=temperature,
            num_ctx=num_ctx or 131072,
        )

    if normalized in {"kimi-k2.6", "kimi26", "kimi-2-6", "kimi-k2-6", "moonshot-kimi-k2.6"}:
        return KimiK26Client(
            max_tokens=max_tokens,
            temperature=temperature,
            disable_thinking=True,
        )

    raise ValueError(f"Unknown model: {model}")
