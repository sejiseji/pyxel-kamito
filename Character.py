import pyxel
import random as rnd
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

        self.draw_x = 0
        self.draw_y = 0

        ###操作中
        self.is_playing = is_playing

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
        if self.character_no in(2,3,4,5,6,7,8,9):
            ### 60frameに１度ランダムにdirectionを変える
            if pyxel.frame_count % 60 == 0:
                self.player_direction = rnd.randint(0,3)
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

    def draw(self):
        if self.character_no in(2,3,4,5,6,7,8,9):
            if self.character_no == C_CHARA_MICHI: #2 ミチ in moon-door
                if self.player_direction == 0:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 3, 128,  16 * 1, 16 * 2.5, 3) # 上向き
                if self.player_direction == 1:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 1, 128,  16 * 1, 16 * 2.5, 3) # 下向き
                if self.player_direction == 2:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 2, 128, -16 * 1, 16 * 2.5, 3) # 左向き
                if self.player_direction == 3:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 2, 128,  16 * 1, 16 * 2.5, 3) # 右向き
            if self.character_no == C_CHARA_LIKI: #2 リキ in soil-door
                if self.player_direction == 0:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 3, 168,  16 * 1, 16 * 3, 3) # 上向き
                if self.player_direction == 1:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 1, 168,  16 * 1, 16 * 3, 3) # 下向き
                if self.player_direction == 2:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 2, 168, -16 * 1, 16 * 3, 3) # 左向き
                if self.player_direction == 3:
                    pyxel.blt(self.draw_x, self.draw_y, 1, 16 * 2, 168,  16 * 1, 16 * 3, 3) # 右向き
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
            if((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 0)):            
                if(self.rtn_txt_no == 0): ### 1回目返事
                    self.rtn_txt_no += 1
                    self.face_no = 7
                    self.name_disp = True
                    self.cancelFlgWaitingResponce() 
                    return ["あ・・・えと。俺は、ラナ。","","",
                            "さ、さっきまで確か神社で・・・","","",
                            "ひとりで参拝してたはず、だ。","","",
                            "手を打って","後ろで声がして","そして・・・・・・。",
                            "そして今・・・だ。","ここ・・・どこなんだ・・・？"]
                if(self.rtn_txt_no == 1): ### 2回目返事
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce() 
                    return ["ま、まってくれよ・・・","","",
                            "願いを途中止めしたから？","ここにいる理由が？","それだけ？",
                            "つーか、ここどこだよ？","からだは？？","ここに引きずり込まれたってことか！？"]
                if(self.rtn_txt_no == 2): ### 3回目返事
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce() 
                    return ["なんだよそりゃあ・・・。","意識って・・・強引にも程があるだろ。","問答無用じゃねえか。",
                            "うーーーーーーーーーーーん・・・。","納得・・・・できてねえけど・・・","",
                            "とりあえず　わかったよ・・・。","願いがハンパだった・・・と。","",
                            "じゃあ・・・、改めて願いをカミサマに伝えれば戻れるのか？"]
                if(self.rtn_txt_no == 3): ### 4回目返事
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce() 
                    return ["そりゃもちろ・・・ん？","あ？","",
                            "思い出せ・・・ない・・・？","","",
                            "思い出せないぞ・・・なんで・・・"]
                if(self.rtn_txt_no == 4): ### 5回目返事
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce() 
                    return ["はあ！？","いや、詰んでんじゃねえかそんなの・・・","",
                            "で、でも！","何かしら伝えておけばいいんだろ？","",
                            "そしたら元の場所に返してもらえるんじゃ・・・"]
                if(self.rtn_txt_no == 5): ### 6回目返事
                    self.rtn_txt_no = 0
                    self.branch_no += 1
                    self.cancelFlgWaitingResponce() 
                    return ["「静かの水域」に集まる、近しい願いの扉・・・。","","",
                            "それを探す・・・。","","",
                            "扉の先の住人と会って、","忘れた願いを思い出す・・・だな。","わかったよ・・・。"]

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
                    return ["ああ。","この水域に集まる扉、ってのを探してる。","その先に行きたいんだけど・・・わかるか？"]
            if((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 2)):   
                if(self.rtn_txt_no == 0): ### 2回目返事
                    self.cancelFlgWaitingResponce() 
                    return ["どうしてそんなに協力的なんだ？","なにか、理由でもあるのか？",""]

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
            if((self.scene_no == 3) and (self.scenario_no == 3) and (self.branch_no == 1)):            
                if(self.rtn_txt_no == 0): ### 1回目返事
                    self.cancelFlgWaitingResponce() 
                    return ["おちつけって。俺はラナ。","あとイヌじゃねえ。オオカミだ。","訳あって、あんたみてーな人達から話を聞いてんだ。"]
            if((self.scene_no == 3) and (self.scenario_no == 3) and (self.branch_no == 2)):   
                if(self.rtn_txt_no == 0): ### 2回目返事
                    self.cancelFlgWaitingResponce() 


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
            if((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 0)):
                if(self.rtn_txt_no == 0):
                    self.face_no = 7
                    self.name_disp = True
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["あ。おはよ。","","",
                            "あたしはカナ。","あなた、自分のことわかる？"]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce() ### 1回目返事待機
                    return ["あと、目覚める前のこと、覚えてる？"]
                if(self.rtn_txt_no == 2):
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce() ### 2回目返事待機
                    return ["うんうん。だいじょうぶそうだね。","えっと・・・","まず端的に言うね。",
                            "あのとき　お願い　途中で止めちゃったでしょ。","心で唱えきる前に、目まで開けちゃって。","それが原因なの。",
                            "願いはまだ、神様にとどいてないの。","そして、願いを捧げないとここからは出られない。","",
                            "それが、キミがここにいる理由だよ。"]
                if(self.rtn_txt_no == 3):
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce() ### 3回目返事待機
                    return ["ここは現世じゃないんだ。神様の庭だよ。","あと、体は大丈夫だよ。","",
                            "ここにあるのは、キミの意識だけなの。","","",
                            "現世では、刹那にも満たない一瞬なんだ。","神様が意識を引っ張ってきちゃうんだけど・・・","ちょっと強引だよね。"]
                if(self.rtn_txt_no == 4):
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce() ### 4回目返事待機
                    return ["そのとおり。","でも、１つ問題があってね・・・。","",
                            "参拝での自分の願い、思い出せる？",""]
                if(self.rtn_txt_no == 5):
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce() ### 5回目返事待機
                    return ["んー・・・やっぱりか。","問題って、それなの。","",
                            "連れてこられた人が、願いを覚えてないんだよね・・・。","","",
                            "意識の間隙で引っ張っちゃうからだと思うんだけど。",""]
                if(self.rtn_txt_no == 6):
                    self.rtn_txt_no = 0
                    self.setFlgWaitingResponce() ### 5回目返事待機
                    return ["それはダメなの。","神様ってさ、全部お見通しだから。","神への虚偽は重罪になっちゃうよ。",
                            "それに詰みってわけでもないんだ。","ここ「静かの水域」は、近い願いの扉が集まるの。","",
                            "扉の住人達が抱えているものを知れば、","きっと、キミの願いのヒントになると思うよ。"]
            if ((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 1)):
                if(self.rtn_txt_no == 0):
                    self.cancelFlgWaitingResponce()
                    return ["まずはここからつながる扉を探しましょ。"]
            if ((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 2)):
                if(self.rtn_txt_no == 0):
                    self.cancelFlgWaitingResponce()
                    return ["わお！扉だよ！","これで、次の場所に行けるね！","さー！はりきって行こー！"]
            if((self.scene_no == 0) and (self.scenario_no >= 1)):
                    self.cancelFlgWaitingResponce()
                    return ["願いの手がかり、見つかりそう？"]

        ### プレイヤー : WOLF →　キャラ　：　MICHIのときの【後者】の発話
        if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == C_CHARA_MICHI)):
            if((self.scene_no == 1) and (self.scenario_no == 1) and (self.branch_no == 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["誰？","","",
                            "どこから来たの？"]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["うっかり迷い込んだの？ご愁傷さま。","","",
                            "え？　猫？","あぁ　アイツまた勝手に招いたのね。","まったく・・・。",
                            "わたしはミチ。ここで花火を見てるんだ。","・・・ずっとね。"]
                if(self.rtn_txt_no == 2):
                    self.rtn_txt_no = 0
                    self.cancelFlgWaitingResponce()
                    self.branch_no += 1
                    return ["戸は奥にあるよ。","あんたと一緒に出てきた。・・・透けちゃうんだけど。","わたしは触れないけど、あなたなら触れるかも。"]
            if((self.scene_no == 1) and (self.scenario_no >= 1) and (self.branch_no == 1))or((self.scene_no == 1) and (self.scenario_no >= 2)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    return ["面白いもの見つけたらさ、見せに来てよ。","たまにときどき・・・　ひとりが寂しくなるから、さ。",""]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no = 0
                    return ["ここの花火ね、","持ち込まれたものに反応するみたいなの。",""]

        # ### プレイヤー : WOLF →　キャラ　：　Jericoのときの【後者】の発話
        # if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == 9900)):
        #     ### ◆シーン１　ー　シナリオ１
        #     if ((self.scene_no == 3) and (self.scenario_no == 0) and (self.branch_no == 0)):
        #         if self.rtn_txt_no == 0:
        #             self.rtn_txt_no += 1
        #             self.cancelFlgWaitingResponce()
        #             return ["・・・・・？","え、うそ。人？","",
        #                     "いや、イヌ？オオカミ？","じゃなくて。","",
        #                     "ま、ままままままってまって。"]
        #         if self.rtn_txt_no == 1:
        #             self.rtn_txt_no = 0
        #             self.name_disp = True
        #             self.setFlgWaitingResponce()
        #             self.branch_no += 1
        #             return ["あああああああたし、ジェリコ！", "あなたは？",""]
        #     if ((self.scene_no == 3) and (self.scenario_no == 0) and (self.branch_no == 1)):
        #         if self.rtn_txt_no == 0:
        #             self.cancelFlgWaitingResponce()
        #             return ["よよよよろしくお願いします・・・。","わわ、わたしもうかれこれ３年も魚としか話してなくて","お会いできてほほほ本当にうれしいです。"]


        ### プレイヤー : WOLF →　キャラ　：　LIKIのときの【後者】の発話
        if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == C_CHARA_LIKI)):
            if((self.scene_no == 6) and (self.scenario_no >= 1) and (self.branch_no == 0)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["ん？おめーどっから来た？"]
                if(self.rtn_txt_no == 1):
                    self.cancelFlgWaitingResponce()
                    return ["ここぁ神聖な場所だかんな。","ぜってーに騒ぐんじゃねえぞ。",""]
        ###会話によってシーン・シナリオ・ブランチに変化を与えたいことがある。ゲーム本体側でこれらの値を取得してゲーム本体側へ上書き利用する。
        # →[self.scene_no, self.scenario_no, self.branch_no]
