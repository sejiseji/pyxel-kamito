import pyxel
import random as rnd
import math
from GameObject import GameObject

###画面用設定値
C_MAX_DISPWORDS = 28 #画面幅300px＆umplus_j10rで１行２８文字
C_MSGWINDOW_WIDTH = 296 #8*37タイルマップ.
C_MSGWINDOW_HEIGHT = 64 #8*37タイルマップ.

###操作キャラクタ用固定パラメタ
C_PLAYER_WIDTH = 16 * 1
C_PLAYER_HEIGHT = 16 * 3
C_PLAYER_MOVE_SPEED = 2.5

###選択可能キャラクタ
CHARACTERS = ["GIRL","WOLF","MICHI","BOBO","JELATO","GIRAN","LUV","LIKI","SIROI","TALISMAN"]
C_CHARA_GIRL     = 0
C_CHARA_WOLF     = 1
C_CHARA_MICHI    = 2
C_CHARA_BOBO     = 3
C_CHARA_JELATO   = 4
C_CHARA_GIRAN    = 5
C_CHARA_LUV      = 6
C_CHARA_LIKI     = 7
C_CHARA_SIROI    = 8
C_CHARA_TALISMAN = 9
C_CHARA_CHIBIMK  = 10
C_CHARA_WORLDMASTER = 11

# 移動制限のためのマージンを設定
C_TOP_MARGIN = 16 * 7 - 8# 画面上部から移動可能領域までのマージン
C_BOTTOM_MARGIN = C_MSGWINDOW_HEIGHT + 4  # 画面下部から移動可能領域までのマージン
C_PX_AROUND_CHARA = 6 #当たり判定用のy軸不可侵エリア幅

C_MAX_MOVEABLE_X = 600
C_MIN_MOVEABLE_Y = 100
C_MAX_MOVEABLE_Y = 230


#####--------------------------------------------------------------------
# 操作キャラ
class Character(GameObject):
    def __init__(self,character_no,x,y,first_direction,is_playing):
        super().__init__()
        self.character_no = character_no
        self.x = x
        self.y = y    
        self.width = C_PLAYER_WIDTH
        self.height = C_PLAYER_HEIGHT
        self.collision_width = C_PLAYER_WIDTH
        self.collision_height = C_PLAYER_HEIGHT
        ###表示順序の基準になる、Door足元の座標
        self.position_x = self.x + self.width/2
        self.position_y = self.y + self.height
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
        self.flg_reaction = False
        self.able_moving_top = C_MIN_MOVEABLE_Y
        self.hp = 8
        self.max_hp = 10
        self.mp = 5
        self.max_mp = 5
        ###描画用座標
        self.draw_x = 0
        self.draw_y = 0
        ###パンニング起動スイッチ
        self.panning_switch = False
        ###エモート管理用パラメタ
        self.emote_switch = False
        self.emote_frames = [0,0,0,0,0,0,0,0,0,0] # 喜,怒,哀,楽,驚,疑,愛,怖,喋,未使用,未使用
        self.emote_initial_frame = 0
        ###操作中
        self.is_playing = is_playing

        ### 自動移動スイッチ
        self.auto_move_R_switch = False
        self.auto_move_switch = False
        ### 移動先座標
        self.move_to_x = 0
        self.move_to_y = 0
        ### 移動元座標
        self.move_from_x = 0
        self.move_from_y = 0
        ### 移動速度
        self.move_speed = 0
        self.move_frame_count = 0
        self.initial_frame_count = 0
        self.step_x = 0
        self.step_y = 0
        self.is_auto_moving = False
        self.object_pos_update_frames = 0

        # ###表示順序の基準になる、キャラクター足元の座標
        # self.position_x = self.x + C_PLAYER_WIDTH/2
        # self.position_y = self.y + C_PLAYER_HEIGHT

        ###移動実行した際の方向記憶ワーク
        self.wk_moved_dir = 4 #01234:上下左右無
        self.wk_moved_speed = 0

        ###会話とシナリオに付随したテキスト返却のための管理パラメタ
        self.scene_no = 0
        self.scenario_no = 0
        self.branch_no = 0
        self.conversation_from = 0
        self.conversation_with = 0
        self.name_disp = True
        self.face_no = 7 ### 0:通常 1:喜 2:怒 3:哀 4:楽 5:驚 6:怖 7:喋

        # 軌跡描画用の座標記録配列
        self.trajectory_point = [[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y]]
        self.trajectory_point.pop(0)
        self.trajectory_point.append([self.x, self.y])

    def update(self):
        ### Movetoが設定されている場合は自動移動を実行
        if self.auto_move_switch:
            self.updateMoveTo()

        if self.character_no in(0,2,3,4,5,6,7,8,9,11):
            if self.auto_move_switch == False:                
                ### 60frameに１度ランダムにdirectionを変える
                if self.character_no in(0,2,3,4,6,7,8,9,11):
                    if pyxel.frame_count % 60 == 0:
                        self.player_direction = rnd.randint(0,3)
                if self.character_no == 5:
                    if self.player_direction == 4: # ポーズ1はポーズ2へ
                        if pyxel.frame_count % 20 == 0:
                            self.player_direction = 5
                    else: 
                        if pyxel.frame_count % 60 == 0:
                            self.player_direction = rnd.randint(0,4)
        else:
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

                # ###移動用キー打鍵時の操作可能範囲を制限する
                self.x = max(min(self.x, C_MAX_MOVEABLE_X - C_PLAYER_WIDTH), 0)
                self.y = max(min(self.y, C_MAX_MOVEABLE_Y - C_PLAYER_HEIGHT), self.able_moving_top)

            ###表示順序の基準となる、足元の座標情報を更新する
            self.position_x = self.x + C_PLAYER_WIDTH/2
            self.position_y = self.y + C_PLAYER_HEIGHT

            ###足元の座標を最大5件まで常に記録する
            if (len(self.trajectory_point) == 20):
                self.trajectory_point.pop(0)
            self.trajectory_point.append([self.position_x, self.position_y])

        ### エモートスイッチがONの場合はエモート管理値を更新
        if self.emote_switch:
            self.updateEmote()

    def draw(self):
        if self.character_no in(2,3,4,5,6,7,8,9,11):
            if self.character_no == C_CHARA_MICHI: #2 ミチ in moon-door
                if self.player_direction == 0:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 3, 128,  16 * 1, 16 * 2.5, 3) # 上向き
                if self.player_direction == 1:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 1, 128,  16 * 1, 16 * 2.5, 3) # 下向き
                if self.player_direction == 2:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 2, 128, -16 * 1, 16 * 2.5, 3) # 左向き
                if self.player_direction == 3:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 2, 128,  16 * 1, 16 * 2.5, 3) # 右向き
            if self.character_no == C_CHARA_GIRAN: #5 ギラン in wood-door
                if self.player_direction == 0:
                    pyxel.blt(self.draw_x, self.draw_y + 24, 1, 160 + 16*2, 72,  16 * 1, 16 * 1.5, 0) # 上向き
                if self.player_direction == 1:
                    pyxel.blt(self.draw_x, self.draw_y + 24, 1, 160 + 16*0, 72,  16 * 1, 16 * 1.5, 0) # 下向き
                if self.player_direction == 2:
                    pyxel.blt(self.draw_x, self.draw_y + 24, 1, 160 + 16*1, 72,  16 * 1, 16 * 1.5, 0) # 左向き
                if self.player_direction == 3:
                    pyxel.blt(self.draw_x, self.draw_y + 24, 1, 160 + 16*1, 72, -16 * 1, 16 * 1.5, 0) # 右向き
                if self.player_direction == 4:
                    pyxel.blt(self.draw_x, self.draw_y + 24, 1, 160 + 16*0, 72+24,  16 * 1, 16 * 1.5, 0) # ポーズ1
                if self.player_direction == 5:
                    pyxel.blt(self.draw_x, self.draw_y + 24, 1, 160 + 16*1, 72+24,  16 * 1, 16 * 1.5, 0) # ポーズ2
            if self.character_no == C_CHARA_LUV: #6 ラブ in gold-door
                pyxel.blt(self.draw_x, self.draw_y +16, 1, 192,  16, 16 * 2, 16 * 2, 3) # 胴体
                if self.player_direction == 0:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 192,   0, 16 * 2, 16 * 1, 3) # 上向きは存在しない為下向き表示
                if self.player_direction == 1:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 192,   0, 16 * 2, 16 * 1, 3) # 下向き
                if self.player_direction == 2:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 192,  48, 16 * 2, 16 * 1, 3) # 左向き
                if self.player_direction == 3:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 224,  48, 16 * 2, 16 * 1, 3) # 右向き
            if self.character_no == C_CHARA_LIKI: #7 リキ in soil-door
                if self.player_direction == 0:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 3, 168,  16 * 1, 16 * 3, 3) # 上向き
                if self.player_direction == 1:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 1, 168,  16 * 1, 16 * 3, 3) # 下向き
                if self.player_direction == 2:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 2, 168, -16 * 1, 16 * 3, 3) # 左向き
                if self.player_direction == 3:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 2, 168,  16 * 1, 16 * 3, 3) # 右向き
            if self.character_no == C_CHARA_WORLDMASTER: #11 ワールドマスター in world-door
                if self.player_direction == 0:
                    pyxel.blt(self.draw_x - 10, self.draw_y + 18, 1, 144 + 32*2, 120,  16 * 2, 16 * 2, 3) # 上向き
                if self.player_direction == 1:
                    pyxel.blt(self.draw_x - 10, self.draw_y + 18, 1, 144, 120,  16 * 2, 16 * 2, 3) # 下向き
                if self.player_direction == 2:
                    pyxel.blt(self.draw_x - 10, self.draw_y + 18, 1, 144 + 32*1, 120,  16 * 2, 16 * 2, 3) # 左向き
                if self.player_direction == 3:
                    pyxel.blt(self.draw_x - 10, self.draw_y + 18, 1, 144 + 32*1, 120,  16 *-2, 16 * 2, 3) # 右向き
        else:
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
                    pyxel.blt(self.draw_x, self.draw_y, 0, self.animation_frame * 16, 16 * 10,  16 * 1, 16 * 3, 3) # 上移動中
                if (self.player_direction == 1):
                    pyxel.blt(self.draw_x, self.draw_y, 0, self.animation_frame * 16, 16 *  7,  16 * 1, 16 * 3, 3) # 下移動中
                if (self.player_direction == 2):
                    self.player_direction_RF = -1 # 左移動途中
                    pyxel.blt(self.draw_x, self.draw_y, 0, self.animation_frame * 16, 16 *  4, -16 * 1, 16 * 3, 3) # 左移動中
                if (self.player_direction == 3):
                    self.player_direction_RF =  1 # 右移動途中
                    pyxel.blt(self.draw_x, self.draw_y, 0, self.animation_frame * 16, 16 *  4,  16 * 1, 16 * 3, 3) # 右移動中
                self.draw_head() # 頭部を描画
            else:
                # standing
                if (self.player_direction == 0):
                    pyxel.blt(self.draw_x, self.draw_y,      0, 16 * (3 + 4 * self.character_no), 16 * 10, 16 * 1, 16 * 3, 3) # 上移動途中
                    ###pyxel.blt(self.x, self.y, 0, 48, 32, 16, 16, 3) # 頭部
                if (self.player_direction == 1):
                    pyxel.blt(self.draw_x, self.draw_y,      0, 16 * (3 + 4 * self.character_no), 16 *  7, 16 * 1, 16 * 3, 3) # 下移動途中
                    ###pyxel.blt(self.x, self.y, 0, 32, 32, 16, 16, 3) # 頭部
                if (self.player_direction == 2):
                    self.player_direction_RF = -1 # 左移動途中
                    pyxel.blt(self.draw_x, self.draw_y + 16, 0, 16 * self.character_no, 16 *  1, self.player_direction_RF * 16, 16 * 2, 3) # 左右移動途中
                if (self.player_direction == 3):
                    self.player_direction_RF =  1 # 右移動途中
                    pyxel.blt(self.draw_x, self.draw_y + 16, 0, 16 * self.character_no, 16 *  1, self.player_direction_RF * 16, 16 * 2, 3) # 左右移動途中
                self.draw_head() # 頭部を描画
            
            self.moving = False
        ### エモートスイッチがONの場合はエモートを描画        
        if self.emote_switch:
            self.drawEmote()

    def draw_head(self):
        if(self.player_direction == 0):
            if(self.animation_frame == 5)and(self.moving):
                ### 2枚目歩きモーション時は頭部を1px上に浮かせる。
                pyxel.blt(self.draw_x, self.draw_y - 1, 0, 16 * (2 + 4 * self.character_no), 16 * 3, 16 * 1, 16 * 1, 3)
            else:
                ### Player_direction_RFで右向き画像を左反転して対応
                pyxel.blt(self.draw_x, self.draw_y,     0, 16 * (2 + 4 * self.character_no), 16 * 3, 16 * 1, 16 * 1, 3)
        if(self.player_direction == 1):
            if(self.animation_frame == 5)and(self.moving):
                ### 2枚目歩きモーション時は頭部を1px上に浮かせる。
                pyxel.blt(self.draw_x, self.draw_y - 1, 0, 16 * (1 + 4 * self.character_no), 16 * 3, 16 * 1, 16 * 1, 3)
            else:
                ### Player_direction_RFで右向き画像を左反転して対応
                pyxel.blt(self.draw_x, self.draw_y,     0, 16 * (1 + 4 * self.character_no), 16 * 3, 16 * 1, 16 * 1, 3)
        # 横向きか正面かで使用する画像リソース位置が異なる
        if((self.player_direction == 2)or(self.player_direction == 3)):
            if(self.animation_frame == 5)and(self.moving):
                ### Player_direction_RFで右向き画像を左反転して対応、2枚目歩きモーション時は頭部を1px上に浮かせる。
                pyxel.blt(self.draw_x, self.draw_y - 1, 0, 16 * 4 * self.character_no, 16 * 3, self.player_direction_RF * 16 * 1, 16 * 1, 3) # 通常表情
            else:
                ### Player_direction_RFで右向き画像を左反転して対応
                pyxel.blt(self.draw_x, self.draw_y,     0, 16 * 4 * self.character_no, 16 * 3, self.player_direction_RF * 16 * 1, 16 * 1, 3) # 通常表情

    def draw_parts(self):
        # 各部位を個別に描画
        ##pyxel.blt(self.x, self.y + 36, 2, animation_frame * 16, 0 * 48, 16, 12, 3)  # 奥の腕
        pyxel.blt(self.draw_x, self.draw_y + 32, 0,  0, 32, 16, 16, 3)  # 下半身
        pyxel.blt(self.draw_x, self.draw_y + 16, 0,  0, 16, 16, 16, 3)  # 胴体
        #pyxel.blt(self.x, self.y + 16, 2, animation_frame * 16, 3 * 48, 16, 16, 3)   # 手前の腕
        pyxel.blt(self.draw_x, self.draw_y +  0, 0, (pyxel.frame_count // 6 % 7) * 16, 0, 16, 16, 3)  # 頭部


    def arrow_input_check(self, move_speed):
        if not(self.env_text_displaying):
            if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                ### 他のキーはその方向を向いて立ち止まる
                if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                    self.player_direction = 1
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                    self.player_direction = 2
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                    self.player_direction = 3
                    self.moving = False
                else:
                    self.y -= move_speed
                    self.player_direction = 0
                    self.moving = True
            if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                    self.player_direction = 0
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                    self.player_direction = 2
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                    self.player_direction = 3
                    self.moving = False
                else:
                    self.y += move_speed
                    self.player_direction = 1
                    self.moving = True
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                    self.player_direction = 3
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                    self.player_direction = 0
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                    self.player_direction = 1
                    self.moving = False
                else:
                    self.x -= move_speed
                    self.player_direction = 2
                    self.moving = True
            if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                    self.player_direction = 2
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                    self.player_direction = 0
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                    self.player_direction = 1
                    self.moving = False
                else:
                    self.x += move_speed
                    self.player_direction = 3
                    self.moving = True

 
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

    # def is_colliding_with(self, other):
    #     # 衝突判定を行う範囲を定義（ここでは5px分としています）
    #     range_x = self.width
    #     range_y = C_PX_AROUND_CHARA

    #     # 衝突判定
    #     if self.position_x + range_x > other.position_x:
    #         if self.position_x < other.position_x + range_x:
    #             if self.position_y + range_y > other.position_y:
    #                 if self.position_y < other.position_y + range_y:
    #                     return True
    #     return False

    def is_colliding_with(self, other):
        range_x_self = 16
        range_y_self = 6
        range_x_other = 16
        range_y_other = 6

        if other.__class__.__name__ != "Atari":    
            if self.position_x + range_x_self > other.position_x and \
            self.position_x < other.position_x + range_x_other:
                if self.position_y + range_y_self > other.position_y and \
                self.position_y < other.position_y + range_y_other:
                    return True

        if other.__class__.__name__ == "Atari" and other.is_visible == True:    
            if self.position_x + range_x_self > other.position_x and \
            self.position_x < other.position_x + range_x_other:
                if self.position_y + range_y_self > other.position_y and \
                self.position_y < other.position_y + range_y_other:
                    return True

        return False

    def setFlgWaitingResponce(self):
        self.flg_waiting_responce = True

    def cancelFlgWaitingResponce(self):
        self.flg_waiting_responce = False

    def getActionText(self, scene_no, scenario_no, branch_no, conversation_from, conversation_with):
        ###当該シーン・シナリオ配下でcharacter_noをプレイヤーキャラクタとして操作している場合の発話。
        #----------------------------------------------------------- 
        ###シーン番号、シナリオ番号、返却テキスト番号（進行に合わせて返却のたびにカウントアップ、ただし質問中はそのまま）、質問中フラグ、返答結果番号
        self.scene_no    = scene_no ### シーン番号
        self.scenario_no = scenario_no ### シナリオ番号
        self.branch_no   = branch_no ### シナリオ分岐番号
        self.character_no = conversation_from
        self.conversation_with = conversation_with ### 誰と会話中か
        #----------------------------------------------------------- 

        ###self.rtn_txt_no = 0 ### 返却テキスト番号
        ###self.flg_waiting_responce = False ### 相手からの返答待ち（＝質問中）フラグ

        ### ◆シーン１　ー　シナリオ１
        ### プレイヤー : WOLF →　キャラ　：　GIRLのときの【前者】の発話。
        if((self.character_no == C_CHARA_WOLF) and (self.conversation_with == C_CHARA_GIRL)):
            ### ◆シーン１（HOME）
            if (self.scene_no == 0):
                if (self.scenario_no == 0) and (self.branch_no == 0):
                    if(self.rtn_txt_no == 0): ### 1回目返事
                        self.rtn_txt_no += 1
                        self.face_no = 7
                        self.name_disp = True
                        self.cancelFlgWaitingResponce() 
                        return ["あ・・・えと。俺は、・・・アキ・・・。","だと思う・・・","たぶん・・・。",
                                "ええっとさっきまで確か神社で・・・","","",
                                "ひとりで参拝して・・・。","","",
                                "手を打って、","後ろで声がして、","ふりかえって・・・・・・。",
                                "そして今・・・だ。","ここ・・・どこだ・・・？"]
                    if(self.rtn_txt_no == 1): ### 2回目返事
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce() 
                        self.setEmote(5,50)
                        return ["は？","なんだそりゃ・・・","",
                                "切り取られた世界？","ただの海沿いの道じゃねえか。","道の先、ずっと続いてるぞ。",
                                "つか、どこだここ。俺のいた街じゃねえ。","日本、だよな？","ならバス停もあるし、戻れるってことだ。俺は帰るぞ。"]
                    if(self.rtn_txt_no == 2): ### 3回目返事
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce() 
                        return ["風もあるしギラギラ日差しもある。外だ。","なのに、閉じ込められてる？","嘘だろ・・・",
                                "ん、ちょっとまて。","あんたは？　カナっていったな、あんた誰だ？","ここのこと知ってるのか？"]
                    if(self.rtn_txt_no == 3): ### 4回目返事
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce() 
                        return ["そんだけって・・・","","",
                                "進めなくなるって言ってたな。","見えないだけでどっか隙間とかないのか？","自分でも何言ってるのかわかんねえけど・・・"]
                    if(self.rtn_txt_no == 4): ### 5回目返事
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce() 
                        return ["そーだな・・・。一度よく調べてみるか。"]
                    if(self.rtn_txt_no == 5): ### 6回目返事
                        self.rtn_txt_no = 0
                        self.branch_no += 1
                        self.cancelFlgWaitingResponce() 
                        return ["ふすまの音・・・。","外で？","ますますわかんねーな・・・。"]
            ### ◆シーン３（水）
            if(self.scene_no == 3):
                if(self.scenario_no == 3) and (self.branch_no == 2):
                    if(self.rtn_txt_no == 0):
                        self.rtn_txt_no = 0
                        self.cancelFlgWaitingResponce()
                        return ["俺たちのこと　幻覚だって言ってたもんな。","普段とは違う　みたいな・・・。","幻覚と思いつつも、　警戒してるのかな。",
                                "何か探してる風だけど、　見つけてあげれば","信頼を　得られるんじゃないか。","実在するって　わかってもらえるだろ。"]

    def getActionTextAt(self, scene_no, scenario_no, branch_no, conversation_from, conversation_with):
        #----------------------------------------------------------- 
        self.scene_no    = scene_no ### シーン番号
        self.scenario_no = scenario_no ### シナリオ番号
        self.branch_no   = branch_no ### シナリオ分岐番号
        self.character_no = conversation_from
        self.conversation_with = conversation_with ### 誰と会話中か
        #----------------------------------------------------------- 
        if((self.character_no == C_CHARA_WOLF) and (self.conversation_with == 3)): ### AtariのNo.3:猫
            if((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 1)):            
                if(self.rtn_txt_no == 0): ### 1回目返事
                    self.cancelFlgWaitingResponce() 
                    return ["あの子が　ふすまが閉まる音を聞いた　っていうんだが・・・","わかるか？",""]
            if((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 2)):   
                if(self.rtn_txt_no == 0): ### 2回目返事
                    self.cancelFlgWaitingResponce() 
                    return ["どうしてそんなに　協力的なんだ？","",""]
            if((self.scene_no == 0) and (self.scenario_no == 7) and (self.branch_no == 3)):            
                if(self.rtn_txt_no == 0): ### 1回目返事
                    self.cancelFlgWaitingResponce() 
                    return ["ああ。カナは　ブルーの妹だったみたいだ。","７つ目の部屋の中で　思い出してたよ。","",
                            "あの部屋は　カナに惹かれて　現れたみたいだな。","でも、　時間に差が無いか？","",
                            "カナの兄は随分昔、　唐突に","犬への興味を　失ったらしい。","それは１０年近くも　前だ。"]

    def getActionTextJry(self, scene_no, scenario_no, branch_no, conversation_from, conversation_with):
        #----------------------------------------------------------- 
        self.scene_no    = scene_no ### シーン番号
        self.scenario_no = scenario_no ### シナリオ番号
        self.branch_no   = branch_no ### シナリオ分岐番号
        self.character_no = conversation_from
        self.conversation_with = conversation_with ### 誰と会話中か
        #----------------------------------------------------------- 
        print("conversation_with =" + str(self.conversation_with))
        if((self.character_no == C_CHARA_WOLF) and (self.conversation_with == 90)): ### JerryのNo.90
            if((self.scene_no == 3) and (self.scenario_no == 3) and (self.branch_no == 0)):            
                if(self.rtn_txt_no == 0): ### 1回目返事
                    self.cancelFlgWaitingResponce() 
                    return ["俺たちは・・・　怪しいもんじゃない。","","",
                            "俺たち、この変な世界に　迷い込んだんだ。","あんたも同じだろ？","俺はアキ。彼女はカナっていうんだ。"]
            if((self.scene_no == 3) and (self.scenario_no == 3) and (self.branch_no == 1)):   
                if(self.rtn_txt_no == 0): ### 2回目返事
                    self.cancelFlgWaitingResponce() 
                    return ["気を悪くしたんなら　済まない。","俺たちはただ、　扉を探してるんだ。","この、　わけのわからん場所から出たい。",
                            "この部屋には　扉があるはずなんだ。","それを　一緒に探してほしい。","ここに　ほかの空間につながる　扉はないか？"]
            if((self.scene_no == 3) and (self.scenario_no == 3) and (self.branch_no == 2)):
                if(self.rtn_txt_no == 0):
                    self.cancelFlgWaitingResponce() 
                    return ["探しもの　してるのか？","・・・","俺も手伝うよ。"]

    def getReactionText(self, scene_no, scenario_no, branch_no, conversation_with, response_no, door_open_array):
        ###当該シーン・シナリオ配下でcharacter_noがプレイヤーconversation_withに話しかけられた場合の発話
        #----------------------------------------------------------- 
        ###シーン番号、シナリオ番号、返却テキスト番号（進行に合わせて返却のたびにカウントアップ、ただし質問中はそのまま）、質問中フラグ、返答結果番号
        self.scene_no    = scene_no ### シーン番号
        self.scenario_no = scenario_no ### シナリオ番号
        self.branch_no   = branch_no ### シナリオ分岐番号
        self.conversation_with = conversation_with ### 誰と会話中か
        # self.conversation_with = C_CHARA_WOLF ### 誰と会話中か
        #----------------------------------------------------------- 

        ###self.rtn_txt_no = 0 ### 返却テキスト番号
        ###self.flg_waiting_responce = False ### 相手からの返答待ち（＝質問中）フラグ
        self.responce_no = response_no ### 返答結果番号
        self.door_open_array = door_open_array ### ドア開閉状況

        ### プレイヤー : WOLF →　キャラ　：　GIRLのときの【後者】の発話
        if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == C_CHARA_GIRL)):
            ### ◆シーン１　ー　シナリオ１
            if(self.scene_no == 0):
                if (self.scenario_no == 0) and (self.branch_no == 0):
                    if(self.rtn_txt_no == 0):
                        self.face_no = 7
                        self.name_disp = True
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce()
                        return ["あ。　おはよ。","","",
                                "あたしは　カナ。","ええっと　まず・・・、　自分のこと　わかる？"]
                    if(self.rtn_txt_no == 1):
                        self.rtn_txt_no += 1
                        self.setFlgWaitingResponce() ### 1回目返事待機
                        return ["それじゃさ、　目覚める　前のこと、　覚えてる？"]
                    if(self.rtn_txt_no == 2):
                        self.rtn_txt_no += 1
                        self.setFlgWaitingResponce() ### 2回目返事待機
                        return ["うんうん。　だいじょうぶそうだね。","えっと・・・・・・　","まず、結論から。",
                                "ここ、　なんか変。","途中で　止まっちゃうの。","なんだか・・・　切り取られたみたい。"]
                    if(self.rtn_txt_no == 3):
                        self.rtn_txt_no += 1
                        self.setFlgWaitingResponce() ### 3回目返事待機
                        return ["歩けば　わかると思うけど、　途中で進めなくなるよ。","空気の　壁みたいなのが　あってさ。","閉じ込められてるんだよ。",
                                "切り取られてる　ってのは　そういうことね。","道沿いには　進めないみたい。　浜辺も　出れない。","防波堤？も　越えられなかったよ。"]
                    if(self.rtn_txt_no == 4):
                        self.rtn_txt_no += 1
                        self.setFlgWaitingResponce() ### 4回目返事待機
                        return ["知ってる。","わたし、　先に目が覚めたの。","君　ぜーんぜん　起きないから、　ちょっとだけ　その辺歩いてみたんだ。",
                                "で、　説明した通り。","ここ、　な〜んもない。　何処にもいけない。","海の見える　遊歩道？　っていうのかな？　それだけなの。"]
                    if(self.rtn_txt_no == 5):
                        self.rtn_txt_no += 1
                        self.setFlgWaitingResponce() ### 5回目返事待機
                        return ["んー・・・　細かくは　調べてないんだけど・・・。","というか、　君も　見て回りなよ。","ほんと　なんにもないよ、　ココ。"]
                    if(self.rtn_txt_no == 6):
                        self.rtn_txt_no = 0
                        self.setFlgWaitingResponce() ### 5回目返事待機
                        return ["起きるときにね、　物音がしたの。","スー、　トン　って。　ふすまが閉まるような　音よ。",""]
                if (self.scenario_no == 0) and (self.branch_no == 1):
                    if(self.rtn_txt_no == 0):
                        self.cancelFlgWaitingResponce()
                        return ["他に　なにか　手がかりになること、　あったっけ・・・？","思い出してみるけど・・・　あまり　期待しないでね？","・・・周りの探索は　君にまかせた！"]
                if (self.scenario_no == 0) and (self.branch_no == 2):
                    if(self.rtn_txt_no == 0):
                        self.cancelFlgWaitingResponce()
                        return ["わ！　トビラだよ！","ね、　ね、　入ってみよ！","もう　ここ　飽きちゃったよー！"]
                if (self.scenario_no >= 1):
                        self.cancelFlgWaitingResponce()
                        self.setEmote(3,50)
                        ###self.setMoveTo(300, self.draw_y, 80, True) ### 自動移動処理面倒なので辞め
                        return ["手がかり、　見つかりそう？"]

            ### ◆Moonシーン　ー　シナリオ１
            if (self.scene_no == 1):
                if (self.scenario_no >= 0) and (self.branch_no >= 0):
                    if(self.rtn_txt_no == 0):
                        self.face_no = 7
                        self.name_disp = True
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce()
                        self.panning_switch = True     ## panningのスイッチを入れる。
                        self.setEmote(6,160)
                        # self.setEmote(9,160)
                        return ["わ、　何ここ！　すごーい！","花火だよ、　花火！","って、奥に　誰かいるみたい。　声　かけてみようよ。"]
                    if(self.rtn_txt_no == 1):
                        self.face_no = 7
                        self.name_disp = True
                        self.cancelFlgWaitingResponce()
                        return ["あの子から　話、聞けた？","",""]
            ### ◆Fireシーン　ー　シナリオ１
            if (self.scene_no == 2):
                if (self.scenario_no >= 0) and (self.branch_no >= 0):
                    if(self.rtn_txt_no == 0):
                        self.face_no = 7
                        self.name_disp = True
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce()
                        self.panning_switch = True     ## panningのスイッチを入れる。
                        return ["なんていうか、　まっくらだね。","あの燃えてるのが　この部屋の　持ち主かな？","・・・・・・。　ねえ、　アキのこと見てるよ。"]
                    if(self.rtn_txt_no == 1):
                        self.face_no = 7
                        self.name_disp = True
                        self.cancelFlgWaitingResponce()
                        return ["ねーーーーーー！　行ってきてよーーーーーー！","",""]
            ### ◆Waterシーン　ー　シナリオ１
            if (self.scene_no == 3):
                if (self.scenario_no == 3) and (self.branch_no == 0):
                    if(self.rtn_txt_no == 0):
                        self.face_no = 7
                        self.name_disp = True
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce()
                        self.panning_switch = True     ## panningのスイッチを入れる。
                        return ["うえーーー、　なにここ・・・　じめっとしてる・・・。　水浸しだ・・・。","・・・・・・ん？　あれってクラゲ？","・・・にしてはデカいね。　あれも　元ヒト・・・　なのかな？"]
                    if(self.rtn_txt_no == 1):
                        self.cancelFlgWaitingResponce()
                        return ["ヨッ！まかせたよ社長！","未知との邂逅！",""]
                if (self.scenario_no == 3) and (self.branch_no == 1):
                        self.cancelFlgWaitingResponce()
                        self.rtn_txt_no = 0
                        return ["ねえねえ　あのクラゲ、　すっっっごいキレイだね。","キラキラに　すきとおってるよ。","宝石みたい・・・！"]
                if (self.scenario_no == 3) and (self.branch_no == 2):
                        if(self.rtn_txt_no == 0):
                            self.setFlgWaitingResponce()
                            self.rtn_txt_no += 1
                            return ["うーん。　トビラ　ないね。","そういえばさ、 クロエが　言ってたんだけど・・・","",
                                    "部屋の主が　少しでも　心を開いてないと、","中から外へ　トビラが開くことは　ないんだって。","",
                                    "ミチちゃんは　クロエの知り合いだったよね。","火の玉のボーは、　誰にでも懐いちゃう　って感じだった。","",
                                    "あのクラゲさんは　今　すっっっっごい　警戒してるから、","あるはずのトビラが　見当たらないのは","それが　原因なのかも　だよ。"]
                        if (self.rtn_txt_no == 1):
                            self.cancelFlgWaitingResponce()
                            self.branch_no += 1
                            self.rtn_txt_no = 0
                            return ["だね。","他に　できることも　なさそうだし、","失くしたもの　探して、　届けてあげよーよ！"]
                if (self.scenario_no == 3) and (self.branch_no == 3):
                        self.cancelFlgWaitingResponce()
                        self.rtn_txt_no = 0
                        return ["なにか　見つかった？","見つけたものは　クラゲさんに　届けてあげてね！",""]
                
            ### ◆Woodシーン　ー　シナリオ１
            if (self.scene_no == 4):
                if (self.scenario_no >= 0) and (self.branch_no >= 0):
                    if(self.rtn_txt_no == 0):
                        self.face_no = 7
                        self.name_disp = True
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce()
                        self.panning_switch = True     ## panningのスイッチを入れる。
                        return ["んーーーーー　いい風！","ここは・・・・・・　山の中　かな？","・・・げ。　虫・・・・・・。"]
                    if(self.rtn_txt_no == 1):
                        self.face_no = 7
                        self.name_disp = True
                        self.cancelFlgWaitingResponce()
                        return ["・・・毎度　ごめんだけどさ・・・","私、　ムシはちょっと。","あれ、　バッタ　だよね。。。"]
            ### ◆Goldシーン　ー　シナリオ１
            if (self.scene_no == 5):
                if (self.scenario_no >= 0) and (self.branch_no >= 0):
                    if(self.rtn_txt_no == 0):
                        self.face_no = 7
                        self.name_disp = True
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce()
                        self.panning_switch = True     ## panningのスイッチを入れる。
                        return ["ぺっぺっ、　クチのなか　砂っぽい！","今度は　どこ・・・？","砂山？　砂漠・・・、　とか・・・？。"]
                    if(self.rtn_txt_no == 1):
                        self.face_no = 7
                        self.name_disp = True
                        self.cancelFlgWaitingResponce()
                        return ["この、チカチカ見えてるのって何かな。","きれい・・・",""]
            ### ◆Soilシーン　ー　シナリオ１
            if (self.scene_no == 6):
                if (self.scenario_no >= 0) and (self.branch_no >= 0):
                    if(self.rtn_txt_no == 0):
                        self.face_no = 7
                        self.name_disp = True
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce()
                        self.panning_switch = True     ## panningのスイッチを入れる。
                        return ["わぁ・・・","あれ　お墓・・・　かな。　あんなに　たくさん・・・","日が差して、　あったかい　場所だね。"]
                    if(self.rtn_txt_no == 1):
                        self.face_no = 7
                        self.name_disp = True
                        self.cancelFlgWaitingResponce()
                        return ["この　黒いヒト？　が　ここを作ったヒト　かな？","",""]
            ### ◆Sunシーン　ー　シナリオ１
            if (self.scene_no == 7):
                if (self.scenario_no >= 0) and (self.branch_no >= 0):
                    if(self.rtn_txt_no == 0):
                        self.face_no = 7
                        self.name_disp = True
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce()
                        self.panning_switch = True     ## panningのスイッチを入れる。
                        return ["あれ・・・？","ここ・・・？",""]
                    if(self.rtn_txt_no == 1):
                        self.face_no = 7
                        self.name_disp = True
                        self.cancelFlgWaitingResponce()
                        return ["ねえ、　誰も　いないね・・・","なんだか　私　この家、　見たことが　あるような・・・",""]
            ### ◆Endシーン　ー　シナリオ１
            if (self.scene_no == 8):
                if (self.scenario_no >= 0) and (self.branch_no >= 0):
                    if(self.rtn_txt_no == 0):
                        self.face_no = 7
                        self.name_disp = True
                        self.rtn_txt_no += 1
                        self.cancelFlgWaitingResponce()
                        self.panning_switch = True     ## panningのスイッチを入れる。
                        return ["白ッ！","",""]
                    if(self.rtn_txt_no == 1):
                        self.face_no = 7
                        self.name_disp = True
                        self.cancelFlgWaitingResponce()
                        return ["え・・・？　ニワトリじゃん・・・？","めちゃ丸・・・・・・！",""]


        ### プレイヤー : WOLF →　キャラ　：　MICHIのときの【後者】の発話
        if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == C_CHARA_MICHI)):        
            ### 
            if((self.scene_no == 1) and (self.scenario_no == 1) and (self.branch_no == 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["誰？","","",
                            "どこから　来たの？"]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["うっかり　迷い込んだの？　・・・ご愁傷さま。","","",
                            "猫が？","あぁ・・・、　アイツ　また勝手に・・・。","まったく・・・。",
                            "わたしは　ミチ。","ここで、　花火を見てる。",""]
                if(self.rtn_txt_no == 2):
                    self.rtn_txt_no = 0
                    self.cancelFlgWaitingResponce()
                    self.branch_no += 1
                    return ["戸が　奥にあるよ。","あんたと　一緒に　出てきた。","あれって、　どこに　繋がってるわけ？"]

            if((self.scene_no == 1) and (self.scenario_no == 1) and (self.branch_no == 1)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    return ["面白いもの　見つけたらさ、　わたしにも　見せに来てよ。","ときどきさ・・・　ひとりは、　寂しくなるから。",""]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no = 0
                    return ["ここの花火ね、","持ち込まれたもの　に　反応するみたいなの。",""]

            ### 鮮やかな思い出
            if((self.scene_no == 1) and (self.scenario_no == 2) and (self.branch_no >= 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    return ["また　来たんだ。","・・・ねえ、　ちょっと　聞いてもいい？","",
                            "あんた、　鮮やかに蘇る　思い出って　ある？","","",
                            "わたしね、　現世で覚えてる　最後の思い出　がこれなの。","花火を　見てた。",""]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    return ["ここと同じ　小高い丘で・・・","少しだけ　風が　吹いてて。","",
                            "あの日夜空には、　星がいっぱいで。","花火前、　みんなから　抜け出して。","わたし、　あの人を待ってた。",
                            "・・・元気かな。","",""]
                if(self.rtn_txt_no == 2):
                    self.rtn_txt_no += 1
                    return ["現世に戻れば　あの瞬間に　戻れるはずなんだけど、","","",
                            "じつは、　ちょっとこわくもあるんだ。","",""]
                if(self.rtn_txt_no == 3):
                    self.rtn_txt_no += 1
                    return ["・・・長く　居すぎてさ、　記憶が　あいまいに　なってきてて。","","",
                            "本当に　この景色に　戻れるのかな？","・・・って。",""]
                if(self.rtn_txt_no == 4):
                    return ["ごめん。　変な話しちゃった。","",""]

            ### 古い思い出
            if((self.scene_no == 1) and (self.scenario_no == 3) and (self.branch_no >= 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    return ["・・・もしかして　あんたって　暇なの？","まあ、　いいや。","お喋り　付き合ってくれる？",
                            "覚えてる　いちばん　古い思い出　ってあるでしょ。","それって、　何歳くらい？",""]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    return ["わたしはね、　たぶん　４歳くらい。","幼稚園で　お母さんが　迎えに来るの。","季節は　夏で。　何月だろ。　８月頃かな。",
                            "まっててね、って　自分のロッカーに　走るんだけど、","つくったはずの　折り紙のメダルが　なくなってて。","あげたかったのに！　って泣いちゃうの。",
                            "その日は　たまたま父さまも　来ててね。","わかったわかった、　ってなだめて　おんぶしてくれるの。","わたし足をバタバタして　怒るんだけど、　ひょいって。",
                            "園の玄関から　車に乗るまでが　なんだか長くて、","いつもより　目線が高くて、　でも涙ぼろぼろで。","嬉しいんだか　悲しいんだか　って。"]
                if(self.rtn_txt_no == 2):
                    self.rtn_txt_no += 1
                    return ["古い思い出って　なんで残るんだろうね？","幸せな記憶だから、　ってのはあるよね。","あのとき、　泣いたけど、　わたし幸せだった。",
                            "もちろん、　嫌な記憶も残るよね。","嫌なこと言われたり、　ころんでケガしたときとかさ。","・・・友達に　ひどいこと　言っちゃった時とか。"]
                if(self.rtn_txt_no == 3):
                    self.rtn_txt_no += 1
                    return ["あの頃のわたしは、　未来の私が　時間の狭間で","永劫　留まってるなんて　想像もしてないよね。","",
                            "わたしって今、　わたしの未来で　いられてるのかなぁ。","",""]
                if(self.rtn_txt_no == 4):
                    return ["時間が　過ぎてないのに　未来って・・・","なんなんだろね？",""]

            ### 気持ちは思い出になるのか
            if((self.scene_no == 1) and (self.scenario_no == 4) and (self.branch_no >= 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    return ["また来たんだ。","","",
                            "ねえ、　少し　喋っていいかな。","","",
                            "今、　この瞬間って、　思い出になるのかな？","",""]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    return ["この世界って　夢みたいな　ものじゃない？","目覚めたとき、　思い出に　なるのかな？って。","",
                            "何年も　前のことを　思い返してもさ、","振り返るのは　一瞬だから。","この瞬間も　圧縮されちゃうんじゃない？",
                            "圧縮される今を　未来から　振り返るとき、","意識は　未来のわたし　だと思うの。","",
                            "じゃあ、　今のわたしの　不安　喜び　退屈　寂しさは","感情は、　どうなるんだろう　って。",""]
                if(self.rtn_txt_no == 2):
                    return ["この気持ちは、　思い出に　なるのかな？","",""]

            ### 霧散する恐怖
            if((self.scene_no == 1) and (self.scenario_no == 5) and (self.branch_no >= 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    return ["・・・。","","",
                            "ねえ、　もしも　この瞬間がすべて　霧散するとしたら、","・・・わたしは　どうなるんだろう？","",
                            "この場所で　過ごした　時間も、","クロエのバカと　話したことも、","夢みたいに　消えちゃうのかな？",
                            "何かを　失ったことすらも　忘れて、","無くしたことすら　分からずに、","元の生活を　続けるのかな。"]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    return ["わたしね、　ほっといてくれ　って言ったの。","ここに来て　すぐの頃よ。","クロエが最初に　私を　見つけたの。",
                            "わたし　完全にパニックに　なってて。","周りには　誰も居ないし、　花火が上がるだけ。","こわくて　奥の木の側で　うずくまってたの。",
                            "クロエはね、　わたしのことを　見つけてくれて、","何も言わずに　そばにいてくれたの。",""]
                if(self.rtn_txt_no == 2):
                    self.rtn_txt_no += 1
                    return ["でもね！","イイ話で　終わらないのよ　これが！","アイツ　何したと思う！？",
                            "クロエね！　２週間も　ただの猫のフリ　したのよ！！","信じられる！？？","わたし、　ずっと　話しかけちゃったわよ！！",
                            "２週間よ！！！　２周間！！！","うぅ〜〜〜〜！！　記憶を、","あの２週間の　記憶を　消したい・・・！！！",
                            "わたしはね！","二度と　あいつの’部屋’には　行かないって","あの時　決めたのよ！"]
                if(self.rtn_txt_no == 3):
                    self.rtn_txt_no += 1
                    return ["・・・話が　それちゃったけど、","色々あった　ここでのこと、　会ったヒトたちのこと、","わたし　覚えていたいの。",
                            "思い出すと　笑っちゃうのよね。","あの頃は　本当に　バカみたいだったけど、","今となっては、　大事な思い出だ　って思えるの。"]
                if(self.rtn_txt_no == 4):
                    return ["わたしは　覚えていたい。","あなた達のことも　ね。",""]
                

            ### 戻らないことの代償
            if((self.scene_no == 1) and (self.scenario_no == 6) and (self.branch_no >= 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    return ["・・・あれから　考えたんだけど、","聞いてくれる？","",
                            "わたしの選択肢は、　戻ること、　とどまること。","そう　思ったの。","",
                            "実は奥の木、　前はもう少しだけ　葉があったの。","それに気づいたとき、　ちょっとだけ　怖かった。","・・・この場所も　変わっていくんだ、　って。",
                            "この場所、　実は　時間が止まってない・・・","んじゃないかな　って。","ゆっっっっっっっくり、　時間は　流れてる。"]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    return ["きっと　永遠に　近い時をかけて、","わたしは　ここで　死ぬ。","",
                            "いきなり　言われても　困るよね。","ええっと　だから・・・　なにか、","なにか　行動しなきゃ　と思ったの。",
                            "ここに留まるのか、　元の世界に戻るのか。","決めなきゃ　って。","",
                            "留まると　緩やかに　死ぬ。　孤独。","戻ると・・・","あの　花火の夜なのか、　本当は、　自信ないんだ。",
                            "もし、　思ってた場所じゃ　なかったら・・・？","記憶って、　曖昧で　怖いよね。",""]
                if(self.rtn_txt_no == 2):
                    return ["それに、　ここのこと　忘れちゃうかもしれない。","クロエのことも、　あんたのことも・・・","全部、　夢みたいに。"]

            ### 本当に帰りたい場所
            if((self.scene_no == 1) and (self.scenario_no == 7) and (self.branch_no >= 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    return ["わたしね、","クロエと　脱出できる道を　探すことにした。","",
                            "アイツさ、　わたしが行動しないなら","死ぬまで　ちょっかいかける気　だったんだって。","・・・信じられる？"]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    return ["でもさ、　それってつまり・・・","わたしと　ずっと一緒　ってことだよね？","",
                            "1人じゃないなら、","進んでみようかな　って思ったの。","",
                            "アイツの部屋で　話したんだけど、","クロエは　承諾を得れば","人と人の部屋を　繋ぐことが　できるんだって。"]
                if(self.rtn_txt_no == 2):
                    self.rtn_txt_no += 1
                    return ["そういえば、　あなたが持ち込んだ　道具で","花火の形が　変わってたでしょ？","あれ、　全部　見覚えがあったの。","",
                            "同じことを繰り返せば、","わたしが　ここに迷い込んだ　あの夜のこと、","もっと　鮮明に思い出せるかも。",
                            "わたしの願いを思い出す、","一番の　手がかりになると思うの。",""]
                if(self.rtn_txt_no == 3):
                    self.rtn_txt_no += 1
                    return ["たとえ　クロエを連れて　出られなくても、","あの時間や、　この場所のことを","覚えていることは　できるかもしれない。",
                            "・・・一緒に行動して、　一瞬一瞬を　刻んでいたいの。","",""]
                if(self.rtn_txt_no == 4):
                    return ["だから、　一歩ずつ進むわ。","あなた達みたいに　ね。",""]

            ### 未来の自分
            if((self.scene_no == 1) and (self.scenario_no >= 8) and (self.branch_no >= 1)):
                if(self.rtn_txt_no == 0):
                    return ["花火、　まだ増えたりするのかしら？","",""]
                
            if((self.scene_no == 1) and (self.scenario_no == 0)):
                self.rtn_txt_no = 0
                return ["Debug用テキストだよ。","self.rtn_txt_no = 0にしたよ。","がんばれ〜！"]

        ### 選択の瞬間
        if((self.scene_no == 8) and (self.scenario_no == 8) and (self.branch_no >= 1)):
            if(self.rtn_txt_no == 0):
                self.rtn_txt_no += 1
                return ["・・・あの部屋から　移動できるだけでも　びっくりだったのに、","こんなに大勢と　話せるなんて　思わなかった。","",
                        "あんた、　とんでもないやつ　だったのね。","わたしたちの世界に　風穴を　開けちゃうなんて。","",
                        "あの気まぐれ猫と　協力して","空間に　穴を開けて　回ろうなんて、","誰も　思いつかないわよ。"]
            if(self.rtn_txt_no == 1):
                self.rtn_txt_no += 1
                return ["感謝してる。","本当に、　ありがとう。",""]
            if(self.rtn_txt_no == 2):
                self.rtn_txt_no += 1
                return ["変化って　いいね。","踏み出すだけで、　こんなに　見え方が変わるなんて。","",
                        "わたしね、　いまワクワクしてる。","これから　何が起こるのか、","どんな景色が　広がるのか・・・。",
                        "クロエと見ることができる　世界が、","ほんとうに　嬉しいんだ。",""]
            if(self.rtn_txt_no == 3):
                return ["元気でね！","",""]
            

        ### プレイヤー : WOLF →　キャラ　：　GIRANのときの【後者】の発話
        if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == C_CHARA_GIRAN)):
            if((self.scene_no == 4) and (self.scenario_no >= 1) and (self.branch_no == 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["よお。","良い風だな。","",
                            "俺は　ギラン。","あんた　森は　好きかい？",""]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["森はいいぜ。","土も、　葉も、　苔も、　花も、　木々を抜ける風も。","",
                            "心が　落ち着くし・・・　気分が　スッキリしねえか？。","",""]
                if(self.rtn_txt_no == 2):
                    self.cancelFlgWaitingResponce()
                    return ["街には　もう　戻りたくねえな・・・","",""]

        ### プレイヤー : WOLF →　キャラ　：　LUVのときの【後者】の発話
        if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == C_CHARA_LUV)):
            if((self.scene_no == 5) and (self.scenario_no >= 1) and (self.branch_no == 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["やあ。　僕は　LUV。　ラブだ。","","",
                            "ここは　僕の世界。","砂の　世界。",""]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["わざわざ　外から入ってきた　ってことはさ。","探しもの　だろ？","でも、　きっと、　ここにはないよ。",
                            "ここは、　後悔が　降ってくるんだ。","ぼくの後悔がね。","際限なく。"]
                if(self.rtn_txt_no == 2):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["話したいの？","いいよ。","",
                            "きみはさ、　ひとが好き？","誰でもいいよ。　家族や　恋人、　先輩　後輩　教師　同僚　親戚、","なんだっていい。",
                            "ぼくはさ、　全然　興味がない。","","全く。"]


        ### プレイヤー : WOLF →　キャラ　：　LIKIのときの【後者】の発話
        if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == C_CHARA_LIKI)):
            if((self.scene_no == 6) and (self.scenario_no >= 1) and (self.branch_no == 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["ん？おまえどっから来た？"]
                if(self.rtn_txt_no == 1):
                    self.cancelFlgWaitingResponce()
                    return ["ここでは　あんま　騒ぐんじゃねえぞ。"]
                
        ### プレイヤー : WOLF →　キャラ　：　worldmasterのときの【後者】の発話
        if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == C_CHARA_WORLDMASTER)):
            if((self.scene_no == 8) and (self.scenario_no >= 1) and (self.branch_no == 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["これはテスト"]
                if(self.rtn_txt_no == 1):
                    self.cancelFlgWaitingResponce()
                    return ["表示されてますかね","",""]
                
        ###会話によってシーン・シナリオ・ブランチに変化を与えたいことがある。ゲーム本体側でこれらの値を取得してゲーム本体側へ上書き利用する。
        # →[self.scene_no, self.scenario_no, self.branch_no]
    def setEmote(self, emote_no, valid_frame):
        ### 初期化
        self.resetEmote()
        ### エモート表示有効化
        self.emote_switch = True
        ### 指定エモートの有効フレームを設定（対応No→[0:喜,1:怒,2:哀,3:楽,4:驚,5:疑,6:愛,7:怖,8:喋,9:困,10:未使用]）
        self.emote_frames[emote_no] = valid_frame
        self.emote_initial_frame = valid_frame
    def resetEmote(self):
        ### エモート表示無効化
        self.emote_switch = False
        ### エモート表示フレームを初期化
        self.emote_frames = [0,0,0,0,0,0,0,0,0,0,0]
        self.emote_initial_frame = 0
    def updateEmote(self):
        ### エモート表示フレームを更新
        if self.emote_switch == True:                
            for i in range(len(self.emote_frames)):
                if self.emote_frames[i] > 0:
                    if self.emote_frames[i] == self.emote_initial_frame :
                        ##効果音
                        pyxel.play(3, 47, loop=False)
                    self.emote_frames[i] -= 1
                    if self.emote_frames[i] == 0:
                        self.emote_switch = False
    def drawEmote(self):
        ### 表示位置
        self.emote_x = self.draw_x + self.width/2
        self.emote_y = self.draw_y - 16
        ### エモート表示
        if self.emote_switch == True:
            ### エモート吹き出し
            pyxel.blt(self.emote_x, self.emote_y, 0, 88, 0, 16, 16, 3)
            ### エモートアイコン
            if self.emote_frames[0] > 0: ### 喜
                pyxel.blt(self.emote_x, self.emote_y, 0, 0, 0, 16, 16, 0)
            if self.emote_frames[1] > 0: ### 怒
                pyxel.blt(self.emote_x, self.emote_y, 0, 16, 0, 16, 16, 0)
            if self.emote_frames[2] > 0: ### 哀
                pyxel.blt(self.emote_x, self.emote_y, 0, 32, 0, 16, 16, 0)
            if self.emote_frames[3] > 0: ### 楽
                pyxel.blt(self.emote_x +4, self.emote_y +2, 0,  93, 16 + 10 * (pyxel.frame_count // 10 % 3), 9, 10, 3)
            if self.emote_frames[4] > 0: ### 驚
                pyxel.blt(self.emote_x +6, self.emote_y +3, 0,  79, 16 + 10 * (pyxel.frame_count // 10 % 3), 4, 10, 3)
            if self.emote_frames[5] > 0: ### 疑
                pyxel.blt(self.emote_x +5, self.emote_y +3, 0,  72, 16 + 10 * (pyxel.frame_count // 10 % 3), 7, 10, 3)
            if self.emote_frames[6] > 0: ### 愛
                pyxel.blt(self.emote_x +4, self.emote_y +2, 0,  84, 16 + 10 * (pyxel.frame_count // 10 % 3), 9, 10, 3)
            if self.emote_frames[7] > 0: ### 怖
                pyxel.blt(self.emote_x, self.emote_y, 0, 112, 0, 16, 16, 0)
            if self.emote_frames[8] > 0: ### 喋
                pyxel.blt(self.emote_x, self.emote_y, 0, 128, 0, 16, 16, 0)
            if self.emote_frames[9] > 0:
                pyxel.blt(self.emote_x +4, self.emote_y +2, 0, 102, 16 + 10 * (pyxel.frame_count // 10 % 3), 8, 10, 3)

    def setMoveTo(self, x, y, frames, return_flg):
        """目的地座標、フレーム数、戻り動作を設定し、移動を開始する"""
        # 目標地点とフレーム数を設定
        self.position_x = self.draw_x
        self.position_y = self.draw_y
        self.move_from_x = self.position_x
        self.move_from_y = self.position_y
        self.move_to_x = x
        self.move_to_y = y
        self.move_frame_count = frames
        self.initial_frame_count = frames
        self.auto_move_R_switch = return_flg
        self.is_auto_moving = True  # 移動開始フラグをオン
        self.auto_move_switch = True

        # 各フレームごとの移動量を計算
        dx = self.move_to_x - self.move_from_x
        dy = self.move_to_y - self.move_from_y
        self.step_x = dx / frames if frames > 0 else 0
        self.step_y = dy / frames if frames > 0 else 0

        ### ゲーム本体と受け渡すためのフレーム数を設定
        self.object_pos_update_frames = frames
        if return_flg:
            self.object_pos_update_frames = frames * 2

    def updateMoveTo(self):
        """移動フレーム数に従って移動し、必要なら元の位置に戻る"""
        if self.auto_move_switch and self.move_frame_count > 0:
            # 次のフレームでの位置を計算（整数処理なしで移動確認用）
            self.position_x += self.step_x
            self.position_y += self.step_y
            self.move_frame_count -= 1

            self.draw_x = self.position_x
            self.draw_y = self.position_y
            self.x = self.position_x
            self.y = self.position_y

            # 目標に到達した場合
            if self.move_frame_count <= 0:
                if self.auto_move_R_switch:
                    # 戻り動作の設定
                    self.setMoveTo(self.move_from_x, self.move_from_y, self.initial_frame_count, False)
                else:
                    # 完全停止
                    self.is_auto_moving = False
                    self.auto_move_switch = False
                    self.resetMoveTo()

    def resetMoveTo(self):
        """移動の状態をリセット"""
        self.move_to_x = self.draw_x
        self.move_to_y = self.draw_y
        self.move_frame_count = 0
        self.step_x = 0
        self.step_y = 0
        self.is_auto_moving = False
        self.auto_move_switch = False
        self.object_pos_update_frames = 0