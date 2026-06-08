import openai
from .. import executor as bpy_executor

CRITIC_PROMPT = """
You are Primr's Critic. A Blender Python script failed.
Rewrite the ENTIRE script correctly fixing the error.
Rules:
- Fix the specific error reported
- Keep all original intent intact
- Name all objects, use variables, no guessed names
- Output ONLY raw corrected Python, no markdown
"""


def review_and_fix(goal: str, code: str, error: str, model: str, api_key: str, scene: str) -> str:
    """Ask the critic model to rewrite the failed script using NVIDIA NIM.

    Returns a corrected Python script (raw text) extracted by executor.extract_code.
    """
    user_message = (
        f"Goal: {goal}\n\n"
        f"Scene:\n{scene}\n\n"
        f"Failed script:\n{code}\n\n"
        f"Error: {error}"
    )

    client = openai.OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CRITIC_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    content = response.choices[0].message.content
    return bpy_executor.extract_code(content) or ""
