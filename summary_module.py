from services.gemini_service import get_gemini_service


async def summarize_text(text: str) -> str:
    prompt = f"""Summarize the following educational passage for quick revision.
Keep all important facts and remove repetition.
Use a short heading followed by concise bullet points.

PASSAGE:
{text}"""
    return await get_gemini_service().generate(prompt, temperature=0.25, max_output_tokens=1800)
