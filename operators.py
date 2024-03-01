# 作者：willimxp
# 所属插件：ACA Builder
# 功能概述：
#   构建逻辑类

import math
import bmesh
import bpy
from bpy_extras import object_utils
from bpy_extras.object_utils import AddObjectHelper
from mathutils import Vector,Matrix,geometry,Euler

from . import data
from .const import ACA_Consts as con
from . import utils
from . import const

# 将模版参数填充入根节点的设计参数中
def setTemplateData(buildingObj:bpy.types.Object,
                    template:const.ACA_template):
    # 映射template对象到ACA_data中
    buildingData = buildingObj.ACA_data
    buildingData['aca_obj'] = True
    buildingData['aca_type'] = con.ACA_TYPE_BUILDING
    buildingData['template'] = template.NAME
    buildingData['DK'] = template.DK
    buildingData['platform_height'] = template.PLATFORM_HEIGHT
    buildingData['platform_extend'] = template.PLATFORM_EXTEND
    buildingData['x_rooms'] = template.ROOM_X
    buildingData['x_1'] = template.ROOM_X1
    buildingData['x_2'] = template.ROOM_X2
    buildingData['x_3'] = template.ROOM_X3
    buildingData['x_4'] = template.ROOM_X4
    buildingData['y_rooms'] = template.ROOM_Y
    buildingData['y_1'] = template.ROOM_Y1
    buildingData['y_2'] = template.ROOM_Y2
    buildingData['y_3'] = template.ROOM_Y3
    buildingData['piller_height'] = template.PILLER_HEIGHT
    buildingData['piller_diameter'] = template.PILLER_D 

# 根据panel中DK的改变，更新整体设计参数
def setTemplateByDK(self, context:bpy.types.Context,
                    dk,
                    buildingObj:bpy.types.Object):
    # 载入模版
    template_name = context.scene.ACA_data.template
    # 根据DK数据，重新计算模版参数
    template = const.ACA_template(template_name,dk)

    # 在根节点绑定模版数据
    setTemplateData(buildingObj,template)
    

# 添加建筑empty根节点，并绑定设计模版
# 返回建筑empty根节点对象
# 被ACA_OT_add_newbuilding类调用
def addBuildingRoot(self, context:bpy.types.Context):
    # 获取panel上选择的模版
    template_name = context.scene.ACA_data.template
    
    # 创建根节点empty
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    buildingObj = context.object
    buildingObj.location = context.scene.cursor.location   # 原点摆放在3D Cursor位置
    buildingObj.name = template_name   # 系统遇到重名会自动添加00x的后缀       
    buildingObj.empty_display_type = 'SPHERE'

    # 在根节点绑定模版数据
    template = const.ACA_template(template_name)
    setTemplateData(buildingObj,template)
    
    print("ACA: Building Root added")
    return buildingObj

# 根据固定模板，创建新的台基
def buildPlatform(self, context:bpy.types.Context,
                 buildingObj:bpy.types.Object):
    buildingData : data.ACA_data_obj = buildingObj.ACA_data

    # 1、创建地基===========================================================
    # 载入模板配置
    platform_height = buildingObj.ACA_data.platform_height
    platform_extend = buildingObj.ACA_data.platform_extend
    # 构造cube三维
    height = platform_height
    width = platform_extend * 2 + buildingData.x_total
    length = platform_extend * 2 + buildingData.y_total
    bpy.ops.mesh.primitive_cube_add(
                size=1.0, 
                calc_uvs=True, 
                enter_editmode=False, 
                align='WORLD', 
                location = (0,0,height/2), 
                scale=(width,length,height))
    pfObj = bpy.context.object
    pfObj.parent = buildingObj
    pfObj.name = con.PLATFORM_NAME
    # 设置插件属性
    pfObj.ACA_data['aca_obj'] = True
    pfObj.ACA_data['aca_type'] = con.ACA_TYPE_PLATFORM

    # 默认锁定对象的位置、旋转、缩放（用户可自行解锁）
    pfObj.lock_location = (True,True,True)
    pfObj.lock_rotation = (True,True,True)
    pfObj.lock_scale = (True,True,True)

     # 更新建筑框大小
    buildingObj.empty_display_size = math.sqrt(
            pfObj.dimensions.x * pfObj.dimensions.x
            + pfObj.dimensions.y * pfObj.dimensions.y
        ) / 2
    
    print("ACA: Platform added")

# 根据插件面板的台基高度、下出等参数变化，更新台基外观
# 绑定于data.py中update_platform回调
def resizePlatform(self, context:bpy.types.Context,
                    buildingObj:bpy.types.Object):

    # 载入根节点中的设计参数
    buildingData : data.ACA_data_obj = buildingObj.ACA_data
    
    # 找到台基对象
    pfObj = utils.getAcaChild(buildingObj,con.ACA_TYPE_PLATFORM)
    # 重绘
    pf_extend = buildingData.platform_extend
    # 缩放台基尺寸
    pfObj.dimensions= (
        pf_extend * 2 + buildingData.x_total,
        pf_extend * 2 + buildingData.y_total,
        buildingData.platform_height
    )
    # 应用缩放(有时ops.object会乱跑，这里确保针对台基对象)
    utils.ApplyScale(pfObj)
    # 平移，保持台基下沿在地平线高度
    pfObj.location.z = buildingData.platform_height /2

    # 对齐柱网
    floorObj = utils.getAcaChild(buildingObj,con.ACA_TYPE_FLOOR)
    floorObj.location.z =  buildingData.platform_height

    # 更新建筑框大小
    buildingObj.empty_display_size = math.sqrt(
            pfObj.dimensions.x * pfObj.dimensions.x
            + pfObj.dimensions.y * pfObj.dimensions.y
        ) / 2
    
    # 重新聚焦建筑根节点
    utils.focusObj(buildingObj)
    print("ACA: Platform updated")

# 准备柱网数据
# 将panel中设置的面宽、进深，组合成柱网数组
# 返回net_x[],net_y[]数组
def getFloorDate(self,context:bpy.types.Context,
                     buildingObj:bpy.types.Object):
    # 载入设计参数
    buildingData : data.ACA_data_obj = buildingObj.ACA_data

    # 构造柱网X坐标序列，罗列了1，3，5，7，9，11间的情况，未能抽象成通用公式
    x_rooms = buildingData.x_rooms   # 面阔几间
    y_rooms = buildingData.y_rooms   # 进深几间

    net_x = []  # 重新计算
    if x_rooms >=1:     # 明间
        offset = buildingData.x_1 / 2
        net_x.append(offset)
        net_x.insert(0, -offset)
    if x_rooms >=3:     # 次间
        offset = buildingData.x_1 / 2 + buildingData.x_2
        net_x.append(offset)
        net_x.insert(0, -offset)  
    if x_rooms >=5:     # 梢间
        offset = buildingData.x_1 / 2 + buildingData.x_2 \
                + buildingData.x_3
        net_x.append(offset)
        net_x.insert(0, -offset)  
    if x_rooms >=7:     # 尽间
        offset = buildingData.x_1 / 2 + buildingData.x_2 \
            + buildingData.x_3 + buildingData.x_4
        net_x.append(offset)
        net_x.insert(0, -offset)  
    if x_rooms >=9:     #更多梢间
        offset = buildingData.x_1 / 2 + buildingData.x_2 \
            + buildingData.x_3 * 2
        net_x[-1] = offset
        net_x[0]= -offset  
        offset = buildingData.x_1 / 2 + buildingData.x_2 \
            + buildingData.x_3 *2 + buildingData.x_4
        net_x.append(offset)
        net_x.insert(0, -offset) 
    if x_rooms >=11:     #更多梢间
        offset = buildingData.x_1 / 2 + buildingData.x_2 \
            + buildingData.x_3 * 3
        net_x[-1] = offset
        net_x[0]= -offset  
        offset = buildingData.x_1 / 2 + buildingData.x_2 \
            + buildingData.x_3 *3 + buildingData.x_4
        net_x.append(offset)
        net_x.insert(0, -offset) 

    # 构造柱网Y坐标序列，罗列了1-5间的情况，未能抽象成通用公式
    net_y=[]    # 重新计算
    if y_rooms%2 == 1: # 奇数间
        if y_rooms >= 1:     # 明间
            offset = buildingData.y_1 / 2
            net_y.append(offset)
            net_y.insert(0, -offset)
        if y_rooms >= 3:     # 次间
            offset = buildingData.y_1 / 2 + buildingData.y_2
            net_y.append(offset)
            net_y.insert(0, -offset)  
        if y_rooms >= 5:     # 梢间
            offset = buildingData.y_1 / 2 + buildingData.y_2 \
                    + buildingData.y_3
            net_y.append(offset)
            net_y.insert(0, -offset) 
    else:   #偶数间
        if y_rooms >= 2:
            net_y.append(0)
            offset = buildingData.y_1
            net_y.append(offset)
            net_y.insert(0,-offset)
        if y_rooms >= 4:
            offset = buildingData.y_1 + buildingData.y_2
            net_y.append(offset)
            net_y.insert(0,-offset)
    
    # 保存通面阔计算结果，以便其他函数中复用
    buildingData.x_total = net_x[-1]-net_x[0]
    # 保存通进深计算结果，以便其他函数中复用
    buildingData.y_total = net_y[-1]-net_y[0]

    return net_x,net_y

# 根据柱网数组，排布柱子
# 1. 第一次按照模板生成，柱网下没有柱，一切从0开始；
# 2. 用户调整柱网的开间、进深，需要保持柱子的高、径、样式
# 3. 修改柱样式时，也会重排柱子
# 建筑根节点（内带设计参数集）
def buildFloor(self,context:bpy.types.Context,
                buildingObj:bpy.types.Object):
    # 1、查找或新建地盘根节点
    floorObj = utils.getAcaChild(buildingObj,con.ACA_TYPE_FLOOR)
    # 清空地盘下所有的柱子、柱础，重建
    if floorObj != None:
        utils.delete_hierarchy(floorObj,True)
    # 创建根对象（empty）===========================================================
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    floorObj = context.object
    floorObj.name = "地盘"
    floorObj.parent = buildingObj  # 挂接在对应建筑节点下
    floorObj.ACA_data['aca_obj'] = True
    floorObj.ACA_data['aca_type'] = con.ACA_TYPE_FLOOR
    #与台基顶面对齐
    floor_z = buildingObj.ACA_data.platform_height
    floorObj.location = (0,0,floor_z)

    # 2、生成一个柱子实例piller_basemesh
    # 从当前场景中载入数据集
    buildingData : data.ACA_data_obj = buildingObj.ACA_data
    piller_source = buildingData.piller_source
    piller_height = buildingData.piller_height
    piller_R = buildingData.piller_diameter /2
    if piller_source == None:
        piller_name = "基本立柱"
        # 默认创建简单柱子
        piller_basemesh = utils.addCylinder(radius=piller_R,
                depth=piller_height,
                location=(0, 0, 0),
                name=piller_name,
                root_obj=floorObj,  # 挂接在柱网节点下
                origin_at_bottom = True,    # 将origin放在底部
            )
    else:
        # 已设置柱样式，根据设计参数实例化
        piller_basemesh:bpy.types.Object = utils.copyObject(
            sourceObj=piller_source,
            name=piller_source.name,
            parentObj=floorObj,
        )
        piller_basemesh.dimensions = (
            buildingData.piller_diameter,
            buildingData.piller_diameter,
            buildingData.piller_height
        )
        utils.ApplyScale(piller_basemesh) # 此时mesh已经与source piller解绑，生成了新的mesh
    # 柱子属性
    piller_basemesh.ACA_data['aca_obj'] = True
    piller_basemesh.ACA_data['aca_type'] = con.ACA_TYPE_PILLER
    
    # 3、根据地盘数据，循环排布每根柱子
    x_rooms = buildingData.x_rooms   # 面阔几间
    y_rooms = buildingData.y_rooms   # 进深几间
    net_x,net_y = getFloorDate(self,context,buildingObj)
    for y in range(y_rooms + 1):
        for x in range(x_rooms + 1):
            # 统一命名为“柱.x/y”，以免更换不同柱形时，减柱设置失效
            piller_copy_name = "柱" + \
                '.' + str(x) + '/' + str(y)
            
            # 减柱验证
            piller_list_str = buildingData.piller_net
            if piller_copy_name not in piller_list_str \
                    and piller_list_str != "" :
                # print("PP: piller skiped " + piller_copy_name)
                continue    # 结束本次循环
            
            # 复制柱子，仅instance，包含modifier
            piller_loc = (net_x[x],net_y[y],piller_basemesh.location.z)
            piller_copy = utils.copyObject(
                sourceObj = piller_basemesh,
                name = piller_copy_name,
                location=piller_loc,
                parentObj = floorObj
            )   

    # 清理临时柱子
    bpy.data.objects.remove(piller_basemesh)

    # 重建柱础
    setPillerBase(self,context,buildingObj)

    print("ACA: Pillers rebuilt")

# 根据用户在插件面板修改的柱高、柱径，缩放柱子外观
# 绑定于data.py中objdata属性中触发的回调
def resizePiller(self,context:bpy.types.Context,
                        buildingObj:bpy.types.Object):
    # 获取一个现有的柱子实例，做为缩放的依据
    pillerObj = utils.getAcaChild(buildingObj,con.ACA_TYPE_PILLER)
    
    buildingData = buildingObj.ACA_data
    # 垂直缩放
    piller_h_scale = (
            buildingData.piller_height 
            / pillerObj.dimensions.z
        )
    # 垂直位移
    piller_z_offset = (
            buildingData.piller_height 
            - pillerObj.dimensions.z
        )/2
    # 平面缩放
    piller_d_scale = (
            buildingData.piller_diameter
            / pillerObj.dimensions.x
        )
    
    # 所有柱子为同一个mesh，只需要在edit mode中修改，即可全部生效
    # bug: 未指定变形中心，导致异常
    utils.focusObj(pillerObj)
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'SELECT')
    bpy.ops.transform.resize(
        value=(piller_d_scale, piller_d_scale, piller_h_scale))
    bpy.ops.transform.translate(value=(0,0,piller_z_offset))
    bpy.ops.object.mode_set(mode = 'OBJECT')

    # 缩放柱础
    pillerbaseObj = utils.getAcaChild(buildingObj,con.ACA_TYPE_PILLERBASE)
    if pillerbaseObj != None:
        pillerbase_z_offset = pillerbaseObj.dimensions.z * (piller_d_scale-1) / 2
        utils.focusObj(pillerbaseObj)
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.transform.resize(
            value=(piller_d_scale, piller_d_scale, piller_d_scale))
        bpy.ops.transform.translate(value=(0,0,pillerbase_z_offset))
        bpy.ops.object.mode_set(mode = 'OBJECT')

    # 重新聚焦建筑根节点
    utils.focusObj(buildingObj)
    print("ACA: Piller updated")

# 柱础的添加、修改、删除
def setPillerBase(self,context:bpy.types.Context,
                       buildingObj:bpy.types.Object):
    # 获取设计参数
    buildingData:data.ACA_data_obj = buildingObj.ACA_data
    # 定位到“ACA”根collection
    # 测试过程中，出现过目录失焦，导致柱础对象绑定到了根目录下
    utils.setCollection(context, con.ROOT_COLL_NAME)
    
    # 获取地盘节点
    floorObj = utils.getAcaChild(buildingObj,con.ACA_TYPE_FLOOR)
    # 声明柱础模版
    # 删除地盘的柱子下的老柱础
    for piller in floorObj.children:
        for obj in piller.children:
            bpy.data.objects.remove(obj)
    
    # 添加新柱础
    # 循环柱网下的每根柱子对象，绑定柱础子对象
    pillerbase_sourceObj = buildingData.piller_base_source
    if pillerbase_sourceObj != None:
        # 复制柱础 
        pillerbaseObj = utils.copyObject(
                    sourceObj=pillerbase_sourceObj,
                    name='柱础',
                    singleUser=True # 独立对象
                )
        
        # 根据柱径的缩放，自动缩放柱础
        pillerOrigin:bpy.types.Object = buildingData.piller_source
        pillerScale = 1
        if pillerOrigin != None:
            piller = floorObj.children[0]        
            pillerScale = piller.dimensions.x / pillerOrigin.dimensions.x
            pillerbaseObj.dimensions = pillerbaseObj.dimensions * pillerScale
        # bug: 未设柱形时，柱础就不会缩放了
        # 为了解决这个问题硬是写死了以下代码，非常难看
        else:
            # 设置一个默认值
            s = 1.6
            pillerbaseObj.dimensions = (
                piller.dimensions.x * s,
                piller.dimensions.y * s,
                pillerbaseObj.dimensions.z * piller.dimensions.x * s /pillerbaseObj.dimensions.x)

        for piller in floorObj.children:
            # 绑定新的柱础
            pillerbaseCopy = utils.copyObject(
                sourceObj=pillerbaseObj,
                name='柱础',
                parentObj=piller,
            )
            pillerbaseCopy.ACA_data['aca_obj'] = True
            pillerbaseCopy.ACA_data['aca_type'] = con.ACA_TYPE_PILLERBASE
            # 设置为不可选中
            #pillerbaseCopy.hide_select = True

        # 清理临时柱础
        bpy.data.objects.remove(pillerbaseObj)

    # 重新聚焦建筑根节点
    utils.focusObj(buildingObj)
    print("ACA: Piller-base added")

# 执行营造整体过程
# 输入buildingObj，自带设计参数集，且做为其他构件绑定的父节点
def buildAll(self, context:bpy.types.Context,
             buildingObj:bpy.types.Object):
    # 解决bug：面阔间数在鼠标拖拽时可能为偶数，出现异常
    if buildingObj.ACA_data.x_rooms % 2 == 0:
        # 不处理偶数面阔间数
        utils.ShowMessageBox("面阔间数不能为偶数","ERROR")
        return
    
    # 清除建筑根节点下所有对象
    utils.delete_hierarchy(buildingObj)
    # 生成柱网
    buildFloor(self,context,buildingObj)
    # 生成台基
    buildPlatform(self,context,buildingObj)
    # 重新聚焦建筑根节点
    utils.focusObj(buildingObj)

# 生成新建筑
# 所有自动生成的建筑统一放置在项目的“ACA”collection中
# 每个建筑用一个empty做为parent，进行树状结构的管理
# 各个建筑之间的设置参数数据隔离，互不影响
#（后续可以提供批量修改的功能）
# 用户在场景中选择时，可自动回溯到该建筑
class ACA_OT_add_building(bpy.types.Operator):
    bl_idname="aca.add_newbuilding"
    bl_label = "添加新建筑"

    def execute(self, context):      
        # 1.定位到“ACA”根collection，如果没有则新建
        utils.setCollection(context, con.ROOT_COLL_NAME)

        # 2.添加建筑empty
        # 其中绑定了模版数据
        buildingObj = addBuildingRoot(self,context)

        # 3.调用营造序列
        buildAll(self,context,buildingObj)     

        # 聚焦到建筑根节点
        utils.focusObj(buildingObj)
        return {'FINISHED'}