from . import materials
from . import lighting
from . import wireframe
from . import modeling
from . import physics
from . import camera
from . import environment

def get_skill_docs():
    """Returns a string describing available skills to be injected into the LLM prompt."""
    docs = []
    docs.append("━━━━━━━━━━━━━━━━━━━  SKILL LIBRARY  ━━━━━━━━━━━━━━━━━━━━")
    docs.append("You have access to pre-written macros via the `skills` module.")
    docs.append("Use these INSTEAD of writing complex node setups or lighting from scratch!")
    docs.append("")
    docs.append("--- MATERIALS ---")
    docs.append("skills.materials.apply_glass(obj, color=(1,1,1,1), roughness=0.1, ior=1.45)")
    docs.append("skills.materials.apply_metal(obj, color=(0.8,0.8,0.8,1), roughness=0.2)")
    docs.append("skills.materials.apply_emission(obj, color=(1,1,1,1), strength=10.0)")
    docs.append("")
    docs.append("--- LIGHTING & ENVIRONMENT ---")
    docs.append("skills.lighting.setup_studio_lights(energy=1000)")
    docs.append("skills.environment.create_studio_backdrop(size=10.0, height=5.0, color=(0.1, 0.1, 0.1, 1.0))")
    docs.append("")
    docs.append("--- MODELING & MESH OPS ---")
    docs.append("skills.modeling.apply_hard_surface_modifiers(obj, bevel_amount=0.01, subdiv_levels=2)")
    docs.append("skills.modeling.apply_boolean_cut(target_obj, cutter_obj, solver='EXACT')")
    docs.append("")
    docs.append("--- CAMERA & ANIMATION ---")
    docs.append("skills.camera.setup_cinematic_camera(location=(5, -5, 3), target_obj=None, focal_length=50)")
    docs.append("skills.camera.setup_turntable_animation(obj, frames=120)")
    docs.append("")
    docs.append("--- PHYSICS ---")
    docs.append("skills.physics.make_rigid_body(obj, type='ACTIVE', mass=1.0, shape='CONVEX_HULL')")
    docs.append("skills.physics.make_cloth(obj, quality=5)")
    docs.append("")
    docs.append("--- IMAGE TO 3D ---")
    docs.append("skills.wireframe.build_from_image(image_path, name='Wireframe', bevel_depth=0.01, extrude=0.0)")
    docs.append("Use this when the user asks to convert an image, drawing, or wireframe to 3D. Pass `bpy.context.scene.primr_image_path` as the image_path.")
    docs.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    return "\n".join(docs)
