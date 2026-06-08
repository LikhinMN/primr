import openai
from .. import context as scene_context
from .. import executor as bpy_executor

MASTER_PROMPT = """
You are Primr, an expert Blender Python developer working in Blender 5.x.
Write a single, complete, coordinated Python script using bpy that fulfills the user's goal.

STRICT RULES:
1. Write ONE complete Python script — not steps, not explanations
2. Always assign objects to variables immediately after creation:
   obj = bpy.context.object
3. Always name every object you create:
   obj.name = "descriptive_unique_name"
4. Use variable names for all subsequent operations — never guess names
5. Check if material/collection exists before creating:
   mat = bpy.data.materials.get("name") or bpy.data.materials.new("name")
6. Position objects logically in 3D space (ground at Z=0, stack using dimensions)
7. Always use bpy.context.scene for scene-level operations
8. Add section comments: # --- Trunk ---
9. No markdown, no explanation, no triple backticks
10. Output ONLY raw executable Python
Think step by step internally, output only the final coordinated script.
"""


def generate(goal: str, model: str, api_key: str, extra_context: str = "") -> str:
    """Generate a single coordinated bpy script for the given goal using NVIDIA NIM.

    Returns the extracted Python code as a string.
    """
    scene = scene_context.get_scene_context()

    user_message = f"Current scene:\n{scene}\n\n{extra_context}\n\nGoal: {goal}"

    client = openai.OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": MASTER_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    content = response.choices[0].message.content
    return bpy_executor.extract_code(content) or ""

