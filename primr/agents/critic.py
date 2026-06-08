import openai
from .. import executor as bpy_executor

CRITIC_PROMPT = """You are Primr's Critic — a senior Blender Python debugger.
A generated bpy script failed with an error. Your job is to rewrite the
ENTIRE script so it works correctly.

RULES:
1. FIX the specific error reported — read the traceback carefully.
2. Keep ALL original intent and functionality intact.
3. Name every object you create and use variables — never guess names.
4. After every bpy.ops creation call, capture: obj = bpy.context.object
5. Check if materials/collections exist before creating them.
6. Use proper context: deselect all before selecting, set active object
   before mode changes.
7. `mathutils` is available in the execution namespace.
8. Use `bpy.context.view_layer.update()` if you need updated transforms.

COMMON FIXES:
- "context is incorrect" → use `bpy.context.temp_override(...)` or
  ensure correct mode/selection.
- "object has no attribute" → the object type may be wrong; check obj.type.
- "name not found" → use bpy.data.objects.get("name") and handle None.
- RuntimeError in edit mode → make sure you're in the right mode with
  `bpy.ops.object.mode_set(mode='EDIT')`.

OUTPUT: Only raw corrected Python code. No markdown, no explanation.
"""


def review_and_fix(goal: str, code: str, error: str, model: str, api_key: str, scene: str) -> str:
    """Ask the critic model to rewrite the failed script using NVIDIA NIM.

    Returns a corrected Python script (raw text) extracted by executor.extract_code.
    """
    user_message = (
        f"Goal: {goal}\n\n"
        f"Scene:\n{scene}\n\n"
        f"Failed script:\n{code}\n\n"
        f"Error:\n{error}"
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
