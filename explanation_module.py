from __future__ import annotations

import asyncio
from functools import lru_cache

from config import get_settings
from services.gemini_service import GeminiServiceError, get_gemini_service


@lru_cache(maxsize=1)
def _load_local_model():
    """Load LaMini only when explicitly enabled; this avoids a large startup/download by default."""
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    settings = get_settings()
    tokenizer = AutoTokenizer.from_pretrained(settings.local_explanation_model)
    model = AutoModelForSeq2SeqLM.from_pretrained(settings.local_explanation_model)
    return tokenizer, model


def _local_explain(topic: str) -> str:
    import torch

    tokenizer, model = _load_local_model()
    prompt = (
        "Explain the following topic for a beginner in simple language. "
        "Use a short definition, 3 key points, and one example.\n\nTopic: " + topic
    )
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=220, num_beams=4)
    return tokenizer.decode(output[0], skip_special_tokens=True).strip()


async def explain_topic(topic: str) -> str:
    settings = get_settings()
    if settings.local_explanation_enabled:
        try:
            return await asyncio.to_thread(_local_explain, topic)
        except Exception:
            # A local model download/runtime problem should not make the application unusable.
            pass

    prompt = f"""Explain this educational topic to a beginner: {topic}

Requirements:
- Start with a one-sentence definition.
- Explain the idea using simple language.
- Give 3 key points.
- Give one practical or everyday example.
- Avoid unnecessary jargon.
- Keep it concise."""
    return await get_gemini_service().generate(prompt, temperature=0.3)
