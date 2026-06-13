import bpy
import os

def build_from_image(image_path: str, name: str = "WireframeMesh", bevel_depth: float = 0.01, extrude: float = 0.0):
    """
    Converts a 2D wireframe image into a 3D Blender Curve/Mesh.
    Requires opencv-python to be installed in Blender's Python environment.
    """
    if not image_path or not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
        
    try:
        import cv2
        import numpy as np
    except ImportError:
        raise ImportError(
            "The 'wireframe-to-3d' skill requires OpenCV. "
            "Please install it in Blender's Python console: "
            "import subprocess; subprocess.call(['python', '-m', 'pip', 'install', 'opencv-python'])"
        )
        
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
        
    # Process image to find contours
    _, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        raise ValueError("No wireframe contours found in the image.")
        
    height, width = img.shape
    
    # Create Curve Data
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = bevel_depth
    curve_data.extrude = extrude
    curve_data.use_fill_caps = True
    
    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    
    for cnt in contours:
        epsilon = 2.0
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        if len(approx) < 3:
            continue
            
        spline = curve_data.splines.new(type='POLY')
        spline.points.add(len(approx) - 1)
        
        for i, p in enumerate(approx):
            px, py = p[0]
            # Normalize to -1 to 1 space
            norm_x = (px / width) * 2.0 - 1.0
            norm_y = 1.0 - (py / height) * 2.0 # Flip Y
            
            spline.points[i].co = (norm_x, norm_y, 0.0, 1.0)
            
        spline.use_cyclic_u = True
        
    return obj
