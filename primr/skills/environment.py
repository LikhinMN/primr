import bpy
import bmesh

def create_studio_backdrop(size=10.0, height=5.0, color=(0.1, 0.1, 0.1, 1.0)):
    """Creates a curved photography studio backdrop."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    backdrop = bpy.context.object
    backdrop.name = "Primr_Backdrop"
    
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    
    bm = bmesh.from_edit_mesh(backdrop.data)
    
    # Find back edge (y > 0)
    back_verts = [v for v in bm.verts if v.co.y > 0]
    back_edges = [e for e in bm.edges if e.verts[0] in back_verts and e.verts[1] in back_verts]
    
    # Extrude
    res = bmesh.ops.extrude_edge_only(bm, edges=back_edges)
    verts = [v for v in res['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, 0, height), verts=verts)
    
    # Find the new corner edge
    corner_edges = [e for e in bm.edges if not e.is_boundary]
    
    # Bevel the corner
    bmesh.ops.bevel(bm, geom=corner_edges, offset=size/4.0, segments=16, profile=0.5, affect='EDGES')
    
    bmesh.update_edit_mesh(backdrop.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    bpy.ops.object.shade_smooth()
    
    # Material
    mat = bpy.data.materials.new("Primr_BackdropMat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.8
    backdrop.data.materials.append(mat)
    
    return backdrop
