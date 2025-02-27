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
from Camera import Camera
from Butterfly import Butterfly

from Moon import Moon
from Firework import Firework
from Lantan import Lantan
from WaterTree import WaterTree
from Tree import Tree
from Grass import Grass
from PyxelExtended import PyxelExtended
from ParticleSystem import ParticleSystem
from WaterSurfaceEffect import WaterSurfaceEffect
from Point3D import Point3D
from Flower import Stem
from EllipticalOrbit import EllipticalOrbit
from EchoChamberVisualizer import EchoChamberVisualizer
from DoorTranParticle import DoorTranParticle
from MovingLines import MovingLines


 
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
C_MAP_WIDTH = 600 #px
C_MAP_HEIGHT = 300 #px
#タイルマップ情報
C_WORLD_WIDTH = 600 #px
C_SCROLLON_AREA_WIDTH = 20
C_SCROLL_SPEED = 2
###シナリオ記録リスト
scenario = list()
# 主要キャラクターリスト
characters = list()
# 移動用ドアリスト
doors = list()
# 背景用当たり判定および調査可能箇所リスト
ataris = list()
# ドア遷移時のパーティクルリスト
door_tran_particles = list()

#---------------------（20230815現在未使用）
# 調べられないモノリスト
non_checkables = list()
# エフェクトリスト
effects = list()
#---------------------（20230815現在未使用）

###Atariオブジェクト用パラメータ定数
C_VISIBLE = True
C_INVISIBLE = False
###gamestate.mode用定数
C_START = 0
C_PLAY  = 1
C_PAUSE = 2
C_MENU  = 3
C_END   = 4
C_DEAD  = 5
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
C_SCENE_CHOICE = 10

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
# player_xy = list()
player_xy = list()
player_xylist = list()


##########-----------------------------------------------------------------------
class GameState:
    def __init__(self):
        self.text_display = False
        self.mode = 0 
        self.scene = 0
        self.scenario = list()
        self.scenario.append([0,0,0])
        self.scenetimer = 0
        ###ナンバリングしたDoorオブジェクトの開放状態を管理する配列
        ###順にHOMEの戸、月の戸、火の戸、水の戸、木の戸、金の戸、土の戸、太陽の戸、エンディングの戸
        self.door_open_array = [False, False, False, False, False, False, False, False, False]
        self.door_open_array_bf = self.door_open_array.copy()

        #-------------------------------------------------------------------------------#
        ### for debug
        ##all doors open
        # self.door_open_array = [True, True, True, True, True, True, True, True, True]
        ##scenarioセット
        # self.scenario[0][1] = 8
        # self.scenario[0][2] = 0

        ##テスト用設定
        self.door_open_array = [True, True, True, True, True, True, True, True, True]
        # self.door_open_array = [False, False, False, False, False, False, False, False, False]
        self.door_open_array_bf = self.door_open_array.copy()
        ##scenarioセット
        self.scenario[0][1] = 7 ###到達済scene番号
        self.scenario[0][2] = 0 ###到達済event番号

        ###door‐通過時用
        self.door_transition = False
        self.door_transition_radius = 1
        self.door_transition_radius_max = 200


    def unlock_door(self, scene_no):
        ###与えられたシーン番号に対応するドアを開放する
        self.door_open_array[scene_no] = True

##########-----------------------------------------------------------------------
class MyApp:
    def __init__(self):
        pyxel.init(300, 300, title=C_TITLE, fps=40, quit_key=pyxel.KEY_NONE, capture_scale=4, capture_sec=10)
        pyxel.load("newgame.pyxres")  

        ###スクロール値管理用Cameraを準備
        self.camera = Camera(0, 0, pyxel.width, pyxel.height, 1.0)
        ###拡張機能のインスタンス生成
        self.ext = PyxelExtended()
        ###パーティクルシステムインスタンス用の配列を準備
        self.psys_instances = list()
        ###WaterSurfaceEffectインスタンスの生成 for WATER-DOOR
        self.wse = WaterSurfaceEffect(0, 0, 600, 200)
        ###ゲームステート管理インスタンス
        self.gamestate = GameState()
        self.gamestate.mode = C_PLAY ##モードをPLAYに設定
        self.gamestate.scene = C_SCENE_HOME ##シーンをホームに設定
        self.gamestate.scenetimer = 0

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

        ###シーンの切り替わりに合わせて、BGMを選択するための変数
        self.prescene = 9
        # self.nowscene = self.gamestate.scene

        ### オブジェクトの自動移動中判断用変数
        self.object_pos_update_frames = 0

        # self.play_music()
        #game実行
        pyxel.run(self.update, self.draw)

    def update(self):
        self.checkSceneMusic()
        ###PLAYモード共通
        if (self.gamestate.mode == C_PLAY):
            if(self.gamestate.door_transition):
                for particle in door_tran_particles[0]:
                    particle.update()
            else:
                ### object_pos_update_framesが残ってるとき、デクリメント
                if self.object_pos_update_frames > 0:
                    self.object_pos_update_frames -= 1
                ### gamestate更新
                # self.gamestate.scenario[0][0] = self.gamestate.scene
                self.gamestate.scenetimer += 1
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
                # ###space打鍵によるチェックが走っていないとき（キャラ操作可能時）に左右キーでのスクロールが有効化される
                if not(self.pressed_space_checking):
                    # 左パララックススクロール背景のため、左右キーの入力を読み取り、その方向を更新。
                    ## ただし、ほかキー入力が同時にあった場合は移動を行わず立ち止まって向きを変えるキャラクタ操作仕様に合わせるため、該当時はスクロール方向を0にする
                    if (0 < self.player.x <= (300 - self.player.width)) and (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)):
                        self.scroll_direction = -1
                        if (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)):
                            self.scroll_direction = 0
                            self.player.moving = False
                    elif (0 <= self.player.x < (300 - self.player.width)) and (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)):
                        self.scroll_direction = 1
                        if (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)):
                            self.scroll_direction = 0
                            self.player.moving = False
                    else:
                        self.scroll_direction = 0
                        self.player.moving = False
                ###cameraのupdate
                self.camera.update(self.player.x, self.player.y, C_MAP_WIDTH, C_MAP_HEIGHT)
                ### すべてのオブジェクトをまとめなおす
                self.all_objects = list()
                self.all_objects += doors + characters + ataris
                # if self.gamestate.scene == C_SCENE_MOON:
                #     self.all_objects += self.fireworks
                if self.gamestate.scene == C_SCENE_FIRE:
                    self.all_objects += self.lantans + self.points3d  
                if self.gamestate.scene == C_SCENE_WATER:
                    self.all_objects += self.water_trees
                if self.gamestate.scene == C_SCENE_WOOD:
                    self.all_objects += self.trees + self.grasses + self.flowers
                if self.gamestate.scene == C_SCENE_GOLD:    
                    self.all_objects += self.elliptical_orbits + self.segments
                #cameraの位置を編集オブジェクト群に反映
                for obj in self.all_objects:
                    self.camera.apply(obj)
                ###doorsのupdate
                for door in doors:
                    door.update()
                ###保持キャラクターリストのupdate
                for baseelem in characters:
                    baseelem.update()
                    ###playerと指定オブジェクトとの衝突判定とスクロールキャンセル
                    if baseelem.is_playing:
                        self.check_collision(baseelem, [characters, doors, ataris])
                ### parallax各背景レイヤーのスクロール位置を更新
                if pyxel.width/2 <= self.player.position_x <= C_MAP_WIDTH - pyxel.width/2:
                    for i in range(9):
                        self.scroll_positions[i] += self.scroll_direction * self.scroll_speeds[i]
                ###プレーヤーオブジェクトとその他のcheckable（＝調べることが可能な）オブジェクト群の位置関係を確認し、
                ###最も近い位置にあるcheckableオブジェクトとの向きを含む隣接状態を捕捉。
                self.updateObjectsPositionCheck()
                ###特定のオブジェクト種別に対し予め関連する手元の保持アイテム数をチェックしておく。
                if self.nearest_obj.__class__.__name__ in("Atari"):
                    ### 手元の保持アイテム数をチェックし、最も近い位置にある特定番号オブジェクトの返却テキストフラグを操作する
                    self.checkInvSysItem(self.nearest_obj)
                ###入力検知の遅延用カウンタを更新（ボタン打鍵の瞬間の連続検知を防ぐ）
                if(self.inputdelay_cnt > 0):
                    self.inputdelay_cnt -= 1
                ###移動キー有効（スクロール有効）でないときだけボタン入力を検知
                if((self.inputdelay_cnt == 0)and(self.scroll_direction == 0)):
                    ###panningじゃないときだけ受付ける
                    if not(self.camera.panning):
                        ###ボタン入力を検知する
                        self.updateBtnInputCheck()
                ###表示が必要なテキスト情報を保持していた場合、表示に必要な分割処理を行う。
                self.updateTextDivide()
                ###Y軸を基準にしたdraw用オブジェクトリストを作成
                self.wk_objectDrawlistBasedAxisY = characters
                self.wk_objectDrawlistBasedAxisY.sort(key=lambda obj: obj.position_y)
                ###doorsのうち最もy軸の高さが大きなものを捕捉
                doors_max_y = 0
                for door in doors:
                    if door.y > doors_max_y:
                        doors_max_y = door.y
                ###移動可能領域の画面上端からの距離をdoorsの位置に指定（基本）
                if not(self.player.able_moving_top == doors_max_y):
                    self.player.able_moving_top = doors_max_y
                ###シーンごとの処理
                if (self.gamestate.scene == C_SCENE_HOME):
                    self.updateHomeScene()
                elif (self.gamestate.scene == C_SCENE_MOON):
                    self.updateMoonScene()
                elif (self.gamestate.scene == C_SCENE_FIRE):
                    self.updateFireScene()
                elif (self.gamestate.scene == C_SCENE_WATER):
                    self.updateWaterScene()
                elif (self.gamestate.scene == C_SCENE_WOOD):
                    if not(self.player.able_moving_top == 100):
                        self.player.able_moving_top = 100
                    self.updateWoodScene()
                elif (self.gamestate.scene == C_SCENE_GOLD):
                    self.updateGoldScene()
                elif (self.gamestate.scene == C_SCENE_SOIL):
                    self.updateSoilScene()
                elif (self.gamestate.scene == C_SCENE_SUN):
                    self.updateSunScene()
                # elif (self.gamestate.scene == C_SCENE_END):
                    # self.updateEndScene()
    
        ###MENUモード共通 ================================
        if (self.gamestate.mode == C_MENU):
            # self.invsys.update()                    
            ###入力検知の遅延用カウンタ（ボタン打鍵の瞬間の連続検知を防ぐ）
            if(self.inputdelay_cnt > 0):
                self.inputdelay_cnt -= 1
            ###スクロールが働いていないときだけボタン入力を検知する
            if((self.inputdelay_cnt == 0)and(self.scroll_direction == 0)):
                ###ボタン入力の検知
                self.updateBtnInputCheck()

        if (self.gamestate.mode == C_DEAD):
            ###入力検知の遅延用カウンタ（ボタン打鍵の瞬間の連続検知を防ぐ）
            if(self.inputdelay_cnt > 0):
                self.inputdelay_cnt -= 1
            ###スクロールが働いていないときだけボタン入力を検知する
            if((self.inputdelay_cnt == 0)and(self.scroll_direction == 0)):
                ###ボタン入力の検知
                self.updateBtnInputCheck()

    ### AtariオブジェクトのVisibleフラグを操作する
    def switchAtariVisible(self, obj_no_list, flg):
        for atari in ataris:
            if atari.obj_no in obj_no_list:
                atari.is_visible = flg

    ### DoorオブジェクトのVisibleフラグを操作する
    def switchDoorVisible(self, flg):
        for door in doors:
                door.visible = flg

    def check_collision(self, base_elem, target_list):
        for target in target_list:
            self.playerUpdateColisionCheckAndScrollCancel(base_elem, target)

    def draw(self):
        if(self.gamestate.mode == C_PLAY):
            ###ドアトランジションが有効で、オブジェクト自動移動中フレーム残がなく、接触中のオブジェクトがDoorかつ接触中オブジェクトとの距離が10以下のとき
            if(self.gamestate.door_transition) :
                if self.gamestate.door_transition_radius < self.gamestate.door_transition_radius_max:
                    ###中心から黒の円を描画。
                    pyxel.circ(150, 150, self.gamestate.door_transition_radius, 0)
                    self.gamestate.door_transition_radius += 3
                    for particle in door_tran_particles[0]:
                        particle.draw()
                else:
                    self.gamestate.door_transition_radius = 1
                    self.gamestate.door_transition = False
                    door_tran_particles.clear()
            else:
                wk_player_moving = self.player.moving
                ###背景描画
                self.drawBG()
                ###オブジェクト描画
                self.drawObjects()
                ###updateで並び替えたオブジェクトリストを順にdrawする
                for obj in self.wk_objectDrawlistBasedAxisY:
                    ###描画後
                    obj.draw()
                ###特定のオブジェクト種別に対しplayer上にフキダシを表示する
                if self.nearest_obj.__class__.__name__ in("Character", "Atari", "Door", "Jerry"):
                    if self.nearest_obj.flg_reaction:
                        ###フキダシ表示
                        ### テキスト表示中ではないときだけ
                        if self.pressed_space_checking == False:
                            if self.nearest_obj.__class__.__name__ in("Atari"):
                                if self.nearest_obj.is_visible:
                                    pyxel.blt(self.player.draw_x, self.player.draw_y -14, 0, 72, 0, 16, 16, 3)
                                    ###フキダシ内のアイコン表示（？マーク）
                                    pyxel.blt(self.player.draw_x +5, self.player.draw_y -12, 0, 72, 16 + 10 * (pyxel.frame_count // 6 % 3), 7, 10, 3)
                            if self.nearest_obj.__class__.__name__ in("Character", "Jerry"):
                                pyxel.blt(self.player.draw_x, self.player.draw_y -14, 0, 72, 0, 16, 16, 3)
                                ###フキダシ内のアイコン表示（！マーク）
                                pyxel.blt(self.player.draw_x +6, self.player.draw_y -12, 0, 79, 16 + 10 * (pyxel.frame_count // 6 % 3), 4, 10, 3)
                            if self.nearest_obj.__class__.__name__ in("Door"):
                                ###ドアが可視状態のときのみ、フキダシ内のアイコン表示（！マーク）
                                if (self.nearest_obj.visible):
                                    pyxel.blt(self.player.draw_x, self.player.draw_y -14, 0, 72, 0, 16, 16, 3)
                                    ###フキダシ内のアイコン表示（！マーク）
                                    pyxel.blt(self.player.draw_x +6, self.player.draw_y -12, 0, 79, 16 + 10 * (pyxel.frame_count // 6 % 3), 4, 10, 3)
                ###前景＋メニューエリアの描画
                self.drawFT(wk_player_moving)
                ###スペースキー打鍵chkフラグON状態のときに、捕捉中のdisptimesに分けて、メッセージを画面表示する。
                self.drawMessageAndWindow()
        elif(self.gamestate.mode == C_MENU):
            ###Menu画面の描画
            self.drawMenu()
        ###デバッグ用デモタイトル表示
        ####pyxel.rect(6, 2, 42, 37, 1)
        ####self.bdf2.draw_text(10, 2, self.getModeName(), 7) 
        ####self.bdf2.draw_text(10,14, self.getSceneName(), 7)            
        ####self.bdf2.draw_text(10,26, self.getScenarioAndBranchNum(), 7)    
        elif(self.gamestate.mode == C_DEAD):
            ### 画面を真っ黒にする
            pyxel.cls(0)
            ### 中央に「GAME OVER」を表示
            pyxel.text(150 - 30, 150 - 4, "GAME OVER", 7)
            ### 「’R’キーで再開」を表示
            pyxel.text(150 - 30, 150 + 4, "'R' to restart", 7)

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
            self.wk_objectDrawlistBasedAxisY = list()
            ###取得したテキストセットを扱うための変数
            self.wk_textset = list()
            # text分割処理にかかる変数
            self.text_divided = False # テキスト分割処置の完了済のフラグ
            self.wk_textset_divided = list() # 初期化。textDivideにて整形。
            self.wk_text_divided_remain = 0
            self.display_cnt = 0
            self.display_finished = False
            self.wk_text_disp_times = 1 ##分割編集済みのテキストを表示した回数の●回目初期値
            self.wk_textset3 = list()
            ###テキストと同時に表示する顔グラ判別用ワーク
            self.talking_chara_no = 0
            self.talking_chara_face_no = 0
            ###話しかけた・調べた対象オブジェクトの向いている方向を変更する際、従前方向を記憶するwk変数
            self.checking_obj_direction = 4 ### リセット用初期値。４方向(0123:上下左右)のどれでもない
            self.position_buffer = 10 ###隣接状態と判定する境界エリア幅
            ###最も近いオブジェクトを格納する変数
            self.nearest_obj = None
            ###最も近いオブジェクトとの距離を格納する変数
            self.nearest_obj_distancetoPlayer = 999
            ###フキダシ表示用の座標変数
            self.fukidashi_nearest_obj_x = 0
            self.fukidashi_nearest_obj_y = 0
            ###テキスト表示用変数
            self.hint_text = ""
            self.hint_text_divided = list()
            self.framecount_for_text_disp_first = 0
            self.framecount_for_text_disp = 0
            self.framecount_for_text_disp1 = 0
            self.framecount_for_text_disp2 = 0
            self.framecount_for_text_disp3 = 0


        ### 冒頭
        if(self.gamestate.scene == C_SCENE_HOME):
            # 各レイヤーのスクロール速度を設定
            self.parallax_value_set(self.gamestate.scene)
            # 各レイヤーのスクロール位置を初期化
            self.scroll_positions = [0.1 for _ in range(9)]
            ###SCENE:MOON用
            self.fireworks = list()
            self.moons = list()
            ###SCENE:FIRE用
            self.points3d = list()
            self.lantans = list()
            ###SCENE:WATER用
            self.fishdx01 = 100
            self.fishdy01 = 100
            self.fishdx02 = 220
            self.fishdy02 = 150
            self.fishdx03 = 340
            self.fishdy03 = 80
            self.fishdx04 = 410
            self.fishdy04 = 130
            self.fishdx05 = 550
            self.fishdy05 = 230
            self.frogx = 160
            self.frogy = 180
            ###SCENE:WOOD用
            self.trees = list()
            self.grasses = list()
            self.flowers = list()
            ###SCENE:GOLD用
            self.elliptical_orbits = list()
            self.segments = list()
            self.sandfall_num = 8 #砂の滝の数
            self.sandfall_points = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.sandx = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.sandy = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.width = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.times = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.sand_frame = [0, 0, 0, 0] #4frame周期
            self.girlsidx01 = 0
            self.girlsidx02 = 0
            ###SCENE:SOIL用
            self.butterflies = list()
            self.sunlines = list()
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
                (self.gamestate.scene == C_SCENE_SUN) or  \
                (self.gamestate.scene == C_SCENE_END):
                    #プレイヤーオブジェクトを生成
                    self.player = Character(1,30,150,3,True)
                    characters.append(self.player) ###キャラクター・オブジェクトリストに追加
                    ### 画面上部から移動可能領域までのマージンを再設定
                    if (self.gamestate.scene in(C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN, C_SCENE_END)):
                        self.player.able_moving_top = 16 * 2 - 8
                    if (self.gamestate.scene == C_SCENE_WOOD):
                        self.player.able_moving_top = 100
                    ### ドアオブジェクトの生成
                    if (self.gamestate.scene in(C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN, C_SCENE_END)):
                        self.generateDoor()
                    ###月オブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_MOON):
                        self.generateUniqueObjectsInMoon()
                    ###火オブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_FIRE):
                        self.generateUniqueObjectsInFire()
                    ###水オブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_WATER):
                        self.generateUniqueObjectsInWater()
                    ###木オブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_WOOD):
                        self.generateUniqueObjectsInWood()
                    ###金オブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_GOLD):
                        self.generateUniqueObjectsInGold()
                    ###土オブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_SOIL):
                        self.generateUniqueObjectsInSoil()
                    ###日オブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_SUN):
                        self.generateUniqueObjectsInSun()
                    ###エンディングオブジェクトを生成
                    if (self.gamestate.scene == C_SCENE_END):
                        self.generateUniqueObjectsInEnd()

    def generateUniqueObjectsInHome(self):
        #プレイヤーオブジェクトを生成
        self.player = Character(1,0,150,3,True)
        characters.append(self.player) ###キャラクター・オブジェクトリストに追加
        #キャラクターオブジェクトを生成
        self.charactor01 = Character(0,200,150,2,False)
        characters.append(self.charactor01) ###キャラクター・オブジェクトリストに追加
        ###Doorオブジェクトを生成
        self.generateDoor()
        ###背景用当たり判定インスタンス群生成
        self.atari001 = Atari(116, 8 * 17 -5, 0, C_SCENE_HOME, C_VISIBLE) ## 横断歩道の歩行者用信号機
        self.atari002 = Atari(333, 8 * 17 -5, 1, C_SCENE_HOME, C_VISIBLE) ## バス停
        self.atari003 = Atari(274, 8 * 17 -5, 2, C_SCENE_HOME, C_VISIBLE) ## 看板（小）
        self.atari004 = Atari(450, 220,       3, C_SCENE_HOME, C_INVISIBLE) ## 猫
        self.atari025   = Atari(15, 135, 25, C_SCENE_HOME, C_VISIBLE) ## 神棚
        ###背景用当たり判定リストに追加
        ataris.append(self.atari001)
        ataris.append(self.atari002)
        ataris.append(self.atari003)
        ataris.append(self.atari004)
        ataris.append(self.atari025)

    def generateUniqueObjectsInMoon(self):
        ###月オブジェクトを生成
        self.moon01 = Moon(150, 70, 50, 0.001)
        self.moons.append(self.moon01)
        ###キャラクターオブジェクトを生成
        self.charactor01 = Character(2,320,160,2,False) #Michi
        characters.append(self.charactor01) ###キャラクター・オブジェクトリストに追加
        #キャラクターオブジェクトを生成
        self.charactor02 = Character(0,130,160,2,False) #Kana
        characters.append(self.charactor02) ###キャラクター・オブジェクトリストに追加
        ###背景用当たり判定インスタンス群
        self.atari007   = Atari(544, 168,  7, C_SCENE_MOON, C_VISIBLE) ## 木の幹03
        self.atari008   = Atari(563, 168,  8, C_SCENE_MOON, C_VISIBLE) ## 木の幹04
        self.atari02401 = Atari( 30, 170, 24, C_SCENE_MOON, C_VISIBLE) ## 灯籠01
        self.atari02402 = Atari(150, 170, 24, C_SCENE_MOON, C_VISIBLE) ## 灯籠01
        self.atari02403 = Atari(270, 170, 24, C_SCENE_MOON, C_VISIBLE) ## 灯籠01
        self.atari02404 = Atari(390, 170, 24, C_SCENE_MOON, C_VISIBLE) ## 灯籠01

        self.atari025   = Atari(215, 165, 25, C_SCENE_MOON, C_VISIBLE) ## 神棚
        
        ###背景用当たり判定リストに追加
        ataris.append(self.atari007)
        ataris.append(self.atari008)
        ataris.append(self.atari02401)
        ataris.append(self.atari02402)
        ataris.append(self.atari02403)
        ataris.append(self.atari02404)
        ataris.append(self.atari025)
    
    def generateUniqueObjectsInFire(self):
        ###蛍オブジェクトを生成
        self.points3d.append(Point3D(center_x=150, center_y=150, center_z=0, radius=100, num_points=40, speed_low=2, speed_high=4, life_low=50, life_high=100, randini=True, pallete=0, cacheflg=False, scene=self.gamestate.scene))
        self.atari010 = Atari(120, 130, 10, C_SCENE_FIRE, C_INVISIBLE) ## 
        ataris.append(self.atari010)
        self.atari025 = Atari(215, 130, 25, C_SCENE_FIRE, C_VISIBLE) ## 神棚
        ataris.append(self.atari025)
        ###さざれ石オブジェクトを生成
        self.atari026 = Atari(320, 120, 26, C_SCENE_FIRE, C_VISIBLE) ## さざれ石
        ataris.append(self.atari026)
        #キャラクターオブジェクトを生成
        self.charactor02 = Character(0,230,160,2,False) #Kana
        characters.append(self.charactor02) ###キャラクター・オブジェクトリストに追加
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

    def generateUniqueObjectsInWater(self):
        ###くらげ生成
        self.jerry01 = Jerry(168,116,90)
        characters.append(self.jerry01) ###キャラクター・オブジェクトリストに追加
        #キャラクターオブジェクトを生成
        self.charactor02 = Character(0,130,160,2,False) #Kana
        characters.append(self.charactor02) ###キャラクター・オブジェクトリストに追加
        ###水シーン用のTreeオブジェクト(drawFT用)を生成
        self.water_trees = list()
        self.atari025   = Atari(235, 135, 25, C_SCENE_WATER, C_VISIBLE) ## 神棚
        ataris.append(self.atari025)
        # アイテム取得用Atariオブジェクトをセット（デフォルトでinvisible）
        self.atari027 = Atari(100, 120, 27, C_SCENE_WATER, C_INVISIBLE) ### 水ステージ探しもの用（ハズレ）
        self.atari028 = Atari(260, 120, 28, C_SCENE_WATER, C_INVISIBLE) ### 水ステージ探しもの用（ハズレ：体力減）
        self.atari029 = Atari(380, 120, 29, C_SCENE_WATER, C_INVISIBLE) ### 水ステージ探しもの用（クラゲずかん）
        self.atari030 = Atari(470, 120, 30, C_SCENE_WATER, C_INVISIBLE) ### 水ステージ探しもの用（古い手鏡）
        self.atari031 = Atari(550, 120, 31, C_SCENE_WATER, C_INVISIBLE) ### 水ステージ探しもの用（サファイアのイヤリング）
        self.atari032 = Atari( 80, 200, 32, C_SCENE_WATER, C_INVISIBLE) ### 水ステージ探しもの用（小さなガラス瓶）
        self.atari033 = Atari(220, 230, 33, C_SCENE_WATER, C_INVISIBLE) ### 甘い水の実
        ataris.append(self.atari027)
        ataris.append(self.atari028)
        ataris.append(self.atari029)
        ataris.append(self.atari030)
        ataris.append(self.atari031)
        ataris.append(self.atari032)
        ataris.append(self.atari033)
        # 木の生成
        self.water_trees.append(WaterTree(60,10))
        self.water_trees.append(WaterTree(90,8))
        self.water_trees.append(WaterTree(140,9))
        self.water_trees.append(WaterTree(230,8))
        # self.water_trees.append(WaterTree(290,10))
        # self.water_trees.append(WaterTree(320,9))
        self.water_trees.append(WaterTree(350,8))
        self.water_trees.append(WaterTree(410,8))
        self.water_trees.append(WaterTree(430,9))
        self.water_trees.append(WaterTree(530,10))
        ###パーティクルシステムを生成
        for _ in range(0,3):
            self.psys_instances.append(ParticleSystem())
        ###パーティクルシステムを初期化
        colors = [7,7,7]
        self.psys_instances[0].activate(
            active_duration=999999999, spawn_interval=17, total_spawns=999999999,
            x=80, y=260, #particle放射の中心座標
            width=600, height=500, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
            num_particles=14, ##一度に放射するパーティクルの数
            pattern=0, ##放射particle形状の指定(0:Dot型)
            size=6, ##Dot型以外で使用されるパーティクルサイズ
            color=colors[0], #particleの色
            speed_range=1,
            direction=12
        )
        self.psys_instances[1].activate(
            active_duration=999999999, spawn_interval=10, total_spawns=999999999,
            x=150, y=260, #particle放射の中心座標
            width=600, height=500, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
            num_particles=12, ##一度に放射するパーティクルの数
            pattern=0, ##放射particle形状の指定(0:Dot型)
            size=1, ##Dot型以外で使用されるパーティクルサイズ
            color=colors[1], #particleの色
            speed_range=1,
            direction=12
        )
        self.psys_instances[2].activate(
            active_duration=999999999, spawn_interval=16, total_spawns=999999999,
            x=220, y=260, #particle放射の中心座標
            width=600, height=500, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
            num_particles=15, ##一度に放射するパーティクルの数
            pattern=0, ##放射particle形状の指定(0:Dot型)
            size=4, ##Dot型以外で使用されるパーティクルサイズ
            color=colors[2], #particleの色
            speed_range=1,
            direction=12
        )


    def generateUniqueObjectsInWood(self):
        ###キャラクターオブジェクトを生成
        self.charactor01 = Character(5,374,95,2,False) #GIRAN
        self.charactor01.collision_width = 16
        self.charactor01.collision_height = 8
        characters.append(self.charactor01) ###キャラクター・オブジェクトリストに追加
        #キャラクターオブジェクトを生成
        self.charactor02 = Character(0,130,160,2,False) #Kana
        characters.append(self.charactor02) ###キャラクター・オブジェクトリストに追加
        ###木オブジェクトを生成 : x=50, y=100, 葉の数=90, 茂みの半径=30
        self.tree01 = Tree(150, 100, 110, 30)
        self.tree02 = Tree(250, 100, 155, 40)
        self.tree03 = Tree(330, 60, 70, 27)
        self.tree04 = Tree( 60, 50, 75, 30)
        self.tree05 = Tree(410, 55, 100, 35)
        self.tree06 = Tree(520, 55, 135, 40)
        # Tree上の葉の座標を1発目更新
        self.tree01.update() 
        self.tree02.update() 
        self.tree03.update() 
        self.tree04.update()
        self.tree05.update()
        self.tree06.update()
        ###木オブジェクトをリストに追加
        self.trees.append(self.tree01)
        self.trees.append(self.tree02)
        self.trees.append(self.tree03)
        self.trees.append(self.tree04)
        self.trees.append(self.tree05)
        self.trees.append(self.tree06)
        ###背景用当たり判定インスタンス群
        self.atari005 = Atari(160, 167, 4, C_SCENE_WOOD, C_INVISIBLE) ## 木の幹01
        self.atari006 = Atari(260, 167, 5, C_SCENE_WOOD, C_INVISIBLE) ## 木の幹02
        self.atari025   = Atari(535, 135, 25, C_SCENE_WOOD, C_VISIBLE) ## 神棚
        ###背景用当たり判定リストに追加
        ataris.append(self.atari005)
        ataris.append(self.atari006)
        ataris.append(self.atari025)
        ###草オブジェクトを生成 : x=10, y=230, 距離=150, 最小の高さ=20, 最大の高さ=50, 草の本数=30
        self.grass01 = Grass(0, 240, 600, 20, 60, 150)
        self.grasses.append(self.grass01)
        ###花オブジェクトを生成
        # Stemをランダムな位置に生成
        for _ in range(14):
            x = Random.randint(10, 550)  # X座標を10から550の間でランダムに選択
            height = Random.randint(40, 60)  # 高さを40から60の間でランダムに選択
            flower = Stem(x, 240, height)
            flower.update_tip() # 花の先端の座標を更新
            self.flowers.append(flower)
        ###パーティクルシステムを生成
        for _ in range(0,3):
            self.psys_instances.append(ParticleSystem())
        ###パーティクルシステムを初期化
        colors = [14,11,10]
        self.psys_instances[0].activate(
            active_duration=999999999, spawn_interval=20, total_spawns=999999999,
            x=-40, y=110, #particle放射の中心座標
            width=600, height=300, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
            num_particles=8, ##一度に放射するパーティクルの数
            pattern=1, ##放射particle形状の指定(0:Dot型)
            size=1, ##Dot型以外で使用されるパーティクルサイズ
            color=colors[0], #particleの色
            speed_range=1,
            direction=3
        )
        self.psys_instances[1].activate(
            active_duration=999999999, spawn_interval=18, total_spawns=999999999,
            x=-40, y=70, #particle放射の中心座標
            width=600, height=300, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
            num_particles=8, ##一度に放射するパーティクルの数
            pattern=1, ##放射particle形状の指定(0:Dot型)
            size=1, ##Dot型以外で使用されるパーティクルサイズ
            color=colors[1], #particleの色
            speed_range=1,
            direction=3
        )
        self.psys_instances[2].activate(
            active_duration=999999999, spawn_interval=18, total_spawns=999999999,
            x=-40, y=90, #particle放射の中心座標
            width=600, height=300, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
            num_particles=15, ##一度に放射するパーティクルの数
            pattern=0, ##放射particle形状の指定(0:Dot型)
            size=1, ##Dot型以外で使用されるパーティクルサイズ
            color=colors[2], #particleの色
            speed_range=1,
            direction=3
        )
            
    def generateUniqueObjectsInGold(self):
        ###キャラクターオブジェクトを生成
        self.charactor01 = Character(6,310,95,2,False) #LUV
        self.charactor01.collision_width = 16
        self.charactor01.collision_height = 16
        characters.append(self.charactor01) ###キャラクター・オブジェクトリストに追加
        #キャラクターオブジェクトを生成
        self.charactor02 = Character(0,130,160,2,False) #Kana
        characters.append(self.charactor02) ###キャラクター・オブジェクトリストに追加
        self.visualizer  = EchoChamberVisualizer(x_center=65,  y_center=200, r=30, treeangle=30, max_depth=10, polygon_sides=6, external=False)
        self.visualizer2 = EchoChamberVisualizer(x_center=450, y_center=200, r=30, treeangle=30, max_depth=10, polygon_sides=8, external=True)
        self.visualizer3 = EchoChamberVisualizer(x_center=320, y_center= 80, r=30, treeangle=30, max_depth=10, polygon_sides=10, external=False)
        self.visualizer4 = EchoChamberVisualizer(x_center=190, y_center=160, r=30, treeangle=30, max_depth=10, polygon_sides=7, external=True)
        self.visualizer5 = EchoChamberVisualizer(x_center=500, y_center=210, r=30, treeangle=30, max_depth=10, polygon_sides=9, external=False)

        self.segments.append(self.visualizer)
        self.segments.append(self.visualizer2)
        self.segments.append(self.visualizer3)
        self.segments.append(self.visualizer4)
        self.segments.append(self.visualizer5)

        point_a_x, point_a_y = 0, 0  # This is just the center of the screen
        point_b = EllipticalOrbit(point_a_x, point_a_y, 40, 30, Math.radians(45), 0.03, pyxel.COLOR_RED)
        point_c = EllipticalOrbit(point_b.x, point_b.y, 20, 20, 0, 0.05, pyxel.COLOR_GREEN, parent=point_b)
        self.elliptical_orbits.append(point_c)
        self.elliptical_orbits.append(point_b)

        ###背景用当たり判定インスタンス群
        # # self.atari009 = Atari(self.elliptical_orbits[0].pjtx, self.elliptical_orbits[0].pjty, 7, C_SCENE_GOLD, C_VISIBLE) ## girls 
        # self.atari009 = Atari(140, 145, 9, C_SCENE_GOLD, C_VISIBLE) ## girls
        # self.atari009.collision_width = 8
        # self.atari009.collision_height = 8
        # ###背景用当たり判定リストに追加
        # ataris.append(self.atari009)
        self.atari022 = Atari(210, 116, 22, C_SCENE_GOLD, C_INVISIBLE) ## 宝石
        self.atari023 = Atari(514, 120, 23, C_SCENE_GOLD, C_INVISIBLE) ## 剣
        self.atari025   = Atari(175, 120, 25, C_SCENE_GOLD, C_VISIBLE) ## 神棚
        ataris.append(self.atari022)
        ataris.append(self.atari023)
        ataris.append(self.atari025)        
    
       
    def generateUniqueObjectsInSoil(self):
        ###キャラクターオブジェクトを生成
        self.charactor01 = Character(7,210,160,2,False) #LIKI
        characters.append(self.charactor01) ###キャラクター・オブジェクトリストに追加
        #キャラクターオブジェクトを生成
        self.charactor02 = Character(0,255,177,2,False) #Kana
        characters.append(self.charactor02) ###キャラクター・オブジェクトリストに追加
        ###蝶を生成
        self.butterfly01 = Butterfly(100, 120, 300, 200, 0)
        self.butterfly02 = Butterfly(200, 140, 400, 250, 1)
        self.butterfly03 = Butterfly(300, 110, 500, 200, 1)
        self.butterfly04 = Butterfly( 50, 130, 350, 200, 0)
        self.butterfly05 = Butterfly(340, 130, 580, 220, 1)
        self.butterfly06 = Butterfly(450, 150, 590, 240, 0)
        
        self.butterflies.append(self.butterfly01)
        self.butterflies.append(self.butterfly02)
        self.butterflies.append(self.butterfly03)
        self.butterflies.append(self.butterfly04)
        self.butterflies.append(self.butterfly05)
        self.butterflies.append(self.butterfly06)
        

        ###MovingLineオブジェクトを生成
        self.movinglines01 = MovingLines(180,-240,110,230,60,30,18,[13, 7, 15, 10],150,230)
        self.movinglines02 = MovingLines(465,-260,395,230,70,30,20,[13, 7, 15, 10],180,250)
        self.movinglines03 = MovingLines(565,-260,495,230,70,30,11,[13, 7, 15, 10],170,230)
        self.sunlines.append(self.movinglines01)
        self.sunlines.append(self.movinglines02)
        self.sunlines.append(self.movinglines03)

        self.atari016 = Atari( 32, 165, 16, C_SCENE_SOIL, C_INVISIBLE) ##柱
        self.atari017 = Atari(182, 165, 16, C_SCENE_SOIL, C_INVISIBLE) ##柱
        self.atari018 = Atari(292, 165, 16, C_SCENE_SOIL, C_INVISIBLE) ##柱
        self.atari019 = Atari(442, 165, 16, C_SCENE_SOIL, C_INVISIBLE) ##柱
        self.atari020 = Atari(572, 165, 16, C_SCENE_SOIL, C_INVISIBLE) ##柱
        self.atari021 = Atari( 55, 130, 17, C_SCENE_SOIL, C_INVISIBLE) ##犬
        ###墓石の墓標
        self.atari022 = Atari(100, 118, 18, C_SCENE_SOIL, C_VISIBLE) ##墓石 1
        self.atari023 = Atari(160, 118, 19, C_SCENE_SOIL, C_VISIBLE) ##墓石 2
        self.atari024 = Atari(260, 118, 20, C_SCENE_SOIL, C_VISIBLE) ##墓石 3
        self.atari025 = Atari(360, 118, 21, C_SCENE_SOIL, C_VISIBLE) ##墓石 4

        self.atari035   = Atari(535, 120, 25, C_SCENE_SOIL, C_VISIBLE) ## 神棚

        ###背景用当たり判定リストに追加
        ataris.append(self.atari016)
        ataris.append(self.atari017)
        ataris.append(self.atari018)
        ataris.append(self.atari019)
        ataris.append(self.atari020)
        ataris.append(self.atari021)
        ###墓石の墓標
        ataris.append(self.atari022)
        ataris.append(self.atari023)
        ataris.append(self.atari024)
        ataris.append(self.atari025)
        ###神棚
        ataris.append(self.atari035)




    def generateUniqueObjectsInSun(self):
        ###パーティクルシステムを生成
        for _ in range(0,2):
            self.psys_instances.append(ParticleSystem())
        ###パーティクルシステムを初期化
        self.psys_instances[0].activate(
            active_duration=999999999, spawn_interval=5, total_spawns=999999999,
            x=90, y=-40, #particle放射の中心座標
            width=500, height=300, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
            num_particles=10, ##一度に放射するパーティクルの数
            pattern=1, ##放射particle形状の指定(0:Dot型)
            size=1, ##Dot型以外で使用されるパーティクルサイズ
            color=7, #particleの色
            speed_range=1,
            direction=7
        )
        self.psys_instances[1].activate(
            active_duration=999999999, spawn_interval=5, total_spawns=999999999,
            x=300, y=-40, #particle放射の中心座標
            width=500, height=300, ##正方エリア内放射パターンで使用されるエリアサイズ指定変数
            num_particles=10, ##一度に放射するパーティクルの数
            pattern=1, ##放射particle形状の指定(0:Dot型)
            size=1, ##Dot型以外で使用されるパーティクルサイズ
            color=7, #particleの色
            speed_range=1,
            direction=7
        )
        ###背景用当たり判定インスタンス群
        self.atari007 = Atari(320, 130,  6, C_SCENE_SUN, C_INVISIBLE) ## ストーブ＆ヤカン 
        self.atari008 = Atari(320, 135,  6, C_SCENE_SUN, C_INVISIBLE) ## 当たり判定の拡張のためのダミー
        self.atari011 = Atari(507, 130, 11, C_SCENE_SUN, C_VISIBLE) ## 本 
        self.atari012 = Atari( 25, 125, 12, C_SCENE_SUN, C_VISIBLE) ## アイアンシェルフ
        self.atari013 = Atari(100, 120, 13, C_SCENE_SUN, C_INVISIBLE) ## ブルー
        self.atari014 = Atari( 80, 145, 14, C_SCENE_SUN, C_INVISIBLE) ##積んだ本 
        self.atari015 = Atari( 80, 141, 14, C_SCENE_SUN, C_INVISIBLE) ##当たり判定拡張のためのダミー 
        self.atari025   = Atari(230, 120, 25, C_SCENE_SUN, C_VISIBLE) ## 神棚
        ###背景用当たり判定リストに追加
        ataris.append(self.atari007)
        ataris.append(self.atari008)
        ataris.append(self.atari011)
        ataris.append(self.atari012)
        ataris.append(self.atari013)
        ataris.append(self.atari014)
        ataris.append(self.atari015)
        ataris.append(self.atari025)

        #キャラクターオブジェクトを生成
        self.charactor02 = Character(0,130,160,2,False) #Kana
        characters.append(self.charactor02) ###キャラクター・オブジェクトリストに追加
    
    def generateUniqueObjectsInEnd(self):
        ###キャラクターオブジェクトを生成
        self.charactor01 = Character(11,150,160,2,False)
        self.charactor01.collision_width = 32
        self.charactor01.collision_height = 28
        characters.append(self.charactor01) ###キャラクター・オブジェクトリストに追加
        #キャラクターオブジェクトを生成
        self.charactor02 = Character(0,40,160,2,False) #Kana
        characters.append(self.charactor02) ###キャラクター・オブジェクトリストに追加

    def deleteObjectsDependingOnScene(self):
        ###PLAYモードにおけるシーン別オブジェクト削除
        if (self.gamestate.mode == C_PLAY):
            if (self.gamestate.scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_FIRE ,C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN, C_SCENE_END)):
                ###Doorオブジェクトを削除
                doors.clear()
                ###キャラクターオブジェクトを削除
                characters.clear()
                ###背景用当たり判定リストを削除
                ataris.clear()
            if (self.gamestate.scene == C_SCENE_FIRE):
                self.points3d.clear()
                self.lantans.clear()
                self.psys_instances.clear()
            if (self.gamestate.scene == C_SCENE_WATER):
                self.psys_instances.clear()
            if (self.gamestate.scene == C_SCENE_WOOD):
                self.trees.clear()
                self.grasses.clear()
                self.flowers.clear()
                self.psys_instances.clear()
            if (self.gamestate.scene == C_SCENE_GOLD):
                self.elliptical_orbits.clear()
                self.segments.clear()
            if (self.gamestate.scene == C_SCENE_SOIL):
                self.butterflies.clear()
                self.sunlines.clear()
            if (self.gamestate.scene == C_SCENE_SUN):
                self.psys_instances.clear()  

    def generateDoor(self):
        if (self.gamestate.mode == C_PLAY):
            if (self.gamestate.scene == C_SCENE_HOME):
                scenario, branch = self.gamestate.scenario[0][1], self.gamestate.scenario[0][2]
                ###Door開放管理配列に基づいて、Doorオブジェクトを生成。Doorリストに追加。
                if self.gamestate.door_open_array[0]:
                    self.door00 = Door( 50,96,8,0)
                    doors.append(self.door00)
                if self.gamestate.door_open_array[1]:
                    self.door01 = Door( 196 -35,96,1,0)
                    doors.append(self.door01)
                if self.gamestate.door_open_array[2]:
                    self.door02 = Door( 246 -35,96,2,0)
                    doors.append(self.door02)
                if self.gamestate.door_open_array[3]:
                    self.door03 = Door( 296 -3,96,3,0)
                    ## 部屋内部の扉の表示状態を設定
                    if scenario == 3 and branch == 0:
                        self.door03.visible = False
                    if (scenario >= 3 and branch >= 9) or (scenario >= 4):
                        self.door03.visible = True
                    doors.append(self.door03)
                if self.gamestate.door_open_array[4]:
                    self.door04 = Door( 396,96,4,0)
                    doors.append(self.door04)
                if self.gamestate.door_open_array[5]:
                    self.door05 = Door( 446,96,5,0)
                    doors.append(self.door05)
                if self.gamestate.door_open_array[6]:
                    self.door06 = Door( 496,96,6,0)
                    doors.append(self.door06)
                if self.gamestate.door_open_array[7]:
                    self.door07 = Door( 546,96,7,0)
                    doors.append(self.door07)

            ###HOMEへのドアを設置
            # if (self.gamestate.scene == C_SCENE_MOON):
            if (self.gamestate.scene == C_SCENE_MOON):
                ###Doorオブジェクトを生成
                self.door01 = Door(450,134,0,3)
                ###Doorオブジェクトリストに追加
                doors.append(self.door01)
            if (self.gamestate.scene in(C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD)):
                ###Doorオブジェクトを生成
                self.door01 = Door(450,94,0,3)
                self.door01.visible = True
                ###Doorオブジェクトリストに追加
                doors.append(self.door01)
            if (self.gamestate.scene == C_SCENE_SOIL):
                ###Doorオブジェクトを生成
                self.door01 = Door(475,94,0,3)
                self.door01.visible = True
                ###Doorオブジェクトリストに追加
                doors.append(self.door01)
            if (self.gamestate.scene == C_SCENE_SUN):
                ###Doorオブジェクトを生成
                self.door01 = Door(450,94,0,3)
                self.door01.visible = False
                ###Doorオブジェクトリストに追加
                doors.append(self.door01)
            if (self.gamestate.scene == C_SCENE_END):
                ###Doorオブジェクトを生成
                self.door01 = Door(475,94,0,3)
                self.door01.visible = True
                ###Doorオブジェクトリストに追加
                doors.append(self.door01)

    def updateHomeScene(self):
        if self.gamestate.door_open_array != self.gamestate.door_open_array_bf:
            self.generateDoor()
            ### Doorオブジェクトへcameraスクロールを適用
            for door in doors:
                self.camera.apply(door)
            self.gamestate.door_open_array_bf = self.gamestate.door_open_array.copy()

    def updateMoonScene(self):
        ###fireworksの中でlifeが0になったものを削除
        for firework in self.fireworks:
            if firework.life == 0:
                self.fireworks.remove(firework)
        ###花火の打ち上げ
        if pyxel.frame_count % 25 == 0:
            x, y = Random.randint(30, 570 - 30), 170
            self.fireworks.append(Firework(x, y))
        ### Fireworkオブジェクトの更新実行
        for obj in self.fireworks:
            obj.update()
            ###花火の破裂音を再生
            if obj.y == obj.peak and obj.active:
                pyxel.play(3, 26)
        ###moonの更新
        for moon in self.moons:
            moon.update()
        

    def updateFireScene(self):
        ###ランタンの数をチェック
        chk_lantan_numbfr = len(self.lantans)
        ###ランタンが画面外（x=-1）に出たらランタンとそれに対応するpsysを削除
        for i in range(len(self.lantans) - 1, -1, -1):  # 逆順で反復処理
            if self.lantans[i].x + 16 < -17:
                self.lantans.pop(i)
                self.psys_instances.pop(i)
        chk_lantan_numaft = len(self.lantans)
        ###ランタンの数が減っていたら、ランタンを補充
        if chk_lantan_numbfr > chk_lantan_numaft:         
            ###Lantanを画面右端に補充
            new_lantan = Lantan(x= 2 * pyxel.width + 16, y= Random.randint(0, 200), speed=1)
            self.camera.apply(new_lantan) ## ランタンの座標を更新
            self.lantans.append(new_lantan)
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
        self.updateParticleSystems()
        ###光の座標群を順にチェックして、中身が空になったものを削除する
        for point3d in self.points3d:
            if len(point3d.points) == 0:
                self.points3d.remove(point3d)
        ### Vキーを押すと、光の座標群を生成する
        if pyxel.btnp(pyxel.KEY_V) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
            self.points3d.append(Point3D(center_x=self.player.x +8, center_y=self.player.y +8, center_z=0, radius=50, num_points=20, speed_low=2, speed_high=4, life_low=50, life_high=100, randini=False, pallete=Random.choice([0, 1, 2]), cacheflg=False, scene=self.gamestate.scene))
        # 光の座標群を更新
        if pyxel.frame_count % 5 == 0:
            for point3d in self.points3d:
                point3d.update()
        
    def updateWaterScene(self):
        ##self.psys_instancesが空でなければ、updateを実行する
        if len(self.psys_instances) > 0:
            for psys in self.psys_instances:
                psys.update_particles(self.camera.x, 1)


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
                tree.update(0 +self.camera.x,300 +self.camera.x)
        ###草grassesをupdate
        if pyxel.frame_count % 10 == 0:
            for grass in self.grasses:
                grass.update(0 +self.camera.x,300 +self.camera.x)
        ###花オブジェクトをupdate
        if pyxel.frame_count % 10 == 0:
            for flower in self.flowers:
                flower.update_tip(0 +self.camera.x,300 +self.camera.x)
        ##self.psys_instancesが空でなければ、updateを実行する
        if len(self.psys_instances) > 0:
            for psys in self.psys_instances:
                psys.update_particles(self.camera.x, 1)
    
    def updateGoldScene(self):
        # オブジェクトのupdateメソッドを呼び出す
        for point in reversed(self.elliptical_orbits):
            point.update()
        # 新しいエコーチャンバーのセグメントを追加する
        new_segments = list()
        for segment in self.segments:
            if segment.x_new != 0:
                new_segments.append(EchoChamberVisualizer(x_center=segment.x_new, y_center=segment.y_new, r=segment.r_new, treeangle=segment.tree_angle_new, max_depth=segment.max_depth_new, polygon_sides=segment.polygon_sides_new, external=segment.external_new))
        self.segments.extend(new_segments)
        # 不要なセグメントを削除する
        self.segments = [segment for segment in self.segments if segment.x_new == 0]
        ###cameraを適用
        for segment in self.segments:
            self.camera.apply(segment)
        ###echo chamberのupdate
        if len(self.segments) > 0:
            # if pyxel.frame_count % 15 == 0:
            #     for segment in self.segments:
            #         segment.angle_offset += 15
            for segment in self.segments:
                segment.update()
    
    def updateSoilScene(self):
        #self.butterfly01.update()
        if len(self.butterflies) > 0:
            for butterfly in self.butterflies:
                butterfly.update()
        if len(self.sunlines) > 0:
            for sunline in self.sunlines:
                sunline.update()

    def updateSunScene(self):
        ###パーティクルシステムのupdate
        ##self.psys_instancesが空でなければ、updateを実行する
        if len(self.psys_instances) > 0:
            for psys in self.psys_instances:
                psys.update_particles(self.camera.x, 1)
    
    # def updateEndScene(self):



    def updateParticleSystems(self):
        #####テスト（パーティクルシステム）
        self.timer_for_psys += 1
        if self.gamestate.scene == C_SCENE_WOOD: ###WOODシーンのみ
            ###Vキーが押されたらパーティクルシステムを起動
            if pyxel.btnp(pyxel.KEY_V) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y):
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
                psys.update_particles(self.camera.x)


    def playerUpdateColisionCheckAndScrollCancel(self,baseelem,list):
        # 引数のリストのオブジェクト群と、playingCharacterが衝突していないかをチェック。
        # 衝突した場合はシーン上のすべてのオブジェクトのスクロール適用計算を順に戻し、背景パララックス用演算値を0に戻す。
        for elem in list:
            if not(elem.is_playing) and baseelem.is_colliding_with(elem):
            # 衝突したら
                # プレイヤーの移動をキャンセルする
                baseelem.cancel_move()
                # 背景のパララックススクロールの方向を０へ
                self.scroll_direction = 0


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
        ###pyxelExtendedの円形クリッピングでCharactererの画像を表示
        self.ext.draw_clipped_circle(status_x, status_y + 14, 0, 16, 0, -16, 16, 8)        
        ###キャラクター画像の下に、選択中アイテムに対しての感想文を表示
        # 現在のgamestateに応じたアイテムへの感想を取得
        scenario, branch = self.gamestate.scenario[0][1], self.gamestate.scenario[0][2]
        self.thought_text = self.invsys.getThoughtOnMenu(scenario, branch, self.player.character_no)
        ###感想文を分割する
        self.thought_text_divided = list()
        ###テキストの分割（結果セットに連続appendする）
        self.textDivide(self.thought_text, self.thought_text_divided, 9)
        ###分割されたテキストを順に表示する
        for i in range(len(self.thought_text_divided)):
            self.bdf1.draw_text(status_x, status_y + 34 + (i * 12), self.thought_text_divided[i], 7)  # 白文字で表示
        # 現在のgamestateに応じてヒントを表示
        scene, scenario, branch = self.gamestate.scenario[0][0], self.gamestate.scenario[0][1], self.gamestate.scenario[0][2]
        self.hint_text = self.getHintOnMenu(scene, scenario, branch, self.player)
        ###ヒントテキストを分割する
        self.hint_text_divided = list()
        ###テキストの分割（結果セットに連続appendする）
        self.textDivide(self.hint_text, self.hint_text_divided, 9)
        ###分割されたテキストを順に表示する
        for i in range(len(self.hint_text_divided)):
            self.bdf1.draw_text(status_x, hint_y + (i * 12), self.hint_text_divided[i], 7)  # 白文字で表示
        ###選択中アイテムの説明文を表示
        ###取得した説明文を分割する
        item_description = [self.invsys.get_selected_description()]
        item_description_divided = list()
        ###テキストの分割（結果セットに連続appendする）
        self.textDivide(item_description, item_description_divided, 28)
        ###分割されたテキストを順に表示する
        for i in range(len(item_description_divided)):
            self.bdf1.draw_text(10, 250 + (i * 12), item_description_divided[i], 7)
        ###アイテム使用時のサブウィンドウを表示
        self.invsys.drawSubWindow()

    def getHintOnMenu(self, scene, scenario, branch, player): ###最大63文字までのヒントテキストを返す
        hint_text = ""
        if scenario == 0:
            if branch == 0:
                    if scene == C_SCENE_HOME:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["ボロボロに朽ちた道路と広大な砂浜がはるか彼方まで続いて見える。周辺を調べないことには何も分かりそうにない。"]
                    elif scene == C_SCENE_MOON:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["打ち上がる花火が眩しい。"]
                    elif scene == C_SCENE_FIRE:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["灯籠が、眼下を流れていく。何処か懐かしさを覚える。"]
                    elif scene == C_SCENE_WATER:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["降りしきる雨で全身が濡れる。部屋は水浸しだ。"]
                    elif scene == C_SCENE_WOOD:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["常に風が吹いているようだ。花々と木々の香りがふんわりと香る。"]
                    elif scene == C_SCENE_GOLD:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["ひんやりとして肌寒い。幾何学模様が空間を漂っている。"]
                    elif scene == C_SCENE_SOIL:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["厳かな雰囲気だ。"]
                    elif scene == C_SCENE_SUN:
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["部屋の中に陽光が差している。窓の外は雪が吹きつけている。"]
            elif branch == 1:
                    if scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN):
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["海辺にいる女の子に話しかけてみよう。"]
            elif branch == 2:
                    if scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN):
                        if player.character_no == C_CHARA_WOLF:
                            hint_text = ["周囲を探索してみよう。"]
        return hint_text


    ###gamestateのsceneの値に応じて対応する変数名の文字列を返す ★DEBUG用
    def getSceneName(self):
        if(self.gamestate.scene == C_SCENE_HOME):
            return "HOME:0"
        if(self.gamestate.scene == C_SCENE_MOON):
            return "MOON:1"
        if(self.gamestate.scene == C_SCENE_FIRE):
            return "FIRE:2"
        if(self.gamestate.scene == C_SCENE_WATER):
            return "WATER:3"
        if(self.gamestate.scene == C_SCENE_WOOD):
            return "WOOD:4"
        if(self.gamestate.scene == C_SCENE_GOLD):
            return "GOLD:5"
        if(self.gamestate.scene == C_SCENE_SOIL):
            return "SOIL:6"
        if(self.gamestate.scene == C_SCENE_SUN):
            return "SUN:7"
        if(self.gamestate.scene == C_SCENE_END):
            return "END:08"
        if(self.gamestate.scene == C_SCENE_MENU):
            return "MENU"
        
    ###gamestateのシナリオ番号（到達済みシーン）と設定中ブランチとの文字列を返す ★DEBUG用
    def getScenarioAndBranchNum(self):
        return str(self.gamestate.scenario[0][1]) + "-" + str(self.gamestate.scenario[0][2])
        
    ###gamestateのmodeの値に応じて対応する変数名の文字列を返す ★DEBUG用
    def getModeName(self):
        if(self.gamestate.mode == C_PLAY):
            return "PLAY"
        if(self.gamestate.mode == C_MENU):
            return "MENU"

    def drawBG(self):
        ###HOMEシーン用背景の描画。パララックス背景の砂浜と、手前の道路を描画する。
        if (self.gamestate.mode == C_PLAY):
                if(self.gamestate.scene == C_SCENE_HOME): 
                    self.drawHomeBG()
                elif(self.gamestate.scene == C_SCENE_MOON): ###月の戸の場合、満月と花火の描写を行う
                    self.drawMoonBG()
                elif(self.gamestate.scene == C_SCENE_FIRE): ###火の戸の場合、ホタル及び灯籠の描写を行う
                    self.drawFireBG()
                elif(self.gamestate.scene == C_SCENE_WATER): ###波紋の戸の場合、雨の描写を行う
                    self.drawWaterBG()
                elif(self.gamestate.scene == C_SCENE_WOOD): ###木の戸の場合、草木花の描写を行う
                    self.drawWoodBG()
                elif(self.gamestate.scene == C_SCENE_GOLD): ###金の戸の場合多角形と樹形図の幾何学図形及び星の描写を行う
                    self.drawGoldBG()
                elif(self.gamestate.scene == C_SCENE_SOIL): ###土の戸の場合、墓地の描写を行う
                    # self.drawMoonBG()
                    self.drawSoilBG()
                elif(self.gamestate.scene == C_SCENE_SUN): ###太陽の戸の場合、ひだまりの描写を行う
                    # self.drawMoonBG()
                    self.drawSunBG()
                elif(self.gamestate.scene == C_SCENE_END): ###終の戸の場合、エンディングの描写を行う
                    self.drawEndBG()

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
        pyxel.bltm(-32 - self.camera.x,8 * 17,     2, 0, 8 * 40, 8 * 40 + self.camera.x + 32, 8 * 12,0)
        ###塀
        pyxel.bltm(-32 - self.camera.x,8 * 15 - 5, 2, 0, 8 * 36, 8 * 40 + self.camera.x + 32, 8 * 4,0)
        ###街灯
        pyxel.blt( 15 - self.camera.x,  55, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
        pyxel.blt(145 - self.camera.x,  55, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
        pyxel.blt(245 - self.camera.x,  55, 2, 16 * 5, 16 * 5,-16 * 1, 16 * 6,3)
        pyxel.blt(360 - self.camera.x,  55, 2, 16 * 5, 16 * 5,-16 * 1, 16 * 6,3)
        pyxel.blt(480 - self.camera.x,  55, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
        ###electric line1
        self.drawElectricalwire(130 -150 - self.camera.x, -5,280 -150 - self.camera.x, -5)
        self.drawElectricalwire(130      - self.camera.x, -5,280      - self.camera.x, -5)
        self.drawElectricalwire(130 +150 - self.camera.x, -5,300 +450 - self.camera.x, -5)
        ###electric line2
        self.drawElectricalwire(130 -150 - self.camera.x,0,280 -150 - self.camera.x, 0)
        self.drawElectricalwire(130      - self.camera.x,0,280      - self.camera.x, 0)
        self.drawElectricalwire(130 +150 - self.camera.x,0,300 +450 - self.camera.x, 0)
        ###電信柱
        pyxel.blt(116       - self.camera.x, -25, 2, 16 * 6, 0, 16 * 1, 16 * 11,3)
        pyxel.blt(116 + 150 - self.camera.x, -25, 2, 16 * 6, 0, 16 * 1, 16 * 11,3)
        pyxel.blt(136 + 450 - self.camera.x, -25, 2, 16 * 6, 0, 16 * 1, 16 * 11,3)
        ###バス停
        pyxel.blt(333 - self.camera.x, 8 * 11, 2, 8 * 5, 16 *  7, 16, 16 * 4,3)
        ###pole red
        pyxel.blt( 92 - self.camera.x, 8 * 17, 2, 16 * 2, 16 *  9, 16 / 2, 16 * 1,3)
        pyxel.blt(100 - self.camera.x, 8 * 17, 2, 16 * 2, 16 *  8, 16 / 2, 16 * 1,3)
        pyxel.blt(108 - self.camera.x, 8 * 17, 2, 16 * 2, 16 * 10, 16 / 2, 16 * 1,3)
        ###看板
        pyxel.blt(278 - self.camera.x, 8 * 14, 2, 16 / 2 * 9, 16 *  9, 16 / 2, 16 * 2, 3)



    def drawMoonBG(self):
        pyxel.cls(0) #DARK BLUE
        ###月の描画
        for moon in self.moons:
            moon.draw(self.camera.x, self.scroll_speeds)
        
        ###花火の描画
        if(len(self.fireworks)>0) :
            for firework in self.fireworks:
                ###アクティブ中は線を描画.
                if firework.active:
                    pyxel.line(firework.x - self.camera.x, firework.y + 4, firework.x - self.camera.x, firework.y + 9, 15)
                    pyxel.line(firework.x - self.camera.x, firework.y,     firework.x - self.camera.x, firework.y + 3,  7)
                    pyxel.pset(firework.x - self.camera.x, firework.y - 1, pyxel.frame_count % 16)
                    # pyxel.line(firework.draw_x, firework.draw_y + 4, firework.draw_x, firework.draw_y + 9, 15)
                    # pyxel.line(firework.draw_x, firework.draw_y,     firework.draw_x, firework.draw_y + 3,  7)
                    # pyxel.pset(firework.draw_x, firework.draw_y - 1, pyxel.frame_count % 16)
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
                            pyxel.line(outer_points[i].real -self.camera.x, outer_points[i].imag, inner_points[i].real -self.camera.x, inner_points[i].imag, rndcolor)
                            pyxel.line(inner_points[i].real -self.camera.x, inner_points[i].imag, outer_points[connection_indices[i]].real -self.camera.x, outer_points[connection_indices[i]].imag, rndcolor)
                    if firework.burst_func == firework.burst_funcs[6]:  # spiral_recursive_burst用
                        ###中心点から各点への線を描画
                        for z in firework.burst:
                            pyxel.line(firework.x -self.camera.x, firework.y, int(z.real) -self.camera.x, int(z.imag), rndcolor)
                    if firework.burst_func == firework.burst_funcs[13]: # radiating_sphere_projection_burst用
                        ###Z座標がプラスのものだけを描画（描画点多くなるため点描）
                        for z in firework.burst:
                            if(z.imag >= 0):
                                pyxel.pset(int(z.real) -self.camera.x,    int(z.imag),    rndcolor)
                    
                    ###デフォルト描画
                    if firework.burst_func != firework.burst_funcs[13]:
                        for z in firework.burst:
                            pyxel.circb(int(z.real) -self.camera.x, int(z.imag), 1, rndcolor)

        ###丘の描画
        pyxel.bltm(-(8*9) - self.camera.x, 8 * 18, 0, 0, 8 * 125, 8 * 200, 8 * 16,0)

        ###柵の描画(10回繰り返し)
        for i in range(0, 40):
            pyxel.blt(0 + i * 16 - self.camera.x, 172, 1, 32, 246, 16, 10, 0)
        

        ###木の描画
        pyxel.bltm(530 - self.camera.x, 8 * 8, 0, 0, 8 * 144, 8 * 8, 8 * 16, 0)

        # ###デモタイトル表示
        # self.bdf2.draw_text(150, 2, "PRESS SPACE : 花火", 7) 

    def drawFireBG(self):
        pyxel.cls(0)
        ###葉っぱ1
        pyxel.blt( 23 - self.camera.x,  40, 1, 208, 80, 16, 16, 0)
        pyxel.blt(127 - self.camera.x,  75, 1, 208, 80, 16, 16, 0)
        pyxel.blt(161 - self.camera.x,  53, 1, 208, 80, 16, 16, 0)
        pyxel.blt(428 - self.camera.x,  81, 1, 208, 80, 16, 16, 0)
        pyxel.blt(529 - self.camera.x,  38, 1, 208, 80, 16, 16, 0)
        ###葉っぱ2
        pyxel.blt( 41 - self.camera.x,  87, 1, 224, 80, 16, 16, 0)
        pyxel.blt(103 - self.camera.x,  39, 1, 224, 80, 16, 16, 0)
        pyxel.blt(312 - self.camera.x,  52, 1, 224, 80, 16, 16, 0)
        pyxel.blt(441 - self.camera.x,  69, 1, 224, 80, 16, 16, 0)

        ###睡蓮
        pyxel.blt(200 - self.camera.x,  40, 1, 224, 64, 16, 16, 0)
        pyxel.blt(110 - self.camera.x,  65, 1, 208, 64, 16, 16, 0)
        pyxel.blt(216 - self.camera.x,  58, 1, 208, 64, 16, 16, 0)
        pyxel.blt(260 - self.camera.x,  43, 1, 224, 64, 16, 16, 0)
        pyxel.blt(425 - self.camera.x,  98, 1, 208, 64, 16, 16, 0)

        
        ###particleの描画
        if len(self.psys_instances) > 0:
            self.drawParticles()
        ###Lantanの描画
        for lantan in self.lantans:
            lantan.draw()
        ###石柱（小）の描画（青）
        for i in range(0, 42):
            ###３００幅の画面外は描画しない
            if(i * 16 - self.camera.x < 300):
                pyxel.blt(13 + i * 16 - self.camera.x, 8 * 15, 1, 64, 240, 8, 16, 0)

        ###
        pyxel.blt(120 - self.camera.x, 130, 1, 96, 160 + 16*(pyxel.frame_count//8 % 4), 16, 16,0)


    def drawWaterBG(self):
        ###reset(Bk)
        pyxel.cls(0)
        # pyxel.cls(1)
        # ###水面の光反射エフェクトを描画（スクロール値適用）
        # self.wse.draw(self.camera.x)
        self.drawfish(0)
        ###波紋を指定区画内にランダムに描画
        # for i in range(0, 12):
        for i in range(0, 6):
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
                    pyxel.line(self.rain_landing_x[i] - self.camera.x, -1, self.rain_landing_x[i] - self.camera.x, self.rain_landing_y[i] -60, 5)
                    pyxel.line(self.rain_landing_x[i] - self.camera.x, self.rain_landing_y[i] -60, self.rain_landing_x[i] - self.camera.x, self.rain_landing_y[i], 1)
                if self.rain_draw_counter[i] in(19,20):
                    pyxel.blt(self.rain_landing_x[i] -8 - self.camera.x, self.rain_landing_y[i] - 4, 2, 40, 24,  16, 8,0)

            # 波紋の描画（水面下の影）
            self.radius_w[i] = self.ripples_w[i] + (20 - self.rain_draw_counter[i]) * 2.2 # 2は広がる速度を示す任意の値。必要に応じて調整可能。
            self.radius_h[i] = self.ripples_h[i] + (20 - self.rain_draw_counter[i]) * 1.1
            self.rain_draw_x[i] = self.rain_x[i] - self.radius_w[i]/2
            self.rain_draw_y[i] = self.rain_y[i] - self.radius_h[i]/2 + 3
            pyxel.ellib(self.rain_draw_x[i] - self.camera.x, self.rain_draw_y[i], self.radius_w[i] -self.rain_reduce[i], self.radius_h[i] -self.rain_reduce[i], 13)
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
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x +wk_ripples_width4/2, self.rain_draw_y[i] +wk_ripples_width4/2, self.radius_w[i]-wk_ripples_width4 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width4 -self.rain_reduce[i],  1)
                if(self.ripple_count[i] >= 4):
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x +wk_ripples_width3/2, self.rain_draw_y[i] +wk_ripples_width3/2, self.radius_w[i]-wk_ripples_width3 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width3 -self.rain_reduce[i],  5)
                if(self.ripple_count[i] >= 3):
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x +wk_ripples_width2/2, self.rain_draw_y[i] +wk_ripples_width2/2, self.radius_w[i]-wk_ripples_width2 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width2 -self.rain_reduce[i], 13)
                if(self.ripple_count[i] >= 2):
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x -wk_ripples_width1/2, self.rain_draw_y[i] -wk_ripples_width1/2, self.radius_w[i]+wk_ripples_width1 -self.rain_reduce[i], self.radius_h[i]+wk_ripples_width1 -self.rain_reduce[i], 12)
                if(self.ripple_count[i] == 1):
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x, self.rain_draw_y[i], self.radius_w[i] -self.rain_reduce[i],   self.radius_h[i] -self.rain_reduce[i], self.rain_color[i])
            else:
                if(self.ripple_count[i] >= 5):
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x +wk_ripples_width4/2, self.rain_draw_y[i] +wk_ripples_width4/2, self.radius_w[i]-wk_ripples_width4 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width4 -self.rain_reduce[i],  1)
                if(self.ripple_count[i] >= 4):
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x +wk_ripples_width3/2, self.rain_draw_y[i] +wk_ripples_width3/2, self.radius_w[i]-wk_ripples_width3 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width3 -self.rain_reduce[i],  1)
                if(self.ripple_count[i] >= 3):
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x +wk_ripples_width2/2, self.rain_draw_y[i] +wk_ripples_width2/2, self.radius_w[i]-wk_ripples_width2 -self.rain_reduce[i], self.radius_h[i]-wk_ripples_width2 -self.rain_reduce[i],  5)
                if(self.ripple_count[i] >= 2):
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x -wk_ripples_width1/2, self.rain_draw_y[i] -wk_ripples_width1/2, self.radius_w[i]+wk_ripples_width1 -self.rain_reduce[i], self.radius_h[i]+wk_ripples_width1 -self.rain_reduce[i],  5)
                if(self.ripple_count[i] == 1):
                    pyxel.ellib(self.rain_draw_x[i] - self.camera.x, self.rain_draw_y[i], self.radius_w[i] -self.rain_reduce[i],   self.radius_h[i] -self.rain_reduce[i], 12)

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
                    pyxel.ellib(self.footprints_draw_x[i] -self.camera.x, self.footprints_draw_y[i], self.fp_radius_w[i], self.fp_radius_h[i], self.footprints_color[i])
            else:
                if (i in(4,12)):
                    # 波紋の広がりの速度を調整
                    self.fp_radius_w[i] = self.fp_ripples_w[i] + (5 - self.footprint_draw_counter[i]) * 1
                    self.fp_radius_h[i] = self.fp_ripples_h[i] + (5 - self.footprint_draw_counter[i]) * 0.5
                    # 波紋の描画位置を設定
                    self.footprints_draw_x[i] = self.footprints_x[i] - self.fp_radius_w[i]/2
                    self.footprints_draw_y[i] = self.footprints_y[i] - self.fp_radius_h[i]/2 
                    # 波紋を描画
                    pyxel.ellib(self.footprints_draw_x[i] -self.camera.x, self.footprints_draw_y[i], self.fp_radius_w[i], self.fp_radius_h[i], self.footprints_color[i])
        self.drawfrog(-1)

    def drawWaterFT(self):
        ###watertreesの描画
        ###適用カメラに係数でパララックスをかける
        for watertree in self.water_trees:
            watertree.draw(self.camera.x * 1.1)
        ###fishの移動
        self.drawfish(1)
        ###particleの描画
        if len(self.psys_instances) > 0:
            self.drawParticles()

    def drawfrog(self,direction=1):
        ###カエル
        frogframe = (pyxel.frame_count//18)%4
        if direction == 1:
            if frogframe == 1:
                self.frogx -= 0.25
                self.frogy -= 0.05
            elif frogframe == 2:
                self.frogx -= 0.25
                self.frogy += 0.05
            if self.frogx < -8:
                self.frogx = 600
                self.frogy = Random.randint(150, 230)
        if direction == -1:
            if frogframe == 1:
                self.frogx += 0.25
                self.frogy -= 0.05
            elif frogframe == 2:
                self.frogx += 0.25
                self.frogy += 0.05
            if self.frogx > 600:
                self.frogx = -8
                self.frogy = Random.randint(150, 230)
        ###frogの描画
        if frogframe in(0,1):
            # if frogframe == 0:
            #     ##楕円の描画
            #     pyxel.ellib(self.frogx -4 -self.camera.x, self.frogy +6, 10, 4, 1)
            pyxel.blt(self.frogx -self.camera.x,self.frogy,1,64,128 + 8*frogframe,direction*8,8,0)
        elif frogframe in(2,3):
            if frogframe == 3:
                ##楕円の描画
                pyxel.ellib(self.frogx -4 -self.camera.x, self.frogy +6, 17, 4, 1)
            pyxel.blt(self.frogx -self.camera.x,self.frogy,1,72,128 + 8*(frogframe-2),direction*8,8,0)

    def drawfish(self, layer):
        ### 魚の描画
        if layer == 0:
            ###fishの描画
            self.fishdx03 -= 0.39
            if self.fishdx03 < -32:
                self.fishdx03 += 600
                self.fishdy03 = Random.randint(0, 230)
            self.fishdx04 -= 0.46
            if self.fishdx04 < -32:
                self.fishdx04 += 600
                self.fishdy04 = Random.randint(0, 230)
            self.fishdx05 -= 0.53
            if self.fishdx05 < -32:
                self.fishdx05 += 600
                self.fishdy05 = Random.randint(0, 230)
            fishframe1 = (pyxel.frame_count//15)%4
            fishframe2 = (pyxel.frame_count//18 +1)%4
            fishframe3 = (pyxel.frame_count//12 +2)%4
            pyxel.blt(self.fishdx03 -self.camera.x,self.fishdy03,1,64,160 + 16*fishframe1,32,16,3)
            pyxel.blt(self.fishdx04 -self.camera.x,self.fishdy04,1,64,160 + 16*fishframe2,32,16,3)
            pyxel.blt(self.fishdx05 -self.camera.x,self.fishdy05,1,64,160 + 16*fishframe3,32,16,3)
        elif layer == 1:
            self.fishdx01 -= 0.34
            if self.fishdx01 < -32:
                self.fishdx01 += 600
                self.fishdy01 = Random.randint(0, 230)
            self.fishdx02 -= 0.52
            if self.fishdx02 < -32:
                self.fishdx02 += 600
                self.fishdy02 = Random.randint(0, 230)
            fishframe4 = (pyxel.frame_count//12)%4
            fishframe5 = (pyxel.frame_count//15 +3)%4
            pyxel.blt(self.fishdx01 -self.camera.x,self.fishdy01,1,64,160 + 16*fishframe4,32,16,3)
            pyxel.blt(self.fishdx02 -self.camera.x,self.fishdy02,1,64,160 + 16*fishframe5,32,16,3)

    def drawWoodBG(self):
        pyxel.cls(0) #1,5,12で基本背景色を設定
        # pyxel.rect(0, 0, 600, 80, 1)
        # pyxel.rect(0, 0, 600, 55, 5)
        # pyxel.rect(0, 0, 600, 35, 12)
        ###背景の木々
        # pyxel.blt( 0 - self.camera.x, 40, 2, 16 * 13.5, 0, 16 * 2.5, 16 * 3.5, 0)
        pyxel.bltm(0 - self.camera.x * 0.4, 8 * 4, 0, 8 * 0 , 8 * 216, 8 * 95, 8 * 8, 0)

        
        ###道路
        pyxel.bltm(-32 - self.camera.x,8 * 18,     2, 0, 8 * 52, 8 * 40 + self.camera.x + 32, 8 * 10,0)
        ###塀
        ###木の描画
        self.drawTreesBG()
        ###花の描画
        pyxel.blt(40 -self.camera.x,100,1,144,0,16,40,0)
        pyxel.blt(570 -self.camera.x,100,1,144,0,16,40,0)
        ###particleの描画
        if len(self.psys_instances) > 0:
            self.drawParticles()

    
    def drawTreesBG(self):
        # 各Treeオブジェクトの葉の座標に対してスプライトを分割表示し、動的な葉の表現を行う
        for tree in self.trees:
            if tree.position_back:
                ###幹の描画
                # pyxel.blt(tree.draw_x -4, tree.draw_y + 16, 2, 16, 192, 40, 64, 0)
                pyxel.blt(tree.draw_x -4, tree.draw_y + 16, 2, 216, 0, 40, 72, 0)
                ###葉と光点の描画
                for i in range(0, len(tree.leaves)):
                    x, y = tree.leaves[i]
                    ###交互に色セットの切り替えを行う
                    if i % 2 == 0:
                        pyxel.pal(3, 11)
                    elif i % 2 == 1:
                        pyxel.pal()
                    ###葉の描画
                    pyxel.blt(x - self.camera.x, y, 2, 0, 208, 16, 16, 0)
                    pyxel.pal()
                ### 落ちた葉の描画
                for i in range(0, 16):
                    if tree.drop_leaves[i][2] == 0:
                        pyxel.blt(tree.drop_leaves[i][0] - self.camera.x, tree.drop_leaves[i][1] +72, 2, 0, 240, 8, 8, 0)
                    if tree.drop_leaves[i][2] == 1:
                        pyxel.blt(tree.drop_leaves[i][0] - self.camera.x, tree.drop_leaves[i][1] +72, 2, 8, 240, 8, 8, 0)
                    if tree.drop_leaves[i][2] == 2:
                        pyxel.blt(tree.drop_leaves[i][0] - self.camera.x, tree.drop_leaves[i][1] +72, 2, 0, 248, 8, 8, 0)
                    if tree.drop_leaves[i][2] == 3:
                        pyxel.blt(tree.drop_leaves[i][0] - self.camera.x, tree.drop_leaves[i][1] +72, 2, 8, 248, 8, 8, 0)
                # pyxel.blt(x - self.camera.x, y +72, 2, 0, 240, 8, 8, 0)
                ### 葉へのcameraスクロール適用
                for leaf in tree.leaves:
                    leaf = leaf[0] + self.camera.x, leaf[1]
    
    def drawTreesFT(self):
        # 各Treeオブジェクトの葉の座標に対してスプライトを分割表示し、動的な葉の表現を行う
        for tree in self.trees:
            if tree.position_front:
                ###幹の描画
                # pyxel.blt(tree.draw_x -4, tree.draw_y + 16, 2, 16, 192, 40, 64, 0)
                pyxel.blt(tree.draw_x -4, tree.draw_y + 16, 2, 216, 0, 40, 72, 0)
                ###葉と光点の描画
                for i in range(0, len(tree.leaves)):
                    x, y = tree.leaves[i]
                    ###交互に色セットの切り替えを行う
                    if i % 2 == 0:
                        pyxel.pal(3, 11)
                    elif i % 2 == 1:
                        pyxel.pal()
                    ###葉の描画
                    pyxel.blt(x - self.camera.x, y, 2, 0, 208, 16, 16, 0)
                    pyxel.pal()
                ### 落ちた葉の描画
                for i in range(0, 16):
                    if tree.drop_leaves[i][2] == 0:
                        pyxel.blt(tree.drop_leaves[i][0] - self.camera.x, tree.drop_leaves[i][1] +72, 2, 0, 240, 8, 8, 0)
                    if tree.drop_leaves[i][2] == 1:
                        pyxel.blt(tree.drop_leaves[i][0] - self.camera.x, tree.drop_leaves[i][1] +72, 2, 8, 240, 8, 8, 0)
                    if tree.drop_leaves[i][2] == 2:
                        pyxel.blt(tree.drop_leaves[i][0] - self.camera.x, tree.drop_leaves[i][1] +72, 2, 0, 248, 8, 8, 0)
                    if tree.drop_leaves[i][2] == 3:
                        pyxel.blt(tree.drop_leaves[i][0] - self.camera.x, tree.drop_leaves[i][1] +72, 2, 8, 248, 8, 8, 0)
                ### 葉へのcameraスクロール適用
                for leaf in tree.leaves:
                    leaf = leaf[0] + self.camera.x, leaf[1]


    def drawGoldBG(self):
        ###reset(Bk)
        pyxel.cls(0)
        ###
        scroll_ratio1 = 1.02
        scroll_ratio2 = 1.08
        scroll_ratio3 = 1.02
        scroll_ratio6 = 1.10
        ###最背景の青い影
        pyxel.bltm(8* 0 -self.camera.x*scroll_ratio6,    5,0,   0,8*64,8*16,8* 4,0) 
        pyxel.bltm(8*16 -self.camera.x*scroll_ratio6,    5,0,   0,8*64,8*16,8* 4,0) 
        pyxel.bltm(8*32 -self.camera.x*scroll_ratio6,    5,0,   0,8*64,8*16,8* 4,0) 
        pyxel.bltm(8*48 -self.camera.x*scroll_ratio6,    5,0,   0,8*64,8*16,8* 4,0)
        pyxel.bltm(8*64 -self.camera.x*scroll_ratio6,    5,0,   0,8*64,8*16,8* 4,0)
        pyxel.bltm(8*80 -self.camera.x*scroll_ratio6,    5,0,   0,8*64,8*16,8* 4,0)
        ###最背景の砂山
        pyxel.bltm(490 -self.camera.x*scroll_ratio2,     5,0,8* 0,8*33,8*22,8* 6,0) #明茶
        ###砂山の裾で広がる砂
        pyxel.bltm(110 -self.camera.x*scroll_ratio1, 50,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(150 -self.camera.x*scroll_ratio1, 60,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(170 -self.camera.x*scroll_ratio1,120,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(235 -self.camera.x*scroll_ratio1,100,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(190 -self.camera.x*scroll_ratio1, 80,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(500 -self.camera.x*scroll_ratio1, 55,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm( 60 -self.camera.x*scroll_ratio1, 70,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm( 90 -self.camera.x*scroll_ratio1, 95,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(440 -self.camera.x*scroll_ratio1, 75,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(-25 -self.camera.x*scroll_ratio1, 75,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(290 -self.camera.x*scroll_ratio1, 95,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(375 -self.camera.x*scroll_ratio1, 75,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(482 -self.camera.x*scroll_ratio1, 45,0,   0,8*56,8*25,8* 5,0) 
        pyxel.bltm(375 -self.camera.x*scroll_ratio1,100,0,   0,8*56,8*25,8* 5,0) 
        ###砂山
        pyxel.bltm(400 -self.camera.x*scroll_ratio2,-15,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        pyxel.bltm(130 -self.camera.x*scroll_ratio2,-10,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        pyxel.bltm( 60 -self.camera.x*scroll_ratio2, -4,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        pyxel.bltm(210 -self.camera.x*scroll_ratio2, -4,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        pyxel.bltm(-50 -self.camera.x*scroll_ratio2,  5,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        pyxel.bltm(510 -self.camera.x*scroll_ratio2, 10,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        pyxel.bltm(260 -self.camera.x*scroll_ratio2, 15,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        pyxel.bltm(370 -self.camera.x*scroll_ratio2, 20,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        pyxel.bltm(310 -self.camera.x*scroll_ratio2, 20,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        pyxel.bltm( 10 -self.camera.x*scroll_ratio2, 20,0,8* 0,8*48,8*23,8* 8,0) #暗茶
        ##砂山
        pyxel.bltm(140 -self.camera.x*scroll_ratio3, 10,0,8* 0,8*33,8*22,8*11,0) #明茶
        pyxel.bltm(-30 -self.camera.x*scroll_ratio3, 15,0,8* 0,8*33,8*22,8* 8,0) #明茶
        pyxel.bltm(230 -self.camera.x*scroll_ratio3, 20,0,8* 0,8*33,8*22,8* 7,0) #明茶
        pyxel.bltm(530 -self.camera.x*scroll_ratio3, 20,0,8* 0,8*33,8*22,8*11,0) #明茶
        pyxel.bltm(290 -self.camera.x*scroll_ratio3, 30,0,8* 0,8*33,8*22,8*10,0) #明茶
        pyxel.bltm(420 -self.camera.x*scroll_ratio3, 30,0,8* 0,8*33,8*22,8* 8,0) #明茶
        ###岩
        pyxel.blt(  34 -self.camera.x*scroll_ratio3,105,1,160,0,16*2,16*2,0)
        pyxel.blt( 115 -self.camera.x*scroll_ratio3, 75,1,160,0,16*2,16*2,0)
        pyxel.blt( 235 -self.camera.x*scroll_ratio3, 87,1,160,0,16*2,16*2,0)
        pyxel.blt( 235 -self.camera.x*scroll_ratio3, 87,1,160,0,16*2,16*2,0)
        pyxel.blt( 417 -self.camera.x*scroll_ratio3, 90,1,160,0,16*2,16*2,0)
        pyxel.blt( 505 -self.camera.x*scroll_ratio3, 85,1,160,0,16*2,16*2,0)
        pyxel.blt( 565 -self.camera.x*scroll_ratio3,105,1,160,0,16*2,16*2,0)
        ###剣
        pyxel.blt( 520 -self.camera.x*scroll_ratio3,110,1,176,32,8*2,8*3,3)
        ###宝石
        pyxel.blt( 210 -self.camera.x*scroll_ratio3,120,1,176,56,8*2,8*2,4)
        ### 落ちる砂の描画
        self.sand_frame[0] = (pyxel.frame_count) // 3 % 4
        self.sand_frame[1] = (pyxel.frame_count + 1) // 3 % 4
        self.sand_frame[2] = (pyxel.frame_count + 2) // 3 % 4
        self.sand_frame[3] = (pyxel.frame_count + 3) // 3 % 4
        if self.sandfall_points[0] == 0:
            ###初期化
            self.sandx = [ 72, 177, 262, 402,  0, 560, 250, 382, 32] #x座標
            self.width = [  5,   9,   7,   3,  6,   5,   4,   2,  2] #横幅
            self.sandy = [-11,  -7, -12, -11,  0,  -8,  -8,  -8, -8] #y座標
            self.times = [  5,   6,   8,   8, 11,  12,  11,  11, 11] #描画周期(縦の長さ)
            self.sandfall_points[0] = self.sandy[0] + 16 * self.times[0]
            self.sandfall_points[1] = self.sandy[1] + 16 * self.times[1]
            self.sandfall_points[2] = self.sandy[2] + 16 * self.times[2]
            self.sandfall_points[3] = self.sandy[3] + 16 * self.times[3]
            self.sandfall_points[4] = self.sandy[4] + 16 * self.times[4]
            self.sandfall_points[5] = self.sandy[5] + 16 * self.times[5]
            self.sandfall_points[6] = self.sandy[6] + 16 * self.times[6]
            self.sandfall_points[7] = self.sandy[7] + 16 * self.times[7]
            self.sandfall_points[8] = self.sandy[8] + 16 * self.times[8]
        #sandfall地点とplayerの位置比較で背景用を描画
        scroll_ratio4 = 1.01
        ###砂の滝でできた砂山
        pyxel.bltm( 30 -self.camera.x*scroll_ratio4, 60,0,   0,8*24,8*11,8*4,0) ##00
        pyxel.bltm(130 -self.camera.x*scroll_ratio4, 80,0,   0,8*28,8*12,8*4,0) ##01
        pyxel.bltm(230 -self.camera.x*scroll_ratio4, 95,0,8*11,8*24,8*9, 8*4,0) ##02
        pyxel.bltm(370 -self.camera.x*scroll_ratio4,110,0,8*12,8*28,8*10,8*4,0) ##03
        for i in range(0, 4):
            if self.player.position_y > self.sandfall_points[i]:
                self.drawSandFlow(self.sandx[i] -self.camera.x*scroll_ratio4, self.sandy[i],self. width[i], self.times[i], self.sand_frame[i%4],i) #x,y、幅、長さセット、描画周期のスタート位置
        ###EllipticalOrbitを描画
        for point in self.elliptical_orbits:
            # if point.pjty <= self.player.position_y:
            point.draw(self.camera.x, pyxel.frame_count)
        ###echoを描画
        for segment in self.segments:
            segment.draw()

    # def drawGoldFT(self):
    #     ###EllipticalOrbitを描画
    #     for point in self.elliptical_orbits:
    #         if point.pjty > self.player.position_y:
    #             point.draw(self.camera.x, pyxel.frame_count)

    def drawSandFlow(self,x,y,width,times,sand_i,sandindex):
        ###砂の滝
        for j in range(times):
            for k in range(width):
                pyxel.blt(x + k*2,y + 16 * j,2,72 + sand_i * 2,232,2,16,0)

    def drawSoilBG(self):
        # pyxel.cls(13)
        ###タイルマップの指定
        pyxel.bltm(0 -self.camera.x,0,0,0,8*160,8*75,8*32)

        soil_prllx_ratios = [0.92, 0.94, 0.96, 0.98, 1.00]
        ###墓石の描画（ノーマル）
        #1列目
        for n in range(7):
            if n in(2,3,4):
                pyxel.blt(130 + n*20 -self.camera.x,  0, 2, 208, 168, 16, 16, 3)
            else:
                pyxel.blt(130 + n*20 -self.camera.x,  0, 2, 192, 168, 16, 16, 3)
        #2列目
        for n in range(9):
            pyxel.blt(115 + n*20 -self.camera.x, 20, 2, 192, 168, 16, 16, 3)
        #3列目
        for n in range(12):
            pyxel.blt(110 + n*20 -self.camera.x, 40, 2, 192, 168, 16, 16, 3)
        #4列目
        for n in range(14):
            pyxel.blt( 90 + n*20 -self.camera.x, 60, 2, 192, 168, 16, 16, 3)
        #5列目
        for n in range(16):
            pyxel.blt( 80 + n*20 -self.camera.x, 80, 2, 192, 168, 16, 16, 3)
        #6列目
        for n in range(18):
            pyxel.blt( 70 + n*20 -self.camera.x,100, 2, 192, 168, 16, 16, 3)
        #7列目
        for n in range(20):
            pyxel.blt( 60 + n*20 -self.camera.x,120, 2, 192, 168, 16, 16, 3)


        ###犬の描画
        x_dog = 55
        y_dog = 136
        ###犬頭部＋胴体
        pyxel.blt(x_dog -self.camera.x, y_dog, 2, 136, 208, 16, 10, 3)
        ###尻尾
        if pyxel.frame_count // 3 % 2 == 0:
            pyxel.blt(x_dog +15 -self.camera.x, y_dog +1, 2, 136, 218, 8, 6, 3)
        elif pyxel.frame_count // 3 % 2 == 1:
            pyxel.blt(x_dog +15 -self.camera.x, y_dog +1 , 2, 144, 218, 8, 6, 3)

        ###playerのy位置が137以上のとき描画
        if self.player.y > 137:
            ###柱（手前列）
            pyxel.bltm( 30 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
            pyxel.bltm(180 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
            pyxel.bltm(290 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
            pyxel.bltm(440 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
            pyxel.bltm(570 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
            ###屋根
            pyxel.bltm(-20 -self.camera.x,  0, 0, 8*6,8*192,8*33,8*8,3)
            pyxel.bltm(243 -self.camera.x,  0, 0, 8*6,8*192,8*33,8*8,3)
            pyxel.bltm(506 -self.camera.x,  0, 0, 8*6,8*192,8*33,8*8,3)

            ###sunlinesの描画
            if len(self.sunlines) > 0:
                for sunline in self.sunlines:
                    sunline.draw(self.camera.x, 0, self.player.position_y)

    def drawSunBG(self):
        ##pyxel.cls(15)
        ###芝
        pyxel.bltm(0 -self.camera.x,0,0,0,72*8,600,300)
        ###キャラクターの描画
        pyxel.blt(100 - self.camera.x,100,1,0,96,24,16,3)
        ###尻尾
        if pyxel.frame_count // 3 % 2 == 0:
            pyxel.blt(100 + 24 - self.camera.x,100,1,24,96,    8,8,3)
        elif pyxel.frame_count // 3 % 2 == 1:
            pyxel.blt(100 + 24 - self.camera.x,100,1,24,96 + 8,8,8,3)
        ###particleの描画
        if len(self.psys_instances) > 0:
            self.drawParticles()
        ###天井からのheight
        ceil_height = 20
        window_height = 8*15
        ###天井付近壁
        pyxel.rect(0,0,600,ceil_height,15)
        ###レール
        pyxel.bltm(  0 - self.camera.x,ceil_height -5,0,0,8*122,8*40,8*1,3)
        pyxel.bltm(390 - self.camera.x,ceil_height -5,0,0,8*122,8*40,8*1,3)
        ###縁側
        pyxel.bltm(70 - 2    - self.camera.x,ceil_height + window_height -16,0,0,8*120, 8*11,8*2,0)
        pyxel.bltm(27 + 8*10.5 - self.camera.x,ceil_height + window_height -16,0,0,8*120,-8*11,8*2,0)
        ###窓１内窓
        pyxel.bltm(   0 - self.camera.x,ceil_height,0,   0,8*104,8*9,window_height,3) ##左
        ###窓２外窓
        pyxel.pal(7,13) ###フレームを暗く
        pyxel.pal(5,13) ###取っ手を暗く
        pyxel.bltm(8*28 - self.camera.x,ceil_height,0,8*12,8*104,8*9,window_height,3) ##右1-1
        pyxel.pal()
        pyxel.pal(7,13) ###フレームを暗く
        pyxel.bltm(8*37 -1 - self.camera.x,ceil_height,0,8* 8 -2,8*104,8*1,window_height,3) ##右1-2
        pyxel.pal()
        ###窓２内窓
        pyxel.bltm(8*24    - self.camera.x,ceil_height,       0,8*12,8*104,8*9,window_height,3) ##右2-1
        pyxel.bltm(8*33    - self.camera.x,ceil_height,       0,8* 7,8*104,8*2,window_height,3) ##右2-2
        pyxel.rect(8*34 -1 - self.camera.x,ceil_height + 8*8 +4,   3,8,7) ##取手消す
        ###窓３外窓
        pyxel.pal(7,13) ###フレームを暗く
        pyxel.pal(5,13) ###取っ手を暗く
        pyxel.bltm(8*59 +1 - self.camera.x,ceil_height,0,8*12,8*104,8*9,window_height,3)
        pyxel.pal()
        pyxel.pal(7,13) ###フレームを暗く
        pyxel.bltm(8*68    - self.camera.x,ceil_height,0,8* 8 -2,8*104,8*1,window_height,3)
        pyxel.pal()
        ###窓３内窓
        pyxel.bltm(8*51 +1   - self.camera.x,ceil_height,       0,8*12,8*104,8*9,window_height,3) ##右2-1
        pyxel.bltm(8*60    - self.camera.x,ceil_height,       0,8* 7,8*104,8*2,window_height,3) ##右2-2
        pyxel.rect(8*61  - self.camera.x,ceil_height + 8*8 +4,   3,8,7) ##取手消す
        ###屋内床
        pyxel.rect(0,ceil_height + window_height,600,300,15)
        ###屋内壁
        wall_width = 110
        pyxel.rect(250 + 56 - self.camera.x, ceil_height, wall_width, window_height, 15)
        ###カーペット1
        pyxel.bltm(    0    - self.camera.x,ceil_height + window_height + 15,0,8*31,8*104,8* 5,8*8,0)
        pyxel.bltm(8*  5 -1 - self.camera.x,ceil_height + window_height + 15,0,8*36,8*104,8*10,8*8,0)
        pyxel.bltm(8* 15 -2 - self.camera.x,ceil_height + window_height + 15,0,8*36,8*104,8*10,8*8,0)
        pyxel.bltm(8* 25 -3 - self.camera.x,ceil_height + window_height + 15,0,8*36,8*104,8*10,8*8,0)
        pyxel.bltm(8* 35 -4 - self.camera.x,ceil_height + window_height + 15,0,8*46,8*104,8* 8,8*8,0)
        ###本達
        pyxel.blt( 8* 10    - self.camera.x,ceil_height + window_height + 10, 2, 224, 152, 8*2, 8*2, 14)
        ##電源
        pyxel.blt( 277     - self.camera.x,150,2,144,160,16,16,3)
        pyxel.line(277 +15 - self.camera.x,157,277 +58 - self.camera.x,157,13)
        pyxel.line(335     - self.camera.x,157,335 +15 - self.camera.x,142,13)
        pyxel.rect(347     - self.camera.x,125,7,10,7)
        pyxel.rect(349     - self.camera.x,129,3,2,13)
        pyxel.line(350     - self.camera.x,142,350     - self.camera.x,130,13)
        ###カーペット2
        pyxel.bltm(8* 45    - self.camera.x,ceil_height + window_height + 15,0,8*46,8*104,-8* 8,8*8,0)
        pyxel.bltm(8* 53 -1 - self.camera.x,ceil_height + window_height + 15,0,8*36,8*104, 8*10,8*8,0)
        pyxel.bltm(8* 63 -2 - self.camera.x,ceil_height + window_height + 15,0,8*36,8*104, 8*10,8*8,0)
        pyxel.bltm(8* 73 -3 - self.camera.x,ceil_height + window_height + 15,0,8*36,8*104, 8*10,8*8,0)
        pyxel.bltm(8* 83 -4 - self.camera.x,ceil_height + window_height + 15,0,8*31,8*104,-8* 5,8*8,0)
        ###本棚1
        pyxel.bltm(15          - self.camera.x, ceil_height + window_height - 8* 7 +5, 0, 8*31, 8*112,  8* 2, 8* 7, 3)
        pyxel.bltm(15 + 8*2 -1 - self.camera.x, ceil_height + window_height - 8* 7 +5, 0, 8*31, 8*112, -8* 2, 8* 7, 3)
        # 1段目
        pyxel.blt(15 +2        - self.camera.x, ceil_height + window_height - 8* 7 +8, 2, 160, 144, 2, 8, 8)
        pyxel.blt(15 +2 +2     - self.camera.x, ceil_height + window_height - 8* 7 +8, 2, 162, 144,14, 8, 8)
        # 2段目
        pyxel.blt(15 +2        - self.camera.x, ceil_height + window_height - 8* 4   , 2, 160, 152,16, 8, 0)
        pyxel.blt(15 +2 +16    - self.camera.x, ceil_height + window_height - 8* 4   , 2, 160, 152,10, 8, 0)
        # 3段目
        pyxel.blt(15 +2 +10    - self.camera.x, ceil_height + window_height - 8* 2   , 2, 160, 160, 1, 8, 8)
        pyxel.blt(15 +2 +11    - self.camera.x, ceil_height + window_height - 8* 2   , 2, 161, 160,15, 8, 0)
        ###本棚２
        pyxel.bltm(560          - self.camera.x, ceil_height + window_height - 8* 7 +5, 0, 8*31, 8*112,  8* 2, 8* 7, 3)
        pyxel.bltm(560 + 8*2 -1 - self.camera.x, ceil_height + window_height - 8* 7 +5, 0, 8*31, 8*112, -8* 2, 8* 7, 3)
        # 1段目
        pyxel.blt(560 +2        - self.camera.x, ceil_height + window_height - 8* 7 +8, 2, 160, 144, 2, 8, 8)
        pyxel.blt(560 +2 +2     - self.camera.x, ceil_height + window_height - 8* 7 +8, 2, 162, 144,14, 8, 8)
        # 2段目
        pyxel.blt(560 +2        - self.camera.x, ceil_height + window_height - 8* 4   , 2, 160, 152,16, 8, 0)
        pyxel.blt(560 +2 +16    - self.camera.x, ceil_height + window_height - 8* 4   , 2, 160, 152,10, 8, 0)
        # 3段目
        pyxel.blt(560 +2 +10    - self.camera.x, ceil_height + window_height - 8* 2   , 2, 160, 160, 1, 8, 8)
        pyxel.blt(560 +2 +11    - self.camera.x, ceil_height + window_height - 8* 2   , 2, 161, 160,15, 8, 0)
        ###絵
        pyxel.bltm(318     - self.camera.x, ceil_height +  0, 0, 8*21, 8*104, 8*5, 8*5, 10)
        pyxel.bltm(318 +35 - self.camera.x, ceil_height +  0, 0, 8*26, 8*104, 8*5, 8*5, 10)
        pyxel.bltm(318     - self.camera.x, ceil_height + 35, 0, 8*21, 8*109, 8*5, 8*5, 10)
        pyxel.bltm(318 +35 - self.camera.x, ceil_height + 35, 0, 8*26, 8*109, 8*5, 8*5, 10)
        pyxel.bltm(318     - self.camera.x, ceil_height + 70, 0, 8*21, 8*114, 8*5, 8*5, 10)
        pyxel.bltm(318 +35 - self.camera.x, ceil_height + 70, 0, 8*26, 8*114, 8*5, 8*5, 10)
        ###カーテン
        pyxel.bltm(250 + 44 - self.camera.x, ceil_height -3, 0, 8*9, 8*104, 8*3, window_height, 0)
        pyxel.bltm(350 + 44 - self.camera.x, ceil_height -3, 0, 8*9, 8*104, 8*3, window_height, 0)

        ###時計
        # for i in range(0, 35):
        #     pyxel.blt(10 +23 * i - self.camera.x, 0, 1, 0, 216, 16, 16, 3) 
        pyxel.blt(10 +23 * 10 - self.camera.x, 0, 1, 0, 216, 16, 16, 3) 
        ###ストーブの光
        ###frame-countで光のゆらぎを表現した円を描画
        pyxel.circ(327 - self.camera.x, ceil_height + window_height -1, 2*Math.sin(pyxel.frame_count // 10 % 16 * Math.pi/16)+12,  9)
        pyxel.circ(327 - self.camera.x, ceil_height + window_height -1, 2*Math.sin(pyxel.frame_count // 10 % 15 * Math.pi/16)+ 8, 10)
        ###ストーブ
        pyxel.blt(320 - self.camera.x, ceil_height + window_height - 8, 1, 0, 232, 16, 24, 3)
        ###ヤカン
        if pyxel.frame_count // 20 % 2 == 0:
            pyxel.blt(318 - self.camera.x, ceil_height + window_height -17, 1, 144, 88, 16, 11, 0)
        elif pyxel.frame_count // 20 % 2 == 1:
            pyxel.blt(318 - self.camera.x, ceil_height + window_height -17, 1, 144, 99, 16, 11, 0)
        ###BOOK
        self.drawBookBG(500 - self.camera.x, ceil_height + window_height - 8* 4 + 5)

    def drawEndBG(self):
        # test-background-color
        pyxel.cls(15)

    def drawParticles(self):
        ### 有効なパーティクルをすべて描画する
        if len(self.psys_instances) > 0:
            for psys in self.psys_instances:
                ###スクロールを加味して画面枠0〜300内のパーティクルのみ描画
                # psys.draw_particles(0,0,300)
                psys.draw_particles(self.camera.x,0,300)


    def drawBookBG(self,x,y):
        ##祠と本を描画
        pyxel.blt(x,y,2,208,104,32,32,15)
        bx,by = x+8,y+10
        dh = 0
        if pyxel.frame_count // 10 % 8 in(0,4):
            dh = 0
        elif pyxel.frame_count // 10 % 8 in(1,3):
            dh = 1
        elif pyxel.frame_count // 10 % 8 == 2:
            dh = 2
        elif pyxel.frame_count // 10 % 8 in(5,7):
            dh = -1
        elif pyxel.frame_count // 10 % 8 == 6:
            dh = -2
        pyxel.blt(bx,by+dh,2,240,88,16,16,0)

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
                pyxel.blt( 15 + 5 - self.camera.x, 145, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
                pyxel.blt(150 + 5 - self.camera.x, 145, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
                pyxel.blt(245 + 5 - self.camera.x, 145, 2, 16 * 5, 16 * 5,-16 * 1, 16 * 6,3)
                pyxel.blt(365 + 5 - self.camera.x, 145, 2, 16 * 5, 16 * 5,-16 * 1, 16 * 6,3)
                pyxel.blt(480 + 5 - self.camera.x, 145, 2, 16 * 5, 16 * 5, 16 * 1, 16 * 6,3)
                ###電線1
                self.drawElectricalwire( 90 -150 - self.camera.x,60 -5,240 -150 - self.camera.x,60 -5)
                self.drawElectricalwire( 90      - self.camera.x,60 -5,240      - self.camera.x,60 -5)
                self.drawElectricalwire( 90 +150 - self.camera.x,60 -5,240 +150 - self.camera.x,60 -5)
                self.drawElectricalwire( 90 +300 - self.camera.x,60 -5,240 +300 - self.camera.x,60 -5)
                self.drawElectricalwire( 90 +450 - self.camera.x,60 -5,240 +450 - self.camera.x,60 -5)
                ###電線2
                self.drawElectricalwire( 90 -150 - self.camera.x,60,240 -150 - self.camera.x,60)
                self.drawElectricalwire( 90      - self.camera.x,60,240      - self.camera.x,60)
                self.drawElectricalwire( 90 +150 - self.camera.x,60,240 +150 - self.camera.x,60)
                self.drawElectricalwire( 90 +300 - self.camera.x,60,240 +300 - self.camera.x,60)
                self.drawElectricalwire( 90 +450 - self.camera.x,60,240 +450 - self.camera.x,60)
                ###電信柱
                pyxel.blt(82 - self.camera.x, 50, 2, 16 * 6, 0, -16 * 1, 16 * 11,3)
                pyxel.rect(93 - self.camera.x, 182, 3, 8, 1)
                pyxel.blt(82 + 150 - self.camera.x, 50, 2, 16 * 6, 0, -16 * 1, 16 * 11,3)
                pyxel.rect(93 + 150 - self.camera.x, 182, 3, 8, 1)
                pyxel.blt(82 + 300 - self.camera.x, 50, 2, 16 * 6, 0, -16 * 1, 16 * 11,3)
                pyxel.rect(93 + 300 - self.camera.x, 182, 3, 8, 1)
                pyxel.blt(82 + 450 - self.camera.x, 50, 2, 16 * 6, 0, -16 * 1, 16 * 11,3)
                pyxel.rect(93 + 450 - self.camera.x, 182, 3, 8, 1)
                ###塀
                pyxel.bltm(-32 - self.camera.x,8 * 25, 2, 0, 8 * 36, 8 * 40 + self.camera.x + 32, 8 * 4,0)
                ###猫
                self.frames = Math.floor(pyxel.frame_count/9) % 10
                pyxel.blt(450 - self.camera.x, 190, 1, 16 * 7, 0 + self.frames * 16,  16 * 1, 16 * 1,6)

            if(self.gamestate.scene == C_SCENE_MOON):
                ###紙垂の描画
                self.drawSideLine(85,9)

            if(self.gamestate.scene == C_SCENE_FIRE):


                for point3d in self.points3d:
                    for point in point3d.points:
                        ###個々の光点の座標がplayerのyより手前にあれば描画
                        # if (point.z > 0 and point.y <= self.player.position_y) or (point.y > self.player.position_y):
                        if (point.draw_y > self.player.position_y):
                            point.draw(self.camera.x)
                ###生成された蛍の描画
                for point3d in self.points3d:
                    for point in point3d.points:
                        ###個々の光点の座標がplayery座標より小さいか、奥にあれば描画
                        # if (point.z <= 0 and point.y > self.player.position_y) or (point.y <= self.player.position_y):
                        if (point.y <= self.player.position_y):
                            point.draw(self.camera.x)
                ###
                ###石柱（小）の描画（青）
                for i in range(0, 42):
                    ###３００幅の画面外は描画しない
                    if(i * 16 - self.camera.x < 300):
                        pyxel.blt( 3 + i * 16 - self.camera.x, 8 * 27, 1, 64, 240, 8, 16, 0)
                

                ###紙垂の描画
                self.drawSideLine( 65,9)
                self.drawSideLine(180,9)

                ###デモタイトル表示
                # self.bdf2.draw_text(150, 2, "PRESS V : 蛍", 7) 

            ###波紋の戸
            if(self.gamestate.scene == C_SCENE_WATER):
                ###雨筋(playerのposition_yよりY値が大きい着水点)
                for i in range(0, 19):
                    if(self.rain_depth[i] == 1):
                        if self.rain_draw_counter[i] == 15:
                            pyxel.line(self.rain_landing_x[i] - self.camera.x, -1, self.rain_landing_x[i] - self.camera.x, self.rain_landing_y[i] -60, 6)
                            pyxel.line(self.rain_landing_x[i] - self.camera.x, self.rain_landing_y[i] -60, self.rain_landing_x[i] - self.camera.x, self.rain_landing_y[i], 12)
                        if self.rain_draw_counter[i] in(14,15):
                            pyxel.blt(self.rain_landing_x[i] -8 - self.camera.x, self.rain_landing_y[i] - 4, 2, 40, 24,  16, 8,0)
                ###playerの足元の水はね
                if player_moving:
                    wk_frames1 = Math.floor(pyxel.frame_count/6) % 4
                    wk_frames2 = Math.floor(pyxel.frame_count/5) % 3
                    wk_frames3 = Math.floor(pyxel.frame_count/5) % 2
                    wk_frames4 = (wk_frames2 + 1)%3
                    if self.player.player_direction == 0:
                        pyxel.blt(self.player.position_x  +2 -self.camera.x, self.player.position_y -8, 2, 64, wk_frames2 * 5,  12, 5, 0)
                        pyxel.blt(self.player.position_x -14 -self.camera.x, self.player.position_y -8, 2, 64, wk_frames4 * 5, -12, 5, 0)
                        pyxel.blt(self.player.position_x  +4 -self.camera.x, self.player.position_y -4, 2, 82, 20 + wk_frames3 * 3, 6, 3, 0)
                        pyxel.blt(self.player.position_x -12 -self.camera.x, self.player.position_y -4, 2, 82, 20 + wk_frames3 * 3,-6, 3, 0)
                        pyxel.blt(self.player.position_x  +4 -self.camera.x, self.player.position_y -2, 2, 76, 20 + wk_frames3 * 6, 6, 6, 0)
                        pyxel.blt(self.player.position_x -12 -self.camera.x, self.player.position_y -2, 2, 76, 20 + wk_frames3 * 6,-6, 6, 0)

                    if self.player.player_direction == 1:
                        pyxel.blt(self.player.position_x  -4 -self.camera.x, self.player.position_y -4, 2, 77, wk_frames1 * 5,  11, 5, 0)
                        pyxel.blt(self.player.position_x  +2 -self.camera.x, self.player.position_y -4, 2, 64, wk_frames2 * 5,  12, 5, 0)
                        pyxel.blt(self.player.position_x -14 -self.camera.x, self.player.position_y -4, 2, 64, wk_frames4 * 5, -12, 5, 0)

                    if self.player.player_direction == 2:
                        pyxel.blt(self.player.position_x -14 -self.camera.x, self.player.position_y -4, 2, 64, wk_frames2 * 5, -12, 5, 0)
                        pyxel.blt(self.player.position_x  +2 -self.camera.x, self.player.position_y -4, 2, 64, wk_frames2 * 5 + 16,  12, 5, 0)
                    if self.player.player_direction == 3:
                        pyxel.blt(self.player.position_x  +2 -self.camera.x, self.player.position_y -4, 2, 64, wk_frames2 * 5,  12, 5, 0)
                        pyxel.blt(self.player.position_x -14 -self.camera.x, self.player.position_y -4, 2, 64, wk_frames2 * 5 + 16, -12, 5, 0)
                
                ###WaterTree
                self.drawWaterFT()
                ###紙垂の描画
                self.drawSideLine(65,9)


            if(self.gamestate.scene == C_SCENE_WOOD):
                ###木の描画
                self.drawTreesFT()
                ###草を描画
                for grass in self.grasses:
                    ###画面枠（X座標０〜３００）外の草は描画しないようにする
                    ###適用カメラに係数でパララックスをかける
                        grass.draw(self.camera.x * 1.2, 0, 300)
                # 花を描画
                ###適用カメラに係数でパララックスをかける
                for flower in self.flowers:
                    flower.draw(self.camera.x * 1.2,0, 0, 300)
                # ###デモタイトル表示
                # self.bdf2.draw_text(150, 2, "PRESS V : particle生成", 7) 

                ###紙垂の描画
                self.drawSideLine(65,9)


            if(self.gamestate.scene == C_SCENE_GOLD):
                ###被playerの位置によって描画順序を変える対象の描画
                # self.drawGoldFT()
                ###sandfall地点とplayerの位置比較で前景として描画
                for i in range(0, 4):
                    if self.player.position_y <= self.sandfall_points[i] :
                        self.drawSandFlow(self.sandx[i] -self.camera.x, self.sandy[i], self.width[i], self.times[i], self.sand_frame[i%4],i) #x,y、幅、長さセット、描画周期のスタート位置

                ###紙垂の描画
                self.drawSideLine(45,1)

                ###最前景用
                scroll_ratio5 = 1.05
                pyxel.bltm( -95 -self.camera.x*scroll_ratio5,160,0,8* 0,8*48,8*23,8* 8,0)
                pyxel.bltm( -40 -self.camera.x*scroll_ratio5,160,0,8* 0,8*33,8*22,8*11,0)
                pyxel.bltm( 310 -self.camera.x*scroll_ratio5,160,0,8* 0,8*33,8*22,8*11,0)
                pyxel.bltm( 470 -self.camera.x*scroll_ratio5,176,0,8* 0,8*48,8*23,8* 8,0)
                pyxel.bltm( 180 -self.camera.x*scroll_ratio5,160,0,8* 0,8*33,8*22,8*11,0)
                ###岩
                pyxel.blt( 142 -self.camera.x*scroll_ratio5, 205,1,160,0,16*2,16*2,0)

                ###流砂
                for i in range(4, 9):
                    self.drawSandFlow(self.sandx[i] -self.camera.x*scroll_ratio5, self.sandy[i], self.width[i], self.times[i], self.sand_frame[i%4],i) #x,y、幅、長さセット、描画周期のスタート位置

                ###デモタイトル表示
                # self.bdf2.draw_text(150, 2, "PRESS E : IN/OUT", 7) 
                # self.bdf2.draw_text(150,14, "PRESS R : 白銀比/黄金比", 7) 
                # self.bdf2.draw_text(150,26, "PRESS T : angle +15", 7) 

            if(self.gamestate.scene == C_SCENE_SOIL):
                ###蝶の描画
                if len(self.butterflies) > 0:
                    for butterfly in self.butterflies:
                        butterfly.draw(self.camera.x)

                ###playerのy位置が137以下のとき描画
                if self.player.y <= 137:
                    ###柱（手前列）
                    pyxel.bltm( 30 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
                    pyxel.bltm(180 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
                    pyxel.bltm(290 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
                    pyxel.bltm(440 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
                    pyxel.bltm(570 -self.camera.x,8*7, 0, 8*0,8*192,8*2,8*16,3)
                    ###屋根
                    pyxel.bltm(-20 -self.camera.x,  0, 0, 8*6,8*192,8*33,8*8,3)
                    pyxel.bltm(243 -self.camera.x,  0, 0, 8*6,8*192,8*33,8*8,3)
                    pyxel.bltm(506 -self.camera.x,  0, 0, 8*6,8*192,8*33,8*8,3)

                ###sunlinesの描画
                if len(self.sunlines) > 0:
                    for sunline in self.sunlines:
                        sunline.draw(self.camera.x, 1, self.player.position_y)
                
                ###紙垂の描画
                self.drawSideLine(55,1)

                ###木々の描画
                pyxel.bltm(-20        -self.camera.x,    0, 0,  0,  8*208,  8*16,  8*8, 0)
                pyxel.bltm(-20 + 8*14 -self.camera.x,  -12, 0,  0,  8*208,  8*16,  8*8, 0)
                pyxel.bltm(-20 + 8*27 -self.camera.x,   -6, 0,  0,  8*208,  8*16,  8*8, 0)
                pyxel.bltm(-20 + 8*41 -self.camera.x,    0, 0,  0,  8*208,  8*16,  8*8, 0)
                pyxel.bltm(-20 + 8*56 -self.camera.x,   -6, 0,  0,  8*208,  8*16,  8*8, 0)
                pyxel.bltm(-20 + 8*71 -self.camera.x,  -13, 0,  0,  8*208,  8*16,  8*8, 0)


            if(self.gamestate.scene == C_SCENE_SUN):
                ###　観葉植物
                # for i in range(0, 60):
                #     pyxel.blt( i*20 - self.camera.x,184,2,192,104,16,48,0)
                pyxel.blt( 5*20 - self.camera.x,184,2,192,104,16,48,0)
                pyxel.blt( 15*20 - self.camera.x,184,2,192,104,16,48,0)
    
                ###紙垂の描画
                self.drawSideLine(20,9)

            if(self.gamestate.scene == C_SCENE_END):
                ###　観葉植物 # テスト用
                pyxel.blt( 5*20 - self.camera.x,184,2,192,104,16,48,0)
                pyxel.blt( 15*20 - self.camera.x,184,2,192,104,16,48,0)

                ###紙垂の描画
                self.drawSideLine(35,1)


            ###scene,scenetimerに応じた描画
            if self.gamestate.door_transition :
                ###円の描画を行う場合
                startsec_stageboard = 15
                endsec_stageboard   = 125
                #--
                startsec_stageline  = 35
                middlesec_stageline = 70
                endsec_stageline    = 90
                #--
                startsec_stagetxt   = 35
                endsec_stagetxt     = 90
            else:
                startsec_stageboard = 0
                endsec_stageboard   = 110
                #--
                startsec_stageline  = 20
                middlesec_stageline = 55
                endsec_stageline    = 65
                #--
                startsec_stagetxt = 20
                endsec_stagetxt = 65

            if startsec_stageboard <= self.gamestate.scenetimer < endsec_stageboard:
                upper_line_y = 127
                lower_line_y = 152
                if startsec_stageline <= self.gamestate.scenetimer < middlesec_stageline:
                    ###画面中央に黒い帯を表示
                    pyxel.rect(0, 125, 300, 30, 0)
                    ###白のlineを描画
                    pyxel.line(0, upper_line_y, 300, upper_line_y, 7)
                    pyxel.line(0, lower_line_y, 300, lower_line_y, 7)
                elif middlesec_stageline <= self.gamestate.scenetimer < endsec_stageline:
                    if startsec_stageline <= self.gamestate.scenetimer < middlesec_stageline:
                        ###画面中央に黒い帯を表示
                        pyxel.rect(0, 125, 300, 30, 0)
                        ###白のlineを描画
                        pyxel.line(0, upper_line_y, 300, upper_line_y, 7)
                        pyxel.line(0 + 20 * (self.gamestate.scenetimer-startsec_stageline), lower_line_y, 300, lower_line_y, 7)
                    elif middlesec_stageline <= self.gamestate.scenetimer < endsec_stageline:
                        ###画面中央に黒い帯を表示
                        pyxel.rect(0, 125, 300, 30 -2*(self.gamestate.scenetimer-middlesec_stageline), 0)
                        ###白のlineを描画
                        pyxel.line(0, upper_line_y, 300 -20 * (self.gamestate.scenetimer-middlesec_stageline), upper_line_y, 7)

                if startsec_stagetxt <= self.gamestate.scenetimer < endsec_stagetxt:
                    if self.gamestate.scene == C_SCENE_HOME:
                        if (self.gamestate.scenario[0][1] == 0):
                            self.bdf2.draw_text(130, 132, "浜辺", 7)
                        if (self.gamestate.scenario[0][1] >= 1):
                            self.bdf2.draw_text(118, 132, "浜辺", 7)
                    if self.gamestate.scene == C_SCENE_MOON:
                        self.bdf2.draw_text(120, 132, "月見丘", 7)
                    if self.gamestate.scene == C_SCENE_FIRE:
                        self.bdf2.draw_text(115, 132, "灯籠の路", 7)
                    if self.gamestate.scene == C_SCENE_WATER:
                        self.bdf2.draw_text(120, 132, "雨の林", 7)
                    if self.gamestate.scene == C_SCENE_WOOD:
                        self.bdf2.draw_text(120, 132, "緑の桟道", 7)
                    if self.gamestate.scene == C_SCENE_GOLD:
                        self.bdf2.draw_text(120, 132, "砂の檻", 7)
                    if self.gamestate.scene == C_SCENE_SOIL:
                        self.bdf2.draw_text(120, 132, "献花場", 7)
                    if self.gamestate.scene == C_SCENE_SUN:
                        self.bdf2.draw_text(120, 132, "雪の日", 7)
                    if self.gamestate.scene == C_SCENE_END:
                        self.bdf2.draw_text(120, 132, "主の部屋", 7)
                    if self.gamestate.scene == C_SCENE_CHOICE:
                        self.bdf2.draw_text(130, 132, "帰路", 7)
            
            ###メニュー＆会話用のエリアを黒く表示する
            pyxel.rect(0, 232, 300, 68, 0)    

            ###デバッグ用デモタイトル表示
            pyxel.rect(5, 2, 110, 51, 1)
            self.bdf2.draw_text(10, 2, self.getModeName(), 7) 
            self.bdf2.draw_text(10,14, self.getSceneName(), 7) 
            self.bdf1.draw_text(55, 2, "x:" + str(self.player.x), 7) 
            self.bdf1.draw_text(55,12, "y:" + str(self.player.y), 7) 
            self.bdf1.draw_text(45,22, "scene   :" + str(self.gamestate.scenario[0][0]), 7)
            self.bdf1.draw_text(45,32, "scenario:" + str(self.gamestate.scenario[0][1]), 7)
            self.bdf1.draw_text(45,42, "branch  :" + str(self.gamestate.scenario[0][2]), 7)


    def drawElectricalwire(self,sx,sy,ex,ey,col=1):
        ###PLAYモード共通ロジック
        if (self.gamestate.mode == C_PLAY):
            self.start_point = [sx,sy]
            self.end_point = [ex,ey]
            self.full_line = ex - sx
            self.line_color = col #deepblue
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

    def drawSideLine(self,by=85,sidecol=9):
                ###紙垂用ラインのパラメタ指定
                start_x = 90
                end_x = 240
                base_y = by
                base_spanx = 150
                sideline_col = sidecol
                paper_start_x = 64
                side_spanx = 32

                blocknum0, blocknum1, blocknum2, blocknum3 = 0, 1, 2, 3

                ###紙垂用のライン１
                self.drawElectricalwire( start_x -base_spanx   - self.camera.x,base_y,end_x -base_spanx   - self.camera.x,base_y,sideline_col)
                self.drawElectricalwire( start_x               - self.camera.x,base_y,end_x               - self.camera.x,base_y,sideline_col)
                self.drawElectricalwire( start_x +base_spanx  - self.camera.x,base_y,end_x +base_spanx   - self.camera.x,base_y,sideline_col)
                self.drawElectricalwire( start_x +base_spanx*2 - self.camera.x,base_y,end_x +base_spanx*2 - self.camera.x,base_y,sideline_col)
                self.drawElectricalwire( start_x +base_spanx*3 - self.camera.x,base_y,end_x +base_spanx*3 - self.camera.x,base_y,sideline_col)
                ###紙垂1
                pyxel.blt(paper_start_x - base_spanx + side_spanx * 0 - self.camera.x, base_y + 3, 1, 64 + 4*blocknum0, 224, 4, 16, 0)
                pyxel.blt(paper_start_x - base_spanx + side_spanx * 1 - self.camera.x, base_y + 2, 1, 64 + 4*blocknum1, 224, 4, 16, 0)
                pyxel.blt(paper_start_x - base_spanx + side_spanx * 2 - self.camera.x, base_y + 6, 1, 64 + 4*blocknum2, 224, 4, 16, 0)
                pyxel.blt(paper_start_x - base_spanx + side_spanx * 3 - self.camera.x, base_y + 7, 1, 64 + 4*blocknum3, 224, 4, 16, 0)
                ###紙垂2
                pyxel.blt(paper_start_x + base_spanx * 0 + side_spanx * 0 - self.camera.x, base_y + 3, 1, 64 + 4*blocknum0, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 0 + side_spanx * 1 - self.camera.x, base_y + 2, 1, 64 + 4*blocknum1, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 0 + side_spanx * 2 - self.camera.x, base_y + 6, 1, 64 + 4*blocknum2, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 0 + side_spanx * 3 - self.camera.x, base_y + 7, 1, 64 + 4*blocknum3, 224, 4, 16, 0)
                ###紙垂3
                pyxel.blt(paper_start_x + base_spanx * 1 + side_spanx * 0 - self.camera.x, base_y + 3, 1, 64 + 4*blocknum0, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 1 + side_spanx * 1 - self.camera.x, base_y + 2, 1, 64 + 4*blocknum1, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 1 + side_spanx * 2 - self.camera.x, base_y + 6, 1, 64 + 4*blocknum2, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 1 + side_spanx * 3 - self.camera.x, base_y + 7, 1, 64 + 4*blocknum3, 224, 4, 16, 0)
                ###紙垂4
                pyxel.blt(paper_start_x + base_spanx * 2 + side_spanx * 0 - self.camera.x, base_y + 3, 1, 64 + 4*blocknum0, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 2 + side_spanx * 1 - self.camera.x, base_y + 2, 1, 64 + 4*blocknum1, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 2 + side_spanx * 2 - self.camera.x, base_y + 6, 1, 64 + 4*blocknum2, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 2 + side_spanx * 3 - self.camera.x, base_y + 7, 1, 64 + 4*blocknum3, 224, 4, 16, 0)
                ###紙垂5
                pyxel.blt(paper_start_x + base_spanx * 3 + side_spanx * 0 - self.camera.x, base_y + 3, 1, 64 + 4*blocknum0, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 3 + side_spanx * 1 - self.camera.x, base_y + 2, 1, 64 + 4*blocknum1, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 3 + side_spanx * 2 - self.camera.x, base_y + 6, 1, 64 + 4*blocknum2, 224, 4, 16, 0)
                pyxel.blt(paper_start_x + base_spanx * 3 + side_spanx * 3 - self.camera.x, base_y + 7, 1, 64 + 4*blocknum3, 224, 4, 16, 0)

    def drawObjects(self):
        ###HOMEシーン用オブジェクトの描画
        if (self.gamestate.mode == C_PLAY):
            if(self.gamestate.scene in(C_SCENE_HOME, C_SCENE_MOON, C_SCENE_FIRE, C_SCENE_WATER, C_SCENE_WOOD, C_SCENE_GOLD, C_SCENE_SOIL, C_SCENE_SUN, C_SCENE_END)):
                for obj in doors:
                    obj.draw()
                ###当たり判定用オブジェクト（非描画）をスクロール加味しない状態への「戻し」
                for obj in ataris:
                    obj.draw()

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
                self.nearest_obj,self.nearest_obj_distancetoPlayer = self.checkObjectsListDistance()
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

            return self.rtn_obj, distance

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



    def updateBtnInputCheck(self):
        ###PLAYモード共通ロジック
        if (self.gamestate.mode == C_PLAY) and (self.inputdelay_cnt == 0):
            ###ボタン入力検知（Tキー） ### デバッグ用のシナリオ番号操作キー。ブランチはリセットする。
            if pyxel.btnp(pyxel.KEY_T):
                self.gamestate.scenario[0][1] += 1
                if(self.gamestate.scenario[0][1] == 9):
                    self.gamestate.scenario[0][1] = 0
                self.gamestate.scenario[0][2] = 0
                self.inputdelay_cnt = self.inptdelay_C #入力受付遅延用カウンタをリセット
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
                                    self.name_disp = self.player.name_disp
                                    self.talking_chara_face_no = self.player.face_no
                                else:
                                    if (self.nearest_obj.__class__.__name__ in("Jerry","Atari")):
                                        wk_no = self.nearest_obj.obj_no
                                        if len(str(wk_no)) == 1:
                                            wk_no4 = "990"+str(wk_no)
                                        elif len(str(wk_no)) == 2:
                                            wk_no4 = "99"+str(wk_no)
                                        self.talking_chara_no = int(wk_no4)
                                        self.name_disp = self.nearest_obj.name_disp
                                    else:
                                        self.talking_chara_no = 99
                                ###会話相手の返答待ち状態フラグを戻す
                                self.nearest_obj.cancelFlgWaitingResponce()
                            else:
                                ###相手が自身から発話するとき
                                ###ドアの場合、可視状態じゃない時は何もしない
                                if (self.nearest_obj.__class__.__name__ == "Door"):
                                    if (self.nearest_obj.visible == True):
                                        self.getText(self.nearest_obj)
                                        self.talking_chara_no = 99                                        
                                if (self.nearest_obj.__class__.__name__ in("Character","Jerry","Atari")):
                                    self.getText(self.nearest_obj)
                                    ###テキストウィンドウ表示用顔グラ判別のためのキャラ番号取得
                                    if (self.nearest_obj.__class__.__name__ == "Character"):
                                        self.talking_chara_no = self.nearest_obj.character_no
                                        self.name_disp = self.nearest_obj.name_disp
                                        self.talking_chara_face_no = self.nearest_obj.face_no
                                    if (self.nearest_obj.__class__.__name__ in("Jerry","Atari")):
                                        wk_no = self.nearest_obj.obj_no
                                        if len(str(wk_no)) == 1:
                                            wk_no4 = "990"+str(wk_no)
                                        elif len(str(wk_no)) == 2:
                                            wk_no4 = "99"+str(wk_no)
                                        self.talking_chara_no = int(wk_no4)
                                        self.name_disp = self.nearest_obj.name_disp

                            if (self.nearest_obj.__class__.__name__ == "Door"):
                                if (self.nearest_obj.visible == True):
                                    self.pressed_space_checking = True
                                    self.display_finished = False
                                    self.inputdelay_cnt = self.inptdelay_C #入力受付遅延用カウンタをリセット
                            if (self.nearest_obj.__class__.__name__ in("Character","Jerry","Atari")):
                                self.pressed_space_checking = True
                                self.display_finished = False
                                self.inputdelay_cnt = self.inptdelay_C #入力受付遅延用カウンタをリセット

                    ##スペース打鍵によるチェックフラグが有効中
                    else:
                        if (self.nearest_obj.__class__.__name__ == "Door"):
                            self.nearest_obj.flg_ocreaction = True
                        if(self.display_finished): ##分割テキストを表示完了
                            ###テキストが表示完了しているとき
                            if(len(self.wk_textset3)==1) and \
                            (self.framecount_for_text_disp >= (len(self.wk_textset3[0]))) \
                            or(len(self.wk_textset3)==2) and \
                            (self.framecount_for_text_disp >= (len(self.wk_textset3[0])+len(self.wk_textset3[1]))) \
                            or(len(self.wk_textset3)==3) and \
                            (self.framecount_for_text_disp >= (len(self.wk_textset3[0])+len(self.wk_textset3[1])+len(self.wk_textset3[2]))):

                                ###話しかけた・調べた対象のオブジェクトがキャラクターだった場合、方向を元の位置に戻す
                                if (self.nearest_obj.__class__.__name__ == "Character"):
                                    self.nearest_obj.player_direction = self.checking_obj_direction

                                self.pressed_space_checking = False #「SPACEキー打鍵によるチェック中」フラグをOFF
                                self.inputdelay_cnt = self.inptdelay_C #入力受付遅延用カウンタをリセット
                                self.wk_textset_divided = list() #表示用テキストをリセット。
                                self.text_divided = False #分割済みフラグのクリア

                                ###話しかけた・調べた対象のオブジェクトがドアだった場合、戸が持つルーム番号に応じてgamestateのシーン番号を変える
                                if  (self.nearest_obj.__class__.__name__ == "Door"):
                                    if (self.nearest_obj.visible == True) and \
                                      self.nearest_obj_distancetoPlayer < 10 and self.object_pos_update_frames == 0:
                                        if (self.nearest_obj.room_no != 0)  or \
                                        (self.nearest_obj.room_no == 0 and self.gamestate.scene != 0):
                                            ###現在のscene情報を退避
                                            self.prescene = self.gamestate.scene
                                            self.deleteObjectsDependingOnScene() ##現在のシーンに応じてオブジェクトを削除しリセット
                                            self.gamestate.door_open_array_bf = self.gamestate.door_open_array.copy() #ドアの開閉状態を保持
                                            ###現在のシーンで戸を出るとき、次のナンバリングの戸をアンロックする
                                            next_scene = (self.gamestate.scene + 1) % len(self.gamestate.door_open_array)
                                            self.gamestate.unlock_door(next_scene)
                                            ###テキスト処理用変数をリセット
                                            self.inputdelay_cnt = 0 #入力受付遅延用カウンタをリセット
                                            self.pressed_space_checking = False #「SPACEキー打鍵によるチェック中」フラグをOFF
                                            # ###scroll関係変数をリセット
                                            self.scroll_direction = 0
                                            # self.scroll_x = 0
                                            # self.scroll_distance = 0
                                            self.gamestate.scene = self.nearest_obj.room_no
                                            self.gamestate.scenario[0][0] = self.nearest_obj.room_no
                                            self.gamestate.scenetimer = 0
                                            ##選択中ドア(＝scene)と現在シナリオ状態から、ドア先用にシナリオ番号の初期値をセットし直す
                                            self.doorScenarioSet(self.nearest_obj.room_no, self.gamestate.scenario[0][1], self.gamestate.scenario[0][2])
                                            ###パララックス背景用変化率をSceneに応じてリセット
                                            self.parallax_value_set(self.gamestate.scene)
                                            ###パララックス背景用スクロール値をリセット
                                            self.scroll_positions = [0.1 for _ in range(9)]
                                            # ###パーティクルシステムのインスタンスをリセット
                                            self.psys_instances = list()
                                            self.generateObjects() ##現在のシーンに応じてオブジェクトを生成
                                            ###チェック中のオブジェクトをリセット
                                            self.nearest_obj = None
                                            self.nearest_obj_distancetoPlayer = 999
                                            ###チェック中のオブジェクトがいる方向、をリセット
                                            self.checking_obj_direction = 4
                                            ###パーティクルシステムのタイマーをリセット
                                            self.timer_for_psys = 0
                                            ###トランジション描画のために、フェードアウト用のフラグをONにする
                                            self.gamestate.door_transition = True
                                            door_tran_particles.append([DoorTranParticle() for _ in range(48)])

                                ###話しかけた・調べた対象がキャラクターまたはアタリオブジェクトだった場合、オブジェクトチェック機能を呼び出す。
                                if (self.nearest_obj.__class__.__name__ in("Character", "Atari", "Jerry")):
                                    ##取得アイテムチェック
                                    self.checkGetItem(self.nearest_obj)
                                    ###話しかけた・調べた対象objと進行度に応じた周辺オブジェクトへの状態変化を実行
                                    self.checkObjStatusChange(self.nearest_obj)
                                    ##体力への影響チェック（減少）
                                    self.checkDamage(self.nearest_obj)
                                    ##体力への影響チェック（増加）
                                    self.checkRecovery(self.nearest_obj)
                                    
                            else:
                                ###テキストが表示完了していないとき、テキスト表示を完了させる
                                self.framecount_for_text_disp = 999


                        else: ##分割テキストを表示未完了
                            ###テキスト表示用フレームカウントが規定値に達している場合に打鍵を受け付ける
                            if(len(self.wk_textset3)==1) and \
                            (self.framecount_for_text_disp >= (len(self.wk_textset3[0]))) \
                            or(len(self.wk_textset3)==2) and \
                            (self.framecount_for_text_disp >= (len(self.wk_textset3[0])+len(self.wk_textset3[1]))) \
                            or(len(self.wk_textset3)==3) and \
                            (self.framecount_for_text_disp >= (len(self.wk_textset3[0])+len(self.wk_textset3[1])+len(self.wk_textset3[2]))):
                                ###テキストセット表示カウンタを進める
                                self.wk_text_disp_times += 1
                                ###テキスト表示経過時間の管理変数をリセット
                                self.framecount_for_text_disp = 0
                                self.framecount_for_text_disp1 = 0
                                self.framecount_for_text_disp2 = 0
                                self.framecount_for_text_disp3 = 0
                                self.framecount_for_text_disp_first = 0
                            else:
                                ###テキストが表示完了していないとき、テキスト表示を完了させる
                                self.framecount_for_text_disp = 999

                
                    ###Doorオブジェクトのopen/close状態変化
                    if self.wk_player.player_direction == 0:
                        for door in doors:
                            if door.flg_ocreaction :
                                if door.is_closed:
                                    door.openStart()
                                if door.is_opened:
                                    door.closeStart()

            ###ボタン入力検知（Mキー）
            if pyxel.btnp(pyxel.KEY_M) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                print("M key is pressed in PLAY-MODE!")
                pyxel.play(3,22) #SE再生(Menuオープン)
                self.gamestate.mode = C_MENU
                self.inputdelay_cnt = self.inptdelay_C

        if (self.gamestate.mode == C_MENU) and (self.inputdelay_cnt == 0):
            ###ボタン入力検知（Mキー）
            if pyxel.btnp(pyxel.KEY_M) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_X):
                pyxel.play(3,23) #SE再生(Menuクローズ)
                print("M key is pressed in MENU-MODE!")
                self.gamestate.mode = C_PLAY
                self.inputdelay_cnt = self.inptdelay_C

            if not(self.invsys.subwindow_open) and (len(self.invsys.items_and_valuables) > 0):
                if pyxel.btnp(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                    self.invsys.selected_index = max(0, self.invsys.selected_index - 1)
                    pyxel.play(3,8) #SE再生(カーソル移動)
                elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                    self.invsys.selected_index = min(len(self.invsys.items_and_valuables) - 1, self.invsys.selected_index + 1)
                    pyxel.play(3,8) #SE再生(カーソル移動)

            if self.invsys.subwindow_open:
                if pyxel.btnp(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                    self.invsys.subwindow_selected_index = max(0, self.invsys.subwindow_selected_index - 1)
                    pyxel.play(3,8) #SE再生(カーソル移動)
                elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                    self.invsys.subwindow_selected_index = min(1, self.invsys.subwindow_selected_index + 1)
                    pyxel.play(3,8) #SE再生(カーソル移動)
                elif pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                    ###「使う」選択肢を選んだとき
                    ###選択中アイテムに応じたテキスト取得や効果実行
                    if self.invsys.subwindow_selected_index == 0:
                        ###選択中アイテム名を取得
                        selected_item_name = list(self.invsys.items_and_valuables.keys())[self.invsys.selected_index]
                        scene    = self.gamestate.scenario[0][0]
                        scenario = self.gamestate.scenario[0][1]
                        branch   = self.gamestate.scenario[0][2]
                        ###使用アイテムとシーン・シナリオ・隣接キャラクタ・プレイヤー状態に応じたテキストを取得する
                        if self.nearest_obj.__class__.__name__ in("Character", "Atari", "Door", "Jerry"):
                            if self.nearest_obj.flg_reaction:
                                self.get_text_on_use_item(selected_item_name, scene, scenario, branch, self.player, self.nearest_obj)
                            else:
                                self.get_text_on_use_item(selected_item_name, scene, scenario, branch, self.player)
                    self.invsys.execute_option()  # 選択肢を実行
                    self.invsys.subwindow_open = False  # サブウィンドウを閉じる
                    self.invsys.subwindow_selected_index = 0
                    print("SUBWINDOW CLOSED!")

            else:
                if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                    if (len(self.invsys.items_and_valuables) > 0):
                        self.invsys.subwindow_open = True  # サブウィンドウを開く
                        pyxel.play(3,22) #SE再生(Menuオープン)
                        print("SUBWINDOW OPENED!")

        if (self.gamestate.mode == C_DEAD):
            if pyxel.btnp(pyxel.KEY_R) and (self.inputdelay_cnt == 0):
                self.gamestate.mode = C_PLAY
                self.gamestate.scene = C_SCENE_HOME
                ###現在のscene情報を退避
                self.prescene = self.gamestate.scene
                self.deleteObjectsDependingOnScene() ##現在のシーンに応じてオブジェクトを削除しリセット
                self.gamestate.door_open_array_bf = self.gamestate.door_open_array.copy() #ドアの開閉状態を保持
                ###テキスト処理用変数をリセット
                self.inputdelay_cnt = 0 #入力受付遅延用カウンタをリセット
                self.pressed_space_checking = False #「SPACEキー打鍵によるチェック中」フラグをOFF
                # ###scroll関係変数をリセット
                self.scroll_direction = 0
                self.gamestate.scene = self.nearest_obj.room_no
                self.gamestate.scenario[0][0] = self.nearest_obj.room_no
                self.gamestate.scenetimer = 0
                ##選択中ドア(＝scene)と現在シナリオ状態から、ドア先用にシナリオ番号の初期値をセットし直す
                self.doorScenarioSet(self.nearest_obj.room_no, self.gamestate.scenario[0][1], self.gamestate.scenario[0][2])
                ###パララックス背景用変化率をSceneに応じてリセット
                self.parallax_value_set(self.gamestate.scene)
                ###パララックス背景用スクロール値をリセット
                self.scroll_positions = [0.1 for _ in range(9)]
                # ###パーティクルシステムのインスタンスをリセット
                self.psys_instances = list()
                self.generateObjects() ##現在のシーンに応じてオブジェクトを生成
                ###チェック中のオブジェクトをリセット
                self.nearest_obj = None
                self.nearest_obj_distancetoPlayer = 999
                ###チェック中のオブジェクトがいる方向、をリセット
                self.checking_obj_direction = 4
                ###パーティクルシステムのタイマーをリセット
                self.timer_for_psys = 0
                ###インプット遅延カウンタをリセット
                self.inputdelay_cnt = self.inptdelay_C

    def doorScenarioSet(self, scene, scenario, branch):
        ##選択中ドアと現在シナリオ状態でドア先でのシナリオ状態をセットし直す
        ### 【初回】 HOMEシーン -> 【初回】 MOONシーン
        if scene == C_SCENE_MOON and scenario == 0 and branch == 2:
            self.gamestate.scenario[0][1] = 1
            self.gamestate.scenario[0][2] = 0


    def get_text_on_use_item(self, item_name, scene, scenario, branch, player, obj_with=None):
        ###使用アイテム応じたテキスト・効果を取得する
        print("You selected " + item_name + "and get_text_on_use_item() is called!")
        if item_name == "おにぎり":
            self.get_text_on_use_item_onigiri(scene, scenario, branch, player, obj_with)
        elif item_name == "まんじゅう":
            self.get_text_on_use_item_manju(scene, scenario, branch, player, obj_with)
        elif item_name == "クッキー":
            self.get_text_on_use_item_cookie(scene, scenario, branch, player, obj_with)
        elif item_name == "チョコレート":
            self.get_text_on_use_item_chocolate(scene, scenario, branch, player, obj_with)
        elif item_name == "ぽんぽこペパロニピザ":
            self.get_text_on_use_item_pizza(scene, scenario, branch, player, obj_with)
        elif item_name == "甘い水の実":
            self.get_text_on_use_item_waterpear(scene, scenario, branch, player, obj_with)
        # elif item_name == "金のコイン":
        #     self.get_text_on_use_item_coin(scene, scenario, branch, player, obj_with)
        # elif item_name == "囁く葉":
        #     self.get_text_on_use_item_leaf(scene, scenario, branch, player, obj_with)
        # elif item_name == "冷たい小瓶":
        #     self.get_text_on_use_item_bottle(scene, scenario, branch, player, obj_with)
        # elif item_name == "煤けた灰":
        #     self.get_text_on_use_item_ash(scene, scenario, branch, player, obj_with)
        # elif item_name == "歌う花":
        #     self.get_text_on_use_item_flower(scene, scenario, branch, player, obj_with)
        # elif item_name == "きれいな葉":
        #     self.get_text_on_use_item_leaf2(scene, scenario, branch, player, obj_with)

    ###シーン・シナリオ・隣接キャラクタ・プレイヤー座標に応じたテキスト取得や効果を得る
    def get_text_on_use_item_onigiri(self, scene, scenario, branch, player, obj_with):
        self.recoverPlayerHp(3)
    def get_text_on_use_item_manju(self, scene, scenario, branch, player, obj_with):
        self.recoverPlayerHp(2)
    def get_text_on_use_item_cookie(self, scene, scenario, branch, player, obj_with):
        self.recoverPlayerHp(1)
    def get_text_on_use_item_chocolate(self, scene, scenario, branch, player, obj_with):
        self.recoverPlayerHp(4)
    def get_text_on_use_item_pizza(self, scene, scenario, branch, player, obj_with):
        self.recoverPlayerHp(8)
    def get_text_on_use_item_waterpear(self, scene, scenario, branch, player, obj_with):
        self.recoverPlayerHp(5)
    # def get_text_on_use_item_coin(self, scene, scenario, branch, player, obj_with):
    # def get_text_on_use_item_leaf(self, scene, scenario, branch, player, obj_with):
    # def get_text_on_use_item_bottle(self, scene, scenario, branch, player, obj_with):
    # def get_text_on_use_item_ash(self, scene, scenario, branch, player, obj_with):
    # def get_text_on_use_item_flower(self, scene, scenario, branch, player, obj_with):
    # def get_text_on_use_item_leaf2(self, scene, scenario, branch, player, obj_with):

    ###playerのHPを引数分だけ回復
    def recoverPlayerHp(self, point):
        if self.player.hp < self.player.max_hp:
            self.player.hp += point
            ###playerのHPが最大値を超えたら最大値に戻す
            if self.player.hp > self.player.max_hp:
                self.player.hp = self.player.max_hp

    ###playerのHPを引数分だけ減少
    def decreasePlayerHp(self, point):
        if self.player.hp > 0:
            self.player.hp -= point
            ###playerのHPが0以下になったら0に戻す
            if self.player.hp < 0:
                self.player.hp = 0
        ###playerのHPが0になったらゲームオーバー

    def parallax_value_set(self, scene):
        # 各レイヤーのスクロール速度を設定
        if scene == 0: ##HOME　   #空、雲、海、波の単振動沖合、島茶、島緑、波の単振動波打ち際１、波の単振動波打ち際２
            self.scroll_speeds = [0.1, 0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 1.0, 1.2]
        elif scene == 1: ##MOON　 #最奥背景、星々、月と影、雲（背景）、崖、前景１、前景２、雲（前景）
            self.scroll_speeds = [0.95, 1.05, 0.90, 1.15, 0.5, 0.55, 0.6, 0.7, 0, 0]
        elif scene == 2: ##FIRE  #最奥背景、灯籠、ガラスの橋、ガラスに反射する光、前景を落ちる火、横に吹く風パーティクル
            self.scroll_speeds = [0.1, 0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 1.0, 1.2]
        elif scene == 3: ##WATER #最奥背景、水中の影、奥雨、手前雨、前景１、前景２
            self.scroll_speeds = [0.1, 0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 1.0, 1.2]
        elif scene == 4: ##WOOD  #最奥背景、背景１、背景２、前景１、前景２
            self.scroll_speeds = [0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.3, 0.3, 0]
        elif scene == 5: ##GOLD  #最奥背景、砂山１、砂山２、前景１、前景２
            self.scroll_speeds = [0.1, 0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 1.0, 1.2]
        elif scene == 6: ##SOIL  #最奥背景、背景１、背景２、前景１、前景２
            self.scroll_speeds = [0.1, 0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 1.0, 1.2]
        elif scene == 7: ##SUN   #最奥背景、背景１、背景２、前景１、前景２
            self.scroll_speeds = [0.1, 0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 1.0, 1.2]
        elif scene == 8: ##END   #最奥背景、背景１、背景２、前景１、前景２
            self.scroll_speeds = [0.1, 0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 1.0, 1.2]

    def getAskText(self,obj_from, obj_with=None):
        ###引数オブジェクト（主にPlayer）のアクションテキストを取得し、画面表示テキスト用ワーク変数へセット
        scene    = self.gamestate.scenario[0][0]
        scenario = self.gamestate.scenario[0][1]
        branch   = self.gamestate.scenario[0][2]
        conversation_from = obj_from.character_no
        self.wk_textset = list()

        ###シーン番号・シナリオ番号・シナリオ枝番を、プレイヤのキャラクタ番号・会話相手のキャラクタ番号とともに渡し、プレイヤの会話テキストを取得する。
        ###取得したテキストは画面表示テキスト用ワーク変数へセットされる。
        if obj_with.__class__.__name__ == "Atari":
            conversation_with = obj_with.obj_no
            self.wk_textset.extend(obj_from.getActionTextAt(scene, scenario, branch, conversation_from, conversation_with))
        elif obj_with.__class__.__name__ == "Jerry":
            conversation_with = obj_with.obj_no
            self.wk_textset.extend(obj_from.getActionTextJry(scene, scenario, branch, conversation_from, conversation_with))
        else :  ###Characterのとき
            conversation_with = obj_with.character_no
            self.wk_textset.extend(obj_from.getActionText(scene, scenario, branch, conversation_from, conversation_with))

        ###対象objの会話テキスト取得中に変化したシーン番号・シナリオ番号・シナリオ枝番を再取り込みし、ゲーム本体に上書きする。
        self.gamestate.scenario[0][0] = obj_from.scene_no
        self.gamestate.scenario[0][1] = obj_from.scenario_no
        self.gamestate.scenario[0][2] = obj_from.branch_no


    def getText(self,obj):
        ###引数オブジェクト（主にNonPlayer）のリアクションテキストを取得し、画面表示テキスト用ワーク変数へセット
        scene    = self.gamestate.scenario[0][0]
        scenario = self.gamestate.scenario[0][1]
        branch   = self.gamestate.scenario[0][2]
        conversation_with = self.player.character_no
        response_no       = self.player.responce_no #playerの発話待ちフラグ
        door_open_array   = self.gamestate.door_open_array

        self.wk_textset = list()
        ###シーン番号・シナリオ番号・シナリオ枝番を、プレイヤのキャラクタ番号・発話待ちフラグとともに渡し、対象objから会話テキストを取得する。
        ###取得したテキストは画面表示テキスト用ワーク変数へセットされる。
        print("scene =" + str(scene))
        print("scenario =" + str(scenario))
        print("branch =" + str(branch))
        print("conversation_with =" + str(conversation_with))
        print("response_no =" + str(response_no))
        print("door_open_array =" + str(door_open_array))
        self.wk_textset.extend(obj.getReactionText(scene, scenario, branch, conversation_with, response_no, door_open_array))

        ###対象objの会話テキスト取得中に変化したシーン番号・シナリオ番号・シナリオ枝番を再取り込みし、ゲーム本体に上書きする。
        self.gamestate.scenario[0][0] = obj.scene_no
        self.gamestate.scenario[0][1] = obj.scenario_no
        self.gamestate.scenario[0][2] = obj.branch_no
        self.gamestate.door_open_array = obj.door_open_array

        if (obj.__class__.__name__ in ["Atari","Character","Jerry"]):
            self.panningControl(obj,self.gamestate.scenario[0][0],self.gamestate.scenario[0][1],self.gamestate.scenario[0][2])
            
    def panningControl(self,obj,scene,scenario,branch):
        ### panning_switchがONのとき、パンニング(target_x, pan_frames, wait_frames, return_frames)を実行する
        if (obj.panning_switch):
            # Home
            if scene == 0 :
                if self.gamestate.scenario[0][1] == 0 and self.gamestate.scenario[0][2] == 2 :
                    if obj.__class__.__name__ == "Atari" and obj.obj_no == 3: #猫調べたとき
                        self.camera.start_pan(self.door01.x -20, 50, 30, 50)
            # Moon
            if scene == 1 :
                if self.gamestate.scenario[0][1] >= 0 and self.gamestate.scenario[0][2] >= 0 :
                    if obj.__class__.__name__ == "Character" and obj.character_no == 0: #Kana調べたとき
                        self.camera.start_pan(180, 80, 30, 60) 
            # Fire
            if scene == 2 :
                if self.gamestate.scenario[0][1] >= 0 and self.gamestate.scenario[0][2] >= 0 :
                    if obj.__class__.__name__ == "Character" and obj.character_no == 0: #Kana調べたとき
                        self.camera.start_pan(180, 60, 20, 60) 
            # Water
            if scene == 3 :
                if self.gamestate.scenario[0][1] >= 0 and self.gamestate.scenario[0][2] >= 0 :
                    if obj.__class__.__name__ == "Character" and obj.character_no == 0: #Kana調べたとき
                        self.camera.start_pan(120, 60, 20, 60) 
            # Wood
            if scene == 4 :
                if self.gamestate.scenario[0][1] >= 0 and self.gamestate.scenario[0][2] >= 0 :
                    if obj.__class__.__name__ == "Character" and obj.character_no == 0: #Kana調べたとき
                        self.camera.start_pan(180, 60, 20, 60)
            # Gold
            if scene == 5 :
                if self.gamestate.scenario[0][1] >= 0 and self.gamestate.scenario[0][2] >= 0 :
                    if obj.__class__.__name__ == "Character" and obj.character_no == 0: #Kana調べたとき
                        self.camera.start_pan(180, 60, 20, 60) 
            # Soil
            if scene == 6 :
                if self.gamestate.scenario[0][1] >= 0 and self.gamestate.scenario[0][2] >= 0 :
                    if obj.__class__.__name__ == "Character" and obj.character_no == 0: #Kana調べたとき
                        self.camera.start_pan(180, 60, 20, 60) 
            # Sun
            if scene == 7 :
                if self.gamestate.scenario[0][1] >= 0 and self.gamestate.scenario[0][2] >= 0 :
                    if obj.__class__.__name__ == "Character" and obj.character_no == 0: #Kana調べたとき
                        self.camera.start_pan(180, 60, 20, 60) 
            # パンニングをOFFにする
            obj.panning_switch = False  


    def checkInvSysItem(self,obj):
        ### 手元の保持アイテム数をチェックし、最も近い位置にある特定番号オブジェクトの返却テキストフラグを操作する
        ###PLAYモード共通ロジック。
        # 現在のシーン、シナリオ、枝番に応じ、引数であるチェック中オブジェクト(キャラクター/アタリ)の返却テキストナンバーをもとにアイテムの保持数をチェックする。
        scene    = self.gamestate.scenario[0][0]
        scenario = self.gamestate.scenario[0][1]
        branch   = self.gamestate.scenario[0][2]
        conversation_with = self.player.character_no
        response_no = self.player.responce_no #playerの発話待ちフラグ

        ###現在のシーンやシナリオ・ブランチをCheckInvSysItem対象objに適用しておく
        obj.scene_no    = scene
        obj.scenario_no = scenario
        obj.branch_no   = branch

        ### アイテム名変数を初期化
        item_name = ''
        ### 消費アイテムを取得する特定シーンでのみチェック実施
        if (scene == C_SCENE_WATER) and (obj.obj_no == 33) :
            ### アイテム名をセット
            item_name = '甘い水の実'
        else :
            ### アイテム名が取得できない場合は、処理を終了
            return
        
        ### アイテム保持数カウントを呼び出し
        nums_of_item = self.invsys.count_item(item_name)
        
        ### 保持数範囲に応じて、最も近くにあるobjectの返却テキストフラグを切替え操作
        if (scene == C_SCENE_WATER) and (obj.obj_no == 33) :
            if nums_of_item >= 0 and nums_of_item < 3:
                obj.rtn_txt_switch = False
            if nums_of_item >= 5 :
                obj.rtn_txt_switch = True


    def checkGetItem(self,obj):
        ###PLAYモード共通ロジック。
        # 現在のシーン、シナリオ、枝番に応じ、引数であるチェック中オブジェクト(キャラクター/アタリ)の返却テキストナンバーをもとにアイテムをaddする。
        scene    = self.gamestate.scenario[0][0]
        scenario = self.gamestate.scenario[0][1]
        branch   = self.gamestate.scenario[0][2]
        conversation_with = self.player.character_no
        response_no = self.player.responce_no #playerの発話待ちフラグ

        ###現在のシーンやシナリオ・ブランチをCheckGetItem対象objに適用しておく
        obj.scene_no    = scene
        obj.scenario_no = scenario
        obj.branch_no   = branch

        ### シーン・シナリオ・ブランチ状態とオブジェクト別返却テキスト番号に応じて、invsysにアイテムをaddする。
        ### WATERシーン用
        if scene == C_SCENE_WOOD and scenario == 3 and branch == 3 :
            if (obj.__class__.__name__ == "Atari"):
                if obj.obj_no == 29:
                    if obj.rtn_txt_no == 1:
                        self.invsys.add_valuable('クラゲずかん') 
                        obj.rtn_txt_no += 1
                if obj.obj_no == 30:
                    if obj.rtn_txt_no == 1:
                        self.invsys.add_valuable('古い手鏡') 
                        obj.rtn_txt_no += 1
                if obj.obj_no == 31:
                    if obj.rtn_txt_no == 1:
                        self.invsys.add_valuable('サファイアのイヤリング') 
                        obj.rtn_txt_no += 1
                if obj.obj_no == 32:
                    if obj.rtn_txt_no == 1:
                        self.invsys.add_valuable('小さなガラス瓶') 
                        obj.rtn_txt_no += 1
                if obj.obj_no == 33:                        
                    ###（アイテム保持数チェックは予めcheckInvSysItemで実施し、対象objのフラグを切り替えておく）
                    self.checkInvSysItem(obj)
                    if obj.rtn_txt_switch == False:
                        self.invsys.add_item('甘い水の実') 
    
        ### WOODシーン用
        if scene == C_SCENE_WOOD and scenario == 4 and branch == 0 :
            if (obj.__class__.__name__ == "Atari"):
                if obj.obj_no == 5:
                    if obj.rtn_txt_no == 1:
                        self.invsys.add_valuable('きれいな葉') 
                        obj.rtn_txt_no += 1
        ### SUNシーン用
        if scene == C_SCENE_SUN and scenario == 7 and branch == 6 :
            if (obj.__class__.__name__ == "Atari"):
                if obj.obj_no == 12:
                    if obj.rtn_txt_no == 1:
                        self.invsys.add_valuable('ジェイコブへのメモ') 
                        branch += 1
                        obj.rtn_txt_no = 0

        ###チェック過程で操作したシーン・シナリオ・ブランチ状態をgamestateに戻す
        self.gamestate.scenario[0][0] = scene
        self.gamestate.scenario[0][1] = scenario
        self.gamestate.scenario[0][2] = branch

    def checkObjStatusChange(self,obj):
        ###PLAYモード共通ロジック。
        # 現在のシーン、シナリオ、枝番に応じ、引数であるチェック中オブジェクト(キャラクター/アタリ)の返却テキストナンバーをもとにSceneに存在するオブジェクト状態を操作する。
        scene    = self.gamestate.scenario[0][0]
        scenario = self.gamestate.scenario[0][1]
        branch   = self.gamestate.scenario[0][2]
        obj_pos_update_frames = self.object_pos_update_frames
        conversation_with = self.player.character_no
        response_no = self.player.responce_no #playerの発話待ちフラグ

        ###現在のシーンやシナリオ・ブランチをCheck対象objに適用しておく
        obj.scene_no    = scene
        obj.scenario_no = scenario
        obj.branch_no   = branch
        obj.object_pos_update_frames = obj_pos_update_frames

        ### シーン・シナリオ・ブランチ状態とオブジェクト別返却テキスト番号に応じて、操作対象オブジェクトを判断。
        ### WATERシーン用
        if scene == C_SCENE_WATER and scenario == 3 and branch == 3 :
            if (obj.__class__.__name__ == "Jerry"):
                self.switchAtariVisible([27,28,29,30,31,32,33], True)

        ### SUNシーン用
        if scene == C_SCENE_SUN and scenario >= C_SCENE_SUN and branch >= 5 :
            if (obj.__class__.__name__ == "Atari"):
                if obj.obj_no == 11: ##本(SUN_ROOM)
                    if obj.rtn_txt_no == 5:
                       doors[0].visible = True ##外につながるドアを出現させる
                if obj.obj_no == 12: ##本棚（SUN_ROOM）
                    if obj.rtn_txt_no == 1:
                       ##本のページをもとに戻す
                       obj.rtn_txt_no = 0

        ###チェック過程で操作したシーン・シナリオ・ブランチ状態をgamestateに戻す
        self.gamestate.scenario[0][0] = scene
        self.gamestate.scenario[0][1] = scenario
        self.gamestate.scenario[0][2] = branch
        self.object_pos_update_frames = obj_pos_update_frames

    ### 調べたオブジェクトに対応してプレイヤーの体力に影響を与える（減少）
    def checkDamage(self,obj):
        if (obj.__class__.__name__ == "Atari"):
            if obj.obj_no == 28:
                self.decreasePlayerHp(2)
    
    def checkRecovery(self,obj):
        if (obj.__class__.__name__ == "Atari"):
            if obj.obj_no in [55]:
                self.recoverPlayerHp(2)


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
                ###テキスト表示経過時間の管理変数をリセット
                self.framecount_for_text_disp = 0
                self.framecount_for_text_disp1 = 0
                self.framecount_for_text_disp2 = 0
                self.framecount_for_text_disp3 = 0
                self.framecount_for_text_disp_first = 0
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
                    if(self.talking_chara_no == 0): ###GIRL
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "カナ", 7)
                        if self.talking_chara_face_no == 0:
                            pyxel.blt(8, 238, 0,  0,  0, 16, 16, 3)
                        if self.talking_chara_face_no == 7:
                            if pyxel.frame_count//10 %2 == 0:
                                pyxel.blt(8, 238, 0,   0,  0, 16, 16, 3)
                            else:
                                pyxel.blt(8, 238, 0, 176,  0, 16, 16, 3)
                    elif(self.talking_chara_no == 1): ###WOLF
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "アキ", 7)
                        if self.talking_chara_face_no == 0:
                            pyxel.blt(8, 238, 0, 16,  0, 16, 16, 3)
                        if self.talking_chara_face_no == 7:
                            if pyxel.frame_count//10 %2 == 0:
                                pyxel.blt(8, 238, 0,  16,  0, 16, 16, 3)
                            else:
                                pyxel.blt(8, 238, 0, 128,  0, 16, 16, 3)
                    elif(self.talking_chara_no == 2): ###MICHI
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "ミチ", 7)
                            if pyxel.frame_count//10 %4 == 0:
                                pyxel.blt(8, 238, 1, 128, 192 + 16*0, 16, 16, 3)
                            elif pyxel.frame_count//10 %4 == 1:
                                pyxel.blt(8, 238, 1, 128, 192 + 16*1, 16, 16, 3)
                            elif pyxel.frame_count//10 %4 == 2:
                                pyxel.blt(8, 238, 1, 128, 192 + 16*2, 16, 16, 3)
                            else:
                                pyxel.blt(8, 238, 1, 128, 192 + 16*3, 16, 16, 3)
                    elif(self.talking_chara_no == 4): ###ジュリ
                        pyxel.blt(8, 238, 1, 88,  0, 16, 16, 3)
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "ジュリ", 7)
                    elif(self.talking_chara_no == 5): ###GIRAN
                        pyxel.blt(8, 238, 1, 160, 72, 16, 16, 0)
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "ギラン", 7)
                    elif(self.talking_chara_no == 6): ###LUV
                        pyxel.blt(8, 238, 1,200,  0, 16, 16, 3)
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "ラブ", 7)
                    elif(self.talking_chara_no == 7): ###LIKI
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "リキ", 7)
                            if pyxel.frame_count//10 %4 == 0:
                                pyxel.blt(8, 238, 1, 144, 192 + 16*0, 16, 16, 3)
                            elif pyxel.frame_count//10 %4 == 1:
                                pyxel.blt(8, 238, 1, 144, 192 + 16*1, 16, 16, 3)
                            elif pyxel.frame_count//10 %4 == 2:
                                pyxel.blt(8, 238, 1, 144, 192 + 16*2, 16, 16, 3)
                            else:
                                pyxel.blt(8, 238, 1, 144, 192 + 16*3, 16, 16, 3)
                    elif(self.talking_chara_no == 11): ###worldMaster
                        #円塗りつぶし
                        pyxel.circ(15, 247, 10, 7)
                        pyxel.blt(8, 238, 1, 152, 128, 16, 16, 3)
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "？？？", 7)
                    elif(self.talking_chara_no == 9903): ###黒猫
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "クロエ", 7)
                        if pyxel.frame_count//10 %2 == 0:
                            pyxel.blt(7, 239, 1, 112, 160, 16, 16, 6)
                        else:
                            pyxel.blt(7, 239, 1, 112, 176, 16, 16, 6)
                    elif(self.talking_chara_no == 9910): ###ボボ（FIRE）
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "ボボ", 7)
                            if pyxel.frame_count//10 %4 == 0:
                                pyxel.blt(8, 238, 1, 96, 160 + 16*0, 16, 16, 0)
                            elif pyxel.frame_count//10 %4 == 1:
                                pyxel.blt(8, 238, 1, 96, 160 + 16*1, 16, 16, 0)
                            elif pyxel.frame_count//10 %4 == 2:
                                pyxel.blt(8, 238, 1, 96, 160 + 16*2, 16, 16, 0)
                            else:
                                pyxel.blt(8, 238, 1, 96, 160 + 16*3, 16, 16, 0)
                    elif(self.talking_chara_no == 9911): ###本（SUN）
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "【ストリングブレイブ】", 7)
                        pyxel.blt(8, 238, 2, 240, 88, 16, 16, 0)
                    elif(self.talking_chara_no == 9911): ###本（SUN）
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "【ストリングブレイブ】", 7)
                        pyxel.blt(8, 238, 2, 240, 88, 16, 16, 0)
                    elif(self.talking_chara_no == 9913): ###ブルー（SUN）
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "ブルー", 7)
                        pyxel.blt(8, 238, 1, 0, 96, 16, 16, 3)
                    elif(self.talking_chara_no == 9990): ###クラゲ
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "ジュリ", 7)
                        if pyxel.frame_count//10 %2 == 0:
                            pyxel.blt(8, 239, 1, 88, 0, 16, 16, 0)
                        else:
                            pyxel.blt(8, 239, 1, 88, 0, 16, 16, 0)
                    elif(self.talking_chara_no == 9922): ###宝石（GOLD）
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "緑に輝く宝石", 7)
                        pyxel.blt(8, 238, 1, 176, 56, 16, 16, 4)
                    elif(self.talking_chara_no == 9923): ###剣（GOLD）
                        if self.name_disp:
                            self.bdf1.draw_text(33, 243, "湾曲した剣", 7)
                        pyxel.blt(8, 238, 1, 176, 32, 16, 16, 3)
                    else:
                        ###キャラクタ画像
                        pyxel.blt(8, 238, 0, 16,  0, 16, 16, 3)
                    ###台紙重ね
                    pyxel.blt(4, 249, 0, 48, 24, 24,  8, 3)

                ###テキストの表示
                ###テキストをframecountの経過に応じて左から開示できるよう、テキスト表示中経過framecountを算出
                if (self.framecount_for_text_disp == 0) and (self.framecount_for_text_disp1 == 0) and (self.framecount_for_text_disp2 == 0) and (self.framecount_for_text_disp3 == 0) and (self.framecount_for_text_disp_first == 0):
                    self.framecount_for_text_disp_first = pyxel.frame_count
                else:
                    if pyxel.frame_count % 2 == 0:
                        self.framecount_for_text_disp += 1
                        if(len(self.wk_textset3)>=1):
                            if self.framecount_for_text_disp < len(self.wk_textset3[0]):
                                self.framecount_for_text_disp1 += 1
                                self.framecount_for_text_disp2  = 0
                                self.framecount_for_text_disp3  = 0
                        if(len(self.wk_textset3)>=2):
                            if len(self.wk_textset3[0]) <= self.framecount_for_text_disp < (len(self.wk_textset3[0])+len(self.wk_textset3[1])):
                                self.framecount_for_text_disp1  = 0
                                self.framecount_for_text_disp2 += 1
                                self.framecount_for_text_disp3  = 0
                        if(len(self.wk_textset3)>=3):
                            if (len(self.wk_textset3[0])+len(self.wk_textset3[1])) <= self.framecount_for_text_disp < 84:
                                self.framecount_for_text_disp1  = 0
                                self.framecount_for_text_disp2  = 0
                                self.framecount_for_text_disp3 += 1
                        # self.framecount_for_text_disp = pyxel.frame_count - self.framecount_for_text_disp_first
                ##text_disp_times（スペース打鍵回数＋１）が表示に必要な回数を超えるまで
                if(self.wk_text_disp_times <= self.display_cnt):
                    ###３つ取得
                    self.wk_textset3 = self.wk_textset_divided[3*(self.wk_text_disp_times -1):3*(self.wk_text_disp_times)]
                if(self.wk_text_disp_times == self.display_cnt): ##最後。次のスペース打鍵で完了する
                    ###テキスト表示用フレームカウントが規定値に達している場合にテキスト表示完了とする
                    if (len(self.wk_textset3)==1 and self.framecount_for_text_disp1 >= len(self.wk_textset3[0])) -1 \
                        or (len(self.wk_textset3)==2 and self.framecount_for_text_disp2 >= len(self.wk_textset3[0]) + len(self.wk_textset3[1])) -1 \
                        or (len(self.wk_textset3)==3 and self.framecount_for_text_disp3 >= len(self.wk_textset3[0]) + len(self.wk_textset3[1]) + len(self.wk_textset3[2]) -1):
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
                    ### テキストをframecountの経過に応じて左から開示できるよう、背景色で隠す
                    width_per_word = 10
                    height_per_word = 11
                    masking_color = 13
                    ###1行目
                    if(len(self.wk_textset3)>=1):
                        if (len(self.wk_textset3[0]) > 0) and (self.framecount_for_text_disp < len(self.wk_textset3[0])):
                            lenwords_displayed   = len(self.wk_textset3[0]) - (self.framecount_for_text_disp1)
                            lenwords_undisplayed = len(self.wk_textset3[0]) - lenwords_displayed
                            pyxel.rect( 10 + lenwords_undisplayed * width_per_word, 249,
                                        lenwords_displayed * width_per_word,  height_per_word, masking_color)
                    ###2行目
                    if(len(self.wk_textset3)>=2):
                        if (len(self.wk_textset3[1]) > 0) and (self.framecount_for_text_disp < len(self.wk_textset3[0])):
                            pyxel.rect( 10, 263, 28 * width_per_word,  height_per_word, masking_color)
                        if (len(self.wk_textset3[1]) > 0) and (len(self.wk_textset3[0]) <= self.framecount_for_text_disp < (len(self.wk_textset3[0]) + len(self.wk_textset3[1]))):
                            lenwords_displayed   = len(self.wk_textset3[1]) - (self.framecount_for_text_disp2)
                            lenwords_undisplayed = len(self.wk_textset3[1]) - lenwords_displayed
                            pyxel.rect( 10 + lenwords_undisplayed * width_per_word, 263,
                                        lenwords_displayed * width_per_word,  height_per_word, masking_color)
                    ###3行目
                    if(len(self.wk_textset3)>=3):
                        if (len(self.wk_textset3[2]) > 0) and (self.framecount_for_text_disp < (len(self.wk_textset3[0])+len(self.wk_textset3[1]))):
                            pyxel.rect( 10, 277, 28 * width_per_word,  height_per_word, masking_color)
                        if (len(self.wk_textset3[2]) > 0) and ((len(self.wk_textset3[0])+len(self.wk_textset3[1])) <= self.framecount_for_text_disp < 84):
                            lenwords_displayed   = len(self.wk_textset3[2]) - (self.framecount_for_text_disp3)
                            lenwords_undisplayed = len(self.wk_textset3[2]) - lenwords_displayed
                            pyxel.rect( 10 + lenwords_undisplayed * width_per_word, 277,
                                        lenwords_displayed * width_per_word,  height_per_word, masking_color)
                else:
                    ###下に詰めて表示する
                    if(len(self.wk_textset3)>=1):
                        self.bdf1.draw_text(10, 259, self.wk_textset3[0], 7) ##MAX 28
                    if(len(self.wk_textset3)>=2):
                        self.bdf1.draw_text(10, 271, self.wk_textset3[1], 7)
                    if(len(self.wk_textset3)>=3):
                        self.bdf1.draw_text(10, 283, self.wk_textset3[2], 7)
                    ### テキストをframecountの経過に応じて左から開示できるよう、背景色で隠す
                    width_per_word = 10
                    height_per_word = 11
                    masking_color = 13
                    ###1行目
                    if(len(self.wk_textset3)>=1):
                        if (len(self.wk_textset3[0]) > 0) and (self.framecount_for_text_disp < len(self.wk_textset3[0])):
                            lenwords_displayed   = len(self.wk_textset3[0]) - (self.framecount_for_text_disp1)
                            lenwords_undisplayed = len(self.wk_textset3[0]) - lenwords_displayed
                            pyxel.rect( 10 + lenwords_undisplayed * width_per_word, 259,
                                        lenwords_displayed * width_per_word,  height_per_word, masking_color)
                    ###2行目
                    if(len(self.wk_textset3)>=2):
                        if (len(self.wk_textset3[1]) > 0) and (self.framecount_for_text_disp < len(self.wk_textset3[0])):
                            pyxel.rect( 10, 271, 28 * width_per_word,  height_per_word, masking_color)
                        if (len(self.wk_textset3[1]) > 0) and (len(self.wk_textset3[0]) <= self.framecount_for_text_disp < (len(self.wk_textset3[0]) + len(self.wk_textset3[1]))):
                            lenwords_displayed   = len(self.wk_textset3[1]) - (self.framecount_for_text_disp2)
                            lenwords_undisplayed = len(self.wk_textset3[1]) - lenwords_displayed
                            pyxel.rect( 10 + lenwords_undisplayed * width_per_word, 271,
                                        lenwords_displayed * width_per_word,  height_per_word, masking_color)
                    ###3行目
                    if(len(self.wk_textset3)>=3):
                        if (len(self.wk_textset3[2]) > 0) and (self.framecount_for_text_disp < (len(self.wk_textset3[0])+len(self.wk_textset3[1]))):
                            pyxel.rect( 10, 283, 28 * width_per_word,  height_per_word, masking_color)
                        if (len(self.wk_textset3[2]) > 0) and ((len(self.wk_textset3[0])+len(self.wk_textset3[1])) <= self.framecount_for_text_disp < 84):
                            lenwords_displayed   = len(self.wk_textset3[2]) - (self.framecount_for_text_disp3)
                            lenwords_undisplayed = len(self.wk_textset3[2]) - lenwords_displayed
                            pyxel.rect( 10 + lenwords_undisplayed * width_per_word, 283,
                                        lenwords_displayed * width_per_word,  height_per_word, masking_color)
                ###効果音
                if pyxel.frame_count % 2 == 0:
                    if(len(self.wk_textset3)==1) and \
                    (self.framecount_for_text_disp < (len(self.wk_textset3[0]))) \
                    or(len(self.wk_textset3)==2) and \
                    (self.framecount_for_text_disp < (len(self.wk_textset3[0])+len(self.wk_textset3[1]))) \
                    or(len(self.wk_textset3)==3) and \
                    (self.framecount_for_text_disp < (len(self.wk_textset3[0])+len(self.wk_textset3[1])+len(self.wk_textset3[2]))):
                        pyxel.play(3, 28)

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

    def play_music(self):
        ###PLAYモードかつHOMEシーン
        if (self.gamestate.mode == C_PLAY):
            if (self.gamestate.scene == C_SCENE_HOME):
                pyxel.playm(7, loop=True)
            if (self.gamestate.scene == C_SCENE_MOON):
                pyxel.playm(7, loop=True)
            if (self.gamestate.scene == C_SCENE_FIRE):
                pyxel.playm(6, loop=True)
            if (self.gamestate.scene == C_SCENE_WATER):
                pyxel.playm(6, loop=True)
            if (self.gamestate.scene == C_SCENE_WOOD):
                pyxel.playm(7, loop=True)
            if (self.gamestate.scene == C_SCENE_GOLD):
                pyxel.playm(2, loop=True)
            if (self.gamestate.scene == C_SCENE_SOIL):
                pyxel.playm(3, loop=True)
            if (self.gamestate.scene == C_SCENE_SUN):
                pyxel.playm(7, loop=True)

    def checkSceneMusic(self):
        if self.prescene != self.gamestate.scene:
            self.prescene = self.gamestate.scene
            pyxel.stop()
            self.play_music()


#----------------------------
MyApp()
