from __future__ import annotations

import asyncio
from typing import Any

from config import get_settings

try:
    from google import genai
    from google.genai import types
except ImportError:  # Allows non-AI unit tests before dependencies are installed.
    genai = None
    types = None


class GeminiServiceError(RuntimeError):
    pass


class GeminiService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: genai.Client | None = None
        self._init_client()

    def _is_valid_key(self, key: str) -> bool:
        return bool(
            key
            and key != "PASTE_MY_API_KEY_HERE"
            and not key.startswith("PASTE_")
        )

    def _init_client(self) -> None:
        self.settings = get_settings()
        if self._is_valid_key(self.settings.gemini_api_key) and genai is not None:
            self.client = genai.Client(api_key=self.settings.gemini_api_key)
        else:
            self.client = None

    @property
    def available(self) -> bool:
        if self.client is None:
            self._init_client()
        return self.client is not None

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.4,
        max_output_tokens: int = 2048,
        response_schema: Any | None = None,
        system_instruction: str | None = None,
    ) -> str:
        if not self.available:
            if self._is_valid_key(self.settings.gemini_api_key) and genai is None:
                raise GeminiServiceError("google-genai is not installed. Run: pip install -r requirements.txt")
            raise GeminiServiceError(
                "Gemini API is not configured. Add GEMINI_API_KEY to your .env file."
            )

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json" if response_schema else "text/plain",
            response_schema=response_schema,
            system_instruction=system_instruction,
        )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.settings.gemini_model,
                contents=prompt,
                config=config,
            )
        except Exception as exc:
            raise GeminiServiceError(f"Gemini request failed: {exc}") from exc

        text = getattr(response, "text", None)
        if not text:
            raise GeminiServiceError("Gemini returned an empty response.")
        return text.strip()


_gemini_service: GeminiService | None = None


def get_gemini_service() -> GeminiService:
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
