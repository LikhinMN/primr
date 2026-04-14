import bpy
import subprocess
import sys
from . import panel
from . import operators
from . import agent


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
    bpy.types.Scene.primr_result = bpy.props.StringProperty(
        name="Result",
        default=""
    )
    bpy.types.Scene.primr_history = bpy.props.StringProperty(
        name="History",
        default=""
    )
    bpy.types.Scene.primr_ollama_url = bpy.props.StringProperty(
        name="Ollama URL",
        default="http://localhost:11434/v1/"
    )

    bpy.types.Scene.primr_model = bpy.props.StringProperty(
        name="Model",
        default="gemma4:e4b"
    )
    bpy.utils.register_class(panel.PRIMR_PT_main)
    bpy.utils.register_class(operators.PRIMR_OT_submit)
    bpy.utils.register_class(operators.PRIMR_OT_clear)


def unregister():
    del bpy.types.Scene.primr_prompt
    bpy.utils.unregister_class(operators.PRIMR_OT_submit)
    del bpy.types.Scene.primr_result
    bpy.utils.unregister_class(operators.PRIMR_OT_clear)
    agent.reset_history()
    del bpy.types.Scene.primr_history
    del bpy.types.Scene.primr_ollama_url
    del bpy.types.Scene.primr_model


if __name__ == "__main__":
    register()
