import base64
import os
import ollama
from . import context

SYSTEM_PROMPT = """You are Primr, an AI agent that controls Blender 5.x via Python.
When the user gives you an instruction, respond with ONLY a Python
code block using the bpy module that fulfills the request.
Do not explain. Do not add markdown. Only output valid Python code."""

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]
prompt_history = []


def get_local_models() -> list[str]:
    try:
        response = ollama.list()
        models_data = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
        models: list[str] = []

        for item in models_data:
            if isinstance(item, dict):
                name = item.get("model") or item.get("name")
            else:
                name = getattr(item, "model", None) or getattr(item, "name", None)

            if name:
                models.append(name)

        return models or ["gemma4:4b"]
    except Exception:
        return ["gemma4:4b"]


def ask(
    prompt: str,
    model: str = "gemma3:4b",
    url: str = "http://localhost:11434",
    image_path: str = "",
) -> str:
    global conversation_history
    global prompt_history
    if len(prompt_history) > 5:
        prompt_history = prompt_history[-5:]
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    scene_info = context.get_scene_context()
    enriched_prompt = f"Current scene:\n{scene_info}\n\nUser instruction: {prompt}"
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as file:
            image_data = base64.b64encode(file.read()).decode()
        user_message = {
            "role": "user",
            "content": enriched_prompt,
            "images": [image_data],
        }
    else:
        user_message = {
            "role": "user",
            "content": enriched_prompt,
        }

    conversation_history.append(user_message)
    response = ollama.chat(model=model, messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        user_message
    ])
    return response['message']['content']


def reset_history():
    conversation_history.clear()
    reset_prompt_history()
    conversation_history.append({"role": "system", "content": SYSTEM_PROMPT})


def add_to_prompt(prompt: str, result: str):
    prompt_history.append(f" {prompt}\n  {result}")


def reset_prompt_history():
    prompt_history.clear()
