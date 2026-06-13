import bpy
from . import state

def wrap_text(text: str, width: int = 50) -> list[str]:
    if not text:
        return [""]
    # Simple word wrap
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def draw_message(layout, msg, index):
    box = layout.box()
    
    if msg.role == "user":
        col = box.column()
        row = col.row()
        row.alignment = 'RIGHT'
        row.label(text="You", icon='USER')
        for line in wrap_text(msg.content, 45):
            r = col.row()
            r.alignment = 'RIGHT'
            r.label(text=line)
    else:
        col = box.column()
        row = col.row()
        row.label(text="Primr", icon='AUTO')
        
        if msg.status == "error":
            row.label(icon='ERROR')
            
        if msg.is_code:
            code_row = col.row()
            icon = 'TRIA_DOWN' if msg.code_expanded else 'TRIA_RIGHT'
            op = code_row.operator("primr.toggle_code", text="Generated Script", icon=icon, emboss=False)
            op.msg_index = index
            
            if msg.code_expanded:
                code_box = col.box()
                for line in msg.content.split('\n'):
                    code_box.label(text=line)
        else:
            for line in wrap_text(msg.content, 50):
                col.label(text=line)


class PRIMR_PT_main(bpy.types.Panel):
    bl_label = "Primr AI"
    bl_idname = "PRIMR_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Primr"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # --- Top Bar (Settings Toggle & Clear) ---
        row = layout.row(align=True)
        # Instead of inline settings, just provide a button that opens preferences
        row.operator("screen.userpref_show", text="Settings", icon="PREFERENCES")
        row.operator("primr.clear", text="", icon="TRASH", emboss=False)

        # --- Chat Area ---
        messages = state.get_messages()
        if not messages:
            box = layout.box()
            box.label(text="Welcome to Primr!", icon='INFO')
            box.label(text="1. Set your API key in Settings (above).")
            box.label(text="2. Type an instruction below to generate code.")
            box.label(text="3. Primr remembers your conversation history.")
        else:
            for i, msg in enumerate(messages):
                draw_message(layout, msg, i)

        if state.is_thinking:
            box = layout.box()
            row = box.row()
            row.label(text="Generating script...", icon='TIME')

        layout.separator()

        # --- Input Area ---
        box = layout.box()
        col = box.column(align=True)
        
        # Tools row (Mentions & Images)
        tools_row = col.row(align=True)
        tools_row.prop(scene, "primr_object_picker", text="", icon='RESTRICT_SELECT_OFF')
        tools_row.operator("primr.mention_object", text="Mention", icon='EYEDROPPER')
        
        if scene.primr_image_path:
            img_row = col.row(align=True)
            img_row.prop(scene, "primr_image_path", text="")
            img_row.operator("primr.clear_image", text="", icon='X')

        # Prompt input
        col.separator()
        col.prop(scene, "primr_prompt", text="")
        
        # Submit Button
        col.separator()
        sub_row = col.row()
        sub_row.scale_y = 1.5
        if state.is_thinking:
            sub_row.enabled = False
            sub_row.operator("primr.submit", text="Working...", icon='PLAY')
        else:
            sub_row.operator("primr.submit", text="Generate", icon='PLAY')
