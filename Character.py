import pyxel
from GameObject import GameObject

###画面用設定値
C_MAX_DISPWORDS = 28 #画面幅300px＆umplus_j10rで１行２８文字
C_MSGWINDOW_WIDTH = 296 #8*37タイルマップ.
C_MSGWINDOW_HEIGHT = 64 #8*37タイルマップ.

###操作キャラクタ用固定パラメタ
C_PLAYER_WIDTH = 16 * 1
C_PLAYER_HEIGHT = 16 * 3
C_PLAYER_MOVE_SPEED = 2

###選択可能キャラクタ
CHARACTERS = ["GIRL","WOLF","BOY","MANTA","LEDY","ROBOT","BOOK","RAT","CAT","TALISMAN"]
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

# 移動制限のためのマージンを設定
C_TOP_MARGIN = 16 * 7 - 8# 画面上部から移動可能領域までのマージン
C_BOTTOM_MARGIN = C_MSGWINDOW_HEIGHT + 4  # 画面下部から移動可能領域までのマージン
C_PX_AROUND_CHARA = 6 #当たり判定用のy軸不可侵エリア幅

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
        self.able_moving_top = C_TOP_MARGIN
        self.hp = 10
        self.max_hp = 10
        self.mp = 5
        self.max_mp = 5

        ###操作中
        self.is_playing = is_playing

        ###表示順序の基準になる、キャラクター足元の座標
        self.position_x = self.x + C_PLAYER_WIDTH/2
        self.position_y = self.y + C_PLAYER_HEIGHT

        ###移動実行した際の方向記憶ワーク
        self.wk_moved_dir = 4 #01234:上下左右無
        self.wk_moved_speed = 0

        ###会話とシナリオに付随したテキスト返却のための管理パラメタ

        # 軌跡描画用の座標記録配列
        self.trajectory_point = [[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y],[self.x, self.y]]
        self.trajectory_point.pop(0)
        self.trajectory_point.append([self.x, self.y])

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
            # self.y = max(min(self.y, pyxel.height - C_PLAYER_HEIGHT - C_BOTTOM_MARGIN), C_TOP_MARGIN) # TOPとBOTTOMにマージンを設けている
            self.y = max(min(self.y, pyxel.height - C_PLAYER_HEIGHT - C_BOTTOM_MARGIN), self.able_moving_top) # TOPとBOTTOMにマージンを設けている

        ###表示順序の基準となる、足元の座標情報を更新する
        self.position_x = self.x + C_PLAYER_WIDTH/2
        self.position_y = self.y + C_PLAYER_HEIGHT

        ###足元の座標を最大5件まで常に記録する
        if (len(self.trajectory_point) == 20):
            self.trajectory_point.pop(0)
        self.trajectory_point.append([self.position_x, self.position_y])

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
                ### 他のキーはその方向を向いて立ち止まる
                if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z):
                    self.player_direction = 1
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
                    self.player_direction = 2
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S):
                    self.player_direction = 3
                    self.moving = False
                else:
                    self.y -= move_speed
                    self.player_direction = 0
                    self.moving = True
            if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z):
                if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
                    self.player_direction = 0
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
                    self.player_direction = 2
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S):
                    self.player_direction = 3
                    self.moving = False
                else:
                    self.y += move_speed
                    self.player_direction = 1
                    self.moving = True
            if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
                if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S):
                    self.player_direction = 3
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
                    self.player_direction = 0
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z):
                    self.player_direction = 1
                    self.moving = False
                else:
                    self.x -= move_speed
                    self.player_direction = 2
                    self.moving = True
            if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_S):
                if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
                    self.player_direction = 2
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
                    self.player_direction = 0
                    self.moving = False
                elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_Z):
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

    def is_colliding_with(self, other):
        # 衝突判定を行う範囲を定義（ここでは5px分としています）
        range_x = self.width
        range_y = C_PX_AROUND_CHARA

        # 衝突判定
        if self.position_x + range_x > other.position_x:
            if self.position_x < other.position_x + range_x:
                if self.position_y + range_y > other.position_y:
                    if self.position_y < other.position_y + range_y:
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
        self.scene_no = scene_no ### シーン番号
        self.scenario_no = scenario_no ### シナリオ番号
        self.branch_no = branch_no ### シナリオ分岐番号
        # self.character_no == C_CHARA_WOLF
        # self.conversation_with = C_CHARA_GIRL ### 誰と会話中か
        self.character_no == conversation_from
        self.conversation_with = conversation_with ### 誰と会話中か
        #----------------------------------------------------------- 

        ###self.rtn_txt_no = 0 ### 返却テキスト番号
        ###self.flg_waiting_responce = False ### 相手からの返答待ち（＝質問中）フラグ

        ### ◆シーン１　ー　シナリオ１
        if((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 0)):
            ### プレイヤー : WOLF →　キャラ　：　GIRLのときの【前者】の発話。
            if((self.character_no == C_CHARA_WOLF) and (self.conversation_with == C_CHARA_GIRL)):
                if(self.rtn_txt_no == 0): ### 1回目返事
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce() 
                    return ["言われてみれば覚えてない・・・。","","","俺はそこの堤防で寝てたんだが、前の記憶がすっぽり抜け落ちてるな。","あんたも同じか？"]

    def getReactionText(self, scene_no, scenario_no, branch_no, conversation_with, response_no):
        ###当該シーン・シナリオ配下でcharacter_noがプレイヤーconversation_withに話しかけられた場合の発話
        #----------------------------------------------------------- 
        ###シーン番号、シナリオ番号、返却テキスト番号（進行に合わせて返却のたびにカウントアップ、ただし質問中はそのまま）、質問中フラグ、返答結果番号
        self.scene_no = scene_no ### シーン番号
        self.scenario_no = scenario_no ### シナリオ番号
        self.branch_no = branch_no ### シナリオ分岐番号
        self.conversation_with = conversation_with ### 誰と会話中か
        # self.conversation_with = C_CHARA_WOLF ### 誰と会話中か
        #----------------------------------------------------------- 

        ###self.rtn_txt_no = 0 ### 返却テキスト番号
        ###self.flg_waiting_responce = False ### 相手からの返答待ち（＝質問中）フラグ
        self.responce_no = response_no ### 返答結果番号

        ### ◆シーン１　ー　シナリオ１
        if((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 0)):
            ### プレイヤー : WOLF →　キャラ　：　GIRLのときの【後者】の発話
            if((self.conversation_with == C_CHARA_WOLF) and (self.character_no == C_CHARA_GIRL)):
                if(self.rtn_txt_no == 0):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["ここってなんだか変じゃない？なんて言うか……進めないの。"]
                if(self.rtn_txt_no == 1):
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce() ### 1回目返事待機
                    return ["それに、ここに来たときのこと覚えて無いんだよね。","あなたはどう？"]
                if(self.rtn_txt_no == 2):
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["わたしは……","","","真っ白な光の中で波の音を聞いてたら、徐々に視界がハッキリしてきて……","うーん、だめ、これ以上思い出せないや。"]
                if(self.rtn_txt_no == 3):
                    self.cancelFlgWaitingResponce()
                    return ["これ以上思い出せそうにないや。ごめんね。","すこし、時間をちょうだい。"]
            
        ###会話によってシーン・シナリオ・ブランチに変化を与えたいことがある。ゲーム本体側でこれらの値を取得してゲーム本体側へ上書き利用する。
        # →[self.scene_no, self.scenario_no, self.branch_no]
