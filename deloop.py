# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_deloop

import bmesh
import bpy
from bpy.types import Operator, Panel
from bpy.utils import register_class, unregister_class

bl_info = {
    "name": "Deloop",
    "description": "Remove edges with linked faces that all have the same material.",
    "author": "Nikita Akimov, Paul Kotelevets",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool panel > 1D > Deloop",
    "doc_url": "https://github.com/Korchy/1d_deloop",
    "tracker_url": "https://github.com/Korchy/1d_deloop",
    "category": "All"
}


# MAIN CLASS

class Deloop:

    @staticmethod
    def remove_edges(context):
        # dissolve linked edges started from selected vertices with same material
        #   on both linked faces
        src_obj = context.active_object
        # current mode
        mode = src_obj.mode
        # switch to OBJECT mode
        if src_obj.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
        # process object
        # get data from source mesh
        bm = bmesh.new()
        bm.from_mesh(context.object.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        # STEP 1 - dissolve edges with same material on linked faces
        # selected vertices (except first and last)
        vertices = (vertex for vertex in bm.verts if vertex.select
                    and len([e for e in vertex.link_edges if e.select]) > 1)
        if vertices:
            # non-selected edges, linked to these vertices
            edges = [edge for vertex in vertices
                     for edge in vertex.link_edges if not edge.select]
            # get only edges with same material on linked polygons
            edges_same_mat = [edge for edge in edges
                              if len(set(face.material_index for face in edge.link_faces)) == 1]
            # dissolve founded edges
            bmesh.ops.dissolve_edges(bm, edges=edges_same_mat)
        # STEP 2 - dissolve vertices with same material on linked faces
        vertices = (vertex for vertex in bm.verts if vertex.select
                    and len([e for e in vertex.link_edges if e.select]) > 1)
        if vertices:
            # filter by same material on linked faces
            vertices_same_mat = [vertex for vertex in vertices
                                 if len(set(face.material_index for face in vertex.link_faces)) == 1]
            # dissolve founded vertices
            bmesh.ops.dissolve_verts(bm, verts=vertices_same_mat)
        # save changed data to mesh
        bm.to_mesh(src_obj.data)
        bm.free()
        # return mode back
        context.scene.objects.active = src_obj
        bpy.ops.object.mode_set(mode=mode)


# OPERATORS

class Deloop_OT_remove_edges(Operator):
    bl_idname = 'deloop.remove_edges'
    bl_label = 'Deloop'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Deloop.remove_edges(
            context=context
        )
        return {'FINISHED'}


# PANELS

class Deloop_PT_panel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Deloop"
    bl_category = '1D'

    def draw(self, context):
        self.layout.operator(
            operator='deloop.remove_edges',
            icon='AUTOMERGE_ON'
        )


# REGISTER

def register():
    register_class(Deloop_OT_remove_edges)
    register_class(Deloop_PT_panel)


def unregister():
    unregister_class(Deloop_PT_panel)
    unregister_class(Deloop_OT_remove_edges)


if __name__ == "__main__":
    register()
