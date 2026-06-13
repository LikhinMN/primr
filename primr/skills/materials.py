import bpy

def _get_or_create_material(name):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    return mat

def _assign_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def apply_glass(obj, color=(1, 1, 1, 1), roughness=0.1, ior=1.45):
    """Applies a realistic glass material to the object."""
    mat = _get_or_create_material(f"Primr_Glass_{obj.name}")
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Roughness"].default_value = roughness
        
        # Blender 4.0+ uses 'Transmission Weight' instead of 'Transmission'
        transmission_input = principled.inputs.get("Transmission Weight")
        if not transmission_input:
            transmission_input = principled.inputs.get("Transmission")
            
        if transmission_input:
            transmission_input.default_value = 1.0
            
        principled.inputs["IOR"].default_value = ior
    _assign_material(obj, mat)

def apply_metal(obj, color=(0.8, 0.8, 0.8, 1), roughness=0.2):
    """Applies a realistic metal material to the object."""
    mat = _get_or_create_material(f"Primr_Metal_{obj.name}")
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = color
        principled.inputs["Metallic"].default_value = 1.0
        principled.inputs["Roughness"].default_value = roughness
    _assign_material(obj, mat)

def apply_emission(obj, color=(1, 1, 1, 1), strength=10.0):
    """Applies an emissive (glowing) material to the object."""
    mat = _get_or_create_material(f"Primr_Emission_{obj.name}")
    nodes = mat.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    if principled:
        # Blender 4.0+ Principled BSDF Emission
        emission_color = principled.inputs.get("Emission Color")
        if not emission_color:
            emission_color = principled.inputs.get("Emission")
        if emission_color:
            emission_color.default_value = color
            
        emission_strength = principled.inputs.get("Emission Strength")
        if emission_strength:
            emission_strength.default_value = strength
    _assign_material(obj, mat)
