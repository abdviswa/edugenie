from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)


class Settings(BaseModel):
    app_name: str = "EduGenie"
    app_version: str = "1.0.0"
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-3.8-flash")
    local_explanation_enabled: bool = False
    local_explanation_model: str = "MBZUAI/LaMini-Flan-T5-783M"
    app_env: str = "development"
    max_input_chars: int = 20000


def get_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env", override=True)
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip(),
        local_explanation_enabled=os.getenv("LOCAL_EXPLANATION_ENABLED", "false").lower() == "true",
        local_explanation_model=os.getenv(
            "LOCAL_EXPLANATION_MODEL", "MBZUAI/LaMini-Flan-T5-783M"
        ).strip(),
        app_env=os.getenv("APP_ENV", "development").strip(),
    )
