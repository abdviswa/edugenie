from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from config import get_settings
from explanation_module import explain_topic
from learning_path import get_learning_recommendations
from qna import answer_question
from quiz_module import generate_quiz
from services.gemini_service import GeminiServiceError, get_gemini_service
from summary_module import summarize_text


# ---------------------------------------------------------
# Application configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


# ---------------------------------------------------------
# Static files and templates
# ---------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=settings.max_input_chars,
    )


class LearningPathRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )

    level: str = Field(
        default="beginner",
        min_length=1,
        max_length=50,
    )


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
        },
    )


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "gemini_configured": get_gemini_service().available,
        "model": settings.gemini_model,
        "local_explanation_enabled": settings.local_explanation_enabled,
    }


# ---------------------------------------------------------
# Question & Answer
# ---------------------------------------------------------

@app.post("/qa")
async def qa(payload: TextRequest):
    try:
        return {
            "answer": await answer_question(payload.text)
        }

    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------

@app.post("/explain")
async def explain(payload: TextRequest):
    try:
        return {
            "explanation": await explain_topic(payload.text)
        }

    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Explanation failed: {exc}",
        ) from exc


# ---------------------------------------------------------
# Quiz generation
# ---------------------------------------------------------

@app.post("/quiz")
async def quiz(payload: TextRequest):
    try:
        return await generate_quiz(payload.text)

    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------
# Summarization
# ---------------------------------------------------------

@app.post("/summarize")
async def summarize(payload: TextRequest):
    try:
        return {
            "summary": await summarize_text(payload.text)
        }

    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------
# Learning recommendations
# ---------------------------------------------------------

@app.post("/learn/recommendations")
async def learning_recommendations(
    payload: LearningPathRequest
):
    try:
        return {
            "recommendations": await get_learning_recommendations(
                payload.topic,
                payload.level,
            )
        }

    except GeminiServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc


# ---------------------------------------------------------
# Run application
# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )