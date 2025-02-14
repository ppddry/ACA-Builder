# 作者：willimxp
# 所属插件：ACA Builder
# 功能概述：
#   公共的工具方法

import bpy
import bmesh
import math
import logging
import traceback
from mathutils import Vector,Euler,Matrix,geometry
import numpy as np
import time
from typing import List

from . import data
from .const import ACA_Consts as con

# 获取console窗口的context
# 以便在console_print中override
def console_get():
    for area in bpy.context.screen.areas:
        if area.type == 'CONSOLE':
            for space in area.spaces:
                if space.type == 'CONSOLE':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            return area, space, region
    return None, None, None

# 在blender内部的console窗口中输出调试信息
# 这个方法已经不再使用，发现进程引起blender的崩溃
def console_print(*args, clear=False):
    s = " ".join([str(arg) for arg in args])
    area, space, region = console_get()

    if space is None:
        return
    context_override = bpy.context.copy()
    context_override.update({
        "space": space,
        "area": area,
        "region": region,
    })
    with bpy.context.temp_override(**context_override):
        for line in s.split("\n"):
            bpy.ops.console.scrollback_append(text=line, type='OUTPUT')

def console_clear():
    area, space, region = console_get()
    if space is None:
        return
    context_override = bpy.context.copy()
    context_override.update({
        "space": space,
        "area": area,
        "region": region,
    })
    with bpy.context.temp_override(**context_override):
        bpy.ops.console.clear()

# # 弹出提示框
# def popMessageBox(message = "", title = "Message Box", icon = 'INFO'):
#     def draw(self, context):
#         self.layout.label(text=message)
#     bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

# 弹出模态提示框
# 实际调用的是operator.py中的ACA_OT_Show_Message_Box
# 因为使用了模态对话框，必须按照blender的operator声明，并在init中注册绑定
def popMessageBox(message = "", icon = 'INFO'):
    # 写入日志
    logger = logging.getLogger('ACA')
    logger.info(message)

    bpy.ops.aca.show_message_box('INVOKE_DEFAULT', 
        message=message, 
        icon=icon, 
        center=True)
    return

# 递归查询，并选择collection，似乎没有找到更好的办法
# Recursivly transverse layer_collection for a particular name
# https://blender.stackexchange.com/questions/127403/change-active-collection
def recurLayerCollection(layerColl, collName,is_like = False):
    found = None
    if is_like:
        # 模糊匹配
        if (collName in layerColl.name):
            return layerColl
    else:
        # 精确匹配
        if (layerColl.name == collName):
            return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer,collName,is_like)
        if found:
            return found

# 隐藏目录
def hideCollection(coll_name:str,
                   isShow=False,
                   parentColl:bpy.types.Collection=None):
    if parentColl == None:
        layer_collection = bpy.context.view_layer.layer_collection
    else:
        parentLayerColl = recurLayerCollection(
            bpy.context.view_layer.layer_collection,
            parentColl.name
        )
        layer_collection = parentLayerColl
    # 模糊匹配，因为目录名可能带“.001”后缀
    layerColl = recurLayerCollection(
        layer_collection, coll_name,is_like=True)
    if layerColl != None:
        if isShow:
            layerColl.exclude = False
            #layerColl.hide_viewport = False
        else:
            layerColl.exclude = True
            #layerColl.hide_viewport = True

# 聚焦选中指定名称的目录
def focusCollection(coll_name:str):
    # 根据目录名称获取目录
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection, coll_name)
    # 强制关闭目录隐藏属性，防止失焦
    if layerColl.exclude == True:
        # 在确认“ACA筑韵古建”根目录时，会一同打开所有子目录的exclude
        # 所以这里做了判断，仅在必要的时候进行切换
        layerColl.exclude = False
    layerColl.hide_viewport = False
    layerColl.collection.hide_render = False
    layerColl.collection.hide_viewport = False
    layerColl.collection.hide_select = False
    # 聚焦
    bpy.context.view_layer.active_layer_collection = layerColl

# 聚焦选中指定名称的目录
def focusCollByObj(obj:bpy.types.Object):
    parentColl = obj.users_collection[0].name
    focusCollection(parentColl)

# 新建或聚焦当前场景下的目录
# 所有对象建立在插件目录下，以免与用户自建的内容冲突
def setCollection(name:str, 
                  IsClear=False,
                  isRoot=False,
                  parentColl:bpy.types.Collection=None,
                  colorTag=None):
    coll_name = name  # 在大纲中的目录名称
    coll_found = False
    coll = bpy.types.Collection
    if parentColl == None:
        searchColl = bpy.context.scene.collection
    else:
        searchColl = parentColl
    for coll in searchColl.children:
        # 在有多个scene时，名称可能是“china_arch.001”
        if str.find(coll.name,coll_name) >= 0:
            coll_found = True
            coll_name = coll.name
            break   # 找到第一个匹配的目录

    if not coll_found:    
        # 新建collection，不与其他用户自建的模型打架
        # outputMsg("Add Collection: " + coll_name)
        coll = bpy.data.collections.new(coll_name)
        if isRoot:
            bpy.context.scene.collection.children.link(coll)
        else:
            if parentColl==None:
                bpy.context.collection.children.link(coll)
            else:
                parentColl.children.link(coll)
        # 聚焦到新目录上
        focusCollection(coll.name)
    else:
        # 根据IsClear入参，决定是否要清空目录
        if IsClear:
            # 清空collection，每次重绘
            for obj in coll.objects: 
                bpy.data.objects.remove(obj)
        # 选中目录，防止用户手工选择其他目录而导致的失焦
        focusCollection(coll_name)
    
    if colorTag != None:
        coll.color_tag = 'COLOR_0' + str(colorTag)
    # 返回目录的对象
    return coll

# 复制简单对象（仅复制instance）
def copySimplyObject(
        sourceObj:bpy.types.Object, 
        name=None, 
        parentObj:bpy.types.Object = None, 
        location=None,
        rotation=None,
        dimensions=None,
        scale=None,
        singleUser=False,):
    if sourceObj == None:
        outputMsg("copySimplyObject Failed: sourceObj is None.")
    # 复制基本信息
    newObj:bpy.types.Object = sourceObj.copy()
    if singleUser :
        newObj.data = sourceObj.data.copy()
    bpy.context.collection.objects.link(newObj)  
    if name == None:
        newObj.name = sourceObj.name
    else:
        newObj.name = name
    if location != None:
        newObj.location = location
    if rotation != None:
        newObj.rotation_euler = rotation
    if scale != None:
        newObj.scale = scale
    if dimensions != None:
        newObj.dimensions = dimensions
        # 缩放后需要更新数据，以便生效
        updateScene()
    if parentObj != None:
        newObj.parent = parentObj
    showObj(newObj)
    return newObj

# 复制对象（仅复制instance，包括modifier）
def copyObject(
        sourceObj:bpy.types.Object, 
        name=None, 
        parentObj:bpy.types.Object = None, 
        location=None,
        rotation=None,
        dimensions=None,
        scale=None,
        singleUser=False)->bpy.types.Object:
    # 强制原对象不能隐藏
    IsHideEye = sourceObj.hide_get()
    sourceObj.hide_set(False)
    IsHideViewport = sourceObj.hide_viewport
    sourceObj.hide_viewport = False
    IsHideRender = sourceObj.hide_render
    sourceObj.hide_render = False
    
    # 复制基本信息
    newObj:bpy.types.Object = sourceObj.copy()
    if singleUser :
        newObj.data = sourceObj.data.copy()
    bpy.context.collection.objects.link(newObj) 
    if name == None:
        newObj.name = sourceObj.name
    else:
        newObj.name = name
    if location != None:
        newObj.location = location
    if rotation != None:
        newObj.rotation_euler = Euler(rotation,'XYZ')
    if scale != None:
        newObj.scale = scale
    if dimensions != None:
        newObj.dimensions = dimensions
        # 缩放后需要更新数据，以便生效
        updateScene()
    if parentObj != None:
        newObj.parent = parentObj
    # 复制子对象
    if len(sourceObj.children) > 0 :
        for child in sourceObj.children:
            copyObject(
                sourceObj=child, 
                name=child.name, 
                parentObj=newObj, 
                location=child.location,
                singleUser=singleUser) 
            
    # 恢复原对象的隐藏属性
    sourceObj.hide_set(IsHideEye)
    sourceObj.hide_viewport = IsHideViewport
    sourceObj.hide_render = IsHideRender
    
    return newObj

# 查找当前对象的兄弟节点
# 如，根据台基对象，找到对应的柱网对象
def getAcaSibling(object:bpy.types.Object,
                  acaObj_type:str) -> bpy.types.Object:
    siblings = object.parent.children
    sibling = None
    for obj in siblings:
        if obj.ACA_data.aca_type == acaObj_type:
            sibling = obj
    return sibling
        
# 递归查找当前对象的子节点
# 只返回第一个对象，为了偷懒，没有返回所有
# 如，根据台基对象，找到对应的柱网对象
def getAcaChild(object:bpy.types.Object,
                  acaObj_type:str) -> bpy.types.Object:
    children = object.children
    child = None
    for obj in children:
        if obj.ACA_data.aca_type == acaObj_type:
            child = obj
            break # 如果找到，直接停止
        # 递归，深挖下一级子节点
        if len(obj.children) > 0:
            child = getAcaChild(obj,acaObj_type)
            if child != None: break
            
    return child

# 递归查找父节点，输入对象类型
def getAcaParent(object:bpy.types.Object,
                    acaObj_type:str) -> bpy.types.Object:
    parent = object.parent
    if parent != None:
        if hasattr(parent, 'ACA_data'):
            parentData : data.ACA_data_obj = parent.ACA_data
            if 'aca_type' in parentData:
                if parentData.aca_type != acaObj_type :
                    parent = getAcaParent(parent,acaObj_type)
            else:
                parent = getAcaParent(parent,acaObj_type)
    
    return parent

# 应用缩放(有时ops.object会乱跑，这里确保针对台基对象)      
def applyScale(object:bpy.types.Object):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = object
    object.select_set(True)
    bpy.ops.object.transform_apply(
        scale=True,
        rotation=False,
        location=False,
        isolate_users=True) # apply多用户对象时可能失败，所以要加上这个强制单用户

# 应用缩放、旋转、位置
def applyTransfrom(ob, 
                    use_location=False, 
                    use_rotation=False, 
                    use_scale=False):
    mb = ob.matrix_basis
    I = Matrix()
    loc, rot, scale = mb.decompose()

    # rotation
    T = Matrix.Translation(loc)
    R = mb.to_3x3().normalized().to_4x4()
    S = Matrix.Diagonal(scale).to_4x4()

    transform = [I, I, I]
    basis = [T, R, S]

    def swap(i):
        transform[i], basis[i] = basis[i], transform[i]

    if use_location:
        swap(0)
    if use_rotation:
        swap(1)
    if use_scale:
        swap(2)
        
    M = transform[0] @ transform[1] @ transform[2]
    if hasattr(ob.data, "transform"):
        ob.data.transform(M)
    for c in ob.children:
        c.matrix_local = M @ c.matrix_local
        
    ob.matrix_basis = basis[0] @ basis[1] @ basis[2]
    # 强制一次刷新，以便对象的dimension能够准确应用
    updateScene()

# 强制聚焦到对象
def focusObj(object:bpy.types.Object):
    # 先要保证对象可见，否则后续无法选中
    showObj(object)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = object
    object.select_set(True)

# 删除树状层次下的所有对象
def deleteHierarchy(parent_obj:bpy.types.Object,del_parent=False):
    #utils.outputMsg("deleting...")
    if parent_obj == None:
        # 没有可删除的对象
        return
    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.data.objects[parent_obj.name]
    obj.animation_data_clear()
    names = set()
    # Go over all the objects in the hierarchy like @zeffi suggested:
    def get_child_names(obj):
        for child in obj.children:
            names.add(child.name)
            if child.children:
                get_child_names(child)
    get_child_names(obj)
    
    # 是否删除根节点？
    if del_parent:
        names.add(parent_obj.name)
    objects = bpy.data.objects
    if names:
        for child_name in names:
            bpy.data.objects.remove(objects[child_name])

    delOrphan()
    # 数据清理
    updateScene()

# 计算两个点之间距离
# 使用blender提供的mathutils库中的Vector类
# https://sinestesia.co/blog/tutorials/calculating-distances-in-blender-with-python/
def getVectorDistance(point1: Vector, point2: Vector) -> float:
    """Calculate distance between two points.""" 
    return (point2 - point1).length

# 把对象旋转与向量对齐
# 对象要求水平放置，长边指向+X方向
# 向量为原点到坐标点，两点需要先相减
# 返回四元向量
def alignToVector(vector) -> Vector:
    quaternion = vector.to_track_quat('X','Z')
    euler = quaternion.to_euler('XYZ')
    return euler

# 添加一个empty对象
def addEmpty(name=None,
            type='PLAIN_AXES',
            radius=1,
            location=(0,0,0),
            rotation=(0,0,0),
            parent=None,
            hide=True,
            ):
    bpy.ops.object.empty_add(
        type=type,
        radius=radius,
        location=location,
        rotation=rotation
        )
    emptyObj = bpy.context.object

    if name != None:
        emptyObj.name = name
    else:
        emptyObj.name = 'empty'
        
    if parent != None:
        emptyObj.parent = parent
    if hide:
        hideObj(emptyObj)
    return emptyObj

# low level cube create
# https://blender.stackexchange.com/questions/305262/low-level-fast-way-to-create-cube
# 特别是避免了applyTransform中updateScene导致的性能影响
def addCube(name='Cube',
            location=(0,0,0),
            rotation=(0,0,0),
            dimension=(1,1,1),
            parent=None):
    # Generate the vertices and faces, edges are inferred from the polygons
    x = dimension[0] / 2
    y = dimension[1] / 2
    z = dimension[2] / 2
    # 按照blender的primitive cube的vertex顺序
    vertices = [
                (-x, -y, -z),
                (-x, -y, z),
                (-x, y, -z),
                (-x, y, z),
                (x, -y, -z),
                (x, -y, z),
                (x, y, -z),
                (x, y, z),
    ]
    # 所有的编号应该按逆时针排列，否则会导致面朝向错误
    faces = [
                (0,1,3,2),   # 左
                (2,3,7,6),   # 后
                (6,7,5,4),   # 右
                (4,5,1,0),   # 前
                (2,6,4,0),   # 下
                (7,3,1,5),   # 上
    ]

    # Create a new mesh and set generated data
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    
    # 当以上的面数组顺序调整正确后，就没有出现错误的面朝向了
    # # 重新计算Normal
    # bm = bmesh.new()
    # bm.from_mesh(mesh)
    # bm.edges.ensure_lookup_table()
    # bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # bm.to_mesh(mesh)
    # bm.free()

    # Create a new object to hold the mesh and set its location
    cube = bpy.data.objects.new(name, mesh)
    cube.location = location
    cube.rotation_euler = rotation
    if parent != None:
        cube.parent = parent
    bpy.context.collection.objects.link(cube)

    # 强制聚焦在cube上，以免后续bpy.ops的操作找错对象
    # bpy.ops.mesh.primitive_cube_add原来直接返回了context.object
    focusObj(cube)
    return cube

# 根据起始点，创建连接的矩形
# 长度在X轴方向
def addCubeBy2Points(start_point:Vector,
                     end_point:Vector,
                     depth:float,
                     height:float,
                     name:str,
                     root_obj:bpy.types.Object,
                     origin_at_bottom = False,
                     origin_at_end = False,
                     origin_at_start=False):
    length = getVectorDistance(start_point,end_point)
    # 默认origin在几何中心
    origin_point = (start_point+end_point)/2
    rotation = alignToVector(start_point - end_point)
    rotation.x = 0 # 避免x轴翻转

    # 调用基本cube函数
    cube = addCube(
        name=name,
        location=origin_point,
        rotation=rotation,
        dimension=(length,depth,height),
        parent=root_obj,
    )

    # 将Origin置于底部
    if origin_at_bottom :
        origin = Vector((0,0,-height/2))
        setOrigin(cube,origin)
    if origin_at_end :
        origin = Vector((-length/2,0,0))
        setOrigin(cube,origin)
    if origin_at_start :
        origin = Vector((length/2,0,0))
        setOrigin(cube,origin)

    return cube

# 添加球体
def addSphere(
        name='球',
        radius=1,
        segments=10,
        ringCount=10,
        rotation=(0,0,0),
        location=(0,0,0),
        parent=None
        ):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        segments=segments,
        ring_count=ringCount,
        rotation=rotation,
        location=location
    )
    sphereObj = bpy.context.object
    sphereObj.name = name
    sphereObj.data.name = name
    sphereObj.parent = parent

    shaderSmooth(sphereObj)
    return sphereObj

# 获取对象的原始尺寸
# 排除modifier的影响
# 参考 https://blender.stackexchange.com/questions/238109/how-to-set-the-dimensions-of-an-object-without-its-modifiers
def getMeshDims(object):
    me = object.data
    if object.type == "CURVE":
        me = bpy.data.meshes.new_from_object(object)

    coords = np.empty(3 * len(me.vertices))
    me.vertices.foreach_get("co", coords)

    x, y, z = coords.reshape((-1, 3)).T

    return Vector((
            x.max() - x.min(),
            y.max() - y.min(),
            z.max() - z.min()
            ))

# 绘制六边形，用于窗台、槛墙等
def drawHexagon(dimensions:Vector,
                location:Vector,
                half=False,
                name='六棱柱',
                parent=None,):
    # 创建bmesh
    bm = bmesh.new()
    # 各个点的集合
    vectors = []

    # 六边形位移距离
    offset = dimensions.y/math.tan(math.radians(60))
    # 左顶点
    v1=Vector((-dimensions.x/2,
               0,
               -dimensions.z/2))
    vectors.append(v1)
    # 左上点
    v2=Vector((
        -dimensions.x/2+offset,
        dimensions.y/2,
        -dimensions.z/2))
    vectors.append(v2)
    # 右上点
    v3=Vector((
        dimensions.x/2-offset,
        dimensions.y/2,
        -dimensions.z/2))
    vectors.append(v3)
    # 右顶点
    v4=Vector((dimensions.x/2,
               0,
               -dimensions.z/2))
    vectors.append(v4)
    if not half:
        # 右下点
        v5=Vector((
            dimensions.x/2-offset,
            -dimensions.y/2,
            -dimensions.z/2))
        vectors.append(v5)
        # 左下点
        v6=Vector((
            -dimensions.x/2+offset,
            -dimensions.y/2,
            -dimensions.z/2))
        vectors.append(v6)
    else:
        # 右下点
        v5=Vector((
            dimensions.x/2-offset,
            0,
            -dimensions.z/2))
        vectors.append(v5)
        # 左下点
        v6=Vector((
            -dimensions.x/2+offset,
            0,
            -dimensions.z/2))
        vectors.append(v6)

    # 摆放点
    vertices=[]
    for n in range(len(vectors)):
        if n==0:
            vert = bm.verts.new(vectors[n])
        else:
            # 挤出
            return_geo = bmesh.ops.extrude_vert_indiv(bm, verts=[vert])
            vertex_new = return_geo['verts'][0]
            del return_geo
            # 给挤出的点赋值
            vertex_new.co = vectors[n]
            # 交换vertex给下一次循环
            vert = vertex_new
        vertices.append(vert)
    
    # 创建面
    bm.faces.new((vertices[0],vertices[1],vertices[2],vertices[3],vertices[4],vertices[5]))

    # 挤出厚度
    return_geo = bmesh.ops.extrude_face_region(bm, geom=bm.faces)
    verts = [elem for elem in return_geo['geom'] if type(elem) == bmesh.types.BMVert]
    bmesh.ops.translate(bm, verts=verts, vec=(0, 0,dimensions.z))

    # 确保face normal朝向
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj) 
    bm.to_mesh(mesh)
    bm.free()
    obj.location = location
    if parent != None:
        obj.parent = parent

    return obj

# 快速执行bpy.ops执行
# 原理上，是禁用了bpy.ops操作时反复更新scene，效果有5倍的提升
# 注意：传入的参数为函数指针
# 如果函数不需要参数可不带括号直接传入
# 如果函数带参数，需要用偏函数或闭包进行封装后传入
# https://blender.stackexchange.com/questions/7358/python-performance-with-blender-operators
def fastRun(func):
    # 清理垃圾数据
    delOrphan()
    
    # 关闭viewlayer的刷新
    from bpy.ops import _BPyOpsSubModOp
    view_layer_update = _BPyOpsSubModOp._view_layer_update
    def dummy_view_layer_update(context):
        pass
    try:
        _BPyOpsSubModOp._view_layer_update = dummy_view_layer_update
        result = func()
    except Exception as e:
        print(e)
        logError(e)
        return {'CANCELLED':e}
    finally:
        _BPyOpsSubModOp._view_layer_update = view_layer_update
    
    # 清理重复的材质
    cleanDupMat()
    
    # 再次清理数据
    delOrphan()

    return result

# 格式化输出内容
def outputMsg(msg:str):
    # # 打印到python console中
    # stime = time.strftime("%H:%M:%S", time.localtime())
    # strout = "ACA[" + stime + "]: " + msg
    # print(strout)

    # 输出到日志文件中
    logger = logging.getLogger('ACA')
    logger.info(msg)

    # 更新到build进度中
    from . import build
    build.buildStatus = msg
    # 更新进度条
    if build.progress < 0.5:
        build.progress += 0.05
    elif build.progress < 0.8:
        build.progress += 0.02
    else:
        build.progress += 0.01
    
    # 界面刷新
    try:
        #console_print(strout)
        redrawViewport()
        return 
    except Exception as e:
        print(e)
        logError(e)
        return

# 隐藏对象，包括viewport和render渲染
def hideObj(object:bpy.types.Object) : 
    object.hide_set(True)          # 隐藏“眼睛”，暂时隐藏
    object.hide_viewport = True    # 隐藏“屏幕”，不含在viewport中
    object.hide_render = True      # 隐藏“相机”，不渲染

# 只显示边框
def hideObjFace(object:bpy.types.Object) : 
    object.hide_render = True      # 隐藏“相机”，不渲染
    object.display_type = 'WIRE' # 仅显示线框
    object.visible_camera = False
    object.visible_diffuse = False
    object.visible_glossy = False
    object.visible_transmission = False
    object.visible_volume_scatter = False
    object.visible_shadow = False

# 强制显示对象
def showObj(object:bpy.types.Object) : 
    object.hide_set(False)          # “眼睛”
    object.hide_viewport = False    # “屏幕”，含在viewport中
    object.hide_render = False      # “相机”，渲染

# 创建一个基本圆柱体，可用于柱等直立构件
def addCylinder(radius=0.5,
                depth=1,
                name='cylinder',
                root_obj=None,
                location=(0,0,0),
                rotation=(0,0,0),
                edge_num = 16,
                origin_at_bottom = False):
    # 定义圆柱体圆周面上的面数，不宜太高造成面数负担，也不宜太低影响美观
    bpy.ops.mesh.primitive_cylinder_add(
                        vertices = edge_num, 
                        radius = radius, 
                        depth = depth,
                        end_fill_type='NGON', 
                        calc_uvs=True, 
                        enter_editmode=False, 
                        align='WORLD', 
                        location=location, 
                        rotation=rotation, 
                        scale=(1,1,1)
                    )
    cylinderObj = bpy.context.object
    cylinderObj.name = name
    cylinderObj.data.name = name
    cylinderObj.parent = root_obj
    cylinderObj.ACA_data.aca_obj = True
    shaderSmooth(cylinderObj)

    # 将Origin置于底部
    if origin_at_bottom :
        # bpy.ops.object.mode_set(mode = 'EDIT')
        # bpy.ops.mesh.select_all(action = 'SELECT')
        # bpy.ops.transform.translate(value=(0,0,depth/2))
        # bpy.ops.object.mode_set(mode = 'OBJECT')    
        setOrigin(cylinderObj,Vector((0,0,-depth/2)))

    return cylinderObj

# 创建一个水平放置的圆柱体，可用于桁、椽等构件
def addCylinderHorizontal(radius,depth,name,root_obj,
                location=(0,0,0),
                rotation=(0,0,0),
                edge_num=16):
    # 圆柱旋转到横向摆放（默认为相对World垂直摆放）
    rotation_default = (0,math.radians(90),0)
    cylinder = addCylinder(radius=radius,
        depth=depth,
        location=location,
        rotation=rotation_default,
        name=name,
        root_obj=root_obj,
        edge_num=edge_num
    )
    # apply rotation
    #bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    applyTransfrom(cylinder,use_rotation=True)
    # 旋转到实际角度
    cylinder.rotation_euler = rotation
    return cylinder

# 根据起始点，创建连接的圆柱体
# 注意，该圆柱体已经经过翻转，长度指向+X轴
def addCylinderBy2Points(radius:float,
                         start_point:Vector,
                         end_point:Vector,
                         name:str,
                         root_obj:bpy.types.Object):
    depth = getVectorDistance(start_point,end_point)
    location = (start_point+end_point)/2
    rotation = alignToVector(end_point-start_point)
    rotation.x = 0 # 避免x轴翻转
    cylinder = addCylinderHorizontal(
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation,
        name=name,
        root_obj=root_obj
    )
    # 设置origin到椽头，便于后续向外檐出
    origin = locationTrans(start_point,root_obj,cylinder)
    setOrigin(cylinder,origin)
    return cylinder

# 添加阵列修改器
def addModifierArray(object:bpy.types.Object,
                     count:int,
                     offset:float,
                     name='Array',
                     use_relative_offset=False,
                     use_constant_offset=True,
                     ):
    Xarray:bpy.types.ArrayModifier = \
            object.modifiers.new(name,'ARRAY')
    Xarray.count = count
    Xarray.use_relative_offset = use_relative_offset
    Xarray.use_constant_offset = use_constant_offset
    Xarray.constant_offset_displace = offset

# 添加镜像修改器
def addModifierMirror(object:bpy.types.Object,
                      mirrorObj:bpy.types.Object,
                      use_axis=(False,False,False),
                      use_bisect=(False,False,False),
                      use_flip=(False,False,False),
                      name='Mirror',):
    mod:bpy.types.MirrorModifier = \
            object.modifiers.new(name,'MIRROR')
    mod.mirror_object = mirrorObj
    mod.use_axis = use_axis
    mod.use_bisect_axis = use_bisect
    mod.use_bisect_flip_axis = use_flip

# 应用所有修改器
def applyAllModifer(object:bpy.types.Object):
    # 仅在有修改器，或为curve等非mesh对象上执行，以便提升效率
    if (len(object.modifiers) > 0
        or object.type != 'MESH'):
        focusObj(object)
        bpy.ops.object.convert(target='MESH')

# 翻转对象的normal
def flipNormal(object:bpy.types.Object):
    bm = bmesh.new()
    me = object.data    
    bm.from_mesh(me) # load bmesh
    for f in bm.faces:
        f.normal_flip()
    bm.normal_update() # not sure if req'd
    bm.to_mesh(me)
    me.update()
    bm.clear() #.. clear before load next
    return object

# 基于面的裁切
def addBisect(object:bpy.types.Object,
              pStart=Vector((0,0,0)),
              pEnd=Vector((0,0,0)),
              pCut=Vector((0,0,0)),
              clear_outer=False,
              clear_inner=False,
              direction  = 'Z',
              use_fill = True)    :
    focusObj(object)
    # 将对象的mesh数据single化，避免影响场景中其他对象
    object.data = object.data.copy()
    if direction == 'Z':
        # 1、计算剪切平面，先将由戗投影到XY平面，再沿Z轴旋转90度
        pstart_project = Vector((pStart.x,pStart.y,0))
        pend_project = Vector((pEnd.x,pEnd.y,0))
        bisect_normal = Vector(pend_project-pstart_project)
        bisect_normal.rotate(Euler((0,0,math.radians(90)),'XYZ'))
    elif direction == 'Y':
        # 1、计算剪切平面，先将由戗投影到YZ平面，再沿X轴旋转90度
        pstart_project = Vector((0,pStart.y,pStart.z))
        pend_project = Vector((0,pEnd.y,pEnd.z))
        bisect_normal = Vector(pend_project-pstart_project)
        bisect_normal.rotate(Euler((math.radians(90),0,0),'XYZ'))
    elif direction == 'X':
        # 1、计算剪切平面，先将由戗投影到XZ平面，再沿Y轴旋转90度
        pstart_project = Vector((pStart.x,0,pStart.z))
        pend_project = Vector((pEnd.x,0,pEnd.z))
        bisect_normal = Vector(pend_project-pstart_project)
        bisect_normal.rotate(Euler((0,math.radians(90),0),'XYZ'))
    elif direction == 'V':
        # 250110 建筑旋转90度后，以上normal算法错误
        # 实际的需求就是做水平横切，所以强制把normal置为Z轴方向
        bisect_normal = Vector((0,0,-1))
    bisect_normal = Vector(bisect_normal).normalized() # normal必须normalized,注意不是normalize

    # 2、选中并裁切
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bisect(
        plane_co=pCut, 
        plane_no=bisect_normal, 
        clear_outer=clear_outer,
        clear_inner=clear_inner,
        use_fill=use_fill
    )
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.editmode_toggle()  
    # 250124 之前这里将对象做了平面化，为什么？没有理解，先注释掉观察看看
    # bpy.ops.object.shade_flat()

# 寻找对象最外侧（远离原点）的面的中心点
# 注意，返回的坐标基于root_obj为parent的local坐标系
def getObjectHeadPoint(object:bpy.types.Object,
                       eval:bool=False,
                       is_symmetry=[False,False,False])-> Vector:
    if eval:
        # 获取应用modifier后的整体对象，包括镜像、阵列等
        # 参考 https://docs.blender.org/api/current/bpy.types.Depsgraph.html
        # 参考 https://blender.stackexchange.com/questions/7196/how-to-get-a-new-mesh-with-modifiers-applied-using-blender-python-api
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = object.evaluated_get(depsgraph)
    else:
        obj_eval = object

    # 发现有的时候获取端点还是会有异常，只能刷一把状态了
    # 比如，歇山山面飞椽的定位就会异常
    updateScene()

    # 将对象的几何数据载入bmesh
    bm = bmesh.new()
    bm.from_mesh(obj_eval.data)

    # 轮询面集合，查找最大值
    headPoint = Vector((0,0,0))
    for face in bm.faces:
        # 面的几何中心点
        faceCenter = face.calc_center_median()
        # 240709 用本地坐标系转换后进行比较
        # 为了解决查找最后一根飞椽头的bug，如果从几何中心比较，飞椽侧边反而成了最远的面
        # 为了矫正这个问题，从原点0的坐标来比较，更加合理
        # if faceCenter > headPoint:
        faceCenterLocal = object.matrix_local @ faceCenter
        headPointLocal = object.matrix_local @ headPoint
        if faceCenterLocal > headPointLocal:
            headPoint = faceCenter      
    # 基于origin点进行转换，转换到局部坐标（以root_obj为参考）
    objMatrix  = object.matrix_local
    headPoint= objMatrix @ headPoint
    
    # 如果对称，取正值
    for n in range(len(is_symmetry)):
        if is_symmetry[n]:
            headPoint[n]=abs(headPoint[n])

    bm.free()
    return headPoint

# 复制对象的所有modifier
def copyModifiers(from_0bj,to_obj):
    # 先取消所有选中，以免进入本函数前有其他选择项的干扰
    bpy.ops.object.select_all(action='DESELECT')
    # 分别选中from，to
    from_0bj.select_set(True)
    bpy.context.view_layer.objects.active = from_0bj
    to_obj.select_set(True)
    # 复制modifiers
    bpy.ops.object.make_links_data(type='MODIFIERS')
    # 取消选中
    bpy.ops.object.select_all(action='DESELECT')

# 在坐标点上摆放一个cube，以便直观看到
def showVector(point: Vector,parentObj=None,name="定位点") -> object :
    bpy.ops.mesh.primitive_cube_add(size=0.3,location=point)
    cube = bpy.context.active_object
    if parentObj != None:
        cube.parent = parentObj
    cube.name = name
    return cube

# 设置origin到cursor
# 输入的origin必须为相对于object的局域坐标
def setOrigin(object:bpy.types.Object,origin:Vector):
    # Low Level，其实没有觉得有明显性能区别
    # https://blender.stackexchange.com/questions/16107/is-there-a-low-level-alternative-for-bpy-ops-object-origin-set
    # 强制刷新，以便正确获得object的matrix信息
    updateScene()
    # 转换到相对于object的本地坐标
    origin_world = object.matrix_world @ origin
    origin_local = object.matrix_world.inverted() @ origin_world
    # 反向移动原点
    mat = Matrix.Translation(-origin_local)
    me = object.data
    if me.is_editmode:
        bm = bmesh.from_edit_mesh(me)
        bm.transform(mat)
        bmesh.update_edit_mesh(me, False, False)
    else:
        me.transform(mat)
    if object.type == "CURVE":
        updateScene()
    else:
        me.update()
    # 再次正向移动，回归到原来位置
    object.matrix_world.translation = origin_world

# 场景数据刷新
# 特别在fastrun阻塞过程中，bpy.ops等操作的数据无法及时更新，导致执行的错误
# 这时可以手工刷新一次
# 老中医，药到病除的办法
def updateScene():
    #bpy.context.view_layer.update() 

    # 按照文章的说法，这个消耗更低
    dg = bpy.context.evaluated_depsgraph_get() 
    dg.update()

# 刷新viewport，避免长时间卡死，并可见到建造过程
def redrawViewport():
    updateScene()

    # 设置窗口视角
    lockView = bpy.context.scene.ACA_data.is_auto_viewall
    if lockView:
        areas  = [area for area 
                  in bpy.context.screen.areas 
                  if area.type == 'VIEW_3D']
        if areas:
            regions = [region for region 
                       in areas[0].regions 
                       if region.type == 'WINDOW']

            if regions:
                context_override = bpy.context.copy()
                context_override.update({
                    'area': areas[0],
                    'region': regions[0],
                })     
                with bpy.context.temp_override(**context_override):
                    bpy.ops.view3d.view_axis(type='FRONT')
                    bpy.ops.view3d.view_all()
                    #bpy.ops.view3d.view_selected()

    # 窗口刷新显示
    do = bpy.context.scene.ACA_data.is_auto_redraw
    if do:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

# 删除所有无用数据，以免拖累性能
def delOrphan():
    bpy.ops.outliner.orphans_purge(
                do_local_ids=True, 
                do_linked_ids=True, 
                do_recursive=True)
    
    # for block in bpy.data.collections:
    #     if block.users == 0:
    #         bpy.data.collections.remove(block)

    # for block in bpy.data.objects:
    #     if block.users == 0:
    #         bpy.data.objects.remove(block)
    
    # for block in bpy.data.meshes:
    #     if block.users == 0:
    #         bpy.data.meshes.remove(block)
    
    # for block in bpy.data.curves:
    #     if block.users == 0:
    #         bpy.data.curves.remove(block)

    # for block in bpy.data.materials:
    #     if block.users == 0:
    #         bpy.data.materials.remove(block)

    # for block in bpy.data.textures:
    #     if block.users == 0:
    #         bpy.data.textures.remove(block)

    # for block in bpy.data.images:
    #     if block.users == 0:
    #         bpy.data.images.remove(block)
    
    # for block in bpy.data.node_groups:
    #     if block.users == 0:
    #         bpy.data.node_groups.remove(block)

    # bpy.data.orphans_purge()
    return

# 获取对象的几何中心
# 已经在代码中使用评估对象，可以抗阻塞 
# https://blender.stackexchange.com/questions/129473/typeerror-element-wise-multiplication-not-supported-between-matrix-and-vect 
def getMeshCenter(object:bpy.types.Object):
    # 准确获取对象状态，避免脚本阻塞产生
    obj_eval = getEvalObj(object)
    local_bbox_center = 0.125 * sum((Vector(b) for b in obj_eval.bound_box), Vector())
    global_bbox_center = obj_eval.matrix_local @ local_bbox_center
    return global_bbox_center

# 重新设置对象的旋转角，而不改变对象的原来的旋转
def changeOriginRotation(RotationChange,Object:bpy.types.Object):
    # 先预存原旋转角度
    # 当心，原来直接使用返回值出现了bug，中间会变化
    old_rot_x,old_rot_y,old_rot_z = Object.rotation_euler
    # 以飞椽上皮角度做为调节角度
    change_rot_x,change_rot_y,change_rot_z = alignToVector(RotationChange)
    # 先矫枉
    Object.rotation_euler = Euler((
        -change_rot_x,
        -change_rot_y,
        -change_rot_z),'XYZ')
    # Apply
    applyTransfrom(ob=Object,use_rotation=True)
    Object.rotation_euler = Euler(
        (old_rot_x+change_rot_x,
         old_rot_y+change_rot_y,
         old_rot_z+change_rot_z),'XYZ'
    )
    

# 返回评估对象
# 在代码阻塞过程中，可以及时的计算对象当前的状态，刷新实际的尺寸、旋转和坐标
# 如果在fastrun中出现问题，多试试这个方法
# https://docs.blender.org/api/current/bpy.types.Depsgraph.html
def getEvalObj(object:bpy.types.Object)->bpy.types.Object:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = object.evaluated_get(depsgraph)
    return obj_eval

# 将A对象的相对坐标，转换到B坐标系中
def locationTrans(loc:Vector,
                  fromObj:bpy.types.Object,
                  toObj:bpy.types.Object):
    # 刷新获得准确的矩阵
    updateScene()
    # 转换到全局坐标
    loc_world = fromObj.matrix_world @ loc
    # 转换到B坐标系
    loc_local = toObj.matrix_world.inverted() @ loc_world
    return loc_local

def transBezierPoint(pfrom:bpy.types.BezierSplinePoint,
                     pto:bpy.types.BezierSplinePoint):
    pto.co = pfrom.co
    pto.handle_left = pfrom.handle_left
    pto.handle_right = pfrom.handle_right
    pto.handle_left_type = pfrom.handle_left_type
    pto.handle_right_type = pfrom.handle_right_type

def setEaveCurvePoint(pStart,pEnd,direction='X'):
    if direction == 'X':
        pStart_handle_right = (
            pStart.x,
            pStart.y,
            pStart.z)
        pEnd_handle_left = (
            (pStart.x + pEnd.x)/2,
            pStart.y,
            pStart.z)
    else:
        pStart_handle_right = (
            pStart.x,
            pStart.y,
            pStart.z)
        pEnd_handle_left = (
            pStart.x,
            (pStart.y + pEnd.y)/2,
            pStart.z)
    CurvePoints = [pStart,pStart_handle_right,pEnd_handle_left,pEnd]
    return CurvePoints

# 创建贝塞尔曲线
def addBezierByPoints(
        CurvePoints,
        name,
        root_obj,
        tilt=0,
        height=0,
        width=0,
        resolution=64,
        order_u = 3
        ):
    # 创建曲线data集
    curveData = bpy.data.curves.new(name, type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = resolution
    curveData.fill_mode = 'FULL'
    curveData.use_fill_caps = True

    # 创建曲线spline
    polyline = curveData.splines.new('BEZIER')
    polyline.bezier_points.add(1)
    polyline.bezier_points[0].co = CurvePoints[0]
    polyline.bezier_points[0].handle_left = CurvePoints[0]
    polyline.bezier_points[0].handle_right = CurvePoints[1]
    polyline.bezier_points[1].handle_left = CurvePoints[2]
    polyline.bezier_points[1].handle_right = CurvePoints[3]
    polyline.bezier_points[1].co = CurvePoints[3]
    polyline.bezier_points[0].tilt = tilt
    polyline.bezier_points[1].tilt = tilt
    
    polyline.order_u = order_u # nurbs的平滑度
    polyline.use_endpoint_u = True

    # 定义曲线横截面
    if width!=0 and height!=0:
        bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,0))
        bevel_object = bpy.context.object
        bevel_object.scale = (width,height,0)
        bevel_object.name = name + '.bevel'
        bevel_object.parent = root_obj
        # 将Plane Mesh转换为Curve，才能绑定到curve上
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.convert(target='CURVE')
        # 翻转curve，否则会导致连檐的face朝向不对
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.switch_direction()
        bpy.ops.object.editmode_toggle()

        curveData.bevel_mode = 'OBJECT'
        curveData.bevel_object = bevel_object
        polyline.use_smooth = False
        hideObj(bevel_object)

    # 曲线对象加入场景
    curveOBJ = bpy.data.objects.new(name, curveData)
    bpy.context.collection.objects.link(curveOBJ)
    bpy.context.view_layer.objects.active = curveOBJ
    curveOBJ.parent = root_obj  
    
    return curveOBJ

# 提取bezier曲线上X方向等分的坐标点
# 局限性，1，仅可判断两点定义的曲线，2，取值为近似值
def getBezierSegment(curveObj,count,
                     withCurveEnd=False):
    accuracy = 1000   # 拟合精度，倍数越高越精确
    
    bez_points:bpy.types.SplinePoints = \
        curveObj.data.splines[0].bezier_points
    # 以精度的倍数，在曲线上创建插值
    tile_on_curveF = geometry.interpolate_bezier(
        bez_points[0].co,
        bez_points[0].handle_right,
        bez_points[1].handle_left,
        bez_points[1].co,
        count * accuracy)
    
    segments = []
    # X方向等分间距
    span = (bez_points[0].co[0] - bez_points[1].co[0]) /(count+1)
    for n in range(count):
        # 等分点的X坐标
        pX = bez_points[0].co[0] - span * (n+1)
        # 在插值点中查找最接近的插值点
        near1 = 99999 # 一个超大的值
        for point in tile_on_curveF:
            near = math.fabs(point[0] - pX)
            if near < near1 :
                nearPoint = point
                near1 = near
        segments.append(nearPoint)
    
    # 是否在结果中包括曲线两头的端点？
    # 在通过檐口线计算椽头定位点时，不需要包括曲线端点
    # 在通过檐口线计算望板时，应该包括曲线端点
    if withCurveEnd:
        segments.insert(0, bez_points[0].co)
        segments.append(bez_points[1].co)
    return segments

# 根据3点，创建一根弧线
def addCurveByPoints(CurvePoints,
                     name,
                     root_obj,
                     tilt=0,
                     tilt_head=None,
                     height=0,
                     width=0,
                     resolution=4,
                     order_u = 3
                     ):
    # 创建曲线data集
    curveData = bpy.data.curves.new(name, type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = resolution
    curveData.fill_mode = 'FULL'
    curveData.use_fill_caps = True

    # 创建曲线spline
    polyline = curveData.splines.new('NURBS')
    polyline.points.add(len(CurvePoints)-1)
    for i, coord in enumerate(CurvePoints):
        x,y,z = coord
        polyline.points[i].co = (x, y, z, 1)
        if tilt_head != None:
            # 第一个点有不同的斜率
            if i==len(CurvePoints)-1:
                polyline.points[i].tilt = tilt
            else:
                polyline.points[i].tilt = tilt_head
        else:
            polyline.points[i].tilt = tilt
    polyline.order_u = order_u # nurbs的平滑度
    polyline.use_endpoint_u = True
    
    # 定义曲线横截面
    if width!=0 and height!=0:
        bpy.ops.mesh.primitive_plane_add(size=1,location=(0,0,0))
        bevel_object = bpy.context.object
        bevel_object.scale = (width,height,0)
        bevel_object.name = name + '.bevel'
        bevel_object.parent = root_obj
        # 将Plane Mesh转换为Curve，才能绑定到curve上
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.convert(target='CURVE')
        # 翻转curve，否则会导致连檐的face朝向不对
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.switch_direction()
        bpy.ops.object.editmode_toggle()

        curveData.bevel_mode = 'OBJECT'
        curveData.bevel_object = bevel_object
        polyline.use_smooth = False

    # 曲线对象加入场景
    curveOBJ = bpy.data.objects.new(name, curveData)
    bpy.context.collection.objects.link(curveOBJ)
    bpy.context.view_layer.objects.active = curveOBJ
    curveOBJ.parent = root_obj  
    
    return curveOBJ

# 提取Nurbs曲线上的等分点
# 精度依赖于curve的resolution_u
def getNurbsSegment(nurbsObj:bpy.types.Object,count,
                    withCurveEnd=False):
    nurbs_points= nurbsObj.data.splines[0].points
    # X方向等分间距
    span = (nurbs_points[2].co.x - nurbs_points[0].co.x) /(count+1)

    # create a temporary mesh
    obj_data = nurbsObj.to_mesh()
    verts_on_curve = [v.co for v in obj_data.vertices]
    
    # 轮询逼近等分点
    segments = []
    for n in range(count):
        # 等分点的X坐标
        pX = nurbs_points[0].co.x + span * (n+1)
        # 在插值点中查找最接近的插值点
        near1 = 99999 # 一个超大的值
        for vert in verts_on_curve:
            near = math.fabs(vert.x - pX)
            if near < near1 :
                nearPoint = vert
                near1 = near
        segments.append(nearPoint)
    # 是否在结果中包括曲线两头的端点？
    # 在通过檐口线计算椽头定位点时，不需要包括曲线端点
    # 在通过檐口线计算望板时，应该包括曲线端点
    if withCurveEnd:
        segments.insert(0, nurbs_points[0].co.to_3d())
        segments.append(nurbs_points[2].co.to_3d())

    return segments

# 设置几何节点修改器的输入参数
def setGN_Input(mod:bpy.types.NodesModifier,
                inputName:str,
                value):
    if bpy.app.version >= (4,0,0):
        # V4.0以后用这个方法    
        id = mod.node_group.interface.items_tree[inputName].identifier
    else:
        # V4.0前用以下方法
        id = mod.node_group.inputs[inputName].identifier

    mod[id] = value
    return

# 合并对个对象
# https://blender.stackexchange.com/questions/13986/how-to-join-objects-with-python
# https://docs.blender.org/api/current/bpy.ops.html#overriding-context
def joinObjects(objList:List[bpy.types.Object],
                newName=None,
                baseObj=None,
                cleanup=False):
    if newName==None:
        newName = objList[0].name
    # timeStart = time.time()
    
    # 1、选择可以合并的对象，抛弃None,empty等
    # 与上面的循环要做分开，否则context的选择状态会打架
    # todo：也可以用临时context来解决
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objList:
        # 不能为空对象
        if ob == None: continue
        # 只处理实体对象，不考虑empty,camera,light等
        if ob.type not in ('MESH','CURVE'):
            continue
        try:
            ob.select_set(True)
        except ReferenceError:
            # 传入的对象错误，直接忽略
            continue

        # 将对象的mesh数据single化，避免影响场景中其他对象
        if ob.data.users > 1:
            ob.data = ob.data.copy()
    if len(bpy.context.selected_objects) ==0:
        outputMsg("没有可以合并的对象")
        return None

    # 2、设置合并的Origin基准
    if baseObj == None:
        bpy.context.view_layer.objects.active = objList[0]
    else:
        bpy.context.view_layer.objects.active = baseObj

    # 3、应用了所有的modifier
    bpy.ops.object.convert(target='MESH')
    
    # 4、合并对象
    bpy.ops.object.join()
    joinedObj = bpy.context.object
    
    joinedObj.name = newName
    joinedObj.data.name = newName

    # 5、合并顶点
    if cleanup:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set( mode = 'OBJECT' )

    # 清理垃圾数据
    delOrphan()

    # print("Objects join in %.2f秒" 
    #            % (time.time()-timeStart))
    
    return joinedObj

# 返回根对象
def getRoot(object:bpy.types.Object):
    buildingObj = None
    bData = None
    objData = None
    isRoot = False
    if hasattr(object, 'ACA_data'):
        objData:data.ACA_data_obj = object.ACA_data
        if 'aca_type' in object.ACA_data:
            if objData['aca_type'] in (
                    con.ACA_TYPE_BUILDING,
                    con.ACA_TYPE_YARDWALL,
                ):
                isRoot = True

        if isRoot:
            buildingObj = object
            bData = objData
        else:
            buildingObj = getAcaParent(
                    object,con.ACA_TYPE_BUILDING)
            if buildingObj != None:
                bData:data.ACA_data_obj = buildingObj.ACA_data
            else:
                buildingObj = getAcaParent(
                    object,con.ACA_TYPE_YARDWALL
                )
                if buildingObj != None:
                    bData:data.ACA_data_obj = buildingObj.ACA_data

    return buildingObj,bData,objData

# 隐藏显示目录
def hideLayer(context,name,isShow):
    # 查找对应的建筑根节点，以便能区分不同建筑的组件，互不干扰
    buildingObj,bData,objData = getRoot(context.object)
    buildingColl = buildingObj.users_collection[0]
    # 隐藏
    hideCollection(name,
        isShow=isShow,
        parentColl=buildingColl)
    # 恢复聚焦到根节点
    focusObj(buildingObj)
    # 立即刷新显示，否则可能因为需要刷新所有panel而有延迟感
    redrawViewport()
    return 

# 删除对象的边
def dissolveEdge(object:bpy.types.Object,
                 index:List):
    focusObj(object)
    # 强制一次刷新
    # 发现在垂带生成的过程中，出现无法裁剪生效的问题
    # 最终发现在这里刷新一次就好了
    # cube建立的时候没有刷新，这里来还债，性能上更合算
    updateScene()
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.new()
    bm = bmesh.from_edit_mesh(object.data)
    bpy.ops.mesh.select_mode(type = 'EDGE')
    bm.edges.ensure_lookup_table()
    bpy.ops.mesh.select_all(action = 'DESELECT')
    for e in index:
        bm.edges[e].select = True
    bpy.ops.mesh.dissolve_edges()
    bmesh.update_edit_mesh(bpy.context.object.data ) 
    bm.free() 
    bpy.ops.object.mode_set( mode = 'OBJECT' )
    return

# 整体缩放对象，不区分XYZ
def resizeObj(object:bpy.types.Object,
              scale:float):
    object.scale.x = object.scale.x * scale
    object.scale.y = object.scale.y * scale
    object.scale.z = object.scale.z * scale
    # 强制生效，以免在fastrun时被其他操作覆盖
    updateScene()
    return object

# 表面平滑
def shaderSmooth(object:bpy.types.Object):
    focusObj(object)
    
    if bpy.app.version >= (4, 1, 0) :
        # 此方法为Blender 4.1中新提供的，4.0以及以前都不支持
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(45))
    elif bpy.app.version >= (3, 3, 0) :
        # 在Blender 3.3~4.0提供了use_auto_smooth的参数
        # 但在4.1中已经移除了这个参数
        bpy.ops.object.shade_smooth(
            use_auto_smooth=True, 
            auto_smooth_angle=math.radians(45))
    else:
        # 这个函数目前可以适应各个版本
        # 但效果不是很好，normal可能有问题
        bpy.ops.object.shade_smooth()

    return

# 锁定对象
def lockObj(obj:bpy.types.Object):
    obj.hide_select = True
    obj.lock_scale = (True,True,True)
    obj.lock_location = (True,True,True)
    obj.lock_rotation = (True,True,True)
    return

# 返回数字的正负数
# https://stackoverflow.com/questions/1986152/why-doesnt-python-have-a-sign-function
def getSign(value):
    return math.copysign(1,value)

# 拆分对象
def separateObject(objArray:bpy.types.Object):
    # 将array modifier生成的对象实例化
    applyAllModifer(objArray)
    # 拆分成独立实体
    bpy.ops.mesh.separate(type="LOOSE")
    objList = []
    for obj in bpy.context.view_layer.objects.selected:
        objList.append(obj)
    
    return objList

# 替换对象
# 传递旧对象的位置、旋转、尺寸、名称、父子关系、修改器
# 保持新对象的造型、材质
# （需要手工保证两个对象的origin一致）
# 根据delete定义是删除还是隐藏原对象
def replaceObject(
        fromObj:bpy.types.Object,
        toObj:bpy.types.Object,
        delete=False,
        use_Modifier=True,
        use_Name=True,
        use_Dimension=True):
    # 传递旧对象的位置、旋转、尺寸、名称、父子关系、修改器
    toObj.location = fromObj.location
    toObj.rotation_euler = fromObj.rotation_euler
    toObj.parent = fromObj.parent

    if use_Dimension:
        toObj.dimensions = getMeshDims(fromObj) # 排除modifier的尺寸
        applyTransfrom(toObj,use_scale=True)
    
    if use_Modifier:
        copyModifiers(fromObj,toObj)

    if use_Name:
        # 先释放原对象名称，以免被添加.001后缀
        fromName = fromObj.name
        fromObj.name += '.backup'
        fromObj.data.name += '.backup'
        toObj.name = fromName
        toObj.data.name = fromName

    if delete:
        # 删除原对象
        bpy.data.objects.remove(fromObj)
    else:
        # 隐藏原对象
        hideObj(fromObj)
    return

# 为对象增加细分
def subdivideObject(object:bpy.types.Object,level=1):
    focusObj(object)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action='SELECT')
    for n in range(level):
        bpy.ops.mesh.subdivide()
    bpy.ops.object.mode_set(mode="OBJECT")
    return object

# 封装对象删除
def delObject(object:bpy.types.Object):
    bpy.data.objects.remove(object)
    return

# 更换对象的父节点
def changeParent(object:bpy.types.Object,
                 newParent:bpy.types.Object,
                 resetOrigin=True):
    preParent = object.parent
    if preParent == None:
        outputMsg("Can't change Parent of " + object.name )
        return
    
    # 应用所有transform
    if resetOrigin:
        applyTransfrom(
            object,
            use_location=True,
            use_rotation=True,
            use_scale=True,
    )
    # 转换坐标矩阵
    object.matrix_local = (
        newParent.matrix_world.inverted()
        @ preParent.matrix_world
        @ object.matrix_local
    )
    # 应用新父节点
    object.parent = newParent
    return

# 清理重复的材质
# https://blender.stackexchange.com/questions/55233/disable-material-duplication
def cleanDupMat():
    # 清理重复的材质
    mats = bpy.data.materials
    for obj in bpy.data.objects:
        for slt in obj.material_slots:
            part = slt.name.rpartition('.')
            if part[2].isnumeric() and part[0] in mats:
                slt.material = mats.get(part[0])
    return

# 将点投影到平面上
# param point: 点的坐标，格式为 (x0, y0, z0)
# param plane_coeffs: 平面的系数，格式为 (A, B, C, D)
# return: 投影点的坐标
def project_point_to_plane(point, plane_coeffs):
    x0, y0, z0 = point
    A, B, C, D = plane_coeffs
    
    # 计算法向量的模的平方
    normal_length_squared = A**2 + B**2 + C**2
    
    # 计算点到平面的距离
    distance = (A * x0 + B * y0 + C * z0 + D) / normal_length_squared
    
    # 计算投影点的坐标
    x_proj = x0 - distance * A
    y_proj = y0 - distance * B
    z_proj = z0 - distance * C

    newPoint = Vector((x_proj,y_proj,z_proj))
    
    return newPoint

# 将点按相对于参考点的极角排序
# param points: 点的列表，每个点是一个元组 (x, y)
# param reference_point: 参考点 (x0, y0)
# return: 按极角排序后的点列表
def polar_angle_sort(points, reference_point):
    
    # 计算每个点相对于参考点的极角
    def calculate_angle(point):
        x, y = point
        x0, y0 = reference_point
        return np.arctan2(y - y0, x - x0)
    
    # 按极角排序
    sorted_points = sorted(points, key=calculate_angle)
    return sorted_points


# 根据距离阈值合并点
# param points: 点的列表，每个点是一个元组 (x, y, z)
# param threshold: 合并的距离阈值
# return: 合并后的点列表
def merge_points(points, threshold):
    merged_points = []
    for point in points:
        merged = False
        for i, merged_point in enumerate(merged_points):
            # 计算当前点与已合并点的距离
            distance = np.linalg.norm(np.array(point) - np.array(merged_point))
            if distance < threshold:
                # 如果距离小于阈值，则合并
                merged_points[i] = tuple((np.array(point) + np.array(merged_point)) / 2)
                merged = True
                break
        if not merged:
            # 如果没有合并，则将当前点加入合并后的点列表
            merged_points.append(point)
    return merged_points

# 将一组实体投影到一个平面，并返回组合的轮廓
def unionProject(
        name = 'projectObj',
        projectNormal = Vector((0,0,1)),
        projectCenter = Vector((0,0,0)),
        objectList = [bpy.types.Object],
        insetThickness = 0,
):
    # 定义投影面Ax+By+Cz+D=0
    A,B,C = projectNormal
    # 常量为向量与原点做点积
    D = -projectNormal.dot(projectCenter)
    plane_coeffs = (A,B,C,D)

    # 收集实体的坐标点
    vertices = []
    
    for obj in objectList:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for v in bm.verts:
            # 复制点，避免bm.free后v失效
            updateScene()
            vWorld = obj.matrix_world @ v.co
            vertices.append(vWorld.copy())
        bm.free() 

    # 投影到切面
    vOnPlane = []
    for v in vertices:
        vNew = project_point_to_plane(
            v,plane_coeffs)
        v2D = ((vNew.x,vNew.y))
        vOnPlane.append(v2D)

    # 点清理
    vMerged = merge_points(
        points=vOnPlane,
        threshold=0.001)

    # 点排序
    reference_point = (projectCenter.x,projectCenter.y)
    vSorted = polar_angle_sort(vMerged,reference_point)

    # 创建平面
    bm = bmesh.new()
    # 3D坐标转换
    verts3D = []
    for v in vSorted:
        v3D = bm.verts.new(Vector((v[0],v[1],0)))
        verts3D.append(v3D)
    # 创建面
    face = bm.faces.new((verts3D[:]))
    # 创建内缩
    bm.normal_update()  # 试了很多次，发现必须做这一步，否则无法内缩
    if insetThickness != 0:
        insetFaces=bmesh.ops.inset_region(
            bm,
            faces=bm.faces[:],
            thickness=insetThickness,
            depth=.0,
            use_boundary=True,
            use_even_offset=True,
        )
    # 新建mesh
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    # 新建Object
    projectObj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(projectObj) 


    return

# 输出异常信息
def logError(e):
    from . import build
    build.isFinished = True
    logger = logging.getLogger('ACA')
    logger.error(f"Exception occurred: {e}")
    logger.error(traceback.format_exc())
    return

# 按照指定长度，将字符串切分
# 中文算两个长度
def splitText(text, max_length=40):
    result = []  # 存储切分后的段落
    current_segment = []  # 当前正在处理的段落
    current_length = 0  # 当前段落的长度

    for char in text:
        # 判断字符长度：中文字符算两个长度，其他字符算一个长度
        char_length = 2 if '\u4e00' <= char <= '\u9fff' else 1

        # 如果当前段落长度加上当前字符长度超过最大长度，则切分
        if current_length + char_length > max_length:
            result.append(''.join(current_segment))  # 将当前段落加入结果数组
            current_segment = [char]  # 开始新的段落
            current_length = char_length  # 重置当前段落长度
        else:
            current_segment.append(char)  # 将字符加入当前段落
            current_length += char_length  # 更新当前段落长度

    # 处理剩余的字符
    if current_segment:
        result.append(''.join(current_segment))

    return result