import bpy
import subprocess
import sys
from . import panel
from . import operators


def ensure_dependencies():
    try:
        import ollama
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "ollama"], check=True)
        import ollama


def register():
    ensure_dependencies()
    bpy.types.Scene.primr_prompt = bpy.props.StringProperty(
        name="Prompt",
        description="Your instruction to Primr",
        default=""
    )
    bpy.utils.register_class(panel.PRIMR_PT_main)
    bpy.utils.register_class(operators.PRIMR_OT_submit)


def unregister():
    del bpy.types.Scene.primr_prompt
    bpy.utils.unregister_class(operators.PRIMR_OT_submit)


if __name__ == "__main__":
    register()
