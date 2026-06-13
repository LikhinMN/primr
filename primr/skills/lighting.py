import bpy

def setup_studio_lights(energy=1000):
    """Creates a professional 3-point studio lighting setup."""
    
    # Create target for lights to point at
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    target = bpy.context.object
    target.name = "Primr_LightTarget"
    
    def _create_light(name, location, light_energy, color):
        bpy.ops.object.light_add(type='AREA', radius=2.0, location=location)
        light = bpy.context.object
        light.name = name
        light.data.energy = light_energy
        light.data.color = color
        
        constr = light.constraints.new(type='TRACK_TO')
        constr.target = target
        constr.track_axis = 'TRACK_NEGATIVE_Z'
        constr.up_axis = 'UP_Y'
        return light

    # Key Light (Warm, main source)
    _create_light("Primr_KeyLight", (3, -3, 3), energy, (1.0, 0.9, 0.8))
    
    # Fill Light (Cool, softer)
    _create_light("Primr_FillLight", (-4, -2, 2), energy * 0.4, (0.8, 0.9, 1.0))
    
    # Rim Light (Bright, behind object)
    _create_light("Primr_RimLight", (0, 4, 4), energy * 1.5, (1.0, 1.0, 1.0))
