"""
Copyright (c) 2018 iCyP
Released under the MIT license
https://opensource.org/licenses/mit-license.php

"""
#blender内蔵の機能を使えるようにする1
import bpy
#blender内蔵の機能を使えるようにする2
from mathutils import Vector

#Blenderのaddon情報を記載する（dict形式　"key":"値" で書く、１要素ごとにコンマで区切る）
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

#オペレータ （アドオン本体）　命名規則があるのでぐぐる。　bpy.types.Operatorを継承する
class ICYP_OT_metaballs_from_bone(bpy.types.Operator):
    #オペレータの内部の名前
    bl_idname = "icyp.mataball_from_bone"
    #UI上の名前
    bl_label = "Make mataballs from bone"
    #ツールチップの文字列
    bl_description = "Make mataballs from active armature"
    #おまじない
    bl_options = {'REGISTER', 'UNDO'}

    #オペレータの変数登録
    metaball_size :  bpy.props.FloatProperty(name = "metaball size magnification",default = 1)
    #オペレータが呼ばれたときに実行する関数
    def execute(self, context):
        #現在アクティブなオブジェクトを取得して、変数 armature　に格納する
        armature = context.view_layer.objects.active
        #armatureに入っているオブジェクトがアーマチュアでなければ、実行を終了する（なにもしない）
        if armature.type != "ARMATURE":
            return {'FINISHED'}
        #アーマチュアの編集モードに入る（アーマチュアの編集モードでのみボーンの頭座標と尻尾座標を取れるEditBone変数を扱えるため #嘘でしたごめんなさいbonesで取れます（readonly=編集は出来ないですが
        bpy.ops.object.mode_set(mode='EDIT')
        #メタボールの置きたい座標を記録するリスト
        positions = []
        #メタボールの大きさを格納するリスト
        sizes = []
        #EditBonesリストの中身を一つずつedb変数に格納して順番に見ていく
        #positionsとsizesに同じものから見た要素を作っていくことで、positionsとsizesの中身はボーンの毎の対になる
        for edb in armature.data.edit_bones:
            pos = [0,0,0] #メタボールの置きたい座標を記録する変数を作る
            #メタボールの置きたい場所をposに設定する
            #座標は3要素なので、range(3) で呼ばれるたびに、0から1ずつ足したものをiに代入して、iが2になったら次で終了するfor文
            for i in range(3):
                #posのi番目（X:0番目,Y:1番目,Z:2番目）（プログラミングでは順番は0番目からはじまります）
                #の要素に、edit_bone(edb)の先端の座標のi番目（X:0番目ry）の要素から、edit_boneの根本の座標のi要素（ｒｙ）を足して2で割ったもの
                #つまり、ボーンの真ん中の座標をそれぞれ代入します
                pos[i] =  (edb.tail[i] + edb.head[i]) /2 
            #メタボールの置きたい場所を記録するリストに、座標の変数を追加する
            positions.append(pos)

            #ボーンのサイズを格納する変数
            size = 0.5
            #一時的にボーンのベクトルを格納する変数
            bone_vector = [0,0,0]
            #XYZ各要素について、ボーンがどこを向いているかを計算する
            #下のfor文と下の文と同義
            #bone_vector[0] = edb.head[0] - edb.tail[0] # X座標についてボーンがどっちを向いているか
            #bone_vector[1] = edb.head[1] - edb.tail[1] # Y座標について（ｒｙ
            #bone_vector[2] = edb.head[2] - edb.tail[2] # Z（ｒｙ
            for i in range(3):
                bone_vector[i] = edb.head[i] - edb.tail[i]
            #ボーンのベクトルをリスト型から、BlenderのmathutilsのVector型にキャスト（変換）して、length要素でその長さを得る
            size = Vector(bone_vector).length
            #メタボールのサイズのリストに、求めたサイズを追加する
            sizes.append(size)
        
        #メタボールを追加する方に手順に入りたいのでいったんオブジェクトモードに戻る
        bpy.ops.object.mode_set(mode='OBJECT')
        #メタボールをつくって、それを変数mbに格納する（せつめいしづらい
        mb = bpy.data.metaballs.new("metaball_base")
        #メタボールを格納するオブジェクトをつくって、変数objに格納する（同上
        obj = bpy.data.objects.new("metaball_base_obj",mb)
        #メタボールオブジェクトの座標をアーマチュアの座標と同じにする
        obj.location = armature.location
        #メタボールオブジェクトをシーンに配置する
        context.scene.collection.objects.link(obj)
        #メタボールオブジェクトをアクティブにする
        context.view_layer.objects.active = obj
        #メタボールオブジェクトの編集モードに入る
        bpy.ops.object.mode_set(mode='EDIT')
        #一番小さいメタボールのサイズを格納する変数min_sizeをつくる
        min_size = 999999
        #zip関数でpositionsとsizeを同時にそれぞれ変数pos,siに1要素ずつ格納してみていく
        for pos,si in zip(positions,sizes):
            #メタボールを追加して、それをelemに格納する
            elem = mb.elements.new()
            #メタボールの座標をposとする（ボーンの中間座標
            elem.co = pos
            #メタボールのサイズにメタボールサイズの係数 x ボーンのベクトルの長さの1/2を代入する
            elem.radius = self.metaball_size * si/2
            #メタボールのサイズがいままでで一番小さい時
            if min_size > elem.radius:
                #そのサイズを記録する
                min_size = elem.radius
            #備考：オペレータでメタボールを追加すると死ぬほど動作が遅かったのでこの作り方になっています
        #メタボールの一番小さいサイズをメタボールのビューポート表示閾値に設定する
        mb.resolution = min_size
        #メタボールの一番小さいサイズをメタボールのレンダリング表示閾値に設定する
        mb.render_resolution = min_size
        #正常終了しました
        return {'FINISHED'}

#BlenderのUIに上のオペレータを追加するコード１
def add_metaball_icyp(self, context):
    #メタボールの欄に追加するときに、どの関数を、どういう表示名で、どういうアイコンで表示するかを示す
    op = self.layout.operator(ICYP_OT_metaballs_from_bone.bl_idname, text="add metaball from active armature",icon="META_BALL")

#オペレータクラスをリストに記録する
classes = [
    ICYP_OT_metaballs_from_bone,
]
#アドオンが登録されたときに実行する
def register():
    #先のリストに記録されたクラスをBlenderに登録する
    for cls in classes:
        bpy.utils.register_class(cls)
    #BlenderのUI（メタボールの欄）に上のオペレータを追加するコード２
    bpy.types.VIEW3D_MT_metaball_add.append(add_metaball_icyp)
    

#アドオンが削除されたときに実行する
def unregister():
    #BlenderのUIから上のオペレータを削除するコード
    bpy.types.VIEW3D_MT_metaball_add.remove(add_metaball_icyp)
    #先のリストに記録されたクラスをBlenderから削除する
    for cls in classes:
        bpy.utils.unregister_class(cls)

#おまじない
if "__main__" == __name__:
    register()
