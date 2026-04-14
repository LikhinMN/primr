import bpy


class PRIMR_PT_main(bpy.types.Panel):
    bl_label = "Primr"
    bl_idname = "PRIMR_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Primr"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "primr_ollama_url", text="Ollama URL")
        layout.prop(scene, "primr_model", text="Model")
        layout.separator()
        layout.label(text="What do you want to build?")
        layout.prop(scene, "primr_prompt", text="")
        layout.operator("primr.submit", text="Generate")
        layout.separator()
        layout.label(text="History:")
        box = layout.box()
        for entry in scene.primr_history.split("\n\n"):
            box.label(text=entry)
        layout.separator()
        layout.operator("primr.clear", text="Clear History")
