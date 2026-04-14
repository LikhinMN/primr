import re
import bpy


def extract_code(response: str) -> str:
    match = re.search(r"```python(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response.strip()


def execute_code(code: str) -> str:
    try:
        bpy.ops.ed.undo_push(message="Primr: " + code[:40])
        exec(code, {"bpy": bpy})
        return "Code executed successfully."
    except Exception as e:
        return f"Error executing code: {e}"
