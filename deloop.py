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
    "version": (1, 1, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool panel > 1D > Deloop",
    "doc_url": "https://github.com/Korchy/1d_deloop",
    "tracker_url": "https://github.com/Korchy/1d_deloop",
    "category": "All"
}


# MAIN CLASS

class Deloop:

    @classmethod
    def desolve_edges(cls, context):
        # dissolve edges from selection that is not: crease, sharp, seam, bevel edge, freestyle edge
        # at present - only select edges
        src_obj = context.active_object
        # current mode
        mode = src_obj.mode
        # switch to OBJECT mode
        if src_obj.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
        # switch to "edge selection" mode
        context.tool_settings.mesh_select_mode = (False, True, False)
        # process object
        # get data from source mesh
        bm = bmesh.new()
        bm.from_mesh(src_obj.data)
        bm.edges.ensure_lookup_table()
        # get crease layer to check "mean crease" edges
        crease_layer = bm.edges.layers.crease.verify()
        # get bevel weight layer to check "mean bevel weight" edges
        bevel_weight_layer = bm.edges.layers.bevel_weight.verify()
        # freestyle edges - get from common mesh (not implemented in BMesh yet)
        freestyle_edges_ids = [edge.index for edge in src_obj.data.edges if edge.use_freestyle_mark]
        # process selected edges
        selected_edges = [edge for edge in bm.edges if edge.select]
        # deselect all edges
        cls._deselect_all(bm=bm)
        # select only by conditions
        for edge in selected_edges:
            # edges with same material on both linked faces
            # and not crease (crease == 0)
            # and not sharp (smooth == True)
            # and not uv seam (seam == False)
            # and not bevel weight (mean bevel weight == 0)
            # and not freestyle (edge id is not in freestyle_edges_ids list)
            if len(set(face.material_index for face in edge.link_faces)) <= 1 \
                    and edge[crease_layer] <= 0.0 \
                    and edge.smooth \
                    and not edge.seam \
                    and edge[bevel_weight_layer] <= 0.0\
                    and edge.index not in freestyle_edges_ids:
                edge.select = True
        # save changed data to mesh
        bm.to_mesh(src_obj.data)
        bm.free()
        # return mode back
        context.scene.objects.active = src_obj
        bpy.ops.object.mode_set(mode=mode)

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

    @staticmethod
    def _deselect_all(bm):
        # remove all selection from edges and vertices in bmesh
        for face in bm.faces:
            face.select = False
        for edge in bm.edges:
            edge.select = False
        for vertex in bm.verts:
            vertex.select = False

    # @staticmethod
    # def _deselect_edge(bm_edge):
    #     # deselect bmesh edge
    #     # for face in bm_edge.link_faces:
    #     #     face.select = False
    #     bm_edge.select = False
    #     for vert in bm_edge.verts:
    #         vert.select = False

    @staticmethod
    def ui(layout, context):
        # ui panel
        layout.operator(
            operator='deloop.remove_edges',
            icon='AUTOMERGE_ON'
        )
        layout.operator(
            operator='deloop.desolve_edges',
            icon='PARTICLE_POINT'
        )


# OPERATORS

class Deloop_OT_remove_edges(Operator):
    bl_idname = 'deloop.remove_edges'
    bl_label = 'Deloop'
    bl_description = ('Clean up edges connected to the inner vertices of a selected loop that has the same '
                      'adjacent material')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Deloop.remove_edges(
            context=context
        )
        return {'FINISHED'}


class Deloop_OT_desolve_edges(Operator):
    bl_idname = 'deloop.desolve_edges'
    bl_label = 'Desolve'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        Deloop.desolve_edges(
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
        Deloop.ui(
            layout=self.layout,
            context=context
        )


# REGISTER

def register(ui=True):
    register_class(Deloop_OT_remove_edges)
    register_class(Deloop_OT_desolve_edges)
    if ui:
        register_class(Deloop_PT_panel)


def unregister(ui=True):
    if ui:
        unregister_class(Deloop_PT_panel)
    unregister_class(Deloop_OT_desolve_edges)
    unregister_class(Deloop_OT_remove_edges)


if __name__ == "__main__":
    register()
