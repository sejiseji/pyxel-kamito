import pyxel
import math as Math
import random as Random
from font.bdfrenderer import BDFRenderer
from GameObject import GameObject
from Door import Door
from Character import Character
from Jerry import Jerry
from Atari import Atari
from InventorySystem import InventorySystem

from Firework import Firework
from Lantan import Lantan
from Tree import Tree
from Grass import Grass
from PyxelExtended import PyxelExtended
from ParticleSystem import ParticleSystem
from WaterSurfaceEffect import WaterSurfaceEffect
from Point3D import Point3D
from Flower import Stem
from EllipticalOrbit import EllipticalOrbit
from EchoChamberVisualizer import EchoChamberVisualizer


 
######----------------------------------------------------
#PYXEL-COLOR
# 0 : BLACK   1 : NAVY       2 : PURPLE      3 : GREEN
# 4 : BROWN   5 : DEEPBLUE   6 : LIGHTBLUE   7 : WHITE
# 8 : RED     9 : ORANGE    10 : YELLOW     11 : LIME
#12 : CYAN   13 : GRAY      14 : PINK       15 : PEACH
######----------------------------------------------------
C_TITLE = "newgame"
###画面用設定値
C_MAX_DISPWORDS = 28 #画面幅300px＆umplus_j10rで１行２８文字
C_MSGWINDOW_WIDTH = 296 #8*37タイルマップ.
C_MSGWINDOW_HEIGHT = 64 #8*37タイルマップ.
###スクロール処理に必要な情報
#タイルマップ情報
C_WORLD_WIDTH = 600 #px
C_SCROLLON_AREA_WIDTH = 20
C_SCROLL_SPEED = 2
###シナリオ記録リスト
scenario = []
# 主要キャラクターリスト
characters = []
# 移動用ドアリスト
doors = []
# 背景用当たり判定および調査可能箇所リスト
ataris = []

#---------------------（20230815現在未使用）
# 調べられないモノリスト
non_checkables = []
# エフェクトリスト
effects = []
#---------------------（20230815現在未使用）

##スクロール値の記憶領域
scroll_memory = [0]
###Atariオブジェクト用パラメータ定数
C_VISIBLE = True
C_INVISIBLE = False
###gamestate.mode用定数
C_START = 0
C_PLAY  = 1
C_PAUSE = 2
C_MENU  = 3
C_END   = 4
###gamestate.scene用定数
C_SCENE_HOME  = 0
C_SCENE_MOON  = 1
C_SCENE_FIRE  = 2
C_SCENE_WATER = 3
C_SCENE_WOOD  = 4
C_SCENE_GOLD  = 5
C_SCENE_SOIL  = 6
C_SCENE_SUN   = 7
C_SCENE_END   = 8
C_SCENE_MENU  = 9

###パーティクルシステムで同時使用する最大数
C_MAX_PARTICLE_SYSTEM_FOR_WOOD = 4

###Characterオブジェクト用パラメータ定数
C_CHARA_GIRL     = 0
C_CHARA_WOLF     = 1
C_CHARA_BOY      = 2
C_CHARA_MANTA    = 3
C_CHARA_LEDY     = 4
C_CHARA_ROBOT    = 5
C_CHARA_BOOK     = 6
C_CHARA_RAT      = 7
C_CHARA_CAT      = 8
C_CHARA_TALISMAN = 9

#-----------------------------------------------
#プレイヤーの座標
player_xy = []
player_xylist = []


##########-----------------------------------------------------------------------
class GameState:
    def __init__(self):
        self.text_display = False
        self.mode = 0 
        self.scene = 0
        self.scenario = []
        self.scenario.append([0,0,0])

##########-----------------------------------------------------------------------
class MyApp:
    def __init__(self):
        pyxel.init(300, 300, title=C_TITLE, fps=40, quit_key=pyxel.KEY_NONE, capture_scale=4, capture_sec=10)
        pyxel.load("newgame.pyxres")  

        ###拡張機能のインスタンス生成
        self.ext = PyxelExtended()
        ###パーティクルシステムインスタンス用の配列を準備
        self.psys_instances = []
        ###WaterSurfaceEffectインスタンスの生成 for WATER-DOOR
        self.wse = WaterSurfaceEffect(0, 0, 600, 200)
        ###ゲームステート管理インスタンス
        self.gamestate = GameState()
        self.gamestate.mode = C_PLAY ##モードをPLAYに設定
        self.gamestate.scene = C_SCENE_HOME ##シーンをホームに設定

        ###変数宣言
        self.hensuSengen()
        ###フォント設定
        self.fontSetting()
        ###シーン用オブジェクトの生成
        self.generateObjects()

        ##InventorySystemインスタンスの生成
        self.invsys = InventorySystem()
        ###テスト：インベントリシステムに取得したアイテム名を渡す
        self.invsys.add_item('おにぎり')
        self.invsys.add_item('まんじゅう')
        self.invsys.add_item('クッキー')
        self.invsys.add_item('チョコレート')
        self.invsys.add_item('ぽんぽこペパロニピザ')
        self.invsys.add_valuable('金のコイン')
        self.invsys.add_valuable('囁く葉')
        self.invsys.add_valuable('冷たい小瓶')
        self.invsys.add_valuable('煤けた灰')
        self.invsys.add_valuable('歌う花')

        ###サウンド再生
        # self.playSounds()
        #game実行
        pyxel.run(self.update, self.draw)

    ####-------------------------------------------------------------------------------
    def hensuSengen(self):
        ###PLAYモード共通ロジック
        if (self.gamestate.mode == C_PLAY):
            ###キー操作用変数、固定値、カウンタ
            self.pressed_space_checking = False
            self.gamestate.text_display = False
            self.inptdelay_C = 8 #キー打鍵の瞬間の連続検知を防ぐ 
            self.inputdelay_cnt = self.inptdelay_C
            # スクロール制御用のキー入力方向捕捉変数
            self.scroll_direction = 0
            ###遠景背景ではない描画背景およびオブジェクト群のスクロール位置調整用変数
            self.scroll_x = 0
            ###オブジェクトリストのDraw順序組み換え用に使うワークリスト
            self.wk_objectDrawlistBasedAxisY = []
            ###取得したテキストセットを扱うための変数
            self.wk_textset = []
            # text分割処理にかかる変数
            self.text_divided = False # テキスト分割処置の完了済のフラグ
            self.wk_textset_divided = [] # 初期化。textDivideにて整形。
            self.wk_text_divided_remain = 0
            self.display_cnt = 0
            self.display_finished = False
            self.wk_text_disp_times = 1 ##分割編集済みのテキストを表示した回数の●回目初期値
            self.wk_textset3 = []
            ###テキストと同時に表示する顔グラ判別用ワーク
            self.talking_chara_no = 0
            ###話しかけた・調べた対象オブジェクトの向いている方向を変更する際、従前方向を記憶するwk変数
            self.checking_obj_direction = 4 ### リセット用初期値。４方向(0123:上下左右)のどれでもない
            self.position_buffer = 10 ###隣接状態と判定する境界エリア幅
            ###最も近いオブジェクトを格納する変数
            self.nearest_obj = None
            ###フキダシ表示用の座標変数
            self.fukidashi_nearest_obj_x = 0
            self.fukidashi_nearest_obj_y = 0

            ###テキスト表示用変数
            self.hint_text = ""
            self.hint_text_divided = []

        ### 冒頭
        if(self.gamestate.scene == C_SCENE_HOME):
            # 各レイヤーのスクロール速度を設定
            self.scroll_speeds = [0.1, 0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 1.0, 1.2]
            # 各レイヤーのスクロール位置を初期化
            self.scroll_positions = [0.1 for _ in range(9)]

            ###SCENE:MOON用
            self.fireworks = []

            ###SCENE:FIRE用
            self.points3d = []
            self.lantans = []

            ###SCENE:WOOD用
            self.trees = []
            self.grasses =[]
            self.flowers = []

            ###SCENE:GOLD用
            self.elliptical_orbits = []
            self.segments = []

            ###テスト用(パーティクルシステム)
            self.timer_for_psys = 0

            ###SCENE:WATER用
            # 波紋描画用カウンタ。波紋が広がる周期となる。バラバラにすることで、波紋が同時に広がらないようにする。
            self.rain_draw_counter = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 15, 14, 13, 12, 11]
            self.rainAxisColorSengen() # 各波紋描画用変数の宣言
            # 足跡波紋描画用カウンタ。波紋が広がる周期となる。バラバラにすることで、波紋の広がりを段階的にする。
            # self.footprint_draw_counter = [20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
            self.footprint_draw_counter = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
            self.footprintsAxisColorSengen() # 各波紋描画用変数の宣言


    def fontSetting(self):
        ###モード・シーン共通
        # ビットマップフォントの表示。BDFRendererはpyxel.init()後に呼び出す.
        self.bdf1 = BDFRenderer("font/umplus_j10r.bdf")
        self.bdf2 = BDFRenderer("font/umplus_j12r.bdf")

    def generateObjects(self):
        ###PLAYモード
        if (self.gamestate.mode == C_PLAY):
            ###HOMEシーン
            if (self.gamestate.scene == C_SCENE_HOME):
                self.generateUniqueObjectsInHome()
            ###DOOR別シーン
            if (self.gamestate.scene == C_SCENE_MOON) or \
                (self.gamestate.scene == C_SCENE_FIRE) or \
                (self.gamestate.scene == C_SCENE_WATER) or \
                (self.gamestate.scene == C_SCENE_WOOD) or \
                (self.gamestate.scene == C_SCENE_GOLD) or \
                (self.gamestate.scene == C_SCENE_SOIL) or \
                (self.gamestate.scene == C_SCENE_SUN):
                    #プレイヤーオブジェクトを生成
                    self.player = Character(1,0,150,3,True)
                    characters.append(self.player) ###キャラクター・オブジェクトリストに追加
                    ### 画面上部から移動可能領域までのマージンを再設定
                    # if (self.gamestate.scene in(C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN)):
                    #     self.player.able_moving_top = 16 * 2 - 8
                    ### ドアオブジェクトの生成
                    if (self.gamestate.scene in(C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN)):
                        self.generateDoor()
                    ###球内をさまよう光点の追加
                    if (self.gamestate.scene == C_SCENE_FIRE):
                        self.generateUniqueObjectsInFire()
                    ###木オブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_WOOD):
                        self.generateUniqueObjectsInWood()
                    ###象徴するオブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_GOLD):
                        self.generateUniqueObjectsInGold()

    def generateUniqueObjectsInHome(self):
        #プレイヤーオブジェクトを生成
        self.player = Character(1,0,150,3,True)
        characters.append(self.player) ###キャラクター・オブジェクトリストに追加
        #キャラクターオブジェクトを生成
        self.charactor01 = Character(0,200,150,2,False)
        characters.append(self.charactor01) ###キャラクター・オブジェクトリストに追加
        ###Doorオブジェクトを生成
        self.generateDoor()
        ###くらげ生成
        self.jerry01 = Jerry(128,116)
        characters.append(self.jerry01) ###キャラクター・オブジェクトリストに追加
        ###背景用当たり判定インスタンス群生成
        self.atari001 = Atari(116, 8 * 17 -5, 0, C_SCENE_HOME, C_VISIBLE) ## 横断歩道の歩行者用信号機
        self.atari002 = Atari(333, 8 * 17 -5, 1, C_SCENE_HOME, C_VISIBLE) ## バス停
        self.atari003 = Atari(274, 8 * 17 -5, 2, C_SCENE_HOME, C_VISIBLE) ## 看板（小）
        self.atari004 = Atari(450, 220,       3, C_SCENE_HOME, C_INVISIBLE) ## 猫
        ###背景用当たり判定リストに追加
        ataris.append(self.atari001)
        ataris.append(self.atari002)
        ataris.append(self.atari003)
        ataris.append(self.atari004)

    # def generateUniqueObjectsInMoon(self):
    
    def generateUniqueObjectsInFire(self):
        ###蛍オブジェクトを生成
        self.points3d.append(Point3D(center_x=150, center_y=150, center_z=0, radius=100, num_points=40, speed_low=2, speed_high=4, life_low=100, life_high=300, randini=True, pallete=0, cacheflg=False, scene=self.gamestate.scene))

        ###ランタンオブジェクトの生成
        lantan_num = 15
        for _ in range(lantan_num):
            lantan = Lantan(x=Random.randint(100,550), y=Random.randint(20,240), speed=1)
            self.lantans.append(lantan)
        ###各ランタン用のパーティクルシステムを生成
        for _ in range(len(self.lantans)):
            self.psys_instances.append(ParticleSystem())
        ###各ランタン用のパーティクルシステムを初期化
        for i in range(len(self.lantans)):
            self.psys_instances[i].activate(
                active_duration=6000, spawn_interval=5, total_spawns=4000,
                #particle放射の中心座標は、対応させる灯籠blt画像内の光源位置を指定
                x=self.lantans[i].position_x + 4, y=self.lantans[i].position_y - 8,
                width=0, height=0, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
                num_particles=5, ##一度に放射するパーティクルの数
                pattern=0, ##放射particle形状の指定(0:Dot型)
                size=1, ##Dot型以外で使用されるパーティクルサイズ
                color=Random.choice([9,10,7]), ##particleの色
                speed_range=1
            )
        ###psys紐づけ済みフラグをTrueに
        for i in range(len(self.lantans)):
            self.lantans[i].is_attached = True

    # def generateUniqueObjectsInWater(self):
    
    def generateUniqueObjectsInWood(self):
        ###木オブジェクトを生成 : x=50, y=100, 葉の数=90, 茂みの半径=30
        self.tree01 = Tree(150, 100, 110, 30)
        self.tree01.update() # 葉の座標を1発目更新
        self.trees.append(self.tree01)
        self.tree02 = Tree(250, 100, 130, 40)
        self.tree02.update() # 葉の座標を1発目更新
        self.trees.append(self.tree02)
        ###背景用当たり判定インスタンス群
        self.atari005 = Atari(160, 163, 4, C_SCENE_WOOD, C_INVISIBLE) ## 木の幹01
        self.atari006 = Atari(260, 163, 5, C_SCENE_WOOD, C_INVISIBLE) ## 木の幹02
        ###背景用当たり判定リストに追加
        ataris.append(self.atari005)
        ataris.append(self.atari006)
        ###草オブジェクトを生成 : x=10, y=230, 距離=150, 最小の高さ=20, 最大の高さ=50, 草の本数=30
        self.grass01 = Grass(0, 240, 600, 20, 60, 140)
        self.grasses.append(self.grass01)
        ###花オブジェクトを生成
        # Stemをランダムな位置に生成
        for _ in range(5):
            x = Random.randint(10, 550)  # X座標を10から550の間でランダムに選択
            height = Random.randint(40, 60)  # 高さを40から60の間でランダムに選択
            flower = Stem(x, 240, height)
            flower.update_tip() # 花の先端の座標を更新
            self.flowers.append(flower)
            


    def generateUniqueObjectsInGold(self):
        self.visualizer  = EchoChamberVisualizer(x_center=65,  y_center=200, r=30, treeangle=30, max_depth=10, polygon_sides=6, external=False)
        self.visualizer2 = EchoChamberVisualizer(x_center=180, y_center=200, r=30, treeangle=30, max_depth=10, polygon_sides=8, external=False)
        self.visualizer3 = EchoChamberVisualizer(x_center=100, y_center= 80, r=30, treeangle=30, max_depth=10, polygon_sides=10, external=False)
        self.segments.append(self.visualizer)
        self.segments.append(self.visualizer2)
        self.segments.append(self.visualizer3)

        point_a_x, point_a_y = 0, 0  # This is just the center of the screen
        point_b = EllipticalOrbit(point_a_x, point_a_y, 40, 30, Math.radians(45), 0.03, pyxel.COLOR_RED)
        point_c = EllipticalOrbit(point_b.x, point_b.y, 20, 20, 0, 0.05, pyxel.COLOR_GREEN, parent=point_b)
        self.elliptical_orbits.append(point_c)
        self.elliptical_orbits.append(point_b)
       
    # def generateUniqueObjectsInSoil(self):

    # def generateUniqueObjectsInSun(self):

    def deleteObjectsDependingOnScene(self):
        ###PLAYモードにおけるシーン別オブジェクト削除
        if (self.gamestate.mode == C_PLAY):
            if (self.gamestate.scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_FIRE ,C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN)):
                ###Doorオブジェクトを削除
                doors.clear()
                ###キャラクターオブジェクトを削除
                characters.clear()
                ###背景用当たり判定リストを削除
                ataris.clear()
            if (self.gamestate.scene == C_SCENE_FIRE):
                self.points3d.clear()
            if (self.gamestate.scene == C_SCENE_WOOD):
                self.trees.clear()
                self.grasses.clear()
                self.flowers.clear()
            if (self.gamestate.scene == C_SCENE_GOLD):
                self.elliptical_orbits.clear()
                self.segments.clear()
            

    def generateDoor(self):
        if (self.gamestate.mode == C_PLAY):
            if (self.gamestate.scene == C_SCENE_HOME):
                ###Doorオブジェクトを生成
                self.door01 = Door( 50,99,0,0)
                self.door02 = Door( 196 -35,99,1,0)
                self.door03 = Door( 246 -35,99,2,0)
                self.door04 = Door( 296 -3,99,3,0)
                self.door05 = Door( 396,99,4,0)
                self.door06 = Door( 446,99,5,0)
                self.door07 = Door( 496,99,6,0)
                self.door08 = Door( 546,99,7,0)
                ###Doorオブジェクトリストに追加
                doors.append(self.door01)
                doors.append(self.door02)
                doors.append(self.door03)
                doors.append(self.door04)
                doors.append(self.door05)
                doors.append(self.door06)
                doors.append(self.door07)
                doors.append(self.door08)
            ###HOMEへのドアを設置
            # if (self.gamestate.scene == C_SCENE_MOON):
            if (self.gamestate.scene in(C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD)):
                ###Doorオブジェクトを生成
                self.door01 = Door(450,94,0,3)
                ###Doorオブジェクトリストに追加
                doors.append(self.door01)
            # if (self.gamestate.scene in(C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_GOLD, C_SCENE_WOOD, C_SCENE_SOIL, C_SCENE_SUN)):
            if (self.gamestate.scene in(C_SCENE_SOIL, C_SCENE_SUN)):
                ###Doorオブジェクトを生成
                self.door01 = Door(450,94,0,3)
                ###Doorオブジェクトリストに追加
                doors.append(self.door01)

    def scrollMemory(self,scroll):
        ###クラス内変数としてスクロール値を記録する
        if(len(scroll_memory) > 0):
            scroll_memory.pop(0)    
        scroll_memory.append(scroll)

    def update(self):
        ###PLAYモード共通
        if (self.gamestate.mode == C_PLAY):
            ### gamestate更新
            self.gamestate.scenario[0][0] = self.gamestate.scene

            ### 退避済スクロール値を取出して扱う
            self.scroll_x = scroll_memory[0]

            ###拡張機能のupdate
            self.ext.update_angle()

            ###パーティクルシステムインスタンスのupdate
            ###psys_instancesがあれば、その数だけupdateを実行する
            if len(self.psys_instances) > 0:
                for psys in self.psys_instances:
                    psys.update_angle()

            ###gamestate更新
            self.gamestate.text_display = self.pressed_space_checking
            self.player.env_text_displaying = self.pressed_space_checking

            ###space打鍵によるチェックが走っていないとき（キャラ操作可能時）に左右キーでのスクロールが有効化される
            if not(self.pressed_space_checking):
                # 左パララックススクロール背景のため、左右キーの入力を読み取り、その方向を更新。
                ## ただし、ほかキー入力が同時にあった場合は移動を行わず立ち止まって向きを変えるキャラクタ操作仕様に合わせるため、該当時はスクロール方向を0にする
                if (0 < self.player.x <= (300 - self.player.width)) and (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A)):
                    self.scroll_direction = -1
                    if (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z)):
                        self.scroll_direction = 0
                        self.player.moving = False
                elif (0 <= self.player.x < (300 - self.player.width)) and (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S)):
                    self.scroll_direction = 1
                    if (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z)):
                        self.scroll_direction = 0
                        self.player.moving = False
                else:
                    self.scroll_direction = 0
                    self.player.moving = False

            #有効な左右スクロール方向に応じてX方向スクロール位置を加算・減算する
            self.scroll_distance = 0
            if self.scroll_direction == 1:
                self.scroll_distance += C_SCROLL_SPEED
            if self.scroll_direction == -1:
                self.scroll_distance -= C_SCROLL_SPEED
            self.scroll_x += self.scroll_distance  # self.scroll_xはスクロールの累計距離として利用する
            ###スクロール値をオブジェクトに適用
            self.affectScroll(self.scroll_x)
            for baseelem in characters:
                baseelem.update()
                ###衝突判定とスクロールキャンセル
                if baseelem.is_playing:
                    self.playerUpdateColisionCheckAndScrollCancel(baseelem,characters)
                    self.playerUpdateColisionCheckAndScrollCancel(baseelem,doors)
                    self.playerUpdateColisionCheckAndScrollCancel(baseelem,ataris)
                    self.playerUpdateColisionCheckAndScrollCancel(baseelem,self.trees)
            ### 各背景レイヤーのスクロール位置を更新
            for i in range(9):
                self.scroll_positions[i] += self.scroll_direction * self.scroll_speeds[i]

            ###プレーヤーオブジェクトとその他のcheckable（＝調べることが可能な）オブジェクト群の位置関係を確認し、
            ###最も近い位置にあるcheckableオブジェクトとの向きを含む隣接状態を捕捉していく。
            self.updateObjectsPositionCheck()

            ###入力検知の遅延用カウンタ（ボタン打鍵の瞬間の連続検知を防ぐ）
            if(self.inputdelay_cnt > 0):
                self.inputdelay_cnt -= 1
            ###スクロールが働いていないときだけボタン入力を検知する
            if((self.inputdelay_cnt == 0)and(self.scroll_direction == 0)):
                ###ボタン入力の検知
                self.updateBtnInputCheck_SPACE()
            ###表示が必要なテキスト情報を保持していた場合、表示に必要な分割処理を行う。
            self.updateTextDivide()

            #最終順序リストをcharacter
            self.wk_objectDrawlistBasedAxisY = characters
            #並び替え
            self.wk_objectDrawlistBasedAxisY.sort(key=lambda obj: obj.position_y)

            ###PLAYモード最後の処理
            ###scroll値を退避
            self.scrollMemory(self.scroll_x)

            if (self.gamestate.scene == C_SCENE_MOON):
                self.updateMoonScene()

            elif (self.gamestate.scene == C_SCENE_FIRE):
                self.updateFireScene()

            elif (self.gamestate.scene == C_SCENE_WATER):
                self.updateWaterScene()

            elif (self.gamestate.scene == C_SCENE_WOOD):
                self.updateWoodScene()

            elif (self.gamestate.scene == C_SCENE_GOLD):
                self.updateGoldScene()

        ###MENUモード共通 ================================
        if (self.gamestate.mode == C_MENU):
            # self.invsys.update()                    
            ###入力検知の遅延用カウンタ（ボタン打鍵の瞬間の連続検知を防ぐ）
            if(self.inputdelay_cnt > 0):
                self.inputdelay_cnt -= 1
            ###スクロールが働いていないときだけボタン入力を検知する
            if((self.inputdelay_cnt == 0)and(self.scroll_direction == 0)):
                ###ボタン入力の検知
                self.updateBtnInputCheck_SPACE()
                
    def updateMoonScene(self):
        ###fireworksの中でlifeが0になったものを削除
        for firework in self.fireworks:
            if firework.life == 0:
                self.fireworks.remove(firework)
        ###SPACEまたはAボタンが押されたら花火を打ち上げる
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            x, y = Random.randint(30, 570 - 30), 170
            self.fireworks.append(Firework(x -scroll_memory[0], y))

    def updateFireScene(self):
        ###ランタンの数をチェック
        chk_lantan_numbfr = len(self.lantans)
        ###ランタンが画面外（x=-1）に出たらランタンとそれに対応するpsysを削除
        for i in range(len(self.lantans) - 1, -1, -1):  # 逆順で反復処理
            if self.lantans[i].x + 16 < -1:
                self.lantans.pop(i)
                self.psys_instances.pop(i)
        chk_lantan_numaft = len(self.lantans)
        ###ランタンの数が減っていたら、ランタンを補充
        if chk_lantan_numbfr > chk_lantan_numaft:         
            ###Lantanを画面右端に補充
            self.lantans.append(Lantan(x= 2 * pyxel.width + 16, y= Random.randint(0, 200), speed=1))
            ###psysを補充
            self.psys_instances.append(ParticleSystem())
            ###psysを初期化
            self.psys_instances[-1].activate(
                active_duration=6000, spawn_interval=5, total_spawns=4000,
                x=self.lantans[-1].position_x + 4, y=self.lantans[-1].position_y - 8,
                width=0, height=0, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
                num_particles=5, ##一度に放射するパーティクルの数
                pattern=0, ##放射particle形状の指定(0:Dot型)
                size=1, ##Dot型以外で使用されるパーティクルサイズ
                color=Random.choice([9,10]), ##particleの色
                speed_range=1
            )
        ###ランタンとpsysを更新
        if (len(self.lantans) > 0) and (len(self.lantans) == len(self.psys_instances)):
            for i in range(len(self.lantans)):
                if pyxel.frame_count % 3 == 0:
                    self.lantans[i].update() # ランタンを更新
                    self.psys_instances[i].x = self.lantans[i].position_x -4# psysのx座標をランタンのx座標に合わせる
        self.updateParticleSystems(scroll_x=0)

        ###光の座標群を順にチェックして、中身が空になったものを削除する
        for point3d in self.points3d:
            if len(point3d.points) == 0:
                self.points3d.remove(point3d)
        ### Vキーを押すと、光の座標群を生成する
        if pyxel.btnp(pyxel.KEY_V):
            self.points3d.append(Point3D(center_x=self.player.x +8 +scroll_memory[0], center_y=self.player.y +8, center_z=0, radius=50, num_points=20, speed_low=2, speed_high=4, life_low=50, life_high=100, randini=False, pallete=Random.choice([0, 1, 2]), cacheflg=False, scene=self.gamestate.scene))
        # 光の座標群を更新
        if pyxel.frame_count % 5 == 0:
            for point3d in self.points3d:
                point3d.update()
        


    def updateWaterScene(self):
        ###WaterSurfaceEffectインスタンスのupdate
        self.wse.update()
    
    def updateWoodScene(self):

        ###木オブジェクトのplayerに対しての前後状態をupdate
        for tree in self.trees:
            if tree.position_y < self.player.position_y:
                tree.position_back = True
                tree.position_front = False
            else:
                tree.position_back = False
                tree.position_front = True

        if pyxel.frame_count % 15 == 0:
            # 各Treeオブジェクトのupdateメソッドを呼び出す
            for tree in self.trees:
                tree.update(0,300)
                # tree.update(0 +scroll_memory[0],300 +scroll_memory[0])
        ###草grassesをupdate
        if pyxel.frame_count % 10 == 0:
            for grass in self.grasses:
                grass.update(0 +scroll_memory[0],300 +scroll_memory[0])
        ###花オブジェクトをupdate
        if pyxel.frame_count % 10 == 0:
            for flower in self.flowers:
                flower.update_tip(0 +scroll_memory[0],300 +scroll_memory[0])
        ###particlesystemのupdate
        self.updateParticleSystems(scroll_x=0)
    
    def updateGoldScene(self):
        # オブジェクトのupdateメソッドを呼び出す
        for point in reversed(self.elliptical_orbits):
            point.update()
        # 新しいエコーチャンバーのセグメントを追加する
        new_segments = []
        for segment in self.segments:
            if segment.x_new != 0:
                new_segments.append(EchoChamberVisualizer(x_center=segment.x_new, y_center=segment.y_new, r=segment.r_new, treeangle=segment.tree_angle_new, max_depth=segment.max_depth_new, polygon_sides=segment.polygon_sides_new, external=segment.external_new))
        self.segments.extend(new_segments)
        # 不要なセグメントを削除する
        self.segments = [segment for segment in self.segments if segment.x_new == 0]
        ###echo chamberのupdate
        if len(self.segments) > 0:
            for segment in self.segments:
                segment.update()

    # def updateSoilScene(self):

    # def updateSunScene(self):

    def updateParticleSystems(self,scroll_x):
        #####テスト（パーティクルシステム）
        self.timer_for_psys += 1
        if self.gamestate.scene == C_SCENE_WOOD: ###WOODシーンのみ
            ###Vキーが押されたらパーティクルシステムを起動
            if pyxel.btnp(pyxel.KEY_V):
                ##パーティクルシステムのインスタンスを生成
                for _ in range(C_MAX_PARTICLE_SYSTEM_FOR_WOOD): ###必要数を指定
                    self.psys_instances.append(ParticleSystem())
                ###パーティクルシステムを起動
                self.psys_instances[0].activate(active_duration=400, spawn_interval=20, total_spawns=60 ,x=80,  y=140, width=50, height=50, num_particles=5, pattern=0, size=1, color=pyxel.COLOR_WHITE,  speed_range=0, direction=9)
                self.psys_instances[1].activate(active_duration=400, spawn_interval=20, total_spawns=60 ,x=90,  y=140, width=50, height=50, num_particles=5, pattern=1, size=2, color=pyxel.COLOR_CYAN,   speed_range=1, direction=11)
                self.psys_instances[2].activate(active_duration=400, spawn_interval=20, total_spawns=60 ,x=100, y=140, width=50, height=50, num_particles=5, pattern=2, size=3, color=pyxel.COLOR_PINK,   speed_range=2, direction=1)
                self.psys_instances[3].activate(active_duration=400, spawn_interval=20, total_spawns=60 ,x=110, y=140, width=50, height=50, num_particles=5, pattern=3, size=4, color=pyxel.COLOR_YELLOW, speed_range=3, direction=3)
        ###非アクティブなパーティクルシステムがあれば、除去する
        if len(self.psys_instances) > 0:
            for psys in self.psys_instances:
                if not(psys.is_active):
                    self.psys_instances.remove(psys)
        ###パーティクルシステムのupdateを実行し、各システム毎のパーティクルの位置を更新
        ##self.psys_instancesが空でなければ、updateを実行する
        if len(self.psys_instances) > 0:
            for psys in self.psys_instances:
                psys.update_particles(scroll_x)

    def affectScroll(self,scroll_diff):
        if (self.gamestate.mode == C_PLAY):
            if (self.gamestate.scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_WATER, C_SCENE_WOOD)):
                for obj in self.wk_objectDrawlistBasedAxisY:
                    ###playingではないオブジェクトのx座標をスクロール値でずらして更新
                    if not(obj.is_playing) :
                        obj.x -= scroll_diff

            ###HOMEおよびDoor先の共通処理：基本オブジェクト群のスクロール適用処理
            if (self.gamestate.scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN)):
                ### Doorオブジェクトの位置をスクロール値でずらして更新
                for obj in doors:
                    obj.x -= scroll_diff
                ### Atariオブジェクトの位置をスクロール値でずらして更新
                for obj in ataris:
                    obj.x -= scroll_diff
                ### Treeオブジェクトの位置をスクロール値でずらして更新
                for obj in self.trees:
                    obj.x -= scroll_diff
                    for leaf in obj.leaves:
                        leaf = leaf[0] - scroll_diff, leaf[1]
                ### Doorオブジェクトの更新実行
                for obj in doors:
                    obj.update()
                ### Atariオブジェクトの更新実行
                for obj in ataris:
                    obj.update()

            if (self.gamestate.scene == C_SCENE_MOON): ###MOON固有の処理
                ### Fireworkオブジェクトの更新実行
                for obj in self.fireworks:
                    obj.update()

    def playerUpdateColisionCheckAndScrollCancel(self,baseelem,list):
        # 引数のリストのオブジェクト群と、playingCharacterが衝突していないかをチェック。
        # 衝突した場合はシーン上のすべてのオブジェクトのスクロール適用計算を順に戻し、背景パララックス用演算値を0に戻す。
        for elem in list:
            if not(elem.is_playing) and baseelem.is_colliding_with(elem):
            # 衝突したら
                # プレイヤーの移動をキャンセルする
                baseelem.cancel_move()

                ###Doorオブジェクトのx座標スクロール加味を戻す
                for obj in doors:
                    obj.x += self.scroll_distance
                ###Atariオブジェクトのx座標スクロール加味を戻す
                for obj in ataris:
                    obj.x += self.scroll_distance
                ###Treeオブジェクトのx座標スクロール加味を戻す
                for obj in self.trees:
                    obj.x += self.scroll_distance
                    for leaf in obj.leaves:
                        leaf = leaf[0] + self.scroll_distance, leaf[1]


                ###Characterオブジェクト
                for obj in self.wk_objectDrawlistBasedAxisY:
                    ###playingではないオブジェクトのx座標のスクロール加味を戻す
                    if not(obj.is_playing) :
                        obj.x += self.scroll_distance

                ###スクロール背景用　のX軸方向オフセットの増分をキャンセル
                if (self.scroll_direction == 1):
                    self.scroll_x -= C_SCROLL_SPEED
                if (self.scroll_direction == -1):
                    self.scroll_x += C_SCROLL_SPEED

                # 背景のパララックススクロールの方向を０へ
                self.scroll_direction = 0

    def draw(self):
        if(self.gamestate.mode == C_PLAY):
            ###スクロール値を取得し直す
            self.scroll_x = scroll_memory[0]
            wk_player_moving = self.player.moving
            ###背景描画
            self.drawBG()
            ###オブジェクト描画
            self.drawObjects()
            ###デモタイトル表示
            pyxel.rect(6, 2, 38, 25, 1)
            self.bdf2.draw_text(10, 2, self.getModeName(), 7) 
            self.bdf2.draw_text(10,14, self.getSceneName(), 7) 
            ###updateで並び替えたオブジェクトリストを順にdrawする
            for obj in self.wk_objectDrawlistBasedAxisY:
                ###描画後
                obj.draw()
            ###特定のオブジェクト種別に対しplayer上にフキダシを表示する
            if self.nearest_obj.__class__.__name__ in("Character", "Atari", "Door", "Jerry"):
                if self.nearest_obj.flg_reaction:
                    ###フキダシ表示
                    pyxel.blt(self.player.x, self.player.y -14, 0, 72, 0, 16, 16, 3)
                    if self.nearest_obj.__class__.__name__ in("Atari"):
                        ###フキダシ内のアイコン表示（？マーク）
                        # pyxel.blt(self.player.x +5, self.player.y -12, 0, 72, 16, 7, 10, 3)
                        pyxel.blt(self.player.x +5, self.player.y -12, 0, 72, 16 + 10 * (pyxel.frame_count // 6 % 3), 7, 10, 3)
                    if self.nearest_obj.__class__.__name__ in("Character", "Door", "Jerry"):
                        ###フキダシ内のアイコン表示（！マーク）
                        # pyxel.blt(self.player.x +6, self.player.y -12, 0, 79, 16, 4, 10, 3)
                        pyxel.blt(self.player.x +6, self.player.y -12, 0, 79, 16 + 10 * (pyxel.frame_count // 6 % 3), 4, 10, 3)

            ###前景＋メニューエリアの描画
            self.drawFT(wk_player_moving)
            ###スペースキー打鍵chkフラグON状態のときに、捕捉中のdisptimesに分けて、メッセージを画面表示する。
            self.drawMessageAndWindow()
            for obj in self.wk_objectDrawlistBasedAxisY:
                if not(obj.is_playing) :
                    ##本来のスクロールを加味しない位置に戻す
                    obj.x += self.scroll_x

        elif(self.gamestate.mode == C_MENU):
            ###Menu画面の描画
            self.drawMenu()

            ###デモタイトル表示
            pyxel.rect(6, 2, 38, 25, 1)
            self.bdf2.draw_text(10, 2, self.getModeName(), 7) 
            self.bdf2.draw_text(10,14, self.getSceneName(), 7)
            

    def drawMenu(self):
    ###Menu画面の描画
        ###下画面エリアを黒背景で塗りつぶす
        pyxel.rect(0, 235, 300, 65, 0)
        ###黒背景
        pyxel.rect(20,  20, 260, 210, 0)
        ###白枠線
        pyxel.rectb(20,  20, 260, 210, 7)
        ###仕切り縦線
        pyxel.line(180,  20, 180, 229, 7)
        ###仕切り線横（右側）
        pyxel.line(180, 140, 279, 140, 7)            
        ###インベントリシステム描画
        self.invsys.draw()

        ###ステータスとヒントのエリア
        status_x = 185  # ステータス表示の開始X座標
        status_y = 25   # ステータス表示の開始Y座標
        hint_y = 144    # ヒント表示の開始Y座標
        
        # 現在のgamestateに応じてステータスを表示
        # status_text = "Status: Not Bad"
        ###体力の表示
        status_hp = str(self.player.hp) + " / " + str(self.player.max_hp)
        color_hp = 7
        if self.player.hp == self.player.max_hp:
            color_hp = 3
        elif 1 < self.player.hp < 6:
            color_hp = 10
        elif self.player.hp == 1:
            color_hp = 8
        self.bdf1.draw_text(status_x, status_y, status_hp, color_hp)
        ###気力の表示
        status_mp = str(self.player.mp) + " / " + str(self.player.max_mp)
        color_mp = 7
        if self.player.mp == self.player.max_mp:
            color_mp = 3
        elif 1 < self.player.mp < 3:
            color_mp = 10
        elif self.player.mp == 1:
            color_mp = 8
        self.bdf1.draw_text(status_x + 60, status_y, status_mp, color_mp)

        # pyxel.text(status_x, status_y, status_text, 7)  # 白文字で表示
        ###pyxelExtendedの円形クリッピングでCharactererの画像を表示
        self.ext.draw_clipped_circle(status_x, status_y + 14, 0, 16, 0, -16, 16, 8)
        
        ###キャラクター画像の下に、選択中アイテムに対しての感想文を表示
        # 現在のgamestateに応じたアイテムへの感想を取得
        scenario, branch = self.gamestate.scenario[0][1], self.gamestate.scenario[0][2]
        self.thought_text = self.invsys.getThoughtOnMenu(scenario, branch, self.player.character_no)
        ###感想文を分割する
        self.thought_text_divided = []
        ###テキストの分割（結果セットに連続appendする）
        self.textDivide(self.thought_text, self.thought_text_divided, 9)
        ###分割されたテキストを順に表示する
        for i in range(len(self.thought_text_divided)):
            self.bdf1.draw_text(status_x, status_y + 34 + (i * 12), self.thought_text_divided[i], 7)  # 白文字で表示

        # 現在のgamestateに応じてヒントを表示
        scene, scenario, branch = self.gamestate.scenario[0][0], self.gamestate.scenario[0][1], self.gamestate.scenario[0][2]
        self.hint_text = self.getHintOnMenu(scene, scenario, branch, self.player)
        ###ヒントテキストを分割する
        self.hint_text_divided = []
        ###テキストの分割（結果セットに連続appendする）
        self.textDivide(self.hint_text, self.hint_text_divided, 9)
        ###分割されたテキストを順に表示する
        for i in range(len(self.hint_text_divided)):
            self.bdf1.draw_text(status_x, hint_y + (i * 12), self.hint_text_divided[i], 7)  # 白文字で表示
        
        ###選択中アイテムの説明文を表示
        ###取得した説明文を分割する
        item_description = [self.invsys.get_selected_description()]
        item_description_divided = []
        ###テキストの分割（結果セットに連続appendする）
        self.textDivide(item_description, item_description_divided, 28)
        ###分割されたテキストを順に表示する
        for i in range(len(item_description_divided)):
            self.bdf1.draw_text(10, 250 + (i * 12), item_description_divided[i], 7)

        # self.bdf1.draw_text(10, 250, self.invsys.get_selected_item_description(), 7)  # 白文字で表示

        ###アイテム使用時のサブウィンドウを表示
        self.invsys.drawSubWindow()

    def getHintOnMenu(self, scene, scenario, branch, player): ###最大63文字までのヒントテキストを返す
        hint_text = ""
        if scenario == 0:
            if branch == 0:
                    if scene == C_SCENE_HOME:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["ここはどこだろうか？ボロボロに朽ちた道路と広大な砂浜がはるか彼方まで続いて見える。周辺を調べないことには何も分かりそうにない。"]
                    elif scene == C_SCENE_MOON:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["打ち上がる花火が眩しい。ここが何処なのかわかる気がしない。"]
                    elif scene == C_SCENE_FIRE:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["触れられない灯籠が、足元を流れていく。何処か懐かしさを覚える風景だ。"]
                    elif scene == C_SCENE_WATER:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["降りしきる雨が全身を濡らしている。部屋は水浸しだ。排水が働いているのか、水面が足元から上がってくる様子はない。"]
                    elif scene == C_SCENE_WOOD:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["この部屋は常に風が吹いているようだ。芳しい花々、瑞々しい木々の香りが届く。"]
                    elif scene == C_SCENE_GOLD:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["ひんやりとして肌寒い。何かの形をした多角形が空間を漂っている。"]
                    elif scene == C_SCENE_SOIL:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["物悲しい雰囲気の空間だ。"]
                    elif scene == C_SCENE_SUN:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["遥か遠く頭上から陽光が差している。"]
            elif branch == 1:
                    if scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN):
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["海辺にいる女の子に話しかけよう"]
            elif branch == 2:
                    if scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN):
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["周囲を探索してみよう"]
        return hint_text


    ###gamestateのsceneの値に応じて対応する変数名の文字列を返す ★DEBUG用
    def getSceneName(self):
        if(self.gamestate.scene == C_SCENE_HOME):
            return "HOME"
        if(self.gamestate.scene == C_SCENE_MOON):
            return "MOON"
        if(self.gamestate.scene == C_SCENE_FIRE):
            return "FIRE"
        if(self.gamestate.scene == C_SCENE_WATER):
            return "WATER"
        if(self.gamestate.scene == C_SCENE_WOOD):
            return "WOOD"
        if(self.gamestate.scene == C_SCENE_GOLD):
            return "GOLD"
        if(self.gamestate.scene == C_SCENE_SOIL):
            return "SOIL"
        if(self.gamestate.scene == C_SCENE_SUN):
            return "SUN"
        if(self.gamestate.scene == C_SCENE_END):
            return "END"
        if(self.gamestate.scene == C_SCENE_MENU):
            return "MENU"

    ###gamestateのmodeの値に応じて対応する変数名の文字列を返す ★DEBUG用
    def getModeName(self):
        if(self.gamestate.mode == C_PLAY):
            return "PLAY"
        if(self.gamestate.mode == C_MENU):
            return "MENU"

    def drawBG(self):
        ###HOMEシーン用背景の描画。パララックス背景の砂浜と、手前の道路を描画する。
        # if (self.gamestate.mode == C_PLAY and self.gamestate.scene == C_SCENE_HOME):
        if (self.gamestate.mode == C_PLAY):
            if(self.gamestate.scene == C_SCENE_HOME):
                self.drawHomeBG()
            ###月の戸の場合、満月と花火の描写を行う
            elif(self.gamestate.scene == C_SCENE_MOON):
                ###専用背景を描画
                self.drawMoonBG()
            ###火の戸の場合、ホタル及び灯籠の描写を行う
            elif(self.gamestate.scene == C_SCENE_FIRE):
                ###専用背景を描画
                self.drawFireBG()
            ###波紋の戸の場合、雨の描写を行う
            elif(self.gamestate.scene == C_SCENE_WATER):
                ###専用背景を描画
                self.drawWaterBG()
            ###木の戸の場合、草木花の描写を行う
            elif(self.gamestate.scene == C_SCENE_WOOD):
                ###専用背景を描画
                self.drawWoodBG()
            ###金の戸の場合多角形と樹形図の幾何学図形及び星の描写を行う
            elif(self.gamestate.scene == C_SCENE_GOLD):
                ###専用背景を描画
                self.drawGoldBG()
            ###土の戸の場合、墓地の描写を行う
            elif(self.gamestate.scene == C_SCENE_SOIL):
                ###専用背景を描画
                self.drawMoonBG()
                # self.drawSoilBG()
            ###太陽の戸の場合、ひだまりの描写を行う
            elif(self.gamestate.scene == C_SCENE_SUN):
                ###専用背景を描画
                self.drawMoonBG()
                # self.drawSunBG()

    def drawHomeBG(self):
        ###背景を塗りつぶし
        pyxel.cls(11)
        ###奥行き背景用のエリアを１色で表示する
        pyxel.rect(0,   0, 300, 112, 6)
        ###各背景レイヤーを描画
        for i in range(-1, 6):
                ###空
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[0] % (8 * 40) - 32, 0, 2, 0, 0, 8 * 40 - 32, 8 *  8,0)
                ###雲
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[1] % (8 * 40),        16, 2, 0, 8 *  8, 8 * 40, 8 *  8,0)
                ###海
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[2] % (8 * 40), 8 * 10 -4, 2, 0, 8 * 16, 8 * 40, 8 * 11,0)
                ###波の単振動沖合
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[3] % (8 * 40), 1.5 * Math.cos(pyxel.frame_count / 30) + 8 * 11 -3, 2, 0, 8 * 17, 8 * 40, 7,0)
                ###島茶
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[4] % (8 * 40),     8 * 9, 2, 0, 8 * 34, 8 * 40, 8 * 2,0)
                ###島緑
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[5] % (8 * 40),     8 * 9, 2, 0, 8 * 32, 8 * 40, 8 * 2,0)
                ###波の単振動波打ち際１
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[6] % (8 * 40), 2.5 * Math.cos(pyxel.frame_count / 28) + 8 * 13 -4, 2, 0, 8 * 19, 8 * 40, 8 * 1,0)
                ###波の単振動波打ち際２
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[7] % (8 * 40), 2.5 * Math.cos(pyxel.frame_count / 30) + 8 * 13   , 2, 0, 8 * 20, 8 * 40, 8 * 3,0)
        ###操作キャラのX軸方向移動に合わせてscroll+描画位置を変える。
        ###道路
        pyxel.bltm(-32 - scroll_memory[0],8 * 17,     2, 0, 8 * 40, 8 * 40 + scroll_memory[0] + 32, 8 * 12,0)
        ###塀
        pyxel.bltm(-32 - scroll_memory[0],8 * 15 - 5, 2, 0, 8 * 36, 8 * 40 + scroll_memory[0] + 32, 8 * 4,0)
        ###街灯
        pyxel.blt( 15 - scroll_memory[0],  55, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
        pyxel.blt(145 - scroll_memory[0],  55, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
        pyxel.blt(245 - scroll_memory[0],  55, 2, 16 * 5, 16 * 5,-16 * 1, 16 * 6,3)
        pyxel.blt(360 - scroll_memory[0],  55, 2, 16 * 5, 16 * 5,-16 * 1, 16 * 6,3)
        pyxel.blt(480 - scroll_memory[0],  55, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
        ###electric line1
        self.drawElectricalwire(130 -150 - scroll_memory[0], -5,280 -150 - scroll_memory[0], -5)
        self.drawElectricalwire(130      - scroll_memory[0], -5,280      - scroll_memory[0], -5)
        self.drawElectricalwire(130 +150 - scroll_memory[0], -5,300 +450 - scroll_memory[0], -5)
        ###electric line2
        self.drawElectricalwire(130 -150 - scroll_memory[0],0,280 -150 - scroll_memory[0], 0)
        self.drawElectricalwire(130      - scroll_memory[0],0,280      - scroll_memory[0], 0)
        self.drawElectricalwire(130 +150 - scroll_memory[0],0,300 +450 - scroll_memory[0], 0)
        ###電信柱
        pyxel.blt(116       - scroll_memory[0], -25, 2, 16 * 6, 0, 16 * 1, 16 * 11,3)
        pyxel.blt(116 + 150 - scroll_memory[0], -25, 2, 16 * 6, 0, 16 * 1, 16 * 11,3)
        pyxel.blt(136 + 450 - scroll_memory[0], -25, 2, 16 * 6, 0, 16 * 1, 16 * 11,3)
        ###バス停
        pyxel.blt(333 - scroll_memory[0], 8 * 11, 2, 8 * 5, 16 *  7, 16, 16 * 4,3)
        ###pole red
        pyxel.blt( 92 - scroll_memory[0], 8 * 17, 2, 16 * 2, 16 *  9, 16 / 2, 16 * 1,3)
        pyxel.blt(100 - scroll_memory[0], 8 * 17, 2, 16 * 2, 16 *  8, 16 / 2, 16 * 1,3)
        pyxel.blt(108 - scroll_memory[0], 8 * 17, 2, 16 * 2, 16 * 10, 16 / 2, 16 * 1,3)
        ###看板
        pyxel.blt(278 - scroll_memory[0], 8 * 14, 2, 16 / 2 * 9, 16 *  9, 16 / 2, 16 * 2, 3)


    def drawMoonBG(self):
        pyxel.cls(0) #DARK BLUE
        ###花火の描画
        if(len(self.fireworks)>0) :
            for firework in self.fireworks:
                ###アクティブ中は線を描画
                if firework.active:
                    pyxel.line(firework.x - scroll_memory[0], firework.y + 4, firework.x - scroll_memory[0], firework.y + 9, 15)
                    pyxel.line(firework.x - scroll_memory[0], firework.y,     firework.x - scroll_memory[0], firework.y + 3,  7)
                    pyxel.pset(firework.x - scroll_memory[0], firework.y - 1, pyxel.frame_count % 16)
                    # pyxel.circb(firework.x, firework.y -1, 2, pyxel.frame_count % 16)
                ###バースト中は円を描画
                elif firework.burst:
                    ###花火の残存時間に応じた色を選択
                    rndcolor = 0
                    if firework.life > 50:
                        rndcolor = Random.choice([0, 7, 14, 11])
                    elif 50 >= firework.life > 30:
                        rndcolor = Random.choice([0, 9, 8, 3])
                    elif 30 >= firework.life > 20:
                        rndcolor = Random.choice([0, 10, 2, 1])
                    elif 20 >= firework.life > 0:
                        rndcolor = pyxel.frame_count % 16
                    ###追加ライン描画
                    if firework.burst_func == firework.burst_funcs[5]:  # star_burst用
                        outer_points = firework.burst[:5]  # 外側の五芒星の頂点
                        inner_points = firework.burst[5:]  # 内側の五芒星の頂点
                        connection_indices = [3, 4, 0, 1, 2]  # 内側の頂点と外側の頂点を結ぶためのインデックス
                        # 外側の頂点と内側の頂点を交互に結ぶ
                        for i in range(5):
                            pyxel.line(outer_points[i].real - scroll_memory[0], outer_points[i].imag, inner_points[i].real - scroll_memory[0], inner_points[i].imag, rndcolor)
                            pyxel.line(inner_points[i].real - scroll_memory[0], inner_points[i].imag, outer_points[connection_indices[i]].real - scroll_memory[0], outer_points[connection_indices[i]].imag, rndcolor)
                    if firework.burst_func == firework.burst_funcs[6]:  # spiral_recursive_burst用
                        ###中心点から各点への線を描画
                        for z in firework.burst:
                            pyxel.line(firework.x - scroll_memory[0], firework.y, int(z.real) - scroll_memory[0], int(z.imag), rndcolor)
                    if firework.burst_func == firework.burst_funcs[13]: # radiating_sphere_projection_burst用
                        ###Z座標がプラスのものだけを描画（描画点多くなるため点描）
                        for z in firework.burst:
                            if(z.imag >= 0):
                                pyxel.pset(int(z.real) - scroll_memory[0],    int(z.imag),    rndcolor)
                    
                    ###デフォルト描画
                    if firework.burst_func != firework.burst_funcs[13]:
                        for z in firework.burst:
                            pyxel.circb(int(z.real) - scroll_memory[0], int(z.imag), 1, rndcolor)
        ###デモタイトル表示
        self.bdf2.draw_text(150, 2, "PRESS SPACE : 花火", 7) 

    def drawFireBG(self):
        pyxel.cls(0)
        ###particleの描画
        if len(self.psys_instances) > 0:
            self.drawParticles()
        ###Lantanの描画
        for lantan in self.lantans:
            lantan.draw(scroll_memory[0])
        ###生成された蛍の描画
        for point3d in self.points3d:
            for point in point3d.points:
                ###個々の光点の座標がplayery座標より小さいか、奥にあれば描画
                # if (point.z <= 0 and point.y > self.player.position_y) or (point.y <= self.player.position_y):
                if (point.y <= self.player.position_y):
                    point.draw(scroll_memory[0])

        ###デモタイトル表示
        self.bdf2.draw_text(150, 2, "PRESS V : 蛍", 7) 


    def drawWaterBG(self):
        ###reset(Bk)
        pyxel.cls(0)
        ###水面の光反射エフェクトを描画（スクロール値適用）
        self.wse.draw(scroll_memory[0])
        ###波紋を指定区画内にランダムに描画
        for i in range(0, 19):
            # カウンタが0になったらリセット
            if self.rain_draw_counter[i] == 0:
                self.rainAxisColorReset(i)
                # 波紋描画用変数をセット
                self.rainAxisColorSet(i, Random.randint(0, 600), Random.randint(0, 200), Random.choice([6, 7, 12]))
                # self.rainAxisColorSet(i, Random.randint(0, 300), Random.randint(0, 200), 7)
                self.ripples_w[i] = (((pyxel.frame_count)+i)/20)%25
                self.ripples_h[i] = self.ripples_w[i]/2
                self.ripple_count[i] = Random.randint(1, 5) ###波紋を何重で描画するか
                # self.rain_draw_counter[i] = 15
                self.rain_draw_counter[i] = 20
                ###雨筋の描画point
                self.rain_landing_x[i] = self.rain_x[i] - self.ripples_w[i]/2 +3
                self.rain_landing_y[i] = self.rain_y[i] - self.ripples_h[i]/2 +2
                ###y値が低い（画面上部）ほど、波紋の幅の減補正を大きくする
                if (self.rain_landing_y[i] < 50):
                    self.rain_reduce[i] = 10
                elif (self.rain_landing_y[i] < 100):
                    self.rain_reduce[i] =  7
                elif (self.rain_landing_y[i] < 150):
                    self.rain_reduce[i] =  4
                else:
                    self.rain_reduce[i] =  0
                ###雨の対playerの深さ
                if(self.rain_landing_y[i] < self.player.position_y):
                    self.rain_depth[i] = -1
                else:
                    self.rain_depth[i] = 1
            else:
                self.rain_draw_counter[i] -= 1
            
            ###雨筋（playerのposition_yよりY値が小さい着水点）
            if(self.rain_depth[i] == -1):
                if self.rain_draw_counter[i] == 20:
                    pyxel.line(self.rain_landing_x[i] - scroll_memory[0], -1, self.rain_landing_x[i] - scroll_memory[0], self.rain_landing_y[i] -60, 5)
                    pyxel.line(self.rain_landing_x[i] - scroll_memory[0], self.rain_landing_y[i] -60, self.rain_landing_x[i] - scroll_memory[0], self.rain_landing_y[i], 1)
                if self.rain_draw_counter[i] in(19,20):
                    pyxel.blt(self.rain_landing_x[i] -8 - scroll_memory[0], self.rain_landing_y[i] - 4, 2, 40, 24,  16, 8,0)

            # 波紋の描画（水面下の影）
            self.radius_w[i] = self.ripples_w[i] + (20 - self.rain_draw_counter[i]) * 2.2 # 2は広がる速度を示す任意の値。必要に応じて調整可能。
            self.radius_h[i] = self.ripples_h[i] + (20 - self.rain_draw_counter[i]) * 1.1
            self.rain_draw_x[i] = self.rain_x[i] - self.radius_w[i]/2
            self.rain_draw_y[i] = self.rain_y[i] - self.radius_h[i]/2 + 3
            pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0], self.rain_draw_y[i], self.radius_w[i] -self.rain_reduce[i], self.radius_h[i] -self.rain_reduce[i], 13)
            # 波紋の描画（水面上）
            self.radius_w[i] = self.ripples_w[i] + (20 - self.rain_draw_counter[i]) * 2.18 # 2は広がる速度を示す任意の値。必要に応じて調整可能。
            self.radius_h[i] = self.ripples_h[i] + (20 - self.rain_draw_counter[i]) * 1.09
            self.rain_draw_x[i] = self.rain_x[i] - self.radius_w[i]/2
            self.rain_draw_y[i] = self.rain_y[i] - self.radius_h[i]/2
            ###波紋が何重かで描画パターンを分岐
            wk_ripples_width1 = 1
            wk_ripples_width2 = 2
            wk_ripples_width3 = 5
            wk_ripples_width4 = 10
            ###波紋の描画カウンタが一定値以下で色セットを切り替える
            if(self.rain_draw_counter[i] > 7):
                if(self.ripple_count[i] >= 5):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0] +wk_ripples_width4/2, self.rain_draw_y[i] +wk_ripples_width4/2, self.radius_w[i]-wk_ripples_width4 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width4 -self.rain_reduce[i],  1)
                if(self.ripple_count[i] >= 4):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0] +wk_ripples_width3/2, self.rain_draw_y[i] +wk_ripples_width3/2, self.radius_w[i]-wk_ripples_width3 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width3 -self.rain_reduce[i],  5)
                if(self.ripple_count[i] >= 3):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0] +wk_ripples_width2/2, self.rain_draw_y[i] +wk_ripples_width2/2, self.radius_w[i]-wk_ripples_width2 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width2 -self.rain_reduce[i], 13)
                if(self.ripple_count[i] >= 2):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0] -wk_ripples_width1/2, self.rain_draw_y[i] -wk_ripples_width1/2, self.radius_w[i]+wk_ripples_width1 -self.rain_reduce[i], self.radius_h[i]+wk_ripples_width1 -self.rain_reduce[i], 12)
                if(self.ripple_count[i] == 1):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0], self.rain_draw_y[i], self.radius_w[i] -self.rain_reduce[i],   self.radius_h[i] -self.rain_reduce[i], self.rain_color[i])
            else:
                if(self.ripple_count[i] >= 5):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0] +wk_ripples_width4/2, self.rain_draw_y[i] +wk_ripples_width4/2, self.radius_w[i]-wk_ripples_width4 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width4 -self.rain_reduce[i],  1)
                if(self.ripple_count[i] >= 4):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0] +wk_ripples_width3/2, self.rain_draw_y[i] +wk_ripples_width3/2, self.radius_w[i]-wk_ripples_width3 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width3 -self.rain_reduce[i],  1)
                if(self.ripple_count[i] >= 3):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0] +wk_ripples_width2/2, self.rain_draw_y[i] +wk_ripples_width2/2, self.radius_w[i]-wk_ripples_width2 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width2 -self.rain_reduce[i],  5)
                if(self.ripple_count[i] >= 2):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0] -wk_ripples_width1/2, self.rain_draw_y[i] -wk_ripples_width1/2, self.radius_w[i]+wk_ripples_width1 -self.rain_reduce[i], self.radius_h[i]+wk_ripples_width1 -self.rain_reduce[i],  5)
                if(self.ripple_count[i] == 1):
                    pyxel.ellib(self.rain_draw_x[i] - scroll_memory[0], self.rain_draw_y[i], self.radius_w[i] -self.rain_reduce[i],   self.radius_h[i] -self.rain_reduce[i], 12)

        ###プレイヤーのtrajectory_pointを利用して波紋を描画する。波紋描画用変数の準備。
        for i in range(0, 19):
            # カウンタが0になったらリセット
            if self.footprint_draw_counter[i] == 0:
                self.footprintsAxisColorReset(i)
                # 波紋描画用変数をセット
                self.footprintsAxisColorSet(i, self.player.trajectory_point[i][0], self.player.trajectory_point[i][1], 6)
                self.fp_ripples_w[i] = i*1.8
                self.fp_ripples_h[i] = self.fp_ripples_w[i]/2
                self.footprint_draw_counter[i] = 18
            else:
                self.footprint_draw_counter[i] -= 1
        # if self.player.moving:
        # 用意した変数から移動中は4つの抽出した波紋を描画、停止中は2つの抽出した波紋を描画
        for i in range(19, 0, -1):
            if self.player.moving:
                if (i in(4,8,12,16)):
                    # 波紋の広がりの速度を調整
                    self.fp_radius_w[i] = self.fp_ripples_w[i] + (5 - self.footprint_draw_counter[i]) * 1
                    self.fp_radius_h[i] = self.fp_ripples_h[i] + (5 - self.footprint_draw_counter[i]) * 0.5
                    # 波紋の描画位置を設定
                    self.footprints_draw_x[i] = self.footprints_x[i] - self.fp_radius_w[i]/2
                    self.footprints_draw_y[i] = self.footprints_y[i] - self.fp_radius_h[i]/2 
                    # 波紋を描画
                    pyxel.ellib(self.footprints_draw_x[i], self.footprints_draw_y[i], self.fp_radius_w[i], self.fp_radius_h[i], self.footprints_color[i])
            else:
                if (i in(4,12)):
                    # 波紋の広がりの速度を調整
                    self.fp_radius_w[i] = self.fp_ripples_w[i] + (5 - self.footprint_draw_counter[i]) * 1
                    self.fp_radius_h[i] = self.fp_ripples_h[i] + (5 - self.footprint_draw_counter[i]) * 0.5
                    # 波紋の描画位置を設定
                    self.footprints_draw_x[i] = self.footprints_x[i] - self.fp_radius_w[i]/2
                    self.footprints_draw_y[i] = self.footprints_y[i] - self.fp_radius_h[i]/2 
                    # 波紋を描画
                    pyxel.ellib(self.footprints_draw_x[i], self.footprints_draw_y[i], self.fp_radius_w[i], self.fp_radius_h[i], self.footprints_color[i])


    def drawWoodBG(self):
        ###reset(Bk)
        pyxel.cls(1)
        ###花の描画
        pyxel.blt(30 -scroll_memory[0],100,1,144,0,16,40,0)
        pyxel.blt(530 -scroll_memory[0],100,1,144,0,16,40,0)
        ###木の描画
        self.drawTreesBG()
        ###particleの描画
        self.drawParticles()
        ###デモタイトル表示
        self.bdf2.draw_text(150, 2, "PRESS V : particle生成", 7) 
    
    def drawTreesBG(self):
        # 各Treeオブジェクトの葉の座標に対してスプライトを分割表示し、動的な葉の表現を行う
        for tree in self.trees:
            if tree.position_back:
                ###幹の描画
                pyxel.blt(tree.x -4, tree.y + 16, 2, 16, 192, 40, 64, 0)
                # pyxel.blt(tree.x -4 -scroll_memory[0], tree.y + 16, 2, 16, 192, 40, 64, 0)
                ###葉と光点の描画
                for i in range(0, len(tree.leaves)):
                    x, y = tree.leaves[i]
                    ###交互に色セットの切り替えを行う
                    if i % 2 == 0:
                        pyxel.pal(3, 11)
                        point_color = pyxel.COLOR_YELLOW
                    elif i % 2 == 1:
                        pyxel.pal()
                        point_color = pyxel.COLOR_WHITE
                    ###葉の描画
                    pyxel.blt(x - scroll_memory[0], y, 2, 0, 192, 16, 16, 0)
                    # ###光点の描画
                    # pyxel.pset(x + 8 - scroll_memory[0], y + 8, point_color) 
                ###draw後にscroll加味を戻す
                ##本来のスクロールを加味しない位置に戻す
                tree.x += self.scroll_x
                for leaf in tree.leaves:
                    leaf = leaf[0] + self.scroll_x, leaf[1]

    def drawTreesFT(self):
        # 各Treeオブジェクトの葉の座標に対してスプライトを分割表示し、動的な葉の表現を行う
        for tree in self.trees:
            if tree.position_front:
                ###幹の描画
                # pyxel.blt(tree.x -4 -scroll_memory[0], tree.y + 16, 2, 16, 192, 40, 64, 0)
                pyxel.blt(tree.x -4, tree.y + 16, 2, 16, 192, 40, 64, 0)
                ###葉と光点の描画
                for i in range(0, len(tree.leaves)):
                    x, y = tree.leaves[i]
                    ###交互に色セットの切り替えを行う
                    if i % 2 == 0:
                        pyxel.pal(3, 11)
                        point_color = pyxel.COLOR_YELLOW
                    elif i % 2 == 1:
                        pyxel.pal()
                        point_color = pyxel.COLOR_WHITE
                    ###葉の描画
                    pyxel.blt(x - scroll_memory[0], y, 2, 0, 192, 16, 16, 0)
                    ###光点の描画
                    pyxel.pset(x + 8 - scroll_memory[0], y + 8, point_color)
                ###draw後にscroll加味を戻す
                ###本来のスクロールを加味しない位置に戻す
                tree.x += self.scroll_x
                for leaf in tree.leaves:
                    leaf = leaf[0] + self.scroll_x, leaf[1]


    def drawGoldBG(self):
        ###reset(Bk)
        pyxel.cls(0)
        ###EllipticalOrbitを描画
        for point in self.elliptical_orbits:
            point.draw(scroll_memory[0])
        ###echoを描画
        for segment in self.segments:
            segment.draw(scroll_memory[0])
        ###デモタイトル表示
        self.bdf2.draw_text(150, 2, "PRESS E : IN/OUT", 7) 
        self.bdf2.draw_text(150,14, "PRESS R : 白銀比/黄金比", 7) 
        self.bdf2.draw_text(150,26, "PRESS T : angle +15", 7) 


    # def drawSoilBG(self):

    # def drawSunBG(self):

    def drawParticles(self):
        ### 有効なパーティクルをすべて描画する
        if len(self.psys_instances) > 0:
            for psys in self.psys_instances:
                ###スクロールを加味して画面枠0〜300内のパーティクルのみ描画
                psys.draw_particles(scroll_memory[0],0,300)


    def rainAxisColorSengen(self):
        ###波紋描画用変数の初期化
        self.rain_x       = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rain_y       = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rain_color   = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ripples_w    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ripples_h    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.radius_w     = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.radius_h     = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rain_draw_x  = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rain_draw_y  = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.ripple_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ###雨筋の描画用
        self.rain_landing_x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rain_landing_y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rain_depth     = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rain_reduce = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
    def rainAxisColorReset(self,index):
        ###波紋描画用変数の初期化
        self.rain_x[index] = 0
        self.rain_y[index] = 0
        self.rain_color[index] = 0
        self.ripples_w[index] = 0
        self.ripples_h[index] = 0
        self.radius_w[index] = 0
        self.radius_h[index] = 0
        self.rain_draw_x[index] = 0
        self.rain_draw_y[index] = 0
        self.ripple_count[index] = 0
        self.rain_landing_x[index] = 0
        self.rain_landing_y[index] = 0
        self.rain_depth[index] = 0
        self.rain_reduce[index] = 0

    def rainAxisColorSet(self,index, inputX, inputY, inputColor):
        ###波紋描画用変数の指定
        self.rain_x[index] = inputX
        self.rain_y[index] = inputY
        self.rain_color[index] = inputColor

    def footprintsAxisColorSengen(self):
        ###波紋描画用変数の初期化
        self.footprints_x      = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.footprints_y      = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.footprints_color  = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.fp_ripples_w      = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.fp_ripples_h      = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.fp_radius_w       = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.fp_radius_h       = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.footprints_draw_x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.footprints_draw_y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def footprintsAxisColorReset(self,index):
        ###波紋描画用変数の初期化
        self.footprints_x[index] = 0
        self.footprints_y[index] = 0
        self.footprints_color[index] = 0
        self.fp_ripples_w[index] = 0
        self.fp_ripples_h[index] = 0
        self.fp_radius_w[index] = 0
        self.fp_radius_h[index] = 0
        self.footprints_draw_x[index] = 0
        self.footprints_draw_y[index] = 0

    def footprintsAxisColorSet(self,index, inputX, inputY, inputColor):
        ###波紋描画用変数の指定
        self.footprints_x[index] = inputX
        self.footprints_y[index] = inputY
        self.footprints_color[index] = inputColor

    def drawFT(self, player_moving=False):
        ###HOMEシーン用前景の描画。プレイヤーの移動状態を受け取り、挙動を日に合わせて描画する。
        if (self.gamestate.mode == C_PLAY):
            if(self.gamestate.scene == C_SCENE_HOME):
                ###街灯
                pyxel.blt( 15 + 5 - scroll_memory[0], 145, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
                pyxel.blt(150 + 5 - scroll_memory[0], 145, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
                pyxel.blt(245 + 5 - scroll_memory[0], 145, 2, 16 * 5, 16 * 5,-16 * 1, 16 * 6,3)
                pyxel.blt(365 + 5 - scroll_memory[0], 145, 2, 16 * 5, 16 * 5,-16 * 1, 16 * 6,3)
                pyxel.blt(480 + 5 - scroll_memory[0], 145, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
                ###electric line1
                self.drawElectricalwire( 90 -150 - scroll_memory[0],60 -5,240 -150 - scroll_memory[0],60 -5)
                self.drawElectricalwire( 90      - scroll_memory[0],60 -5,240      - scroll_memory[0],60 -5)
                self.drawElectricalwire( 90 +150 - scroll_memory[0],60 -5,240 +150 - scroll_memory[0],60 -5)
                self.drawElectricalwire( 90 +300 - scroll_memory[0],60 -5,240 +300 - scroll_memory[0],60 -5)
                self.drawElectricalwire( 90 +450 - scroll_memory[0],60 -5,240 +450 - scroll_memory[0],60 -5)
                ###electric line2
                self.drawElectricalwire( 90 -150 - scroll_memory[0],60,240 -150 - scroll_memory[0],60)
                self.drawElectricalwire( 90      - scroll_memory[0],60,240      - scroll_memory[0],60)
                self.drawElectricalwire( 90 +150 - scroll_memory[0],60,240 +150 - scroll_memory[0],60)
                self.drawElectricalwire( 90 +300 - scroll_memory[0],60,240 +300 - scroll_memory[0],60)
                self.drawElectricalwire( 90 +450 - scroll_memory[0],60,240 +450 - scroll_memory[0],60)
                ###電信柱
                pyxel.blt(82 - scroll_memory[0], 50, 2, 16 * 6, 0, -16 * 1, 16 * 11,3)
                pyxel.rect(93 - scroll_memory[0], 182, 3, 8, 1)
                pyxel.blt(82 + 150 - scroll_memory[0], 50, 2, 16 * 6, 0, -16 * 1, 16 * 11,3)
                pyxel.rect(93 + 150 - scroll_memory[0], 182, 3, 8, 1)
                pyxel.blt(82 + 300 - scroll_memory[0], 50, 2, 16 * 6, 0, -16 * 1, 16 * 11,3)
                pyxel.rect(93 + 300 - scroll_memory[0], 182, 3, 8, 1)
                pyxel.blt(82 + 450 - scroll_memory[0], 50, 2, 16 * 6, 0, -16 * 1, 16 * 11,3)
                pyxel.rect(93 + 450 - scroll_memory[0], 182, 3, 8, 1)
                ###塀
                pyxel.bltm(-32 - scroll_memory[0],8 * 25, 2, 0, 8 * 36, 8 * 40 + scroll_memory[0] + 32, 8 * 4,0)
                ###猫
                self.frames = Math.floor(pyxel.frame_count/9) % 10
                pyxel.blt(450 - scroll_memory[0], 190, 1, 16 * 7, 0 + self.frames * 16,  16 * 1, 16 * 1,6)


            if(self.gamestate.scene == C_SCENE_FIRE):
                for point3d in self.points3d:
                    for point in point3d.points:
                        ###個々の光点の座標がplayerのyより手前にあれば描画
                        # if (point.z > 0 and point.y <= self.player.position_y) or (point.y > self.player.position_y):
                        if (point.y > self.player.position_y):
                            point.draw(scroll_memory[0])

            ###波紋の戸
            if(self.gamestate.scene == C_SCENE_WATER):
                ###雨筋(playerのposition_yよりY値が大きい着水点)
                for i in range(0, 19):
                    if(self.rain_depth[i] == 1):
                        if self.rain_draw_counter[i] == 15:
                            pyxel.line(self.rain_landing_x[i] - scroll_memory[0], -1, self.rain_landing_x[i] - scroll_memory[0], self.rain_landing_y[i] -60, 6)
                            pyxel.line(self.rain_landing_x[i] - scroll_memory[0], self.rain_landing_y[i] -60, self.rain_landing_x[i] - scroll_memory[0], self.rain_landing_y[i], 12)
                        if self.rain_draw_counter[i] in(14,15):
                            pyxel.blt(self.rain_landing_x[i] -8 - scroll_memory[0], self.rain_landing_y[i] - 4, 2, 40, 24,  16, 8,0)

                ###playerの足元の水はね
                if player_moving:
                    wk_frames1 = Math.floor(pyxel.frame_count/6) % 4
                    wk_frames2 = Math.floor(pyxel.frame_count/5) % 3
                    wk_frames3 = Math.floor(pyxel.frame_count/5) % 2
                    wk_frames4 = (wk_frames2 + 1)%3
                    if self.player.player_direction == 0:
                        pyxel.blt(self.player.position_x  +2, self.player.position_y -8, 2, 64, wk_frames2 * 5,  12, 5, 0)
                        pyxel.blt(self.player.position_x -14, self.player.position_y -8, 2, 64, wk_frames4 * 5, -12, 5, 0)
                        pyxel.blt(self.player.position_x  +4, self.player.position_y -4, 2, 82, 20 + wk_frames3 * 3, 6, 3, 0)
                        pyxel.blt(self.player.position_x -12, self.player.position_y -4, 2, 82, 20 + wk_frames3 * 3,-6, 3, 0)
                        pyxel.blt(self.player.position_x  +4, self.player.position_y -2, 2, 76, 20 + wk_frames3 * 6, 6, 6, 0)
                        pyxel.blt(self.player.position_x -12, self.player.position_y -2, 2, 76, 20 + wk_frames3 * 6,-6, 6, 0)

                    if self.player.player_direction == 1:
                        pyxel.blt(self.player.position_x  -4, self.player.position_y -4, 2, 77, wk_frames1 * 5,  11, 5, 0)
                        pyxel.blt(self.player.position_x  +2, self.player.position_y -4, 2, 64, wk_frames2 * 5,  12, 5, 0)
                        pyxel.blt(self.player.position_x -14, self.player.position_y -4, 2, 64, wk_frames4 * 5, -12, 5, 0)

                    if self.player.player_direction == 2:
                        pyxel.blt(self.player.position_x -14, self.player.position_y -4, 2, 64, wk_frames2 * 5, -12, 5, 0)
                        pyxel.blt(self.player.position_x  +2, self.player.position_y -4, 2, 64, wk_frames2 * 5 + 16,  12, 5, 0)
                    if self.player.player_direction == 3:
                        pyxel.blt(self.player.position_x  +2, self.player.position_y -4, 2, 64, wk_frames2 * 5,  12, 5, 0)
                        pyxel.blt(self.player.position_x -14, self.player.position_y -4, 2, 64, wk_frames2 * 5 + 16, -12, 5, 0)

            if(self.gamestate.scene == C_SCENE_WOOD):
                ###木の描画
                self.drawTreesFT()
                ###草を描画
                for grass in self.grasses:
                    ###画面枠（X座標０〜３００）外の草は描画しないようにする
                        grass.draw(scroll_memory[0],0,300)
                # 花を描画
                for flower in self.flowers:
                    flower.draw(scroll_memory[0],0,0,300)


            ###メニュー＆会話用のエリアを黒く表示する
            pyxel.rect(0, 232, 300, 68, 0)    

    def drawElectricalwire(self,sx,sy,ex,ey):
        ###PLAYモード共通ロジック
        if (self.gamestate.mode == C_PLAY):
            self.start_point = [sx,sy]
            self.end_point = [ex,ey]
            self.full_line = ex - sx
            self.line_color = 1 #deepblue
            ###線分座標のリセット
            self.seg_line1_Spoint = [0,0]
            self.seg_line1_Epoint = [0,0]
            self.seg_line2_Spoint = [0,0]
            self.seg_line2_Epoint = [0,0]
            self.seg_line3_Spoint = [0,0]
            self.seg_line3_Epoint = [0,0]
            self.seg_line4_Spoint = [0,0]
            self.seg_line4_Epoint = [0,0]
            self.seg_line5_Spoint = [0,0]
            self.seg_line5_Epoint = [0,0]
            ###始点と終点を結ぶ線分をその長さ等分する
            if(self.full_line % 5 == 0):
                ###始点から終点までの線分を5分割する線分のための10座標を求める。
                wk_linespanx = self.full_line / 5
                wk_linespany = 4
                self.seg_line1_Spoint = [self.start_point[0], self.start_point[1]] 
                self.seg_line1_Epoint = [self.seg_line1_Spoint[0] + wk_linespanx, self.seg_line1_Spoint[1] + wk_linespany]
                self.seg_line2_Spoint = self.seg_line1_Epoint
                self.seg_line2_Epoint = [self.seg_line2_Spoint[0] + wk_linespanx, self.seg_line2_Spoint[1] + wk_linespany]
                self.seg_line3_Spoint = self.seg_line2_Epoint
                self.seg_line3_Epoint = [self.seg_line3_Spoint[0] + wk_linespanx, self.seg_line3_Spoint[1]]
                self.seg_line4_Spoint = self.seg_line3_Epoint
                self.seg_line4_Epoint = [self.seg_line4_Spoint[0] + wk_linespanx, self.seg_line4_Spoint[1] - wk_linespany]
                self.seg_line5_Spoint = self.seg_line4_Epoint
                self.seg_line5_Epoint = [self.end_point[0], self.end_point[1]]
                ###直線を引く
                pyxel.line(self.seg_line1_Spoint[0], self.seg_line1_Spoint[1], self.seg_line1_Epoint[0], self.seg_line1_Epoint[1], self.line_color)
                pyxel.line(self.seg_line2_Spoint[0], self.seg_line2_Spoint[1], self.seg_line2_Epoint[0], self.seg_line2_Epoint[1], self.line_color)
                pyxel.line(self.seg_line3_Spoint[0], self.seg_line3_Spoint[1], self.seg_line3_Epoint[0], self.seg_line3_Epoint[1], self.line_color)
                pyxel.line(self.seg_line4_Spoint[0], self.seg_line4_Spoint[1], self.seg_line4_Epoint[0], self.seg_line4_Epoint[1], self.line_color)
                pyxel.line(self.seg_line5_Spoint[0], self.seg_line5_Spoint[1], self.seg_line5_Epoint[0], self.seg_line5_Epoint[1], self.line_color)
            elif(self.full_line % 4 == 0):
                ###始点から終点までの線分を4分割する線分のための8座標を求める。
                wk_linespanx = self.full_line / 4
                wk_linespany = 2
                self.seg_line1_Spoint = [self.start_point[0], self.start_point[1]] 
                self.seg_line1_Epoint = [self.seg_line1_Spoint[0] + wk_linespanx, self.seg_line1_Spoint[1] + wk_linespany]
                self.seg_line2_Spoint = self.seg_line1_Epoint
                self.seg_line2_Epoint = [self.seg_line2_Spoint[0] + wk_linespanx, self.seg_line2_Spoint[1] + wk_linespany]
                self.seg_line4_Spoint = self.seg_line2_Epoint
                self.seg_line4_Epoint = [self.seg_line4_Spoint[0] + wk_linespanx, self.seg_line4_Spoint[1] - wk_linespany]
                self.seg_line5_Spoint = self.seg_line4_Epoint
                self.seg_line5_Epoint = [self.end_point[0], self.end_point[1]]
                ###直線を引く
                pyxel.line(self.seg_line1_Spoint[0], self.seg_line1_Spoint[1], self.seg_line1_Epoint[0], self.seg_line1_Epoint[1], self.line_color)
                pyxel.line(self.seg_line2_Spoint[0], self.seg_line2_Spoint[1], self.seg_line2_Epoint[0], self.seg_line2_Epoint[1], self.line_color)
                pyxel.line(self.seg_line4_Spoint[0], self.seg_line4_Spoint[1], self.seg_line4_Epoint[0], self.seg_line4_Epoint[1], self.line_color)
                pyxel.line(self.seg_line5_Spoint[0], self.seg_line5_Spoint[1], self.seg_line5_Epoint[0], self.seg_line5_Epoint[1], self.line_color)
            elif(self.full_line % 3 == 0):
                ###始点から終点までの線分を3分割する線分のための6座標を求める。
                wk_linespanx = self.full_line / 3
                wk_linespany = 2
                self.seg_line1_Spoint = [self.start_point[0], self.start_point[1]] 
                self.seg_line1_Epoint = [self.seg_line1_Spoint[0] + wk_linespanx, self.seg_line1_Spoint[1] + wk_linespany]
                self.seg_line3_Spoint = self.seg_line1_Epoint
                self.seg_line3_Epoint = [self.seg_line3_Spoint[0] + wk_linespanx, self.seg_line3_Spoint[1]]
                self.seg_line5_Spoint = self.seg_line3_Epoint
                self.seg_line5_Epoint = [self.end_point[0], self.end_point[1]]
                ###直線を引く
                pyxel.line(self.seg_line1_Spoint[0], self.seg_line1_Spoint[1], self.seg_line1_Epoint[0], self.seg_line1_Epoint[1], self.line_color)
                pyxel.line(self.seg_line3_Spoint[0], self.seg_line3_Spoint[1], self.seg_line3_Epoint[0], self.seg_line3_Epoint[1], self.line_color)
                pyxel.line(self.seg_line5_Spoint[0], self.seg_line5_Spoint[1], self.seg_line5_Epoint[0], self.seg_line5_Epoint[1], self.line_color)

    def drawObjects(self):
        ###HOMEシーン用オブジェクトの描画
        # if (self.gamestate.mode == C_PLAY and self.gamestate.scene == C_SCENE_HOME):
        # if (self.gamestate.mode == C_PLAY and self.gamestate.scene in(C_SCENE_HOME, C_SCENE_WATER)):
        if (self.gamestate.mode == C_PLAY):
            if(self.gamestate.scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN)):
                ###Doorオブジェクト描画およびスクロール加味しない状態への「戻し」
                for obj in doors:
                    obj.draw()
                    ##本来のスクロールを加味しない位置に戻す
                    obj.x += self.scroll_x
                ###当たり判定用オブジェクト（非描画）をスクロール加味しない状態への「戻し」
                for obj in ataris:
                    obj.draw()
                    ##本来のスクロールを加味しない位置に戻す
                    obj.x += self.scroll_x

    def updateObjectsPositionCheck(self):
        ###PLAYモード共通ロジック
        if (self.gamestate.mode == C_PLAY):
            ####-------------------------------------------------------------------------------
            ###プレーヤーオブジェクトとその他のcheckable（＝調べることが可能な）オブジェクト群の位置関係を確認し、
            ###最も近い位置にあるcheckableオブジェクトとの向きを含む隣接状態を捕捉する。
            ###プレイヤーオブジェクトとほかオブジェクト群との距離を測り、最も近い位置にあるオブジェクトを特定。
            # 併せて、プレイヤーとの位置関係とプレイヤー向きから当該近距離オブジェクトのテキスト返却フラグを常にON/OFF切替チェックする。

            ###各オブジェクトリストの長さの合計が2以上のとき、すなわちプレイヤー以外にオブジェクトが存在するときのみ
            if (len(characters) + len(doors) + len(ataris) >= 2):
                self.nearest_obj = self.checkObjectsListDistance()
            # #最終順序リストをcharactersで初期化
            # self.wk_objectDrawlistBasedAxisY = characters
            # #並び替え
            # self.wk_objectDrawlistBasedAxisY.sort(key=lambda obj: obj.position_y)

    def checkObjectsListDistance(self):
        ###PLAYモード共通ロジック
        if (self.gamestate.mode == C_PLAY):
            ###プレイヤーとほかオブジェクト群との距離を測る
            # self.wk_player = self.charactor01
            self.rtn_obj = None
            # # プレイヤーを確認
            for elem in characters:
                if (elem.is_playing):
                    self.wk_player = elem
            # obj-listごとにチェック
            self.tmp_obj1, distance1 = self.check_nearest_obj_axis(self.wk_player, characters)
            self.tmp_obj2, distance2 = self.check_nearest_obj_axis(self.wk_player, doors)
            self.tmp_obj3, distance3 = self.check_nearest_obj_axis(self.wk_player, ataris)
            # 最小が最も近い
            distance = min(distance1, distance2, distance3)
            # 最も近いオブジェクトをnearestなobjとして保持する
            if  (distance == distance1):
                self.rtn_obj = self.tmp_obj1
            elif(distance == distance2):
                self.rtn_obj = self.tmp_obj2
            elif(distance == distance3):
                self.rtn_obj = self.tmp_obj3
            
            ### 最寄りobjとplayerが隣接しているとき、テキスト返却可能フラグをONにする
            ###playerの足元基準点が衝突基準点なので、これを同様に基準とする
            ### まず最も近いオブジェクトのテキスト返却フラグをリセット
            self.rtn_obj.flg_reaction = False
            ###上方向に対象オブジェクトが隣接
            if(self.wk_player.position_y -10 <= self.rtn_obj.position_y < self.wk_player.position_y):
                if(self.wk_player.position_x - self.wk_player.width/2 -10 <= self.rtn_obj.position_x <= self.wk_player.position_x + self.wk_player.width/2 + 10):
                    ###playerの向きが上なら対象オブジェクトはテキスト返却可能フラグがON
                    if(self.wk_player.player_direction == 0):
                        self.rtn_obj.flg_reaction = True
            ###下方向に対象オブジェクトが隣接
            elif(self.wk_player.position_y <= self.rtn_obj.position_y < self.wk_player.position_y + 10):
                if(self.wk_player.position_x - self.wk_player.width/2 - 10<= self.rtn_obj.position_x <= self.wk_player.position_x + self.wk_player.width/2 + 10):
                ###playerの向きが下なら対象オブジェクトはテキスト返却可能フラグがON
                    if(self.wk_player.player_direction == 1):
                        self.rtn_obj.flg_reaction = True
            ###左方向に対象オブジェクトが隣接
            if(self.wk_player.position_x - self.wk_player.width/2 - 16 <= self.rtn_obj.position_x < self.wk_player.position_x - self.wk_player.width/2):
                if(self.wk_player.position_y - 10 <= self.rtn_obj.position_y <= self.wk_player.position_y + 10):
                ###playerの向きが左なら対象オブジェクトはテキスト返却可能フラグがON
                    if(self.wk_player.player_direction == 2):
                        self.rtn_obj.flg_reaction = True
            ###右方向に対象オブジェクトが位置        
            elif(self.wk_player.position_x + self.wk_player.width/2 -10 < self.rtn_obj.position_x <= self.wk_player.position_x + self.wk_player.width/2 + 10):
                if(self.wk_player.position_y - 10 <= self.rtn_obj.position_y <= self.wk_player.position_y + 10):
                ###playerの向きが右なら対象オブジェクトはテキスト返却可能フラグがON
                    if(self.wk_player.player_direction == 3):
                        self.rtn_obj.flg_reaction = True
            
            ###最も近いオブジェクトのテキスト返却フラグがON、すなわち最も近いオブジェクトが隣接状態にあるとき
            ###フキダシ表示用の座標を初期化
            self.fukidashi_nearest_obj_x, self.fukidashi_nearest_obj_y = 0, 0
            if (self.rtn_obj.flg_reaction):
                    ###フキダシ表示のために、対象オブジェクトの座標を取得
                    self.fukidashi_nearest_obj_x, self.fukidashi_nearest_obj_y = self.rtn_obj.x, self.rtn_obj.y
                    ###最も近いオブジェクトのクラス種別によって、座標を微調整する
                    if self.rtn_obj.__class__.__name__ in("Door", "Jewel"):
                        self.fukidashi_nearest_obj_x += 16
                        self.fukidashi_nearest_obj_y -= 48
                    elif self.rtn_obj.__class__.__name__ in("Character","Atari"):
                        self.fukidashi_nearest_obj_x +=  8
                        self.fukidashi_nearest_obj_y -= 16

            return self.rtn_obj

    def check_nearest_obj_axis(self, player, list):
        ###PLAYモード共通ロジック
        if (self.gamestate.mode == C_PLAY):
            self.wk_player = player
            # 指定のリストオブジェクトのうち最も近いものの座標を返す
            # 返却用座標変数・返却用距離変数の初期値として画面端と画面幅をセット
            rtn_obj = self.wk_player
            rtn_distance = 999999
            for elem in list:
                #距離を測る
                if not(elem.is_playing):
                    distance = Math.sqrt((elem.position_x - self.wk_player.position_x)**2 + (elem.position_y - self.wk_player.position_y)**2)
                    # 計算結果が保持中の評価用距離変数以下の場合、返却用座標と返却用距離を更新する
                    if (distance <= rtn_distance):
                        rtn_obj = elem
                        rtn_distance = distance
            return (rtn_obj, rtn_distance)



    def updateBtnInputCheck_SPACE(self):
        ###PLAYモード共通ロジック
        if (self.gamestate.mode == C_PLAY) and (self.inputdelay_cnt == 0):
            ###オブジェクトリストの合計が2以上のときのみ、スペースキー打鍵を検知する
            if (len(characters) + len(doors) + len(ataris) >= 2):
                ###ボタン入力検知（スペースキー、ゲームパッドAキー）
                if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                    ##スペース打鍵によるチェックフラグが有効中でない
                    if (self.pressed_space_checking == False):
                        if self.nearest_obj.flg_reaction : ### 近接オブジェクトのリアクションフラグが有効中のときだけ
                            ###話しかけた・調べた対象のオブジェクトがキャラクターだった場合、方向をプレイヤへ向き直させる
                            if (self.nearest_obj.__class__.__name__ == "Character"):
                                ###従前の向きを退避
                                self.checking_obj_direction = self.nearest_obj.player_direction
                                ###プレイヤの向きと逆方向を向かせる
                                if(self.player.player_direction == 0):
                                    self.nearest_obj.player_direction = 1
                                if(self.player.player_direction == 1):
                                    self.nearest_obj.player_direction = 0
                                if(self.player.player_direction == 2):
                                    self.nearest_obj.player_direction = 3
                                if(self.player.player_direction == 3):
                                    self.nearest_obj.player_direction = 2
                            
                            ###プレイヤが話しかけた相手オブジェクトの発話待ちフラグに応じてテキスト用意先を振り分ける
                            if(self.nearest_obj.flg_waiting_responce):
                                ###相手がplayerからの発話待ちのとき
                                self.getAskText(self.player, self.nearest_obj) ##発話待ち隣接objに対するplayerの発話テキストを取得
                                ###テキストウィンドウ表示用顔グラ判別のためのキャラ番号取得
                                if (self.player.__class__.__name__ == "Character"):
                                    self.talking_chara_no = self.player.character_no
                                else:
                                    self.talking_chara_no = 99
                                ###会話相手の返答待ち状態フラグを戻す
                                self.nearest_obj.cancelFlgWaitingResponce()
                            else:
                                ###相手が自身から発話するとき
                                self.getText(self.nearest_obj)
                                ###テキストウィンドウ表示用顔グラ判別のためのキャラ番号取得
                                if (self.nearest_obj.__class__.__name__ == "Character"):
                                    self.talking_chara_no = self.nearest_obj.character_no
                                else:
                                    self.talking_chara_no = 99 
                                # ###相手が発話後返答待ちになったら
                                # if(self.nearest_obj.flg_waiting_responce):
                                #     ###相手がplayerからの発話待ちのとき
                                #     self.getAskText(self.player)

                            self.pressed_space_checking = True
                            self.display_finished = False
                            self.inputdelay_cnt = self.inptdelay_C #入力受付遅延用カウンタをリセット
                    ##スペース打鍵によるチェックフラグが有効中
                    else:
                        if(self.display_finished): ##分割テキストを表示完了
                            ###話しかけた・調べた対象のオブジェクトがキャラクターだった場合、方向を元の位置に戻す
                            if (self.nearest_obj.__class__.__name__ == "Character"):
                                self.nearest_obj.player_direction = self.checking_obj_direction

                            self.pressed_space_checking = False #「SPACEキー打鍵によるチェック中」フラグをOFF
                            self.inputdelay_cnt = self.inptdelay_C #入力受付遅延用カウンタをリセット
                            self.wk_textset_divided = [] #表示用テキストをリセット。
                            self.text_divided = False #分割済みフラグのクリア

                            ###話しかけた・調べた対象のオブジェクトがドアだった場合、戸が持つルーム番号に応じてgamestateのシーン番号を変える
                            if (self.nearest_obj.__class__.__name__ == "Door"):
                                if (self.nearest_obj.room_no != 0)  or \
                                (self.nearest_obj.room_no == 0 and self.gamestate.scene != 0):
                                    self.deleteObjectsDependingOnScene() ##現在のシーンに応じてオブジェクトを削除しリセット
                                    ###テキスト処理用変数をリセット
                                    self.inputdelay_cnt = 0 #入力受付遅延用カウンタをリセット
                                    self.pressed_space_checking = False #「SPACEキー打鍵によるチェック中」フラグをOFF
                                    ###パララックス背景用スクロール値をリセット
                                    self.scroll_positions = [0.1 for _ in range(9)]
                                    # ###scroll関係変数をリセット
                                    self.scroll_direction = 0
                                    self.scroll_x = 0
                                    self.scroll_distance = 0
                                    self.scrollMemory(self.scroll_x)
                                    self.gamestate.scene = self.nearest_obj.room_no
                                    self.gamestate.scenario[0][0] = self.nearest_obj.room_no
                                    self.generateObjects() ##現在のシーンに応じてオブジェクトを生成
                                    ###チェック中のオブジェクトをリセット
                                    self.nearest_obj = None
                                    ###チェック中のオブジェクトがいる方向、をリセット
                                    self.checking_obj_direction = 4
                                    ###パーティクルシステムのタイマーをリセット
                                    self.timer_for_psys = 0
                            
                            ###話しかけた・調べた対象がキャラクターまたはアタリオブジェクトだった場合、取得アイテムチェックを呼び出す。
                            if (self.nearest_obj.__class__.__name__ in("Character", "Atari")):
                                self.checkGetItem(self.nearest_obj)

                        else: ##分割テキストを表示未完了
                            self.wk_text_disp_times += 1
                
                    ###★TEST★Doorオブジェクトの状態変化
                    if self.wk_player.player_direction == 0:
                        for door in doors:
                            if door.flg_reaction :
                                if door.is_closed:
                                    door.openStart()
                                if door.is_opened:
                                    door.closeStart()

            ###ボタン入力検知（Mキー）
            if pyxel.btnp(pyxel.KEY_M):
                print("M key is pressed in PLAY-MODE!")
                pyxel.play(3,22) #SE再生(Menuオープン)
                self.gamestate.mode = C_MENU
                self.inputdelay_cnt = self.inptdelay_C

        if (self.gamestate.mode == C_MENU) and (self.inputdelay_cnt == 0):
            ###ボタン入力検知（Mキー）
            if pyxel.btnp(pyxel.KEY_M):
                pyxel.play(3,23) #SE再生(Menuクローズ)
                print("M key is pressed in MENU-MODE!")
                self.gamestate.mode = C_PLAY
                self.inputdelay_cnt = self.inptdelay_C

            if not(self.invsys.subwindow_open) and (len(self.invsys.items_and_valuables) > 0):
                if pyxel.btnp(pyxel.KEY_UP):
                    self.invsys.selected_index = max(0, self.invsys.selected_index - 1)
                    pyxel.play(3,8) #SE再生(カーソル移動)
                elif pyxel.btnp(pyxel.KEY_DOWN):
                    self.invsys.selected_index = min(len(self.invsys.items_and_valuables) - 1, self.invsys.selected_index + 1)
                    pyxel.play(3,8) #SE再生(カーソル移動)

            if self.invsys.subwindow_open:
                if pyxel.btnp(pyxel.KEY_UP):
                    self.invsys.subwindow_selected_index = max(0, self.invsys.subwindow_selected_index - 1)
                    pyxel.play(3,8) #SE再生(カーソル移動)
                elif pyxel.btnp(pyxel.KEY_DOWN):
                    self.invsys.subwindow_selected_index = min(1, self.invsys.subwindow_selected_index + 1)
                    pyxel.play(3,8) #SE再生(カーソル移動)
                elif pyxel.btnp(pyxel.KEY_SPACE):
                    self.invsys.execute_option()  # 選択肢を実行
                    self.invsys.subwindow_open = False  # サブウィンドウを閉じる
                    self.invsys.subwindow_selected_index = 0
                    print("SUBWINDOW CLOSED!")
            else:
                if pyxel.btnp(pyxel.KEY_SPACE):
                    if (len(self.invsys.items_and_valuables) > 0):
                        self.invsys.subwindow_open = True  # サブウィンドウを開く
                        pyxel.play(3,22) #SE再生(Menuオープン)
                        print("SUBWINDOW OPENED!")

    def getAskText(self,obj_from, obj_with=None):
        ###引数オブジェクト（主にPlayer）のアクションテキストを取得し、画面表示テキスト用ワーク変数へセット
        scene = self.gamestate.scenario[0][0]
        scenario = self.gamestate.scenario[0][1]
        branch = self.gamestate.scenario[0][2]
        conversation_from = obj_from.character_no
        conversation_with = obj_with.character_no

        self.wk_textset = []
        ###シーン番号・シナリオ番号・シナリオ枝番を、プレイヤのキャラクタ番号・会話相手のキャラクタ番号とともに渡し、プレイヤの会話テキストを取得する。
        ###取得したテキストは画面表示テキスト用ワーク変数へセットされる。
        self.wk_textset.extend(obj_from.getActionText(scene, scenario, branch, conversation_from, conversation_with))

        ###対象objの会話テキスト取得中に変化したシーン番号・シナリオ番号・シナリオ枝番を再取り込みし、ゲーム本体に上書きする。
        self.gamestate.scenario[0][0] = obj_from.scene_no
        self.gamestate.scenario[0][1] = obj_from.scenario_no
        self.gamestate.scenario[0][2] = obj_from.branch_no

    def getText(self,obj):
        ###引数オブジェクト（主にNonPlayer）のリアクションテキストを取得し、画面表示テキスト用ワーク変数へセット
        scene = self.gamestate.scenario[0][0]
        scenario = self.gamestate.scenario[0][1]
        branch = self.gamestate.scenario[0][2]
        conversation_with = self.player.character_no
        response_no = self.player.responce_no #playerの発話待ちフラグ

        self.wk_textset = []
        ###シーン番号・シナリオ番号・シナリオ枝番を、プレイヤのキャラクタ番号・発話待ちフラグとともに渡し、対象objから会話テキストを取得する。
        ###取得したテキストは画面表示テキスト用ワーク変数へセットされる。
        self.wk_textset.extend(obj.getReactionText(scene, scenario, branch, conversation_with, response_no))

        ###対象objの会話テキスト取得中に変化したシーン番号・シナリオ番号・シナリオ枝番を再取り込みし、ゲーム本体に上書きする。
        self.gamestate.scenario[0][0] = obj.scene_no
        self.gamestate.scenario[0][1] = obj.scenario_no
        self.gamestate.scenario[0][2] = obj.branch_no

    def checkGetItem(self,obj):
        ###PLAYモード共通ロジック。
        # 現在のシーン、シナリオ、枝番に応じ、引数であるチェック中オブジェクト(キャラクター/アタリ)の返却テキストナンバーをもとにアイテムをaddする。
        scene = self.gamestate.scenario[0][0]
        scenario = self.gamestate.scenario[0][1]
        branch = self.gamestate.scenario[0][2]
        conversation_with = self.player.character_no
        response_no = self.player.responce_no #playerの発話待ちフラグ

        if (obj.__class__.__name__ == "Atari"):
            if obj.obj_no == 5:
                if obj.rtn_txt_no == 1:
                    self.invsys.add_valuable('きれいな葉') 
                    obj.rtn_txt_no += 1

        ###対象objの会話テキスト取得中に変化したシーン番号・シナリオ番号・シナリオ枝番を再取り込みし、ゲーム本体に上書きする。
        self.gamestate.scenario[0][0] = obj.scene_no
        self.gamestate.scenario[0][1] = obj.scenario_no
        self.gamestate.scenario[0][2] = obj.branch_no


    def updateTextDivide(self):
        ###PLAYモード共通ロジック
        if (self.gamestate.mode == C_PLAY):
            ###テキストの分割処理
            if self.pressed_space_checking and not(self.text_divided): #分割処理はdisplay完了後のスペースキー打鍵でフラグクリアされる
                ###テキストの分割チェック（結果セットに連続appendする）
                self.textDivide(self.wk_textset, self.wk_textset_divided, C_MAX_DISPWORDS)
                ###３行に分けて分割表示する際のTOTAL回数を捕捉
                self.wk_text_divided_remain = len(self.wk_textset_divided)
                self.display_cnt = self.wk_text_divided_remain // 3
                if not(self.wk_text_divided_remain % 3 == 0):
                    self.display_cnt += 1
                self.wk_text_disp_times = 1
                self.text_divided = True
    ####-------------------------------------------------------------------------------
    def drawMessageAndWindow(self):
        ###PLAYモード共通ロジック
        if(self.gamestate.mode == C_PLAY):
            ###スペースキー打鍵chkフラグON状態のときに捕捉中のdisptimesに分けてメッセージを画面表示する。
            if self.pressed_space_checking :
                ##メッセージウィンドウの表示
                pyxel.bltm(2, 234, 0, 0, 0, C_MSGWINDOW_WIDTH, C_MSGWINDOW_HEIGHT, 3)
                
                if not(self.talking_chara_no == 99):
                    ##キャラクタ画像の重ね表示
                    ###台紙
                    pyxel.blt( 4, 235, 0, 48,  0, 24, 24, 3)
                    ###キャラクタ画像
                    if(self.talking_chara_no == 0):
                        pyxel.blt(8, 238, 0,  0,  0, 16, 16, 3)
                        #self.bdf1.draw_text(36, 240, "GIRL", 7)
                    if(self.talking_chara_no == 1):
                        pyxel.blt(8, 238, 0, 16,  0, 16, 16, 3)
                        #self.bdf1.draw_text(36, 240, "WOLF", 7)
                    if(self.talking_chara_no == 2):
                        pyxel.blt(8, 238, 0, 32,  8, 16, 16, 3)
                        #self.bdf1.draw_text(36, 240, "BOY", 7)
                    ###台紙重ね
                    pyxel.blt(4, 249, 0, 48, 24, 24,  8, 3)

                ###テキストの表示
                ##text_disp_times（スペース打鍵回数＋１）が表示に必要な回数を超えるまで
                if(self.wk_text_disp_times <= self.display_cnt):
                    ###３つ取得
                    self.wk_textset3 = self.wk_textset_divided[3*(self.wk_text_disp_times -1):3*(self.wk_text_disp_times)]
                if(self.wk_text_disp_times == self.display_cnt): ##最後。次のスペース打鍵で完了する
                    self.display_finished = True
                ##画面下部へテキストを表示する
                if(self.talking_chara_no == 99):
                    ###やや中央寄りに配置する
                    if(len(self.wk_textset3)>=1):
                        self.bdf1.draw_text(10, 249, self.wk_textset3[0], 7) ##MAX 28
                    if(len(self.wk_textset3)>=2):
                        self.bdf1.draw_text(10, 263, self.wk_textset3[1], 7)
                    if(len(self.wk_textset3)>=3):
                        self.bdf1.draw_text(10, 277, self.wk_textset3[2], 7)
                else:
                    ###下に詰めて表示する
                    if(len(self.wk_textset3)>=1):
                        self.bdf1.draw_text(10, 259, self.wk_textset3[0], 7) ##MAX 28
                    if(len(self.wk_textset3)>=2):
                        self.bdf1.draw_text(10, 271, self.wk_textset3[1], 7)
                    if(len(self.wk_textset3)>=3):
                        self.bdf1.draw_text(10, 283, self.wk_textset3[2], 7)

    def textDivide(self, textset, textset_divided, max_dispwords = C_MAX_DISPWORDS):
        ###PLAYモード・MENUモード共通ロジック
        if(self.gamestate.mode in(C_PLAY, C_MENU)):
            ###与えられたテキストセットを先頭から順に１行の最大表示可能文字数で分割し、新たなテキストセットを生成する。
            wk_setlen = len(textset)
            if(wk_setlen > 0):
                for words in textset:
                    # wk_wordslen = len(words)
                    wk_words = words
                    while (len(wk_words) > max_dispwords):
                        textset_divided.append(wk_words[:max_dispwords])
                        wk_words = wk_words[max_dispwords:]
                    textset_divided.append(wk_words)

    # def playSounds(self):
        ###PLAYモードかつHOMEシーン
        # if (self.gamestate.mode == C_PLAY):
        #     if(self.gamestate.scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN)):
        #         pyxel.playm(1, loop = True)


#----------------------------
MyApp()
