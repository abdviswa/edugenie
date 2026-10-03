from services.gemini_service import get_gemini_service


async def answer_question(question: str) -> str:
    prompt = f"""You are EduGenie, an educational question-answering assistant.
Answer the student's question accurately and concisely.

Question:
{question}

Rules:
- Give the direct answer first.
- Add a short explanation when useful.
- If the question is ambiguous, state the assumption.
- Do not invent sources, facts, or citations."""
    return await get_gemini_service().generate(prompt, temperature=0.2)
