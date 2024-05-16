# 作者：willimxp
# 所属插件：ACA Builder
# 功能概述：
#   台基的营造
import bpy
import math
import bmesh

from . import utils
from . import buildFloor
from .const import ACA_Consts as con
from .data import ACA_data_obj as acaData

# 构造台基的几何细节
def __drawPlatform(platformObj:bpy.types.Object):
    # 载入数据
    buildingObj = utils.getAcaParent(
        platformObj,con.ACA_TYPE_BUILDING
    )
    bData:acaData = buildingObj.ACA_data
    (pWidth,pDeepth,pHeight) = platformObj.dimensions
    # 计算柱网数据
    net_x,net_y = buildFloor.getFloorDate(buildingObj)
    
    # 台基第一层
    # 方砖缦地
    brickObj = utils.addCube(
        name='方砖缦地',
        location=(
            0,0,
            pHeight/2-con.STEP_HEIGHT/2
        ),
        scale=(
            bData.x_total+bData.piller_diameter*2,
            bData.y_total+bData.piller_diameter*2,
            con.STEP_HEIGHT
        ),
        parent=platformObj
    )

    # 阶条石
    # 阶条石宽度，从台基边缘做到柱顶石边缘
    stoneWidth = bData.platform_extend-bData.piller_diameter
    
    # 前后檐面阶条石，两头置好头石，尽间为去除好头石长度，明间(次间)对齐
    # 插入第一点，到台明两山尽头（从角柱延伸台基下出长度）
    firstRoomWidth = net_x[1]-net_x[0]    # 尽间宽度
    net_x.insert(0,net_x[0]-bData.platform_extend)
    net_x.append(net_x[-1]+bData.platform_extend)
    # 调整第二点，即好头石长度
    net_x[1] = net_x[0] + ((firstRoomWidth 
                + bData.platform_extend)
                * con.FIRST_LENGTH)
    net_x[-2] = net_x[-1] - ((firstRoomWidth 
                + bData.platform_extend)
                * con.FIRST_LENGTH)
    # 依次做出前后檐阶条石
    for n in range((len(net_x)-1)):
        brickObj = utils.addCube(
            name='阶条石',
            location=(
                (net_x[n+1]+net_x[n])/2,
                pDeepth/2-stoneWidth/2,
                pHeight/2-con.STEP_HEIGHT/2
            ),
            scale=(
                net_x[n+1]-net_x[n],
                stoneWidth,
                con.STEP_HEIGHT
            ),
            parent=platformObj
        )
        # 上下镜像
        utils.addModifierMirror(
            object=brickObj,
            mirrorObj=platformObj,
            use_axis=(False,True,False)
        )
    # 两山阶条石
    # 延长尽间阶条石，与好头石相接
    net_y[0] -= bData.piller_diameter
    net_y[-1] += bData.piller_diameter
    # 依次做出前后檐阶条石
    for n in range((len(net_y)-1)):
        brickObj = utils.addCube(
            name='阶条石',
            location=(
                pWidth/2-stoneWidth/2,
                (net_y[n+1]+net_y[n])/2,
                pHeight/2-con.STEP_HEIGHT/2
            ),
            scale=(
                stoneWidth,
                net_y[n+1]-net_y[n],
                con.STEP_HEIGHT
            ),
            parent=platformObj
        )
        # 上下镜像
        utils.addModifierMirror(
            object=brickObj,
            mirrorObj=platformObj,
            use_axis=(True,False,False)
        )

    # 埋头角柱
    # 角柱高度：台基总高度 - 阶条石 - 土衬
    cornerPillerH = (pHeight 
            - con.STEP_HEIGHT 
             - con.GROUND_BORDER) 
    brickObj = utils.addCube(
        name='埋头角柱',
        location=(
            pWidth/2-stoneWidth/2,
            pDeepth/2-stoneWidth/2,
            (pHeight/2
             -con.STEP_HEIGHT
             -cornerPillerH/2)
        ),
        scale=(
            stoneWidth,             # 与阶条石同宽
            stoneWidth,             # 与阶条石同宽
            cornerPillerH
        ),
        parent=platformObj
    )
    # 四面镜像
    utils.addModifierMirror(
        object=brickObj,
        mirrorObj=platformObj,
        use_axis=(True,True,False)
    )

    # 第二层，陡板
    h = pHeight - con.STEP_HEIGHT - con.GROUND_BORDER
    brickObj = utils.addCube(
        name='陡板-前后檐',
        location=(
            0,pDeepth/2- con.STEP_HEIGHT/2,
            (pHeight/2 - con.STEP_HEIGHT - h/2)
        ),
        scale=(
            pWidth - stoneWidth*2,    # 台基宽度 - 两头的角柱（与阶条石同宽）
            con.STEP_HEIGHT,             # 与阶条石同宽
            h
        ),
        parent=platformObj
    )
    utils.addModifierMirror(
        object=brickObj,
        mirrorObj=platformObj,
        use_axis=(False,True,False)
    )
    brickObj = utils.addCube(
        name='陡板-两山',
        location=(
            pWidth/2- con.STEP_HEIGHT/2,
            0,
            (pHeight/2 - con.STEP_HEIGHT - h/2)
        ),
        scale=(
            con.STEP_HEIGHT,             # 与阶条石同宽
            pDeepth - stoneWidth*2,    # 台基宽度 - 两头的角柱（与阶条石同宽）
            h
        ),
        parent=platformObj
    )
    utils.addModifierMirror(
        object=brickObj,
        mirrorObj=platformObj,
        use_axis=(True,False,False)
    )

    # 第三层，土衬石，从水平露明，并外扩金边
    brickObj = utils.addCube(
        name='土衬',
        location=(
            0,0,
            (-pHeight/2
             +con.GROUND_BORDER/2)
        ),
        scale=(
            pWidth+con.GROUND_BORDER*2,             # 与阶条石同宽
            pDeepth+con.GROUND_BORDER*2,             # 与阶条石同宽
            con.GROUND_BORDER
        ),
        parent=platformObj
    )
    
    # 统一设置
    for obj in platformObj.children:
        # 添加bevel
        modBevel:bpy.types.BevelModifier = \
            obj.modifiers.new('Bevel','BEVEL')
        modBevel.width = 0.04
        # 设置材质
        utils.copyMaterial(bData.mat_rock,obj)
    
    # 隐藏父节点
    utils.hideObj(platformObj)
    return

# 绘制踏跺对象
def __drawStep(stepProxy:bpy.types.Object):
    # 载入数据
    buildingObj = utils.getAcaParent(
        stepProxy,con.ACA_TYPE_BUILDING
    )
    bData:acaData = buildingObj.ACA_data
    (pWidth,pDeepth,pHeight) = stepProxy.dimensions
    stoneWidth = bData.platform_extend \
                    -bData.piller_diameter
    bevel = 0.03
    # 计算柱网数据
    net_x,net_y = buildFloor.getFloorDate(buildingObj)
    utils.hideObjFace(stepProxy)
    
    # 土衬
    brickObj = utils.addCube(
        name='土衬',
        location=(
            0,0,
            (-pHeight/2
             +con.GROUND_BORDER/2)
        ),
        scale=(
            pWidth+con.GROUND_BORDER*2,             # 从stepProxy扩展金边             
            pDeepth+con.GROUND_BORDER*2,    
            con.GROUND_BORDER
        ),
        parent=stepProxy
    )
    # 象眼石
    brickObj = utils.addCube(
        name='象眼石',
        location=(
            -pWidth/2+stoneWidth/2,
            con.STEP_HEIGHT*con.STEP_RATIO/2,
            con.GROUND_BORDER/2 - con.STEP_HEIGHT/2
        ),
        scale=(
            stoneWidth,             
            pDeepth - con.STEP_HEIGHT*con.STEP_RATIO,
            pHeight-con.GROUND_BORDER-con.STEP_HEIGHT
        ),
        parent=stepProxy
    )
    # 删除一条边，变成三角形，index=11
    utils.dissolveEdge(brickObj,[11])
    utils.addModifierMirror(
        object=brickObj,
        mirrorObj=stepProxy,
        use_axis=(True,False,False)
    )
    # 象眼石拉伸，做为boolean对象
    booleanObj = utils.copySimplyObject(
        sourceObj=brickObj,
        parentObj=stepProxy,
        location=brickObj.location
    )
    booleanObj.scale.x = 2
    utils.hideObj(booleanObj)

    # 垂带宽度（与阶条石宽度相同）
    brickObj = utils.addCube(
        name='垂带',
        location=(
            -pWidth/2+stoneWidth/2,
            0,
            con.GROUND_BORDER/2
        ),
        scale=(
            stoneWidth,             
            pDeepth,
            pHeight-con.GROUND_BORDER
        ),
        parent=stepProxy
    )
    # 删除一条边，变成三角形，index=11
    utils.dissolveEdge(brickObj,[11])
    modBool:bpy.types.BooleanModifier = brickObj.modifiers.new(
        'boolean','BOOLEAN')
    modBool.object = booleanObj
    modBool.solver = 'EXACT'
    # 镜像
    utils.addModifierMirror(
        object=brickObj,
        mirrorObj=stepProxy,
        use_axis=(True,False,False)
    )
    # 台阶（上基石、中基石，也叫踏跺心子）
    # 计算台阶数量，每个台阶不超过基石的最大高度（15cm）
    count = math.ceil(
        (pHeight-con.GROUND_BORDER)
        /con.STEP_HEIGHT)
    stepHeight = (pHeight-con.GROUND_BORDER)/count
    stepWidth = pDeepth/(count)
    for n in range(count-1):
        brickObj = utils.addCube(
            name='台阶',
            location=(
                0,
                (-pDeepth/2
                 +(n+1.5)*stepWidth),
                (-pHeight/2
                +con.GROUND_BORDER/2
                + (n+0.5)*stepHeight)
            ),
            scale=(
                pWidth-stoneWidth*2,
                stepWidth+bevel*2,
                stepHeight
            ),
            parent=stepProxy
        )
    
    # 批量设置
    for obj in stepProxy.children:
        modBevel:bpy.types.BevelModifier = \
            obj.modifiers.new('Bevel','BEVEL')
        modBevel.width = bevel
        modBevel.offset_type = 'WIDTH'
        modBevel.use_clamp_overlap = False
        # 设置材质
        utils.copyMaterial(bData.mat_rock,obj)


    return

# 构造台基的踏跺，根据门的设定，自动判断
def __buildStep(platformObj:bpy.types.Object):
    # 载入数据
    buildingObj = utils.getAcaParent(
        platformObj,con.ACA_TYPE_BUILDING
    )
    bData:acaData = buildingObj.ACA_data
    (pWidth,pDeepth,pHeight) = platformObj.dimensions
    # 计算柱网数据
    net_x,net_y = buildFloor.getFloorDate(buildingObj)

    # 解析模版输入的墙体设置，格式如下
    # "wall#3/0#3/3,wall#0/0#3/0,wall#0/3#3/3,window#0/0#0/1,window#0/2#0/3,door#0/1#0/2,"
    wallSetting = bData.wall_net
    wallList = wallSetting.split(',')
    for wallID in wallList:
        if wallID == '': continue
        setting = wallID.split('#')
        # 样式为墙、门、窗
        style = setting[0]
        # 仅在门外设踏跺，槛窗、墙体外不设踏跺
        if style == con.ACA_WALLTYPE_DOOR:
            # 起始柱子
            pFrom = setting[1].split('/')
            pFrom_x = int(pFrom[0])
            pFrom_y = int(pFrom[1])
            # 结束柱子
            pTo = setting[2].split('/')
            pTo_x = int(pTo[0])
            pTo_y = int(pTo[1])

            step_dir = ''
            if pFrom_x == 0 and pTo_x == 0:
                # 西门
                if pFrom_y+pTo_y ==  len(net_y)-1:
                    # 明间
                    step_dir = 'W'
            if pFrom_x == len(net_x)-1 and pTo_x == len(net_x)-1:
                # 东门
                if pFrom_y+pTo_y ==  len(net_y)-1:
                    # 明间
                    step_dir = 'E'
            if pFrom_y == 0 and pTo_y == 0:
                # 南门
                if pFrom_x+pTo_x ==  len(net_x)-1:
                    # 明间
                    step_dir = 'S'
            if pFrom_y == len(net_y)-1 and pTo_y == len(net_y)-1:
                # 北门
                if pFrom_x+pTo_x ==  len(net_x)-1:
                    # 明间
                    step_dir = 'N'
            
            if step_dir != '':
                stepHeight = platformObj.dimensions.z
                stepDeepth = stepHeight * con.STEP_RATIO
                offset = bData.platform_extend+stepDeepth/2
                if step_dir in ('N','S'):
                    stepWidth = abs(net_x[pTo_x] - net_x[pFrom_x])
                    x = (net_x[pTo_x] + net_x[pFrom_x])/2
                    if step_dir == 'N':
                        y = net_y[pFrom_y] + offset
                        rot = (0,0,math.radians(180))
                    if step_dir == 'S':
                        y = net_y[pFrom_y] - offset
                        rot = (0,0,0)
                if step_dir in ('W','E'):
                    stepWidth = abs(net_y[pTo_y] - net_y[pFrom_y])
                    if step_dir == 'W':
                        x = net_x[pFrom_x] - offset
                        rot = (0,0,math.radians(270))
                    if step_dir == 'E':
                        x = net_x[pFrom_x] + offset
                        rot = (0,0,math.radians(90))
                    y = (net_y[pTo_y] + net_y[pFrom_y])/2
                stepProxy = utils.addCube(
                    name='踏跺proxy',
                    location=(x,y,0),
                    scale=(stepWidth,stepDeepth,stepHeight),
                    rotation=rot,
                )
                stepProxy.parent = platformObj
                __drawStep(stepProxy)

    return

# 根据固定模板，创建新的台基
def buildPlatform(buildingObj:bpy.types.Object):
    bData : acaData = buildingObj.ACA_data
    bData.is_showPlatform = True

    # 1、创建地基===========================================================
    # 如果已有，先删除
    pfObj = utils.getAcaChild(buildingObj,con.ACA_TYPE_PLATFORM)
    if pfObj != None:
        utils.deleteHierarchy(pfObj,del_parent=True)

    # 载入模板配置
    platform_height = buildingObj.ACA_data.platform_height
    platform_extend = buildingObj.ACA_data.platform_extend
    # 构造cube三维
    height = platform_height
    width = platform_extend * 2 + bData.x_total
    length = platform_extend * 2 + bData.y_total
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
    # 设置材质
    utils.copyMaterial(bData.mat_rock,pfObj)

    # 默认锁定对象的位置、旋转、缩放（用户可自行解锁）
    pfObj.lock_location = (True,True,True)
    pfObj.lock_rotation = (True,True,True)
    pfObj.lock_scale = (True,True,True)

    # 构造台基细节
    __drawPlatform(pfObj)
    # 构造台基踏跺
    __buildStep(pfObj)

     # 更新建筑框大小
    buildingObj.empty_display_size = math.sqrt(
            pfObj.dimensions.x * pfObj.dimensions.x
            + pfObj.dimensions.y * pfObj.dimensions.y
        ) / 2
    
    # 重新聚焦建筑根节点
    utils.focusObj(buildingObj)

# 根据插件面板的台基高度、下出等参数变化，更新台基外观
# 绑定于data.py中update_platform回调
def resizePlatform(buildingObj:bpy.types.Object):
    # 载入根节点中的设计参数
    bData : acaData = buildingObj.ACA_data
    dk = bData.DK
    
    # 找到台基对象
    pfObj = utils.getAcaChild(buildingObj,con.ACA_TYPE_PLATFORM)
    # 重绘
    pf_extend = bData.platform_extend
    # 缩放台基尺寸
    pfObj.dimensions= (
        pf_extend * 2 + bData.x_total,
        pf_extend * 2 + bData.y_total,
        bData.platform_height
    )
    # 应用缩放(有时ops.object会乱跑，这里确保针对台基对象)
    utils.applyScale(pfObj)
    # 平移，保持台基下沿在地平线高度
    pfObj.location.z = bData.platform_height /2

    # 对齐其他各个层
    # 柱网层
    floorRootObj = utils.getAcaChild(
        buildingObj,con.ACA_TYPE_FLOOR_ROOT)
    floorRootObj.location.z =  bData.platform_height
    # 墙体层
    wallRoot = utils.getAcaChild(
        buildingObj,con.ACA_TYPE_WALL_ROOT)
    wallRoot.location.z = bData.platform_height
    # 屋顶层
    roofRoot = utils.getAcaChild(
        buildingObj,con.ACA_TYPE_ROOF_ROOT)
    tile_base = bData.platform_height \
                + bData.piller_height
    # 如果有斗栱，抬高斗栱高度
    if bData.use_dg:
        tile_base += bData.dg_height
        # 是否使用平板枋
        if bData.use_pingbanfang:
            tile_base += con.PINGBANFANG_H*dk
    else:
        # 以大梁抬升
        # tile_base += con.BEAM_HEIGHT*pd
        # 实际为金桁垫板高度+半桁
        tile_base += con.BOARD_HENG_H*dk + con.HENG_COMMON_D*dk/2
    roofRoot.location.z = tile_base

    # 更新建筑框大小
    buildingObj.empty_display_size = math.sqrt(
            pfObj.dimensions.x * pfObj.dimensions.x
            + pfObj.dimensions.y * pfObj.dimensions.y
        ) / 2
    
    # 重新聚焦建筑根节点
    utils.focusObj(buildingObj)
    utils.outputMsg("Platform updated")