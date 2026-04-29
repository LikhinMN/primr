import bpy


def get_scene_context(prompt: str = "") -> str:
    scene = bpy.context.scene
    objects = list(scene.objects)
    mentioned = [obj for obj in objects if f"@{obj.name}" in prompt]

    lines = []
    lines.append(f"Scene: {scene.name}")
    lines.append(f"Total objects: {len(objects)}")

    if mentioned:
        lines.append("Mentioned objects (high priority):")
        for obj in mentioned:
            lines.append(f"Mentioned Object: {obj.name} ({obj.type})")

    lines.append("Existing objects (use exact names to reference them):")
    for obj in objects:
        location = tuple(round(value, 2) for value in obj.location)
        lines.append(f"  - name: '{obj.name}' | type: {obj.type} | location: {location}")

    for obj in objects:
        prefix = "Object*" if obj in mentioned else "Object"
        lines.append(f"{prefix}: {obj.name} ({obj.type})")

    return "\n".join(lines)
