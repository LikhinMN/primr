import bpy

from . import state


class PRIMR_PT_main(bpy.types.Panel):
    bl_label = "Primr"
    bl_idname = "PRIMR_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Primr"

    def _draw_wrapped_text(self, layout, text, width=52):
        if not text:
            return
        for raw_line in text.splitlines() or [text]:
            line = raw_line.strip()
            if not line:
                continue
            while len(line) > width:
                split_at = line.rfind(" ", 0, width)
                if split_at <= 0:
                    split_at = width
                layout.label(text=line[:split_at])
                line = line[split_at:].lstrip()
            layout.label(text=line)

    def _draw_message(self, layout, message):
        sender = "You" if message.role == "user" else "Primr"
        icon = "USER" if message.role == "user" else "SCRIPT"

        row = layout.row()
        bubble = row.box()
        bubble.label(text=sender, icon=icon)

        if message.is_code:
            meta = bubble.row()
            meta.enabled = False
            meta.label(text="executed code")

        self._draw_wrapped_text(bubble, message.content)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        header = layout.box()
        header_row = header.row(align=True)
        header_row.label(text="Primr", icon="DOT")
        header_row.prop(scene, "primr_model", text="")

        settings = header.column(align=True)
        settings.prop(scene, "primr_ollama_url", text="Ollama URL")

        layout.separator()
        layout.label(text="Chat")
        chat = layout.box()

        messages = state.get_messages()
        if not messages:
            intro = chat.box()
            intro.label(text="Primr", icon="SCRIPT")
            self._draw_wrapped_text(
                intro,
                "Hey! Describe what you want to build. Use @ to reference objects in your scene.",
            )
        else:
            for message in messages:
                self._draw_message(chat, message)

        layout.separator()
        composer = layout.box()
        composer.label(text="Describe what to build")
        composer.prop(scene, "primr_prompt", text="")

        actions = composer.row(align=True)
        actions.operator("primr.submit", text="Generate", icon="PLAY")
        actions.operator("primr.clear", text="Clear", icon="TRASH")
