from __future__ import annotations

import json
from typing import Any

from services.gemini_service import get_gemini_service


def _quiz_schema():
    from google.genai import types

    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            "questions": types.Schema(
                type=types.Type.ARRAY,
                min_items=3,
                max_items=3,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "question": types.Schema(type=types.Type.STRING),
                        "options": types.Schema(
                            type=types.Type.ARRAY,
                            min_items=4,
                            max_items=4,
                            items=types.Schema(type=types.Type.STRING),
                        ),
                        "correct_answer": types.Schema(type=types.Type.STRING),
                        "explanation": types.Schema(type=types.Type.STRING),
                    },
                    required=["question", "options", "correct_answer", "explanation"],
                ),
            )
        },
        required=["questions"],
    )


def clean_json_block(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return text


async def generate_quiz(passage: str) -> dict[str, Any]:
    prompt = f"""Create exactly three educational multiple-choice questions from the passage below.
Each question must have exactly four options.
The correct_answer must exactly match one option.
Include a brief explanation of why the answer is correct.

PASSAGE:
{passage}"""
    raw = await get_gemini_service().generate(
        prompt,
        temperature=0.35,
        max_output_tokens=1800,
        response_schema=_quiz_schema(),
    )
    try:
        data = json.loads(clean_json_block(raw))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Quiz JSON could not be parsed: {exc}") from exc

    questions = data.get("questions", [])
    if len(questions) != 3:
        raise ValueError("Quiz generator did not return exactly 3 questions.")
    for q in questions:
        if len(q.get("options", [])) != 4 or q["correct_answer"] not in q["options"]:
            raise ValueError("Quiz generator returned an invalid question structure.")
    return data
