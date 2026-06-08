import bpy
import mathutils
import json


def _get_aabb(obj):
    """Returns the world-space axis-aligned bounding box (AABB) of a mesh object."""
    if obj.type != "MESH":
        return None

    local_bbox_corners = [mathutils.Vector(corner) for corner in obj.bound_box]
    world_bbox_corners = [obj.matrix_world @ corner for corner in local_bbox_corners]

    min_corner = mathutils.Vector(map(min, zip(*world_bbox_corners)))
    max_corner = mathutils.Vector(map(max, zip(*world_bbox_corners)))

    return {
        "min": [round(v, 3) for v in min_corner],
        "max": [round(v, 3) for v in max_corner],
    }


def _get_material_summary(obj):
    """Get a concise summary of an object's materials."""
    materials = []
    for slot in obj.material_slots:
        if slot.material:
            mat = slot.material
            mat_info = {"name": mat.name}
            if mat.use_nodes and mat.node_tree:
                principled = None
                for node in mat.node_tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        principled = node
                        break
                if principled:
                    bc = principled.inputs.get("Base Color")
                    if bc and hasattr(bc, "default_value"):
                        color = bc.default_value
                        mat_info["base_color"] = [round(color[0], 3), round(color[1], 3), round(color[2], 3)]
                    metallic = principled.inputs.get("Metallic")
                    if metallic and hasattr(metallic, "default_value"):
                        mat_info["metallic"] = round(metallic.default_value, 3)
                    roughness = principled.inputs.get("Roughness")
                    if roughness and hasattr(roughness, "default_value"):
                        mat_info["roughness"] = round(roughness.default_value, 3)
            materials.append(mat_info)
    return materials


def _get_modifier_list(obj):
    """Get a list of modifier names and types on an object."""
    modifiers = []
    for mod in obj.modifiers:
        modifiers.append({"name": mod.name, "type": mod.type})
    return modifiers


def _get_constraint_list(obj):
    """Get a list of constraint names and types on an object."""
    constraints = []
    for con in obj.constraints:
        constraints.append({"name": con.name, "type": con.type})
    return constraints


def _get_object_summary(obj, detailed=False):
    """Build a summary dict for a single object.

    When detailed=True (for @mentioned objects), include materials,
    mesh stats, modifiers, constraints, and bounding box.
    """
    info = {
        "name": obj.name,
        "type": obj.type,
        "location": [round(obj.location.x, 3), round(obj.location.y, 3), round(obj.location.z, 3)],
        "rotation": [round(obj.rotation_euler.x, 3), round(obj.rotation_euler.y, 3), round(obj.rotation_euler.z, 3)],
        "scale": [round(obj.scale.x, 3), round(obj.scale.y, 3), round(obj.scale.z, 3)],
        "visible": obj.visible_get(),
    }

    if obj.parent:
        info["parent"] = obj.parent.name

    children = [c.name for c in obj.children]
    if children:
        info["children"] = children

    # Always include material names
    mat_names = [slot.material.name for slot in obj.material_slots if slot.material]
    if mat_names:
        info["materials"] = mat_names

    # Mesh stats for mesh objects
    if obj.type == "MESH" and obj.data:
        mesh = obj.data
        info["mesh"] = {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "polygons": len(mesh.polygons),
        }

    if detailed:
        # Full material info with node tree summary
        info["material_details"] = _get_material_summary(obj)

        # Bounding box
        bbox = _get_aabb(obj)
        if bbox:
            info["bounding_box"] = bbox

        # Modifiers
        mods = _get_modifier_list(obj)
        if mods:
            info["modifiers"] = mods

        # Constraints
        cons = _get_constraint_list(obj)
        if cons:
            info["constraints"] = cons

    return info


def _get_collections_hierarchy():
    """Build a tree of collections and their members."""
    def _walk(collection):
        result = {"name": collection.name, "objects": [o.name for o in collection.objects]}
        children = [_walk(child) for child in collection.children]
        if children:
            result["children"] = children
        return result

    return _walk(bpy.context.scene.collection)


def get_scene_context(prompt: str = "") -> str:
    """Build a rich JSON scene context string for the LLM.

    Objects whose names appear after '@' in the prompt receive detailed
    introspection (materials, modifiers, bounding boxes, etc.).
    """
    scene = bpy.context.scene
    objects = list(scene.objects)

    # Detect @mentions
    mentioned_names = set()
    if prompt:
        import re
        mentioned_names = set(re.findall(r"@(\S+)", prompt))

    # --- Scene overview ---
    scene_info = {
        "scene_name": scene.name,
        "object_count": len(objects),
        "materials_count": len(bpy.data.materials),
        "render_engine": scene.render.engine,
        "frame_current": scene.frame_current,
        "frame_range": [scene.frame_start, scene.frame_end],
    }

    # Active object
    active = bpy.context.view_layer.objects.active
    if active:
        scene_info["active_object"] = active.name

    # Selected objects
    selected = [o.name for o in bpy.context.selected_objects]
    if selected:
        scene_info["selected_objects"] = selected

    # --- Objects (limit to 20 to avoid token bloat) ---
    object_list = []
    MAX_OBJECTS = 20
    for i, obj in enumerate(objects):
        if i >= MAX_OBJECTS:
            break
        is_mentioned = obj.name in mentioned_names
        object_list.append(_get_object_summary(obj, detailed=is_mentioned))

    if len(objects) > MAX_OBJECTS:
        scene_info["objects_truncated"] = True
        scene_info["objects_shown"] = MAX_OBJECTS

    scene_info["objects"] = object_list

    # --- Collections ---
    scene_info["collections"] = _get_collections_hierarchy()

    # --- World / Lighting summary ---
    lights = [
        {"name": o.name, "light_type": o.data.type, "energy": round(o.data.energy, 1)}
        for o in objects
        if o.type == "LIGHT" and o.data
    ]
    if lights:
        scene_info["lights"] = lights

    cameras = [o.name for o in objects if o.type == "CAMERA"]
    if cameras:
        scene_info["cameras"] = cameras
    if scene.camera:
        scene_info["active_camera"] = scene.camera.name

    return json.dumps(scene_info, indent=2)


def get_object_info(name: str) -> str:
    """Get deep introspection for a specific object by name.

    Returns a JSON string with full details including transforms,
    materials with node tree info, mesh stats, modifiers, constraints,
    bounding box, and parent/children.
    """
    obj = bpy.data.objects.get(name)
    if not obj:
        return json.dumps({"error": f"Object not found: {name}"})

    info = _get_object_summary(obj, detailed=True)
    return json.dumps(info, indent=2)
