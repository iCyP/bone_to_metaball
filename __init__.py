"""
Copyright (c) 2018 iCyP
Released under the MIT license
https://opensource.org/licenses/mit-license.php

"""

import bpy
from mathutils import Vector


bl_info = {
    "name":"bone_to_metaball",
    "author": "iCyP",
    "version": (0, 0),
    "blender": (2, 80, 0),
    "location": "active aramture and add -> metaball",
    "description": "metaball from bones",
    "warning": "",
    "support": "TESTING",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"
}


class ICYP_OT_metaballs_from_bone(bpy.types.Operator):
    bl_idname = "icyp.mataball_from_bone"
    bl_label = "Make mataballs from bone"
    bl_description = "Make mataballs from active armature"
    bl_options = {'REGISTER', 'UNDO'}


    metaball_size :  bpy.props.FloatProperty(name = "metaball size magnification",default = 1)
    def execute(self, context):
        armature = context.view_layer.objects.active
        if armature.type != "ARMATURE":
            return {'FINISHED'}
        bpy.ops.object.mode_set(mode='EDIT')
        positions = []
        sizes = []
        for edb in armature.data.edit_bones:
            positions.append([(edb.tail[i]+edb.head[i])/2 for i in range(3)])
            sizes.append([(edb.tail[i]-edb.head[i]) for i in range(3)])
        bpy.ops.object.mode_set(mode='OBJECT')
        mb = bpy.data.metaballs.new("metaball_base")
        obj = bpy.data.objects.new("metaball_base_obj",mb)
        obj.location = armature.location
        context.scene.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        min = 999999
        for pos,si in zip(positions,sizes):
            elem = mb.elements.new()
            elem.co = pos
            elem.radius = self.metaball_size * Vector(si).length/2
            if min > elem.radius:
                min = elem.radius
        mb.resolution = min
        return {'FINISHED'}

classes = [
    ICYP_OT_metaballs_from_bone,
]
def add_metaball_icyp(self, context):
    op = self.layout.operator(ICYP_OT_metaballs_from_bone.bl_idname, text="add metaball from active armature",icon="META_BALL")


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_metaball_add.append(add_metaball_icyp)
    


def unregister():
    bpy.types.VIEW3D_MT_metaball_add.remove(add_metaball_icyp)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if "__main__" == __name__:
    register()
