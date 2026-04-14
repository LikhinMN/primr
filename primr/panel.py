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
        layout.label(text="What do you want to build?")
        layout.prop(scene, "primr_prompt", text="")
        layout.operator("primr.submit", text="Generate")
        layout.separator()
        layout.label(text=scene.primr_result)
        layout.separator()
        layout.operator("primr.clear", text="Clear History")
