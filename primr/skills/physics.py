import bpy

def setup_rigid_body_world():
    """Ensures the scene has a rigid body world."""
    if bpy.context.scene.rigidbody_world is None:
        bpy.ops.rigidbody.world_add()

def make_rigid_body(obj, type='ACTIVE', mass=1.0, shape='CONVEX_HULL'):
    """Makes an object a rigid body (ACTIVE or PASSIVE)."""
    setup_rigid_body_world()
    bpy.context.view_layer.objects.active = obj
    if obj.rigid_body is None:
        bpy.ops.rigidbody.object_add()
    
    obj.rigid_body.type = type
    if type == 'ACTIVE':
        obj.rigid_body.mass = mass
    obj.rigid_body.collision_shape = shape

def make_cloth(obj, quality=5):
    """Applies cloth physics to an object."""
    bpy.context.view_layer.objects.active = obj
    cloth = obj.modifiers.new(name="Primr_Cloth", type='CLOTH')
    
    # Add collision so it interacts with other things
    if obj.collision is None:
        bpy.ops.object.modifier_add(type='COLLISION')
        
    obj.modifiers["Primr_Cloth"].settings.quality = quality
    obj.modifiers["Primr_Cloth"].collision_settings.use_self_collision = True
