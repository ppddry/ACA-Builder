# 作者：willimxp
# 所属插件：ACA Builder
# 功能概述：
#   自定义数据结构
#   绑定面板控件
#   触发控件数据更新

import bpy
from . import operators
import xml.etree.ElementTree as ET
import os
from .const import ACA_Consts as con
from . import buildwall
from functools import partial
from . import utils

# 初始化自定义属性
def initprop():
    # 在scene中添加可全局访问的自定义数据集
    bpy.types.Scene.ACA_data = bpy.props.PointerProperty(
        type=ACA_data_scene,
        name="古建场景属性集"
    )
    bpy.types.Object.ACA_data = bpy.props.PointerProperty(
        type=ACA_data_obj,
        name="古建构件属性集"
    )

# 销毁自定义属性
def delprop():
    del bpy.types.Scene.ACA_data
    del bpy.types.Object.ACA_data

# 筛选资产目录
def p_filter(self, object:bpy.types.Object):
    #print("filter:" + object.name + "/" + str(len(object.users_collection)))
    return object.users_collection[0].name == 'Assets'

# 解析XML，获取模版列表
def getTemplateList():
    # 载入XML
    path = os.path.join('template', 'simplyhouse.xml')
    tree = ET.parse(path)
    root = tree.getroot()
    templates = root.findall('template')

    template_list = []
    for template in templates:
        template_name = template.find('name').text
        template_list.append((template_name,template_name,''))
    
    print("ACA: Get template list")
    return template_list

# 重建整体建筑
# todo:和update_building有些重复，后续看是否删除
def update_floor(self, context:bpy.types.Context):
    # 确认选中为building节点
    buildingObj = context.object 
    if buildingObj.ACA_data.aca_type == con.ACA_TYPE_BUILDING:
        # 调用营造序列
        operators.buildAll(buildingObj)
    else:
        print("ACA: updated building failed, context.object should be buildingObj")
        return

# 重建整体建筑
def update_building(self, context:bpy.types.Context):
    # 确认选中为building节点
    buildingObj = context.object 
    if buildingObj.ACA_data.aca_type == con.ACA_TYPE_BUILDING:
        # 调用营造序列
        operators.buildAll(buildingObj)
    else:
        print("ACA: updated building failed, context.object should be buildingObj")
        return

# 调整建筑斗口
def update_dk(self, context:bpy.types.Context):
    # 确认选中为building节点
    buildingObj = context.object
    dk = buildingObj.ACA_data.DK
    if buildingObj.ACA_data.aca_type == con.ACA_TYPE_BUILDING:
        # 更新DK值
        operators.setTemplateByDK(dk,buildingObj)
        operators.buildAll(buildingObj)
    else:
        print("ACA: updated building failed, context.object should be buildingObj")
        return

def update_platform(self, context:bpy.types.Context):
    # 确认选中为building节点
    buildingObj = context.object
    if buildingObj.ACA_data.aca_type == con.ACA_TYPE_BUILDING:
        # 调用台基缩放
        operators.resizePlatform(buildingObj)
    else:
        print("ACA: updated platform failed, context.object should be buildingObj")
        return
    
def update_piller(self, context:bpy.types.Context):
    # 确认选中为building节点
    buildingObj = context.object
    if buildingObj.ACA_data.aca_type == con.ACA_TYPE_BUILDING:
        # 缩放柱形
        operators.resizePiller(buildingObj)
        # 重新生成墙体
        wallBuilder = buildwall.wallBuilder()
        # wallBuilder.buildWallLayout(buildingObj)
        funproxy = partial(wallBuilder.buildWallLayout,buildingObj=buildingObj)
        utils.fastRun(funproxy)
    else:
        print("ACA: updated platform failed, context.object should be buildingObj")
        return

def update_wall(self, context:bpy.types.Context):
    # 确认选中为building节点
    buildingObj = context.object
    if buildingObj.ACA_data.aca_type == con.ACA_TYPE_BUILDING:
        # 重新生成墙体
        wallBuilder = buildwall.wallBuilder()
        #wallBuilder.buildWallLayout(buildingObj)
        funproxy = partial(wallBuilder.buildWallLayout,buildingObj=buildingObj)
        utils.fastRun(funproxy)
    else:
        print("ACA: updated platform failed, context.object should be buildingObj")
        return

# 对象范围的数据
# 可绑定面板参数属性
# 属性声明的格式在vscode有告警，但blender表示为了保持兼容性，无需更改
# 直接添加“# type:ignore”
# https://blender.stackexchange.com/questions/311578/how-do-you-correctly-add-ui-elements-to-adhere-to-the-typing-spec
class ACA_data_obj(bpy.types.PropertyGroup):
    # 通用对象属性
    aca_obj : bpy.props.BoolProperty(
            name = '是ACA对象',
            default = False
        ) # type: ignore
    aca_type : bpy.props.StringProperty(
            name = '对象类型',
        ) # type: ignore
    
    DK: bpy.props.FloatProperty(
            name = "斗口",
            min=0.01,
            update = update_dk
        ) # type: ignore


    # 台基对象属性
    platform_height : bpy.props.FloatProperty(
            name = "台基高度",
            min = 0.01, 
            update = update_platform # 绑定回调
        ) # type: ignore
    platform_extend : bpy.props.FloatProperty(
            name = "台基下出",
            min = 0.01, 
            update = update_platform    # 绑定回调
        ) # type: ignore
    
    # 柱网对象属性
    x_total : bpy.props.FloatProperty(
            name = "通面阔"
        )# type: ignore
    y_total : bpy.props.FloatProperty(
            name = "通进深"
        )# type: ignore
    x_rooms : bpy.props.IntProperty(
            name = "面阔间数",
            min = 1, max = 11,step = 2,
            update= update_floor
        )# type: ignore
    x_1 : bpy.props.FloatProperty(
            name = "明间宽度",
            min = 0, 
            update = update_floor
        )# type: ignore
    x_2 : bpy.props.FloatProperty(
            name = "次间宽度",
            min = 0, 
            update = update_floor
        )# type: ignore
    x_3 : bpy.props.FloatProperty(
            name = "梢间宽度",
            min = 0, 
            update = update_floor
        )# type: ignore
    x_4 : bpy.props.FloatProperty(
            name = "尽间宽度",
            min = 0, 
            update = update_floor
        )# type: ignore
    y_rooms : bpy.props.IntProperty(
            name = "进深间数",
            max = 5,
            min = 1, 
            update = update_floor
        )# type: ignore
    y_1 : bpy.props.FloatProperty(
            name = "明间深度",
            min = 0, 
            update = update_floor
        )# type: ignore
    y_2 : bpy.props.FloatProperty(
            name = "次间深度",
            min = 0, 
            update = update_floor
        )# type: ignore
    y_3 : bpy.props.FloatProperty(
            name = "梢间深度",
            min = 0, 
            update = update_floor
        )# type: ignore
    piller_net : bpy.props.StringProperty(
            name = "保存的柱网列表"
        )# type: ignore
    
    # 柱子属性
    piller_source : bpy.props.PointerProperty(
            name = "柱样式",
            type = bpy.types.Object,
            poll = p_filter,
            update = update_floor
        )# type: ignore
    piller_height : bpy.props.FloatProperty(
            name = "柱高",
            default = 0,
            min = 0.01, 
            update = update_piller
        )# type: ignore
    piller_diameter : bpy.props.FloatProperty(
            name = "柱径",
            default = 0,
            min = 0.01, 
            update = update_piller
        )# type: ignore
    
    # 墙体属性
    wall_layout : bpy.props.EnumProperty(
            name = "墙体布局",
            description = "墙体布局",
            items = [
                ("0","-无墙体-",""),
                ("1","默认(无廊)",""),
                ("2","周围廊",""),
                ("3","前廊",""),
                ("4","斗底槽",""),
            ],
            update = update_wall,
            options = {"ANIMATABLE"}
        ) # type: ignore
    wall_style : bpy.props.EnumProperty(
            name = "墙类型",
            items = [
                ("","",""),
                ("1","槛墙",""),
                ("2","隔扇",""),
                ("3","槛窗",""),
            ],
        ) # type: ignore
    wall_source : bpy.props.PointerProperty(
            name = "墙样式",
            type = bpy.types.Object,
            poll = p_filter,
            update = update_wall
        )# type: ignore 
    
    # 隔扇属性
    door_height : bpy.props.FloatProperty(
            name="中槛高度",
        )# type: ignore 
    door_num : bpy.props.IntProperty(
            name="隔扇数量",
            default=4, max=4,
        )# type: ignore 
    gap_num : bpy.props.IntProperty(
            name="抹头数量",
            default=5,min=2,max=6
        )# type: ignore 
    is_with_wall: bpy.props.BoolProperty(
            default=False,
            name="添加槛墙"
        )# type: ignore 
    lingxin_source:bpy.props.PointerProperty(
            name = "棂心",
            type = bpy.types.Object,
            poll = p_filter
        )# type: ignore 

# 场景范围的数据
# 可绑定面板参数属性
# 也可做为全局变量访问
# 属性声明的格式在vscode有告警，但blender表示为了保持兼容性，无需更改
# 直接添加“# type:ignore”
# https://blender.stackexchange.com/questions/311578/how-do-you-correctly-add-ui-elements-to-adhere-to-the-typing-spec
class ACA_data_scene(bpy.types.PropertyGroup):
    is_auto_redraw : bpy.props.BoolProperty(
            default = True,
            name = "是否实时重绘"
        ) # type: ignore
    template : bpy.props.EnumProperty(
            name = "模版样式",
            description = "模板样式",
            items = getTemplateList(),
            options = {"ANIMATABLE"}
        ) # type: ignore