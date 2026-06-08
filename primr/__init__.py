import bpy
import subprocess
import sys
import queue
from . import panel
from . import operators
from . import agent


def primr_execution_timer():
    """Main-thread timer that drains the execution queue.

    Background threads place (code, result_list, event) tuples into
    executor.code_queue. This timer runs on Blender's main thread at
    ~10 Hz, picks up queued code, executes it safely, writes the result
    back, and signals the waiting thread.
    """
    from . import executor

    try:
        code, result_list, event = executor.code_queue.get_nowait()
        result = executor.execute_code(code)
        result_list.append(result)
        event.set()
    except queue.Empty:
        pass
    return 0.1


def get_scene_objects(self, context):
    scene = context.scene if context else bpy.context.scene
    objects = scene.objects if scene else []
    if not objects:
        return [("NONE", "No objects in scene", "")]
    return [(obj.name, obj.name, obj.type) for obj in objects]


def ensure_dependencies():
    try:
        import openai
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "openai"], check=True)
        import openai


def refresh_panel():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
    return 0.5


# ------------------------------------------------------------------ #
#  Registration
# ------------------------------------------------------------------ #

_classes = (
    panel.PRIMR_PT_main,
    operators.PRIMR_OT_submit,
    operators.PRIMR_OT_toggle_code,
    operators.PRIMR_OT_mention_object,
    operators.PRIMR_OT_clear_image,
    operators.PRIMR_OT_clear,
)


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
    bpy.types.Scene.primr_api_key = bpy.props.StringProperty(
        name="NVIDIA API Key",
        default="",
        subtype="PASSWORD"
    )
    bpy.types.Scene.primr_model = bpy.props.StringProperty(
        name="Model",
        default="meta/llama-3.1-405b-instruct"
    )
    bpy.types.Scene.primr_image_path = bpy.props.StringProperty(
        name="Reference Image",
        description="Path to reference image",
        subtype="FILE_PATH",
        default=""
    )
    bpy.types.Scene.primr_mention = bpy.props.StringProperty(
        name="Mention Object",
        description="Object to mention in prompt",
        default=""
    )
    bpy.types.Scene.primr_object_picker = bpy.props.EnumProperty(
        name="Pick Object",
        items=get_scene_objects
    )
    bpy.types.Scene.primr_show_settings = bpy.props.BoolProperty(
        name="Show Settings",
        default=False
    )

    for cls in _classes:
        bpy.utils.register_class(cls)

    bpy.app.timers.register(refresh_panel, first_interval=0.5)
    bpy.app.timers.register(primr_execution_timer, first_interval=0.1)


def unregister():
    if bpy.app.timers.is_registered(primr_execution_timer):
        bpy.app.timers.unregister(primr_execution_timer)
    if bpy.app.timers.is_registered(refresh_panel):
        bpy.app.timers.unregister(refresh_panel)

    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)

    agent.reset_history()

    del bpy.types.Scene.primr_prompt
    del bpy.types.Scene.primr_result
    del bpy.types.Scene.primr_history
    del bpy.types.Scene.primr_api_key
    del bpy.types.Scene.primr_model
    del bpy.types.Scene.primr_image_path
    del bpy.types.Scene.primr_mention
    del bpy.types.Scene.primr_object_picker
    del bpy.types.Scene.primr_show_settings


if __name__ == "__main__":
    register()
