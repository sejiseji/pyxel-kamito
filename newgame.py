import pyxel
import math
from font.bdfrenderer import BDFRenderer

C_TITLE = "newgame"
###操作キャラクタ用固定パラメタ
C_PLAYER_WIDTH = 16 * 1
C_PLAYER_HEIGHT = 16 * 3
C_PLAYER_MOVE_SPEED = 2
###画面用設定値
C_MAX_DISPWORDS = 28 #画面幅300px＆umplus_j10rで１行２８文字
C_MSGWINDOW_WIDTH = 296 #8*37タイルマップ.
C_MSGWINDOW_HEIGHT = 64 #8*37タイルマップ.
# 移動制限のためのマージンを設定
C_TOP_MARGIN = 16 * 7  # 画面上部から移動可能領域までのマージン
C_BOTTOM_MARGIN = C_MSGWINDOW_HEIGHT + 4  # 画面下部から移動可能領域までのマージン
C_PX_AROUND_CHARA = 6 #当たり判定用のy軸不可侵エリア幅
###スクロール処理に必要な情報
#タイルマップ情報
C_WORLD_WIDTH = 600 #px
C_SCROLLON_AREA_WIDTH = 20

###選択可能キャラクタ
CHARACTERS = ["wolf","girl","boy","ledy","robot","book","rat"]

###シナリオ記録
scenario = []

# >> オブジェクト種別毎の配列
# 主要キャラクター
characters = []
# 調べられるモノ
checkables = []
# 調べられないモノ
non_checkables = []
# エフェクト
effects = []

text_display = False


#--------------------------

#--------------------------



#####--------------------------------------------------------------------
# ゲームオブジェクト
class GameObject:
	def __init__(self):
        # パラメタ初期化
		self.exists = False
		self.x = 0
		self.y = 0
		self.vx = 0
		self.vy = 0
		self.width = 0
		self.height = 0
		self.checkable = False
		self.message = ""
		self.message_created = False

	def init(self, x, y):
        # インスタンス生成時の引数に基づく初期化
        # 座標
		self.x, self.y = x, y

#####--------------------------------------------------------------------
# 操作キャラ
class Character(GameObject):
    def __init__(self,character_no,x,y,first_direction,is_playing):
        super().__init__()
        # self.x = (pyxel.width / 2)  - C_PLAYER_WIDTH/2
        # self.y = (pyxel.height / 2) - C_PLAYER_HEIGHT/2
        self.character_no = character_no
        self.x = x
        self.y = y    
        self.width = C_PLAYER_WIDTH
        self.height = C_PLAYER_HEIGHT
        self.player_direction = first_direction
        self.player_direction_RF = 1
        self.player_face = 0
        self.frame = 0  # 追加：アニメーションのためのフレーム数
        self.frame_count_wk = 0
        self.animation_frame = 0
        self.is_alive = True
        self.moving = False
        self.checkable = True
        self.env_text_displaying = False
        ###キャラクター・オブジェクトリストに追加する
        characters.append(self)

        ###操作中
        self.is_playing = is_playing

        ###表示順序の基準になる、キャラクター足元の座標
        self.position_x = self.x + C_PLAYER_WIDTH/2
        self.position_y = self.y + C_PLAYER_HEIGHT

        ###移動実行した際の方向記憶ワーク
        self.wk_moved_dir = 4 #01234:上下左右無
        self.wk_moved_speed = 0

    def update(self):
        move_speed = C_PLAYER_MOVE_SPEED
        ###移動した方向の記憶をリセット
        self.wk_moved_dir = 4 #01234:上下左右無

        ###操作中キャラクターの場合だけ、移動キー入力を受け付ける
        if self.is_playing:
            # キー入力と指定動作スピードに応じて座標を増減させる。
            self.arrow_input_check(move_speed)

            if self.moving:
                self.frame += 1  # キャラクターが移動しているときはフレーム位置をずらす。
            else:
                self.frame = 0  # キャラクターが静止しているときはフレーム数をリセットする。

            ###移動用キー打鍵時の操作可能範囲を制限する
            self.x = max(min(self.x, pyxel.width  - C_PLAYER_WIDTH), 0)
            self.y = max(min(self.y, pyxel.height - C_PLAYER_HEIGHT - C_BOTTOM_MARGIN), C_TOP_MARGIN) # TOPとBOTTOMにマージンを設けている

        ###表示順序の基準となる、足元の座標情報を更新する
        self.position_x = self.x + C_PLAYER_WIDTH/2
        self.position_y = self.y + C_PLAYER_HEIGHT


    def draw(self):
        self.frame_count_wk = pyxel.frame_count
        self.animation_frame = 4 * self.character_no + self.frame_count_wk // 6 % 4  # フレーム数を6で割り、その後4で割った余りを取ることでアニメーションフレームを0, 1, 2, 3の範囲に制限する

        ### TEST ★player_faceパラメタで表示切替　★　　　###
        self.player_face = self.frame_count_wk // 6 % 8
        ### TEST ★player_faceパラメタで表示切替　★　　　###

        #　キャラクター画像の描画
        ### キー押下による移動中かストップ中かで大きく描画パターン分け。
        ### また、胴体と頭部の画像リソースを分けているのでそれぞれをセットで描画するようにする。
        if (self.moving):
            # walking
            if (self.player_direction == 0):
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 16 * 10,  16 * 1, 16 * 3, 3) # 上移動中
            if (self.player_direction == 1):
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 16 *  7,  16 * 1, 16 * 3, 3) # 下移動中
            if (self.player_direction == 2):
                self.player_direction_RF = -1 # 左移動途中
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 16 *  4, -16 * 1, 16 * 3, 3) # 左移動中
            if (self.player_direction == 3):
                self.player_direction_RF =  1 # 右移動途中
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 16 *  4,  16 * 1, 16 * 3, 3) # 右移動中
            self.draw_head() # 頭部を描画
        else:
            # standing
            if (self.player_direction == 0):
                pyxel.blt(self.x, self.y,      0, 16 * (3 + 4 * self.character_no), 16 * 10, 16 * 1, 16 * 3, 3) # 上移動途中
                ###pyxel.blt(self.x, self.y, 0, 48, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 1):
                pyxel.blt(self.x, self.y,      0, 16 * (3 + 4 * self.character_no), 16 *  7, 16 * 1, 16 * 3, 3) # 下移動途中
                ###pyxel.blt(self.x, self.y, 0, 32, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 2):
                self.player_direction_RF = -1 # 左移動途中
                pyxel.blt(self.x, self.y + 16, 0, 16 * self.character_no, 16 *  1, self.player_direction_RF * 16, 16 * 2, 3) # 左右移動途中
            if (self.player_direction == 3):
                self.player_direction_RF =  1 # 右移動途中
                pyxel.blt(self.x, self.y + 16, 0, 16 * self.character_no, 16 *  1, self.player_direction_RF * 16, 16 * 2, 3) # 左右移動途中
            self.draw_head() # 頭部を描画
        
        self.moving = False

    def draw_head(self):
        if(self.player_direction == 0):
            if(self.animation_frame == 5)and(self.moving):
                ### 2枚目歩きモーション時は頭部を1px上に浮かせる。
                pyxel.blt(self.x, self.y - 1, 0, 16 * (2 + 4 * self.character_no), 16 * 3, 16 * 1, 16 * 1, 3)
            else:
                ### Player_direction_RFで右向き画像を左反転して対応
                pyxel.blt(self.x, self.y,     0, 16 * (2 + 4 * self.character_no), 16 * 3, 16 * 1, 16 * 1, 3)
        if(self.player_direction == 1):
            if(self.animation_frame == 5)and(self.moving):
                ### 2枚目歩きモーション時は頭部を1px上に浮かせる。
                pyxel.blt(self.x, self.y - 1, 0, 16 * (1 + 4 * self.character_no), 16 * 3, 16 * 1, 16 * 1, 3)
            else:
                ### Player_direction_RFで右向き画像を左反転して対応
                pyxel.blt(self.x, self.y,     0, 16 * (1 + 4 * self.character_no), 16 * 3, 16 * 1, 16 * 1, 3)
        # 横向きか正面かで使用する画像リソース位置が異なる
        if((self.player_direction == 2)or(self.player_direction == 3)):
            if(self.animation_frame == 5)and(self.moving):
                ### Player_direction_RFで右向き画像を左反転して対応、2枚目歩きモーション時は頭部を1px上に浮かせる。
                pyxel.blt(self.x, self.y - 1, 0, 16 * 4 * self.character_no, 16 * 3, self.player_direction_RF * 16 * 1, 16 * 1, 3) # 通常表情
            else:
                ### Player_direction_RFで右向き画像を左反転して対応
                pyxel.blt(self.x, self.y,     0, 16 * 4 * self.character_no, 16 * 3, self.player_direction_RF * 16 * 1, 16 * 1, 3) # 通常表情

    def draw_parts(self):
        # 各部位を個別に描画
        ##pyxel.blt(self.x, self.y + 36, 2, animation_frame * 16, 0 * 48, 16, 12, 3)  # 奥の腕
        pyxel.blt(self.x, self.y + 32, 0,  0, 32, 16, 16, 3)  # 下半身
        pyxel.blt(self.x, self.y + 16, 0,  0, 16, 16, 16, 3)  # 胴体
        #pyxel.blt(self.x, self.y + 16, 2, animation_frame * 16, 3 * 48, 16, 16, 3)   # 手前の腕
        pyxel.blt(self.x, self.y +  0, 0, (pyxel.frame_count // 6 % 7) * 16, 0, 16, 16, 3)  # 頭部


    def arrow_input_check(self, move_speed):
        if not(self.env_text_displaying):
            if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
                self.y -= move_speed
                self.player_direction = 0
                self.moving = True
                if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z):
                    self.y += move_speed
                    self.player_direction = 1
                    self.moving = False
            if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z):
                self.y += move_speed
                self.player_direction = 1
                self.moving = True
                if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
                    self.y -= move_speed
                    self.player_direction = 0
                    self.moving = False
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
                self.x -= move_speed
                self.player_direction = 2
                self.moving = True
                if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S):
                    self.y += move_speed
                    self.player_direction = 3
                    self.moving = False
            if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S):
                self.x += move_speed
                self.player_direction = 3
                self.moving = True
                if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
                    self.y -= move_speed
                    self.player_direction = 2
                    self.moving = False
            ###一旦計算された方向を記憶（衝突判定後にクリアできるように）
            self.wk_moved_dir = self.player_direction
            self.wk_moved_speed = move_speed

    def cancel_move(self):
        if self.wk_moved_dir == 0:
            self.y += self.wk_moved_speed
        if self.wk_moved_dir == 1:
            self.y -= self.wk_moved_speed
        if self.wk_moved_dir == 2:
            self.x += self.wk_moved_speed
        if self.wk_moved_dir == 3:
            self.x -= self.wk_moved_speed
        self.moving = False

    def is_colliding_with(self, other):
        # 衝突判定を行う範囲を定義（ここでは5px分としています）
        range_x = self.width
        range_y = C_PX_AROUND_CHARA
        # # selfとotherの中心点の距離を計算
        # dx = abs((self.position_x) - (other.position_x))
        # dy = abs((self.position_y) - (other.position_y))
        # もし距離が定義した範囲より短ければ衝突していると判定
        # return dx < range_x and dy < range_y

        if self.position_x + range_x > other.position_x:
            if self.position_x < other.position_x + range_x:
                if self.position_y + range_y > other.position_y:
                    if self.position_y < other.position_y + range_y:
                        return True
        return False

##########-----------------------------------------------------------------------

class GameState:
    def __init__(self):
        self.text_display = False
        self.scenario = [0,0,0]

##########-----------------------------------------------------------------------
class MyApp:
    def __init__(self):
        pyxel.init(300, 300, title=C_TITLE, fps=40, quit_key=pyxel.KEY_NONE, capture_scale=4, capture_sec=10)
        pyxel.load("newgame.pyxres")  
        ###ゲームステート管理インスタンス
        self.gamestate = GameState()
        ###変数宣言
        self.hensuSengen()
        # ビットマップフォントの表示。BDFRendererはpyxel.init()後に呼び出す.
        self.bdf1 = BDFRenderer("font/umplus_j10r.bdf")
        self.bdf2 = BDFRenderer("font/umplus_j12r.bdf")

        #プレイヤーオブジェクトを生成
        self.player = Character(1,0,150,3,True)

        #テスト用キャラクターオブジェクトを生成
        ##self.charactor01 = Girl(200,150)
        self.charactor01 = Character(0,200,150,2,False)
        
        ###テスト用オブジェクトを生成
        #self.generateTestObjects()
        #実行
        pyxel.run(self.update, self.draw)

    def update(self):
        ###gamestate更新
        self.gamestate.text_display = self.pressed_space_checking
        self.player.env_text_displaying = self.pressed_space_checking

        ###space打鍵によるチェックが走っていないとき（キャラ操作可能時）に左右キーでスクロールが有効化される
        if not(self.pressed_space_checking):
            # 左パララックススクロール背景のため、左右キーの入力を読み取り、その方向を更新
            if (0 < self.player.x <= (300 - self.player.width)) and (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A)):
                self.scroll_direction = -1
                if (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S)):
                    self.scroll_direction = 0
            elif (0 <= self.player.x < (300 - self.player.width)) and (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S)):
                self.scroll_direction = 1
                if (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A)):
                    self.scroll_direction = 0
            else:
                self.scroll_direction = 0

    # 有効な左右スクロール方向に応じてX方向スクロール位置を加算・減算する
        self.scroll_distance = 0
        if self.scroll_direction == 1:
            self.scroll_distance += C_PLAYER_MOVE_SPEED
        elif self.scroll_direction == -1:
            self.scroll_distance -= C_PLAYER_MOVE_SPEED
        self.scroll_x += self.scroll_distance  # self.scroll_xはスクロールの累計距離として利用する


        for obj in self.wk_objectDrawlistBasedAxisY:
            ###playingではないオブジェクトのx座標をスクロール値でずらして更新
            if not(obj.is_playing) :
                obj.x -= self.scroll_x

        # 各キャラクターを更新
        for character in characters:
            character.update()
            ###★プレイヤーのみがキー操作で動き回る前提
            if(character.is_playing):
                # 他の全てのキャラクターと衝突していないかをチェック
                for other_character in characters:
                    if character != other_character and character.is_colliding_with(other_character):
                        # 衝突したら何らかの処理を行う
                        # キャラクターの移動をキャンセルする
                        character.cancel_move()

                        for obj in self.wk_objectDrawlistBasedAxisY:
                            ###playingではないオブジェクトのx座標のスクロール加味を戻す
                            if not(obj.is_playing) :
                                obj.x += self.scroll_distance
                                # obj.x += self.scroll_x

                        ###スクロール背景用　のX軸方向オフセットの増分をキャンセル
                        if (self.scroll_direction == 1):
                            self.scroll_x -= C_PLAYER_MOVE_SPEED
                        elif (self.scroll_direction == -1):
                            self.scroll_x += C_PLAYER_MOVE_SPEED

                        # 背景のパララックススクロールの方向を０へ
                        self.scroll_direction = 0

        ### 各背景レイヤーのスクロール位置を更新
        for i in range(9):
            self.scroll_positions[i] += self.scroll_direction * self.scroll_speeds[i]

        ###プレーヤーオブジェクトとその他のcheckable（＝調べることが可能な）オブジェクト群の位置関係を確認し、
        ###最も近い位置にあるcheckableオブジェクトとの向きを含む隣接状態を捕捉する。
        self.updateObjectsPositionCheck()

        ###入力検知の遅延用カウンタ（ボタン打鍵の瞬間の連続検知を防ぐ）
        if(self.inputdelay_cnt > 0):
            self.inputdelay_cnt -= 1
        ###スクロールが働いていないときだけボタン入力を検知する
        if((self.inputdelay_cnt == 0)and(self.scroll_direction == 0)):
            ###ボタン入力の検知（スペース）
            self.updateBtnInputCheck_Space()
        ###表示が必要なテキスト情報を保持していた場合、表示に必要な分割処理を行う。
        self.updateTextDivide()

    def draw(self):
        ###背景を塗りつぶし
        pyxel.cls(11)
        ###奥行き背景用のエリアを１色で表示する
        pyxel.rect(0,   0, 300, 112, 6)
        ###メニュー＆会話用のエリアを黒く表示する
        pyxel.rect(0, 232, 300, 68, 0)

        ###各背景レイヤーを描画
        #for layer in range(5):
        for i in range(-1, 6):
                ###空
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[0] % (8 * 40),         0, 2, 0,      0, 8 * 40, 8 *  8,0)
                ###雲
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[1] % (8 * 40),        16, 2, 0, 8 *  8, 8 * 40, 8 *  8,0)
                ###海
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[2] % (8 * 40), 8 * 10 -4, 2, 0, 8 * 16, 8 * 40, 8 * 11,0)
                ###波の単振動沖合
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[3] % (8 * 40), 1.5 * math.cos(pyxel.frame_count / 30) + 8 * 11 -3, 2, 0, 8 * 17, 8 * 40, 7,0)
                ###島茶
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[4] % (8 * 40),     8 * 9, 2, 0, 8 * 34, 8 * 40, 8 * 2,0)
                ###島緑
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[5] % (8 * 40),     8 * 9, 2, 0, 8 * 32, 8 * 40, 8 * 2,0)
                ###波の単振動波打ち際１
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[6] % (8 * 40), 2.5 * math.cos(pyxel.frame_count / 28) + 8 * 13 -4, 2, 0, 8 * 19, 8 * 40, 8 * 1,0)
                ###波の単振動波打ち際２
                pyxel.bltm(i * 8 * 32 - self.scroll_positions[7] % (8 * 40), 2.5 * math.cos(pyxel.frame_count / 30) + 8 * 13   , 2, 0, 8 * 20, 8 * 40, 8 * 3,0)
        
        ###操作キャラのX軸方向移動に合わせて描画のスタート位置を変える。
        ###道路
        pyxel.bltm(0 - self.scroll_x,8 * 17,     2, 0, 8 * 40, 8 * 40 + self.scroll_x, 8 * 12,0)
        ###塀
        pyxel.bltm(0 - self.scroll_x,8 * 15 - 5, 2, 0, 8 * 36, 8 * 40 + self.scroll_x, 8 * 4,0)


        ###デモタイトルを表示
        self.bdf2.draw_text(10, 2, ">>開発中です", 7) 
        
        ###updateで並び替えたオブジェクトリストを順にdrawする
        for obj in self.wk_objectDrawlistBasedAxisY:
            ###描画後
            obj.draw()
            if not(obj.is_playing) :
                ###本来のスクロールを加味しない位置に戻す
                obj.x += self.scroll_x

        ###スペースキー打鍵chkフラグON状態のときに、捕捉中のdisptimesに分けて、メッセージを画面表示する。
        self.drawMessageAndWindow()

    ####-------------------------------------------------------------------------------
    ###プレーヤーオブジェクトとその他のcheckable（＝調べることが可能な）オブジェクト群の位置関係を確認し、
        ###最も近い位置にあるcheckableオブジェクトとの向きを含む隣接状態を捕捉する。
    def updateObjectsPositionCheck(self):
        #最終順序リストをcharactersで初期化
        self.wk_objectDrawlistBasedAxisY = characters
        #並び替え
        self.wk_objectDrawlistBasedAxisY.sort(key=lambda obj: obj.position_y)

    ####-------------------------------------------------------------------------------
    def hensuSengen(self):
        ###キー操作用変数、固定値、カウンタ
        self.pressed_space_checking = False
        self.gamestate.text_display = False
        self.inptdelay_C = 2 #キー打鍵の瞬間の連続検知を防ぐ 
        self.inputdelay_cnt = self.inptdelay_C

        # 各レイヤーのスクロール速度を設定
        self.scroll_speeds = [0.1, 0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 1.0]
        # 各レイヤーのスクロール位置を初期化
        self.scroll_positions = [0.1 for _ in range(9)]
        # スクロール制御用のキー入力方向捕捉変数
        self.scroll_direction = 0

        ###遠景背景ではない描画背景およびオブジェクト群のスクロール位置調整用変数
        self.scroll_x = 0

        ###オブジェクトリストのDraw順序組み換え用に使うワークリスト
        self.wk_objectDrawlistBasedAxisY = []

        ###取得するテキストセットを扱うための変数
        self.wk_textset = []
        ###テスト用に用意したテキスト------------------------------------★
        self.hensuTestSengen()
        ###テスト用に用意したテキスト------------------------------------★

        # text分割処理にかかる変数
        self.text_divided = False # テキスト分割処置の完了済のフラグ
        self.wk_textset_divided = [] # 初期化。textDivideにて整形。
        self.wk_text_divided_remain = 0
        self.display_cnt = 0
        self.display_finished = False
        self.wk_text_disp_times = 1 ##分割編集済みのテキストを表示した回数の●回目初期値
        self.wk_textset3 = []
    def hensuTestSengen(self):
        self.wk_text00 = "ワンワン！"
        self.wk_text01 = "スペースを押したので、文字を表示させます。これは用意した文字列です。"
        self.wk_text02 = "例えばこういう３行に納まらないような文字数のテキストを表示させたいと思って長々とセリフや状況描写を入力した場合は、追加でスペースを打鍵することですべてを表示させられます。"
        self.wk_text03 = "返事がない。"
        #テキストセットに突っ込む
        self.wk_textset.append(self.wk_text00)
        self.wk_textset.append(self.wk_text03)
    #def generateTestObjects():
        ###テスト用にオブジェクトを用意する。


    ####-------------------------------------------------------------------------------
    #def updateObjectsPositionCheck(self):
        ###プレーヤーオブジェクトとその他のcheckable（＝調べることが可能な）オブジェクト群の位置関係を確認し、
        ###最も近い位置にあるcheckableオブジェクトとの向きを含む隣接状態を捕捉する。
        

    def updateBtnInputCheck_Space(self):
        ###ボタン入力検知（スペースキー、ゲームパッドAキー）
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            ##スペース打鍵によるチェックフラグが有効中でない
            if (self.pressed_space_checking == False):

                self.pressed_space_checking = True
                self.display_finished = False
                self.inputdelay_cnt = self.inptdelay_C
            ##スペース打鍵によるチェックフラグが有効中
            else:
                if(self.display_finished): ##分割テキストを表示完了
                    self.pressed_space_checking = False
                    self.inputdelay_cnt = self.inptdelay_C
                    self.wk_textset_divided = [] #表示用テキストをリセット。
                    self.text_divided = False #分割済みフラグのクリア
                else: ##分割テキストを表示未完了
                    self.wk_text_disp_times += 1
    def updateTextDivide(self):
        ###テキストの分割処理
        if self.pressed_space_checking and not(self.text_divided): #分割処理はdisplay完了後のスペースキー打鍵でフラグクリアされる
            ###テキストの分割チェック（結果セットに連続appendする）
            self.textDivide(self.wk_textset)
            ###３行に分けて分割表示する際のTOTAL回数を捕捉
            self.wk_text_divided_remain = len(self.wk_textset_divided)
            self.display_cnt = self.wk_text_divided_remain // 3
            if not(self.wk_text_divided_remain % 3 == 0):
                self.display_cnt += 1
            self.wk_text_disp_times = 1
            self.text_divided = True
    ####-------------------------------------------------------------------------------
    def drawMessageAndWindow(self):
    ###スペースキー打鍵chkフラグON状態のときに捕捉中のdisptimesに分けてメッセージを画面表示する。
        if self.pressed_space_checking :
            ##メッセージウィンドウの表示
            pyxel.bltm(2, 234, 0, 0, 0, C_MSGWINDOW_WIDTH, C_MSGWINDOW_HEIGHT, 3)
            ##text_disp_times（スペース打鍵回数＋１）が表示に必要な回数を超えるまで
            if(self.wk_text_disp_times <= self.display_cnt):
                ###３つ取得
                self.wk_textset3 = self.wk_textset_divided[3*(self.wk_text_disp_times -1):3*(self.wk_text_disp_times)]
            if(self.wk_text_disp_times == self.display_cnt): ##最後。次のスペース打鍵で完了する
                self.display_finished = True
            ##画面下部へテキストを表示する
            if(len(self.wk_textset3)>=1):
                self.bdf1.draw_text(10, 250, self.wk_textset3[0], 7) ##MAX 28
            if(len(self.wk_textset3)>=2):
                self.bdf1.draw_text(10, 265, self.wk_textset3[1], 7)
            if(len(self.wk_textset3)>=3):
                self.bdf1.draw_text(10, 280, self.wk_textset3[2], 7)
    def textDivide(self, textset):
    ###与えられたテキストセットを先頭から順に１行の最大表示可能文字数で分割し、新たなテキストセットを生成する。
        wk_setlen = len(textset)
        if(wk_setlen > 0):
            for words in textset:
                wk_wordslen = len(words)
                wk_words = words
                while (len(wk_words) > C_MAX_DISPWORDS):
                    self.wk_textset_divided.append(wk_words[:C_MAX_DISPWORDS])
                    wk_words = wk_words[C_MAX_DISPWORDS:]
                self.wk_textset_divided.append(wk_words)
    ####-------------------------------------------------------------------------------

#----------------------------
MyApp()
