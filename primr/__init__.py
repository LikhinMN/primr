import bpy
import subprocess
import sys
from . import panel


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


def unregister():
    del bpy.types.Scene.primr_prompt


if __name__ == "__main__":
    register()
