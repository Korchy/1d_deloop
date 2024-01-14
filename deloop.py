# Nikita Akimov
# interplanety@interplanety.org
#
# GitHub
#    https://github.com/Korchy/1d_deloop

# import bmesh
# import bpy
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
        pass


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
