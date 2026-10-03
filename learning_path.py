from services.gemini_service import get_gemini_service


async def get_learning_recommendations(topic: str, level: str = "beginner") -> str:
    prompt = f"""Create a personalized learning path for: {topic}
Learner level: {level}

Structure it from beginner to advanced. Include:
1. Learning stages in order.
2. Key concepts in each stage.
3. A suggested timeline.
4. Practice/project ideas.
5. Types of resources to use (videos, articles, books, documentation).
6. A short milestone/checkpoint for each stage.

Keep the plan practical and adaptable. Do not fabricate exact URLs."""
    return await get_gemini_service().generate(prompt, temperature=0.45, max_output_tokens=2500)
