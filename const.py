# 作者：willimxp
# 所属插件：ACA Builder
# 功能概述：
# 常数定义
# 请务必注意，只读取该属性，不要修改属性

class ACA_Consts(object):
    # 继承object类，提供了__setattr__等方法
    # https://www.jb51.net/article/274253.htm

    # 系统参数
    ROOT_COLL_NAME = 'ACA古建营造'               # 根目录名称
    PLATFORM_NAME = '台基'                      # 台基名称
    ACA_TYPE_BUILDING = 'building'              # ACA类型：建筑根节点
    ACA_TYPE_BASE_ROOT = 'base_root'            # ACA类型：台基根节点
    ACA_TYPE_PLATFORM = 'platform'              # ACA类型：台基
    ACA_TYPE_STEP = 'step'                      # ACA类型：踏跺
    ACA_TYPE_FLOOR_ROOT = 'floor'               # ACA类型：柱网
    ACA_TYPE_PILLER = 'piller'                  # ACA类型：柱子
    ACA_TYPE_FANG = 'fang'                      # ACA类型：枋
    ACA_TYPE_WALL_ROOT = 'wall_root'            # ACA类型：装修布局，墙体的父节点
    ACA_TYPE_WALL = 'wall'                      # ACA类型：墙体
    ACA_TYPE_WALL_CHILD = 'wall_child'          # ACA类型：墙体子对象
    ACA_TYPE_DG_ROOT ='dg_root'                 # ACA类型：斗栱根节点
    ACA_TYPE_ROOF_ROOT ='roof_root'             # ACA类型：屋顶根节点
    ACA_TYPE_BEAM_ROOT = 'beam_root'            # ACA类型：梁架根节点
    ACA_TYPE_RAFTER_ROOT = 'rafter_root'        # ACA类型：椽望根节点
    ACA_TYPE_RAFTER_FB = 'rafter_fb'            # ACA类型：前后檐椽
    ACA_TYPE_RAFTER_LR = 'rafter_lr'            # ACA类型：两山檐椽
    ACA_TYPE_FLYRAFTER_FB = 'flyrafter_fb'      # 前后檐飞椽
    ACA_TYPE_FLYRAFTER_LR = 'flyrafter_lr'      # 两山飞椽
    ACA_TYPE_RAFTER_LKM_FB  = 'rafter_lkm_fb'      # 里口木-前后檐
    ACA_TYPE_RAFTER_LKM_LR  = 'rafter_lkm_lr'      # 里口木-两山
    ACA_TYPE_RAFTER_DLY_FB = 'rafter_dly_fb'       # 大连檐-前后
    ACA_TYPE_RAFTER_DLY_LR = 'rafter_dly_lr'       # 大连檐-两山
    ACA_TYPE_CORNER_BEAM = 'corner_beam'                # 大角梁
    ACA_TYPE_CORNER_BEAM_CHILD = 'corner_beam_child'    # 大角梁
    ACA_TYPE_CORNER_RAFTER_CURVE = 'corner_rafter_curve'         # 翼角椽定位线
    ACA_TYPE_CORNER_FLYRAFTER_CURVE = 'corner_flyfater_curve'    # 翘飞椽定位线
    ACA_TYPE_TILE_ROOT = 'tile_root'            # ACA类型：屋瓦层
    ACA_TYPE_ASSET_ROOT ='asset_root'           # ACA类型：斗栱根节点
    ACA_TYPE_YARDWALL = 'yard_wall'             # ACA类型：院墙
    ACA_WALLTYPE_WALL = 'wall'                  # 隔断属性-墙
    ACA_WALLTYPE_WINDOW = 'window'              # 隔断属性-槛窗
    ACA_WALLTYPE_DOOR = 'door'                  # 隔断属性-隔扇

    # 默认斗口
    DEFAULT_DK = 0.08   # 单位(m)

    # 屋顶类型，与面板的下拉框的值对应
    ROOF_WUDIAN = '1'
    ROOF_XIESHAN = '2'
    ROOF_XUANSHAN = '3'
    ROOF_YINGSHAN = '4'
    ROOF_LUDING = '5'
    ROOF_XUANSHAN_JUANPENG = '6'
    ROOF_YINGSHAN_JUANPENG = '7'
    ROOF_XIESHAN_JUANPENG = '8'

    # 台基
    PLATFORM_HEIGHT = 2         # 台基默认高度(PD)
    PLATFORM_EXTEND = 2.4       # 台基下檐出(PD)
    STEP_HEIGHT = 0.15          # 阶条石、上基石、中基石的高度(m)，刘大可P418
    STEP_SIDE_WIDTH = 0.15      # 垂带宽度占整个踏跺的比例
    # 规定为大式5寸，小式4寸，根据台明高度相除取整
    STEP_RATIO = 2.5
    STEP_WIDTH = STEP_HEIGHT*STEP_RATIO   # 上基石、中基石的宽度
    # 可取值范围较大，这里为了保持踏跺的斜率比例，统一取2.5倍，刘大可p416，p418
    GROUND_BORDER = 0.05        # 土衬的地坪露明和外沿金边(m)
    # 金边大式2寸，小式1.5寸，露明1~2寸，这里统一取了5cm，刘大可p377
    FIRST_LENGTH  = 0.3         # 好头石比例
    # 好头石长度取（尽间面阔+山出）*0.2，刘大可p377

    # 开间
    ROOM_X1 = 77    # 明间宽(DK)
    ROOM_X2 = 66    # 明间宽(DK)
    ROOM_X3 = 66    # 明间宽(DK)
    ROOM_X4 = 22    # 明间宽(DK)
    ROOM_Y1 = 44    # 明间宽(DK)
    ROOM_Y2 = 44    # 明间宽(DK)
    ROOM_Y3 = 22    # 明间宽(DK)

    # 柱子
    PILLER_D_EAVE = 6       # 檐柱直径(DK)
    PILLER_H_EAVE = 57      # 檐柱高(DK)
    PILLER_D_JIN = 6.6      # 金柱直径(DK)
    PILLER_CHILD = 5.2      # 蜀柱边长(DK)
    PILLERBASE_WIDTH = 2    # 柱顶石边长(PD)

    # 枋类
    EFANG_LARGE_H = 6       # 大额枋高(DK)
    EFANG_LARGE_Y = 4.8     # 大额枋厚(DK)
    EFANG_SMALL_H = 4       # 小额枋高(DK)
    EFANG_SMALL_Y = 3.2     # 小额枋厚(DK)
    HENGFANG_H = 3.6        # 金脊枋高(DK)
    HENGFANG_Y = 3          # 金脊枋厚(DK)
    PINGBANFANG_H = 2       # 平板枋高(DK)
    PINGBANFANG_Y = 3.5     # 平板枋宽(DK)
    BAWANGQUAN_H = 0.8      # 霸王拳高：额枋的4/5,参考马炳坚p163
    BAWANGQUAN_Y = 0.5      # 霸王拳厚：0.5D,参考马炳坚p163,本来是0.8额枋，但感觉太厚了
    BAWANGQUAN_L = 1        # 霸王拳长：1D,参考马炳坚p163
    CCFANG_H = 4            # 穿插枋高(DK)，马炳坚p167
    CCFANG_Y = 3.2          # 穿插枋厚(DK)

    # 垫板
    BOARD_YOUE_H = 2        # 由额垫板高(DK)
    BOARD_YOUE_Y = 1        # 由额垫板厚(DK)
    BOARD_HENG_H = 4.8      # 金脊桁檩垫板高(DK)
    BOARD_HENG_Y = 1.5      # 金脊桁檩垫板厚(DK)

    # 门窗（马炳坚数据）
    WALL_DEPTH = 1.5           # 槛墙厚度(PD)
    WALL_BOTTOM_RATE = 1/3      # 墙体下碱的高度比例
    WALL_BOTTOM_LIMIT = 1.5     # 墙体下碱限高(m)
    WALL_SHRINK = 0.015         # 墙体退花碱厚度(m)
    KAN_DOWN_HEIGHT = 0.8       # 下槛高度(PD)
    KAN_DOWN_DEPTH = 0.3       # 下槛深度(PD)，梁思成实际使用的为0.4
    KAN_MID_HEIGHT = 0.66       # 中槛高度(PD)(汤崇平书p20中定为0.64)
    KAN_MID_DEPTH = 0.3        # 中槛深度(PD)
    KAN_UP_HEIGHT = 0.5         # 上槛高度(PD)
    KAN_UP_DEPTH = 0.3         # 上槛深度(PD)
    KAN_WIND_HEIGHT = 0.5       # 风槛高度(PD)
    KAN_WIND_DEPTH = 0.3       # 风槛深度(PD)
    BAOKUANG_WIDTH = 0.66       # 抱框宽度(PD)
    BAOKUANG_DEPTH = 0.3       # 抱框深度(PD)
    BORDER_WIDTH = 0.2          # 边梃、抹头宽(PD)
    BORDER_DEPTH = BAOKUANG_DEPTH         # 边梃、抹头厚(PD)
    ZIBIAN_WIDTH = BORDER_WIDTH*0.5         # 仔边宽(PD)
    ZIBIAN_DEPTH = BORDER_WIDTH*0.5        # 仔边厚(PD)
    TABAN_DEPTH = 1.5          # 榻板宽(PD)
    TABAN_HEIGHT = 3/8          # 榻板高(PD)
    TABAN_EX = 0.1              # 榻板金边(米)
    GESHAN_GAP = 0.02           # 隔扇的间距/门缝(米)
    DOUGONG_SPAN = 11           # 斗栱攒距(DK)
    MENYIN_DEPTH = KAN_DOWN_DEPTH*1.8     # 门楹/窗楹厚(PD)
    MENYIN_HEIGHT = KAN_DOWN_HEIGHT*0.5     # 门楹/窗楹高(PD)
    MENYIN_WIDTH = MENYIN_DEPTH*2          # 门楹/窗楹宽(PD)
    MENZHOU_R = BORDER_WIDTH/2              # 门轴(PD)

    # 桁檩
    HENG_TIAOYAN_D = 4                  # 挑檐桁直径(DK)，梁思成数据
    HENG_COMMON_D = 4                   # 正心桁直径(DK)，梁思成数据
    HENG_EXTEND = HENG_COMMON_D * 2.6     # 桁檩出梢(DK)
    FUJIMU_D = 4                        # 伏脊木直径(DK)
    LIFT_RATIO_DEFAULT = [0.5,0.7,0.8,0.9]      # 梁思成图纸中采用的系数，可以进行比较
    LIFT_RATIO_BIG = [0.5,1,1.5,2]              # 尝试在亭子上使用
    LIFT_RATIO_SMALL = [0.5,0.65,0.75,0.9]      # 清工程做法则例的推荐系数
    JUANPENG_SPAN = HENG_COMMON_D * 3   # 卷棚顶的两根脊桁间距(DK)

    # 梁架
    BEAM_HEIGHT = 1.4       # 梁高(PD)
    BEAM_DEPTH = 1.1        # 梁厚(PD)
    BOFENG_WIDTH = 1.2      # 博缝板厚(DK)
    BOFENG_HEIGHT = 8       # 博缝板高(DK)
    XYB_WIDTH = 1.2         # 象眼板厚(DK)
    JIAOBEI_WIDTH = 2       # 角背厚度(DK)
    GABELBEAM_HEIGHT = 6.5  # 趴梁高(DK),马炳坚p9
    GABELBEAM_DEPTH = 5.2     # 趴梁厚(DK)

    # 椽飞类
    YANCHUAN_EX = 14            # 檐椽平出(DK)
    FLYRAFTER_EX = 7            # 飞椽平出(DK)
    YUANCHUAN_D = 1.5           # 圆椽直径(DK)
    FLYRAFTER_H = 1.5           # 飞椽、方椽高(DK)
    FLYRAFTER_Y = 1.5           # 飞椽、方椽厚(DK)
    WANGBAN_H = 0.5             # 望板厚(DK)
    LIKOUMU_H =  FLYRAFTER_H + WANGBAN_H        # 里口木高度(DK)，一飞椽+一望板
    LIKOUMU_Y = FLYRAFTER_H     # 里口木厚度(DK)
    # DALIANYAN_H = YUANCHUAN_D     # 大连檐(DK)，高同椽径
    DALIANYAN_H = YUANCHUAN_D*2     # 大连檐(DK)，叠加了“瓦口”高度（瓦口定义为1/2椽径或更高，见马炳坚书p179）
    DALIANYAN_Y = YUANCHUAN_D       # 大连檐(DK)，宽1.1-1.2椽径
    FLYRAFTER_HEAD_TILE_RATIO = 1/2.5        # 飞椽头身比，默认一飞二尾五
    QUETAI = YUANCHUAN_D*0.2        # 雀台长度(DK)，(通常1/5~1/3椽径)
    
    # 角梁
    JIAOLIANG_H = 4.5               # 角梁高(DK)，老角梁和子角梁
    JIAOLIANG_Y = 3                 # 角梁厚(DK)，老角梁和子角梁
    JIAOLIANG_WEI_KOUJIN = 0.2      # 角梁尾的扣金系数，则例没有明说，这个值越小，约陡峭
    JIAOLIANG_HEAD_YAJIN = 0.5      # 角梁头的压金系数，则例没有明说，这个值越小，约陡峭
    YOUQIANG_YAJIN = 1-JIAOLIANG_WEI_KOUJIN           #由戗压金系数

    # 其他
    OFFSET_ORIENTATION = 'GLOBAL'       # 'GLOBAL'  'LOCAL' #上下层叠构件的错开方式，一般绘图是垂直位移，但其实相对方向的位移更好看
    YIJIAOCHUAN_OFFSET = JIAOLIANG_Y/4  # 为了防止翼角椽与角梁打架，而做了一定的让渡
    CURVE_RESOLUTION = 500              # 曲线的精细度，在细分翼角椽坐标时提高精确度
    CORNER_RAFTER_START_SPREAD = 2      # 翼角椽尾散开的宽度，单位斗口
    BOOLEAN_TYPE = 'FAST'               # boolean.solver类型：FAST/EXACT
    DEFAULT_PILLER_HEIGHT = 0.8         # 默认柱高，取明间的0.8，马炳坚p4
    SANSHUI_WIDTH = 20                  # 散水宽度(DK)
    SANSHUI_HEIGHT = 0.02               # 散水高度(m)

    # 瓦作类
    # 屋瓦灰背层高度，用于计算铺瓦的高度
    # 一般20cm，北方官式建筑可以达到30cm
    # 其实也考虑了算法中从桁中线垂直向上找点，没有顺着坡面加斜，从而导致的误差
    ROOFMUD_H = 3.75        # 灰背层高度(DK)
    EAVETILE_EX = 2         # 瓦当、滴水出檐长度(DK)
    SHANQIANG_WIDTH = 9     # 山墙厚度(DK)，即1.5柱径
    SHANQIANG_EX = 11       # 山墙墀头延伸(DK)，约1.8柱径
    TILE_HEIGHT = 0.04      # 瓦层高度(米)，预估值
    JUANPENG_PUMP = 6       # 卷棚瓦作的囊(DK)，为了使屋顶更加圆润饱满
    JUANPENG_OVERLAP = 2    # 卷棚顶部瓦片的交叠(DK)

    # 导角尺度(m)
    BEVEL_EXHIGH = 0.04
    BEVEL_HIGH = 0.02
    BEVEL_LOW = 0.01
    BEVEL_EXLOW = 0.005

    def __setattr__(self, name, value):
        raise AttributeError("Can't modify constant values")

#瓦作类，以下数据来自刘大可《中国古建筑瓦石营法》p287
BANWA_SIZE = (          # 板瓦=========
   (43.2,35.2,7.29),    # 二样
   (40,32,6.63),        # 三样
   (38.4,30.4,6.3),     # 四样
   (36.8,27.2,5.64),    # 五样
   (33.6,25.6,5.3),     # 六样
   (32,22.4,4.64),      # 七样
   (30.4,20.8,4.31),    # 八样
   (28.8,19.2,3.98)     # 九样
) # 单位厘米，长、宽、囊（弧高，不含瓦厚)
TONGWA_SIZE = (         # 筒瓦==========
   (40,20.8,10.4),      # 二样
   (36.8,19.2,9.6),     # 三样
   (35.2,17.6,8.8),     # 四样
   (33.6,16,8),         # 五样
   (30.4,14.4,7.2),     # 六样
   (28.8,12.8,6.4),     # 七样
   (27.2,11.2,5.6),     # 八样
   (25.6,9.6,4.8)       # 九样
) # 单位厘米，长、宽、高
TILE_OVERLAP = 0.6      # 底瓦重叠4份，露出6份