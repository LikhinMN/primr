import ollama
from . import context

SYSTEM_PROMPT = """You are Primr, an AI agent that controls Blender 5.x via Python.
When the user gives you an instruction, respond with ONLY a Python
code block using the bpy module that fulfills the request.
Do not explain. Do not add markdown. Only output valid Python code."""

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]


def ask(prompt: str) -> str:
    global conversation_history
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    scene_info = context.get_scene_context()
    enriched_prompt = f"Current scene:\n{scene_info}\n\nUser instruction: {prompt}"
    conversation_history.append({"role": "user", "content": enriched_prompt})
    response = ollama.chat(model="gemma4:e4b", messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": enriched_prompt}
    ])
    print(f"Primr response: {response['message']['content']}")
    return response['message']['content']


def reset_history():
    conversation_history.clear()
    conversation_history.append({"role": "system", "content": SYSTEM_PROMPT})
