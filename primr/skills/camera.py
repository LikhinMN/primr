import bpy
import math

def setup_cinematic_camera(location=(5, -5, 3), target_obj=None, focal_length=50):
    """Creates a camera with cinematic Depth of Field, tracking a target."""
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    cam.name = "Primr_CinematicCam"
    
    cam.data.lens = focal_length
    
    if target_obj:
        constr = cam.constraints.new(type='TRACK_TO')
        constr.target = target_obj
        constr.track_axis = 'TRACK_NEGATIVE_Z'
        constr.up_axis = 'UP_Y'
        
        # Depth of Field
        cam.data.dof.use_dof = True
        cam.data.dof.focus_object = target_obj
        cam.data.dof.aperture_fstop = 2.8
        
    bpy.context.scene.camera = cam
    return cam

def setup_turntable_animation(obj, frames=120):
    """Animates an object rotating 360 degrees perfectly looped."""
    obj.rotation_mode = 'XYZ'
    
    # Frame 1
    obj.rotation_euler.z = 0
    obj.keyframe_insert(data_path="rotation_euler", index=2, frame=1)
    
    # Frame end
    obj.rotation_euler.z = math.radians(360)
    obj.keyframe_insert(data_path="rotation_euler", index=2, frame=frames + 1)
    
    # Make interpolation linear
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            if fcurve.data_path == "rotation_euler" and fcurve.array_index == 2:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'LINEAR'
                    
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = frames
