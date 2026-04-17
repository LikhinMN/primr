import bpy
import subprocess
import sys
from . import panel
from . import operators
from . import agent


def get_models(self, context):
    models = agent.get_local_models()
    return [(m, m, "") for m in models]


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

    bpy.types.Scene.primr_model = bpy.props.EnumProperty(
        name="Model",
        items=get_models
    )
    bpy.types.Scene.primr_image_path = bpy.props.StringProperty(
        name="Reference Image",
        description="Path to reference image",
        subtype="FILE_PATH",
        default=""
    )
    bpy.types.Scene.primr_show_settings = bpy.props.BoolProperty(
        name="Show Settings",
        default=False
    )
    bpy.utils.register_class(panel.PRIMR_PT_main)
    bpy.utils.register_class(operators.PRIMR_OT_submit)
    bpy.utils.register_class(operators.PRIMR_OT_toggle_code)
    bpy.utils.register_class(operators.PRIMR_OT_clear_image)
    bpy.utils.register_class(operators.PRIMR_OT_clear)


def unregister():
    del bpy.types.Scene.primr_prompt
    del bpy.types.Scene.primr_result
    agent.reset_history()
    del bpy.types.Scene.primr_history
    del bpy.types.Scene.primr_ollama_url
    del bpy.types.Scene.primr_model
    del bpy.types.Scene.primr_image_path
    del bpy.types.Scene.primr_show_settings
    bpy.utils.unregister_class(operators.PRIMR_OT_clear)
    bpy.utils.unregister_class(operators.PRIMR_OT_clear_image)
    bpy.utils.unregister_class(operators.PRIMR_OT_toggle_code)
    bpy.utils.unregister_class(operators.PRIMR_OT_submit)
    bpy.utils.unregister_class(panel.PRIMR_PT_main)


if __name__ == "__main__":
    register()
