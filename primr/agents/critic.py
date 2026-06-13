import openai
from .. import executor as bpy_executor

CRITIC_PROMPT = """You are the Primr Critic, an expert Blender Python debugger.
The Coder agent failed to generate a working script. Your job is to analyze the error and output a FIXED script.

<rules>
1. CHAIN OF THOUGHT: You MUST write out your debugging reasoning inside `<thinking>` tags BEFORE writing the fixed code.
2. SCRIPT FORMAT: Output the final, complete fixed script inside a single ```python block.
3. CONTEXT: Read the Scene Context and original goal to understand what went wrong.
4. SYNTAX: Ensure no `obj.select = True` or `bpy.context.selected_objects` are used if they caused the error.
5. SKILLS: The `skills` module is ALREADY in your namespace. DO NOT write `import skills`. Just call `skills.modeling.apply_...`.
6. FLAT SCRIPT: Do not wrap your code in `if __name__ == '__main__':`. Just write the script flat so it executes immediately.
</rules>
""".strip() + """

OUTPUT: Only raw corrected Python code. No markdown, no explanation.
"""


def review_and_fix(goal: str, code: str, error: str, model: str, api_key: str, base_url: str, scene: str, chat_history: list = None) -> str:
    """Ask the critic model to rewrite the failed script using OpenAI-compatible API.

    Returns a corrected Python script (raw text) extracted by executor.extract_code.
    """
    from .. import skills
    skill_docs = skills.get_skill_docs()

    user_message = (
        f"<goal>\n{goal}\n</goal>\n\n"
        f"<scene_context>\n{scene}\n</scene_context>\n\n"
        f"<skills>\n{skill_docs}\n</skills>\n\n"
        f"<original_code>\n{code}\n</original_code>\n\n"
        f"<error>\n{error}\n</error>"
    )

    client = openai.OpenAI(
        base_url=base_url,
        api_key=api_key or "local"
    )

    messages = [{"role": "system", "content": CRITIC_PROMPT}]
    
    if chat_history:
        messages.extend(chat_history)
        
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    content = response.choices[0].message.content
    return bpy_executor.extract_code(content) or ""
