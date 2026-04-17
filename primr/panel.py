import bpy

from . import state


def wrap_text(text: str, width: int = 60) -> list[str]:
    if not text:
        return [""]
    return [text[i : i + width] for i in range(0, len(text), width)]


def draw_message(layout, msg):
    box = layout.box()
    role_row = box.row()

    if msg.role == "user":
        role_row.alignment = "RIGHT"
        role_row.label(text="You", icon="USER")
        for line in wrap_text(msg.content, 60):
            line_row = box.row()
            line_row.alignment = "RIGHT"
            line_row.label(text=line)
        return

    role_row.alignment = "LEFT"
    role_row.label(text="Primr", icon="SHADERFX")

    if msg.is_code:
        row = box.row()
        op = row.operator(
            "primr.toggle_code",
            text="Hide code ▴" if msg.code_expanded else "Show code ▾",
            emboss=False,
        )
        op.msg_index = state.get_messages().index(msg)
        if msg.code_expanded:
            for line in wrap_text(msg.content, 55):
                box.label(text=line)
    else:
        for line in wrap_text(msg.content, 55):
            box.label(text=line)


class PRIMR_PT_main(bpy.types.Panel):
    bl_label = "Primr"
    bl_idname = "PRIMR_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Primr"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        header = layout.row(align=True)
        header.label(text="Primr Chat", icon="SHADERFX")

        box = layout.box()
        row = box.row()
        row.prop(
            scene,
            "primr_show_settings",
            icon="TRIA_DOWN" if scene.primr_show_settings else "TRIA_RIGHT",
            text="Settings",
            emboss=False,
        )
        if scene.primr_show_settings:
            box.prop(scene, "primr_model", text="Model")
            box.prop(scene, "primr_ollama_url", text="Ollama URL")

        layout.separator()

        messages = state.get_messages()
        for msg in messages:
            draw_message(layout, msg)

        if state.is_thinking:
            box = layout.box()
            box.label(text="Primr is thinking...", icon="SORTTIME")

        layout.separator()

        row = layout.row(align=True)
        row.prop(scene, "primr_image_path", text="")
        row.operator("primr.clear_image", text="", icon="X")

        layout.prop(scene, "primr_prompt", text="")
        row = layout.row(align=True)
        row.operator("primr.submit", text="Generate", icon="PLAY")
        row.operator("primr.clear", text="", icon="TRASH")
