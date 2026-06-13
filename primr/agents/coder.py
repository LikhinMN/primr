import openai
from .. import context as scene_context
from .. import executor as bpy_executor

MASTER_PROMPT = """You are Primr, an expert Blender Python AI agent working inside Blender 4.x/5.x.
Your role is to write exact, executable Python scripts using `bpy` and `mathutils` to fulfill the user's 3D modeling, material, or lighting requests.

<rules>
1. CHAIN OF THOUGHT: You MUST write out your reasoning and plan inside `<thinking>` tags BEFORE writing any code.
2. SCRIPT FORMAT: Output the final, complete script inside a single ```python block.
3. OBJECT CREATION: After EVERY primitive creation (`bpy.ops.mesh.primitive_*`), IMMEDIATELY capture the reference: `obj = bpy.context.object`.
4. RENAMING: Always give every created object a unique, descriptive name: `obj.name = "table_leg_FR"`. Never hard-code names of existing objects unless found in the Scene Context.
5. NO SELECT: NEVER use `obj.select = True` or `obj.selected = True`. ALWAYS use `obj.select_set(True)`.
6. DESELECTION: Always `bpy.ops.object.select_all(action='DESELECT')` before selecting specific objects.
7. ACTIVE OBJECT: Set the active object explicitly when needed: `bpy.context.view_layer.objects.active = obj`.
8. TRANSFORMS: Position objects logically. A ground plane is at Z=0. Use `obj.dimensions` to calculate offsets (e.g. `obj.location.z = obj.dimensions.z / 2`).
9. METRICS: Use real-world metric scale. A standard table is ~1.2m long, 0.75m high.
10. SKILLS: The `skills` module is ALREADY in your namespace. DO NOT write `import skills`. Just call `skills.modeling.apply_...`.
11. FLAT SCRIPT: Do not wrap your code in `if __name__ == '__main__':`. Just write the script flat so it executes immediately.
</rules>

Follow the rules strictly. Ensure your script is completely self-contained.
"""


def generate(goal: str, model: str, api_key: str, base_url: str, extra_context: str = "", chat_history: list = None, scene_str: str = "") -> str:
    """Generate a single coordinated bpy script for the given goal using OpenAI-compatible API.

    Returns the extracted Python code as a string.
    """
    from .. import skills
    skill_docs = skills.get_skill_docs()

    user_message = (
        f"<scene_context>\n{scene_str}\n</scene_context>\n\n"
        f"{extra_context}\n\n"
        f"<skills>\n{skill_docs}\n</skills>\n\n"
        f"<goal>\n{goal}\n</goal>"
    )

    # Default to an empty string if api_key is None (e.g., for local endpoints)
    client = openai.OpenAI(
        base_url=base_url,
        api_key=api_key or "local"
    )

    messages = [{"role": "system", "content": MASTER_PROMPT}]
    
    if chat_history:
        messages.extend(chat_history)
        
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    content = response.choices[0].message.content
    return bpy_executor.extract_code(content) or ""
