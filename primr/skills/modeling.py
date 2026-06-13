import bpy

def apply_hard_surface_modifiers(obj, bevel_amount=0.01, subdiv_levels=2):
    """Applies a professional non-destructive hard-surface modifier stack."""
    # Add Bevel
    bevel = obj.modifiers.new(name="Primr_Bevel", type='BEVEL')
    bevel.width = bevel_amount
    bevel.segments = 3
    bevel.limit_method = 'ANGLE'
    bevel.angle_limit = 0.523599 # 30 degrees
    bevel.profile = 0.5
    if hasattr(bevel, "harden_normals"):
        bevel.harden_normals = True
    
    # Add Subdivision
    subdiv = obj.modifiers.new(name="Primr_Subdiv", type='SUBSURF')
    subdiv.levels = subdiv_levels
    subdiv.render_levels = subdiv_levels + 1
    
    # Auto Smooth
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    if hasattr(obj.data, "use_auto_smooth"):
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = 0.523599

def apply_boolean_cut(target_obj, cutter_obj, solver='EXACT'):
    """Performs a non-destructive boolean difference."""
    bool_mod = target_obj.modifiers.new(name=f"Primr_Cut_{cutter_obj.name}", type='BOOLEAN')
    bool_mod.operation = 'DIFFERENCE'
    bool_mod.object = cutter_obj
    bool_mod.solver = solver
    
    # Hide cutter from render and display as bounds
    cutter_obj.display_type = 'BOUNDS'
    cutter_obj.hide_render = True
