import bpy


def get_scene_context() -> str:
    lines = []
    lines.append(f"Scene: {bpy.context.scene.name}")
    lines.append(f"Total objects: {len(bpy.context.scene.objects)}")
    for obj in bpy.context.scene.objects:
        lines.append(f"Object: {obj.name}")
    return "\n".join(lines)
