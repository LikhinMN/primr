import re
import io
import traceback
import queue
from contextlib import redirect_stdout

import bpy
import mathutils
from .logger import logger

code_queue = queue.Queue()


def extract_code(response: str) -> str:
    """Extract Python code from an LLM response.

    Handles fenced ```python blocks or raw Python output.
    """
    match = re.search(r"```(?:python)?(.*?)```", response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response.strip()


def execute_code(code: str) -> str:
    """Execute Blender Python code with undo support, stdout capture,
    and an enriched namespace (bpy + mathutils).

    Returns 'Success' on success, or a detailed error string on failure.
    """
    logger.debug(f"Executing generated code:\n{code}")
    try:
        bpy.ops.ed.undo_push(message="Primr: " + code[:40])

        namespace = {
            "bpy": bpy,
            "mathutils": mathutils,
        }

        # Capture any print() output from the executed code
        capture_buffer = io.StringIO()
        with redirect_stdout(capture_buffer):
            exec(code, namespace)

        stdout_output = capture_buffer.getvalue()
        if stdout_output:
            return f"Success\nOutput:\n{stdout_output}"
        return "Success"
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Execution failed:\n{tb}")
        return f"Error executing code: {e}\n\nTraceback:\n{tb}"
