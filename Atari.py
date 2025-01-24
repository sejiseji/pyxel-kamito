import pyxel
import math as Math
import random
from GameObject import GameObject

###戸
C_ATARI_WIDTH = 16 * 1
C_ATARI_HEIGHT = 16 * 1
C_PX_AROUND_ATARI = 6 #当たり判定用のy軸不可侵エリア幅

###obj_no : object number.
# 0 : 歩行者用信号の付いた電柱
# 1 : バス停
# 2 : 立て看板
# 3 : 猫
# 4 : 木の幹１
# 5 : 木の幹２
# 6 : ストーブ&ヤカン
# 7 : girls
# 8 : 木の幹3
# 9 : 木の幹4
#10 : ボボ




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

##########-----------------------------------------------------------------------
# 背景用当たり判定オブジェクト・・・背景チェックに用いる
class Atari(GameObject):
    def __init__(self, x=0, y=0, obj=0, scene=0, is_visible=True):
        super().__init__(x,y)
        self.width = C_ATARI_WIDTH
        self.height = C_ATARI_HEIGHT
        self.collision_width = C_PX_AROUND_ATARI
        self.collision_height = C_PX_AROUND_ATARI
        ###表示順序の基準になる、Door足元の座標
        self.position_x = self.x + self.width/2
        self.position_y = self.y + self.height

        self.flg_reaction = False
        self.is_playing = False

        self.obj_no = obj
        self.name_disp = True

        ###灯籠用乱数（０，１，２）
        self.rndpoint = random.randint(0,2)

        ###シーンごとに表示するテキストを変えるための変数
        self.scene_no = scene # 0:home 1:door1 2:door2 3:door3 4:door4 5:door5 6:door6 7:door7 8:ending
        self.scenario_no = 0
        self.branch_no = 0
        self.conversation_with = 0
        self.responce_no = 0
        self.rtn_txt_no = 0
        self.face_disp = True
        ### 返却テキストの切り替えスイッチ
        self.rtn_txt_switch = False

        self.is_visible = is_visible

        self.draw_x = 0
        self.draw_y = 0

        self.flg_waiting_responce = False

        self.object_pos_update_frames = 0
        self.collision_other_x = 8
        self.collision_other_y = 8


    def changeSize(self, width, height):
        self.width = width
        self.height = height

    def changePosition(self, x, y):
        ###表示順序の基準になる、Door足元の座標
        self.position_x = self.x + x
        self.position_y = self.y + y

    def changeCollisionSize(self, width, height):
        self.collision_width = width
        self.collision_height = height

    def changeCollisionOtherSize(self, width, height):
        self.collision_other_x = width
        self.collision_other_y = height

    def update(self):
        ###表示順序の基準となる、足元の座標情報を更新する
        self.position_x = self.x + C_ATARI_WIDTH/2
        self.position_y = self.y + C_ATARI_HEIGHT

    def draw(self):
        if self.is_visible:
            if self.obj_no in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 16, 17, 18, \
                               19, 20, 21, 22, 23, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36): 
                self.frames01 = Math.floor(pyxel.frame_count/8) % 7
                self.frames02 = Math.floor(pyxel.frame_count/5) % 12
                self.frames03 = Math.floor((pyxel.frame_count + 11)/5) % 12
                self.frames04 = Math.floor((pyxel.frame_count + 2)/5) % 12
                if Math.floor(pyxel.frame_count/8) % 7 != 6:
                    pyxel.blt(self.draw_x,    self.draw_y +4,  2, 160, 0 + self.frames01 * 16, 16, 16, 0)
            elif self.obj_no == 24: ###灯籠
                self.frames01 = (Math.floor(pyxel.frame_count/45)+ self.rndpoint) % 3
                pyxel.blt(self.draw_x, self.draw_y -32, 1, 112, 208, 16, 48, 3)
                if self.frames01 == 1:
                    pyxel.blt(self.draw_x, self.draw_y -32, 1, 96, 224, 16, 16, 3)
                if self.frames01 == 2:
                    pyxel.blt(self.draw_x, self.draw_y -32, 1, 96, 240, 16, 16, 3)
            elif self.obj_no == 25: ###神棚
                #全体y調整値
                self.y_adjust = -30

                pyxel.blt(self.draw_x -13, self.draw_y -10 +self.y_adjust, 1, 32, 232, 8, 13, 0) #左側上
                pyxel.blt(self.draw_x -13, self.draw_y + 3 +self.y_adjust, 1, 32, 245, 8,  1, 0) #左側中1
                pyxel.blt(self.draw_x -13, self.draw_y + 4 +self.y_adjust, 1, 32, 245, 8,  1, 0) #左側中2
                pyxel.blt(self.draw_x -13, self.draw_y + 5 +self.y_adjust, 1, 32, 245, 8,  1, 0) #左側中3
                pyxel.blt(self.draw_x -13, self.draw_y + 6 +self.y_adjust, 1, 32, 245, 8,  1, 0) #左側中4
                pyxel.blt(self.draw_x -13, self.draw_y + 7 +self.y_adjust, 1, 32, 245, 8,  1, 0) #左側中5
                pyxel.blt(self.draw_x -13, self.draw_y + 8 +self.y_adjust, 1, 32, 245, 8,  1, 0) #左側中6
                pyxel.blt(self.draw_x -13, self.draw_y + 9 +self.y_adjust, 1, 32, 246, 8,  2, 0) #左側下1
                pyxel.blt(self.draw_x -13, self.draw_y +11 +self.y_adjust, 1, 32, 246, 8,  2, 0) #左側下1
                pyxel.blt(self.draw_x -20, self.draw_y + 9 +self.y_adjust, 1, 32, 246, 8,  2, 0) #左側下2
                pyxel.blt(self.draw_x -20, self.draw_y +11 +self.y_adjust, 1, 32, 246, 8,  2, 0) #左側下2
                #-----------------------------------------------------------
                pyxel.blt(self.draw_x - 5, self.draw_y -10 +self.y_adjust, 1, 38, 232, 4, 13, 0) #中央1上
                pyxel.blt(self.draw_x - 5, self.draw_y + 3 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央1中1
                pyxel.blt(self.draw_x - 5, self.draw_y + 4 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央1中2
                pyxel.blt(self.draw_x - 5, self.draw_y + 5 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央1中3
                pyxel.blt(self.draw_x - 5, self.draw_y + 6 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央1中4
                pyxel.blt(self.draw_x - 5, self.draw_y + 7 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央1中5
                pyxel.blt(self.draw_x - 5, self.draw_y + 8 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央1中6                
                pyxel.blt(self.draw_x - 5, self.draw_y + 9 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央1下
                pyxel.blt(self.draw_x - 5, self.draw_y +11 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央1下
                #----------
                pyxel.blt(self.draw_x - 1, self.draw_y -10 +self.y_adjust, 1, 38, 232, 4, 13, 0) #中央2上
                pyxel.blt(self.draw_x - 1, self.draw_y + 3 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央2中1
                pyxel.blt(self.draw_x - 1, self.draw_y + 4 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央2中2
                pyxel.blt(self.draw_x - 1, self.draw_y + 5 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央2中3
                pyxel.blt(self.draw_x - 1, self.draw_y + 6 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央2中4
                pyxel.blt(self.draw_x - 1, self.draw_y + 7 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央2中5
                pyxel.blt(self.draw_x - 1, self.draw_y + 8 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央2中6
                pyxel.blt(self.draw_x - 1, self.draw_y + 9 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央2下
                pyxel.blt(self.draw_x - 1, self.draw_y +11 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央2下
                #----------
                pyxel.blt(self.draw_x + 3, self.draw_y -10 +self.y_adjust, 1, 38, 232, 4, 13, 0) #中央3上
                pyxel.blt(self.draw_x + 3, self.draw_y + 3 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央3中1
                pyxel.blt(self.draw_x + 3, self.draw_y + 4 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央3中2
                pyxel.blt(self.draw_x + 3, self.draw_y + 5 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央3中3
                pyxel.blt(self.draw_x + 3, self.draw_y + 6 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央3中4
                pyxel.blt(self.draw_x + 3, self.draw_y + 7 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央3中5
                pyxel.blt(self.draw_x + 3, self.draw_y + 8 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央3中6
                pyxel.blt(self.draw_x + 3, self.draw_y + 9 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央3下
                pyxel.blt(self.draw_x + 3, self.draw_y +11 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央3下
                #----------
                pyxel.blt(self.draw_x + 7, self.draw_y -10 +self.y_adjust, 1, 38, 232, 4, 13, 0) #中央4上
                pyxel.blt(self.draw_x + 7, self.draw_y + 3 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央4中1
                pyxel.blt(self.draw_x + 7, self.draw_y + 4 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央4中2
                pyxel.blt(self.draw_x + 7, self.draw_y + 5 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央4中3
                pyxel.blt(self.draw_x + 7, self.draw_y + 6 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央4中4
                pyxel.blt(self.draw_x + 7, self.draw_y + 7 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央4中5
                pyxel.blt(self.draw_x + 7, self.draw_y + 8 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央4中6
                pyxel.blt(self.draw_x + 7, self.draw_y + 9 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央4下
                pyxel.blt(self.draw_x + 7, self.draw_y +11 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央4下
                #----------
                pyxel.blt(self.draw_x +11, self.draw_y -10 +self.y_adjust, 1, 38, 232, 4, 13, 0) #中央5上
                pyxel.blt(self.draw_x +11, self.draw_y + 3 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央5中1
                pyxel.blt(self.draw_x +11, self.draw_y + 4 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央5中2
                pyxel.blt(self.draw_x +11, self.draw_y + 5 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央5中3
                pyxel.blt(self.draw_x +11, self.draw_y + 6 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央5中4
                pyxel.blt(self.draw_x +11, self.draw_y + 7 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央5中5
                pyxel.blt(self.draw_x +11, self.draw_y + 8 +self.y_adjust, 1, 38, 245, 4,  1, 0) #中央5中6
                pyxel.blt(self.draw_x +11, self.draw_y + 9 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央5下
                pyxel.blt(self.draw_x +11, self.draw_y +11 +self.y_adjust, 1, 38, 246, 4,  2, 0) #中央5下
                #-----------------------------------------------------------
                pyxel.blt(self.draw_x +15, self.draw_y -10 +self.y_adjust, 1, 40, 232, 8, 13, 0) #右側上
                pyxel.blt(self.draw_x +15, self.draw_y + 3 +self.y_adjust, 1, 40, 245, 8,  1, 0) #右側中1
                pyxel.blt(self.draw_x +15, self.draw_y + 4 +self.y_adjust, 1, 40, 245, 8,  1, 0) #右側中2
                pyxel.blt(self.draw_x +15, self.draw_y + 5 +self.y_adjust, 1, 40, 245, 8,  1, 0) #右側中3
                pyxel.blt(self.draw_x +15, self.draw_y + 6 +self.y_adjust, 1, 40, 245, 8,  1, 0) #右側中4
                pyxel.blt(self.draw_x +15, self.draw_y + 7 +self.y_adjust, 1, 40, 245, 8,  1, 0) #右側中5
                pyxel.blt(self.draw_x +15, self.draw_y + 8 +self.y_adjust, 1, 40, 245, 8,  1, 0) #右側中6
                pyxel.blt(self.draw_x +15, self.draw_y + 9 +self.y_adjust, 1, 40, 246, 8,  2, 0) #右側下
                pyxel.blt(self.draw_x +15, self.draw_y +11 +self.y_adjust, 1, 40, 246, 8,  2, 0) #右側下
                pyxel.blt(self.draw_x +22, self.draw_y + 9 +self.y_adjust, 1, 40, 246, 8,  2, 0) #右側下2
                pyxel.blt(self.draw_x +22, self.draw_y +11 +self.y_adjust, 1, 40, 246, 8,  2, 0) #右側下2
                #-----------------------------------------------------------
                pyxel.blt(self.draw_x -21, self.draw_y - 7 +self.y_adjust, 1, 80, 224, 8, 16, 0) #榊左
                pyxel.blt(self.draw_x +23, self.draw_y - 7 +self.y_adjust, 1, 80, 224, 8, 16, 0) #榊右
                #-----------------------------------------------------------
                pyxel.blt(self.draw_x -14, self.draw_y + 0 +self.y_adjust, 1, 81, 247, 6, 9, 0) #水
                pyxel.blt(self.draw_x +18, self.draw_y + 0 +self.y_adjust, 1, 81, 247, 6, 9, 0) #水
                #-----------------------------------------------------------
                pyxel.blt(self.draw_x - 9, self.draw_y + 3 +self.y_adjust, 1, 80, 240,  4,  6, 0) #台左側
                pyxel.blt(self.draw_x - 5, self.draw_y + 3 +self.y_adjust, 1, 80, 240, 16,  3, 0) #台中央1
                pyxel.blt(self.draw_x +11, self.draw_y + 3 +self.y_adjust, 1, 80, 240,  4,  3, 0) #台中央2
                pyxel.blt(self.draw_x +15, self.draw_y + 3 +self.y_adjust, 1, 80, 240,  4,  6, 0) #台右側
                #-----------------------------------------------------------
                pyxel.blt(self.draw_x + 2, self.draw_y - 7 +self.y_adjust, 1, 89, 246, 6, 10, 0) #札
                #-----------------------------------------------------------
                pyxel.blt(self.draw_x - 6, self.draw_y - 2 +self.y_adjust, 1, 88, 224, 7, 6, 0) #塩
                pyxel.blt(self.draw_x + 1, self.draw_y + 0 +self.y_adjust, 1, 88, 231, 8, 4, 0) #みそ
                pyxel.blt(self.draw_x +10, self.draw_y + 0 +self.y_adjust, 1, 88, 236, 7, 4, 0) #米
            if self.obj_no == 26: ##さざれ石
                pyxel.blt(self.draw_x + 1, self.draw_y -2, 1, 128, 168, 24, 24, 15)







    # def is_colliding_with(self, other):
    #     range_x = self.collision_width
    #     range_y = self.collision_height

    #     if self.position_x + range_x > other.position_x:
    #         if self.position_x < other.position_x + range_x:
    #             if self.position_y + range_y > other.position_y:
    #                 if self.position_y < other.position_y + range_y:
    #                     return True
    #     return False

    def is_colliding_with(self, other):
        range_x_self = self.collision_width
        range_y_self = self.collision_height
        range_x_other = self.collision_other_x
        range_y_other = self.collision_other_y

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

    def getReactionText(self, scene_no, scenario_no, branch_no, conversation_with, response_no, door_open_array):
        ###当該シーン・シナリオ配下でcharacter_noがプレイヤーconversation_withに話しかけられた場合の発話
        #----------------------------------------------------------- 
        ###シーン番号、シナリオ番号、返却テキスト番号（進行に合わせて返却のたびにカウントアップ、ただし質問中はそのまま）、質問中フラグ、返答結果番号
        self.scene_no = scene_no ### シーン番号
        self.scenario_no = scenario_no ### シナリオ番号
        self.branch_no = branch_no ### シナリオ分岐番号
        self.conversation_with = conversation_with ### 誰と会話中か
        #----------------------------------------------------------- 
        self.responce_no = response_no ### 返答結果番号
        self.door_open_array = door_open_array
        self.panning_switch = False

        ### ◆シーン１　ー　シナリオ１
        if self.obj_no == 0: ### 歩行者用信号の付いた電柱
            return ["歩行者用信号だ。","押しボタンは　機能してない。","押すと、　カスカスと　乾いた音がする。"]
        elif self.obj_no == 1: ### バス停
            return ["バス停だ。","停留所名に　「とかくし」　とある。","所々錆びており　随分古く見える。","朝夕に各２本　日中に１本　夜は１本で運行しているようだ。"]
        elif self.obj_no == 2: ### 立て看板
            return ["”とかくし海浜公園/第54回夏まつり (8/6-8/8)","＊花火(第２夜)…有料観覧席：実行委員迄ご連絡下さい。","＊期間中は公共交通機関の混雑が見込まれます。”"]
        elif self.obj_no == 3: ### 猫
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 0) and (self.branch_no == 0)):
                if self.rtn_txt_no == 0:
                    return ["まずは彼女から　話を聞くといいよ。"]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 0) and (self.branch_no == 1)):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce()
                    return ["やあ。　ぼくはクロエ。","おはなし　終わった？","",
                            "ここから　出たいんでしょう？","聞こえてたよ。",""]
                if self.rtn_txt_no == 1:
                    self.rtn_txt_no += 1
                    self.door_open_array[1] = True ## 月の戸を開放する。
                    self.cancelFlgWaitingResponce()
                    return ["ここから繋がってるのは　１つだけだよ。","ちょっと待ってて。　「繋げて」あげる。","",
                            "・・・　・・・　・・・　・・・","","",
                            "ＯＫ。"]
                if self.rtn_txt_no == 2:
                    self.rtn_txt_no = 0            ## 返却テキスト番号の初期化
                    self.panning_switch = True     ## panningのスイッチを入れる。
                    self.branch_no += 1            ## branch_noのup
                    self.cancelFlgWaitingResponce()
                    return ["戸を開いたよ。","","ま、頑張ってみなよ。"]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 0) and (self.branch_no == 2)):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["ここのこと、　すこしだけ　教えてあげる。","","",
                            "ここは、　神様の暇つぶしの庭　なんだ。","君たちは連れてこられたんだ。","",
                            "戸の先には、 部屋の住人がいる。","君たちみたいに　迷い込んできた人さ。","",
                            "この海岸も　「部屋」だよ。","ここは　僕の部屋。",""]
                if self.rtn_txt_no == 1:
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce()
                    return ["ちなみに。","僕が開けられるのは、　鍵のかかってない　部屋だけだよ。","",
                            "開かれてない戸は、　僕の方からは　開けられないんだ。","今開けられるのは、　あの扉だけだね。","",
                            "戸の先かい？","付き合いの長い　友人がいるんだ。","彼女、　どれだけ誘っても　ずうっと　引きこもりでね。"]
                if self.rtn_txt_no == 2:
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["なぜってそりゃあ・・・。","","おもしろいからさ。",
                            "やだなあ、　そんなに眉間に　シワ寄せないでよ。","ほら、　歯もしまって。","こわいよ。"]
                if self.rtn_txt_no == 3:
                    return ["良い報告、　期待してるよ。","",""]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 1) and (self.branch_no >= 0)):
                if self.rtn_txt_no == 0:
                    return ["やあ。","ミチには　会えたかい？","",
                            "扉は開けたままだからさ、","たまに　彼女と話をしてやってくれないかな。","気丈に振る舞ってるけど、　ああ見えて　寂しがってるんだ。"]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 2) and (self.branch_no >= 0)):
                if self.rtn_txt_no == 0:
                    return ["次は　どんな相手だった？","","",
                            "火の玉？","からかってないよね？","火に　包まれたこども・・・。",
                            "すこし、　気をつけたほうがいいかも。","火って　怒りの象徴だから。","こどもの無垢さって　激情に　転じやすいしね。"]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 3) and (self.branch_no >= 0)):
                if self.rtn_txt_no == 0:
                    return ["おつかれさま。","海にでも　潜ったの？","びしょぬれだよ。",
                            "水びたしの部屋の　クラゲ　か・・・。","クラゲになるなんて、　すっごい変化だね。","余程のストレスに　晒されてたのかな・・・。"]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 4) and (self.branch_no >= 0)):
                if self.rtn_txt_no == 0:
                    return ["耳のうしろ、　葉っぱ　付いてるよ。","","",
                            "文明嫌いの　熱血バッタがいた？","ほんとさあ、　今作ってないよね？","",
                            "虫に変化・・・　過去見た限りだと、　疎外感を抱えた人　が多いかな。","",""]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 5) and (self.branch_no >= 0)):
                if self.rtn_txt_no == 0:
                    return ["なんだか　キラキラしてる？","それって　砂？","",
                            "後悔を吐き続ける　でっかいロボットねえ・・・。","きみのキャラクターとは　関係なさそうだね。","あるいは君にも　そんな一面がある　ってことかな？",
                            "前に言ったように、　戸が繋がる相手同士は","何らかのつながりを持つんだ。","親交のあった者、　同じ願いを持つ者、　内に秘めた内面を現した者・・・。",
                            "きみって案外　ナイーブなやつなのかもね。","そんなふうには　見えないのになあ。　あ、いい意味だよ？",""]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 6) and (self.branch_no >= 0)):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["やあ。","今度はどこへ　いったのかな。","・・・墓？",
                            "ああ・・・・・・。","知ってる。　リキは　ぼくの友人でね。","僕らの「この世界」の管理者　の部下さ。",
                            "ってことは・・・、　見たんだろう？","そんな顔　してるんだもの。","眉間、　シワシワじゃん。",
                            "この世界ではね、　肉体的な死を迎えると、　魂ごと一度消滅するんだ。","でも、どちらも再生される。　カミサマによってね。","でも、　それ以後は　この世界に縛られちゃうんだ。",
                            "元の肉体と　魂のリンクが　プッツリ失われて、","元の世界の肉体に　戻れなくなるのさ。",""]
                if self.rtn_txt_no == 1:
                    self.rtn_txt_no += 1
                    return ["もう、　気づいてるんでしょ？","元の世界へ戻るには、　「現実世界で手放しかけてる願い」と、","「きみにとって大切なひと」　２つを思い出す必要がある。",
                            "ふたつを　「この世界」の管理者に　伝えれば、","晴れて開放される　ってわけ。自由だ。","でも・・・",
                            "何人か見てきたけど、","一度　死を経験しちゃうと、","戻れなくなる　みたいなんだ。",
                            "そういうわけで、　僕には、　もう　無理なんだ。","元の世界へは、　もう　戻れない。",""]
                if self.rtn_txt_no == 2:
                    return ["きみから　聞く限りだと、　戻れる可能性があるのは・・・","ミチ以外に、　あと　２人だ。","",
                            "ボボ　って火の玉の子と、　ジュリ　ってクラゲのおねーさんだね。","あとのふたりは・・・　たぶん、もう。",""]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 7) and (self.branch_no == 0)):
                if self.rtn_txt_no == 0:
                    return ["さて・・・７つ目のトビラだね。","",""]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 7) and (self.branch_no == 1)):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["おかえり。","わ、　なんだか君、　フワモコだよ。","あったかいところ　居たの？",
                            "犬？　仲間がいたの？","・・・あ、　そういうこと。","てっきり　君みたいなのが　いたのかと。",
                            "主人を待つ犬、　か・・・。","","・・・・・・。",
                            "ねえ、　その犬ってさ、","きっと、　犬じゃないよ。","",
                            "その部屋の　持ち主だね。","部屋が部屋らしく　形を保ってて、誰もいないんでしょ？","間違いないよ。"]
                if self.rtn_txt_no == 1:
                    return ["７つ目の扉、　もう一度　行くべきだよ。","カナちゃん　何か　知ってるかもなんでしょ？","関係していそうなら　尚更ね。",
                            "君たち、　同時にここへ　迷い込んでたんだ。","きっと君たちには　現実世界の　繋がりがある。","思い出せる何かが　７つ目の戸の先には　あるはずだよ。"]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 7) and (self.branch_no == 2)):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["犬の彼、","もう　ブルー　と呼ぶけど・・・","きっと　元の自分には　戻れないはずだ。",
                            "彼が　思い出すべき相手は、　ブルー・・・飼い犬だったんだろう。","でも　部屋の中でひとり命を落として　現実へは戻れなくなって・・・","その後自身を　愛犬へ変じたんだと思う。",
                            "部屋の主のまま　ブルーになって、","人としての自我を　失ってしまったんじゃないかな・・・。",""]
                if self.rtn_txt_no == 1:
                    self.rtn_txt_no = 0
                    self.setFlgWaitingResponce()
                    self.branch_no += 1
                    return ["カナちゃん。","彼女、部屋を知ってたんだよね？","彼女はおそらく　ブルーの縁者だ。　飼い主ね。",
                            "自宅を　見知っているなら・・・","血縁や友人　だったりするのかな。",""]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 7) and (self.branch_no == 3)):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["ここは　過去現在未来の順序が　ないからね。","カナちゃん主観で１０年前、　お兄さんはここを訪れた。","そして　戻れなかったんだろう。",
                            "カナちゃんの話が確かなら、　ある事実がわかる。","「戻れなくても、元の世界で　'僕'は　生を継続している」。","",
                            "でも、　失う。","この世界を　抜け出すための記憶を。　大切な思いを。","愛や　執着や　拠り所といった、　日々を輝かせる気持ちを。",
                            "僕はもう、変わり「終わっている」。","いまこうして　君と話す僕は、","置き去りにされた　思いそのもの　ってことだ・・・。"]
                if self.rtn_txt_no == 1:
                    return ["じつは、　そんなに悲観してないんだ。","ここには、　ミチがいるからね。","・・・ぼくは、　彼女に　合うことができた。"]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 8) and (self.branch_no >= 0)):
                if self.rtn_txt_no == 0:
                    return ["やあ。　みんなと　お話し終わった？","","",
                            "ありがとう。","きっと　ミチを現実世界へ　戻してみせるよ。","",
                            "ぼく自身は　どうなるか　わからないけど、","ミチは　なんだか張り切ってるみたい。",""]
     




        elif self.obj_no == 4: ### 木の幹１
            if (self.scene_no == C_SCENE_WOOD) :
                return ["やや小振りな枝に　葉が茂っている。",""]
        elif self.obj_no == 5: ### 木の幹２
            if (self.scene_no == C_SCENE_WOOD) :
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["どこからか　風が吹いている。","葉と葉が擦れる　心地よい音がする。","",
                            "足元から　葉を一枚　持っていくことにした。","","",
                            "【きれいな葉】を手に入れた。","",""]
                # if self.rtn_txt_no == 1のとき、ゲーム本体側でアイテム取得の処理を行い、 rtn_txt_no += 1 される。   
                if self.rtn_txt_no == 2:
                    return ["風に葉がさざめき、　心地よい音がする。","",""]
        elif self.obj_no == 6: ### ストーブ&ヤカン
            if (self.scene_no == C_SCENE_SUN):
                if self.rtn_txt_no >= 0:
                    return ["ヤカンから　湯気が　立ち上っている。"]
        elif self.obj_no == 7: ### 木の幹3
            if (self.scene_no == C_SCENE_MOON):
                if self.rtn_txt_no >= 0:
                    return ["大きな樹が　佇んでいる。"]
        elif self.obj_no == 8: ### 木の幹4
            if (self.scene_no == C_SCENE_MOON):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["樹には　大きな「うろ」がある。","中に、　小さなリスが　住み着いているようだ。","",
                            "リスは　こちらに　興味を示さず、","物陰へ　戻っていった。",""]
                if self.rtn_txt_no == 1:
                    self.rtn_txt_no = 0
                    return ["（リスの興味を　引けるものが　ないだろうか・・・）",""]  
        elif self.obj_no == 10: ### ボボ
            if (self.scene_no == C_SCENE_FIRE) :
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["アンタ　だれ？","あ。　オレ、ボボ。　兄ちゃんみたいなヒト？　珍しいよ。","ここに来るやつはさあ、　みんなオレ見ると　逃げるんだぜ。",
                            "傷ついちゃうよね。","オレだって　好きで火の玉　してないってのにさ。",""]
                if self.rtn_txt_no == 1:
                    return ["なあ　なあ。","ここに　何しに　来たんだ？",""]
        elif self.obj_no == 11: ### 太陽の本
            if (self.scene_no == C_SCENE_SUN) :
                if self.scenario_no == 7:
                    if self.branch_no < 6:
                        if self.rtn_txt_no == 0:
                            return ["ページが　ピッタリと　貼り付いて、　開けることが出来ない。",""]
                if self.scenario_no >= 7:
                    if self.branch_no >= 6:
                        if self.rtn_txt_no == 0:
                            self.rtn_txt_no += 1
                            return ["【手繰る糸】","","",
                                    "エミリーは　孤児院の出身　である。","現在は　特待生用の寮で　学生生活を　送っているが、","ふとした時、　孤児院が頭をよぎる。",
                                    "「あの頃は　ジェイコブと　よく遊んだっけ。」","「泣いてばかりの私を　励ましてくれた。」","「赤いマフラーを二人で巻いて、　雪遊びしたっけ。」",
                                    "猛烈な寒波が　街を襲った　12月30日。","エミリーは　ジェイコブに似た人物を　街で見かける。","ジェイコブらしき影は、　あのマフラーをしていた。",
                                    "エミリーは　彼を追う。","マーケット、　古着屋の角、　古書店、　裏路地へと消える。","エミリーは　赤いマフラーを　必死に追った。",
                                    "ジェイコブを追うと、　周囲に異変が起きていた。","ひとつ、　またひとつと　街から色が失われるのだ。","街を進むごとに、　雪はますます勢いを増していく・・・。"]
                        if self.rtn_txt_no == 1:
                            self.rtn_txt_no += 1
                            return ["（もう少し　先を読んでみた。）","","",
                                    "雪の降りしきる街、　暗い路地裏で　エミリーは一人佇んでいる。","手には、　真っ赤なマフラーを握りしめていた。","周囲の風景からは　すっかり色が抜け落ちていた。",
                                    "「だめ・・・、　何も覚えてない。」","「ともかく　今は暖を取らないと・・・。」","かじかむ手で　マフラーを首に巻き、　歩きはじめた。",
                                    "辺りは静まり返り、　雪を踏みしめる足音だけが響く。","進めば進むほど、　街は異様な静けさを増す。","ーー突然、　背後の小さな物音に　エミリーは息をのんだ。",
                                    "ゆっくりと振り返ると、","そこには、　白い犬が座っていた。",""]
                        if self.rtn_txt_no == 2:
                            self.rtn_txt_no += 1
                            return ["犬は　エミリーの目を　じっと見つめる。","「こんにちは」","なんと　犬は人の言葉で　話しかけてきた。",
                                    "驚きはあったが、　おもわず　安堵の息をつく。","もう、　この際なんでもいい。","会話ができれば、　この奇妙な世界でも　不安が和らぐ。",
                                    "（閉ざされた市役所玄関前、　一人と一匹は　暫く話し込む。）","",""]
                        if self.rtn_txt_no == 3:
                            self.rtn_txt_no += 1
                            return ["（もう少し　先を読んでみた。）","","",
                                    "犬は名を持たなかった。　しかしこれでは呼びづらい。","「Blue Moon Cafe」という看板を見やり、","エミリーは彼に　「ブルー」　と名付けた。",
                                    "降りしきる雪に加え、　白いモヤが　街を覆い始めていた。","",""]
                        if self.rtn_txt_no == 4:
                            self.rtn_txt_no += 1
                            ###txt_no:3遷移後、ゲーム本体側でオブジェクト操作を経て、rtn_txt_noをリセットする。
                            return ["（物語の　終章付近を読んでみた。）","","",
                                    "（エミリーが　犬を抱いて　泣いている・・・。）","","",
                                    "（本を閉じた。）","",""]
                        if self.rtn_txt_no == 5:
                            return ["本は　固く　閉ざされている。","",""]
        elif self.obj_no == 12: ### 本棚
            if (self.scene_no == C_SCENE_SUN) :
                if self.scenario_no == C_SCENE_SUN:
                    if self.branch_no < 5:
                        if self.rtn_txt_no == 0:
                            self.branch_no = 6
                            self.rtn_txt_no += 1
                            return ["アイアン製の　ブックスタンドがある。","この部屋の主は　読書家のようだ。","",
                                    "あらゆる　ジャンルの本が　並んでいる。","","",
                                    "・・・？","ぎゅうぎゅうに　詰まった本の隙間に　メモが挟まっている。","",
                                    "【ジェイコブへのメモ】を手に入れた。","",""]
                if self.scenario_no >= C_SCENE_SUN:
                    if self.branch_no >= 7:
                        if self.rtn_txt_no == 0:
                            self.rtn_txt_no += 1
                            return ["料理本、　ビジネス書、　児童書、　画集が乱雑に置かれている。","下段は犬用の本棚みたいだ。","「愛犬と過ごす休日100景」「グルーミング完全攻略の道」"]
        elif self.obj_no == 13: ### 犬（ブルー）
            if (self.scene_no == C_SCENE_SUN):
                if self.rtn_txt_no == 0:
                    return ["いらっしゃい。","ここは　俺と　ゴシュジンの家だよ。","ゴシュジンは　まだ帰ってこないんだ。"]
        elif self.obj_no == 14: ### 積んだ本
            if (self.scene_no == C_SCENE_SUN):
                if self.rtn_txt_no == 0:
                    return ["本が積んである。","ページには　ところどころ　付箋が挟んである。",""]
        elif self.obj_no == 16: ### 柱
            if (self.scene_no == C_SCENE_SOIL):
                if self.rtn_txt_no == 0:
                    return ["大理石の　柱だ。","表面が　ピカピカに　磨かれている。",""]
        elif self.obj_no == 17: ### 犬（黒）
            if (self.scene_no == C_SCENE_SOIL):
                if self.rtn_txt_no == 0:
                    return ["（嬉しそうに　尻尾を振っている。）","",""]
        elif self.obj_no == 18: ### 墓 1
            if (self.scene_no == C_SCENE_SOIL):
                if self.rtn_txt_no == 0:
                    return ["クロード・サマー、　ここに眠る。",""]
        elif self.obj_no == 19: ### 墓 ２
            if (self.scene_no == C_SCENE_SOIL):
                if self.rtn_txt_no == 0:
                    return ["モミジ・コマガタ、　ここに眠る。",""]
        elif self.obj_no == 20: ### 墓 3
            if (self.scene_no == C_SCENE_SOIL):
                if self.rtn_txt_no == 0:
                    return ["ハオ・ジェン、　ここに眠る。",""]
        elif self.obj_no == 21: ### 墓 4
            if (self.scene_no == C_SCENE_SOIL):
                if self.rtn_txt_no == 0:
                    return ["フェデリカ・ロマーノ、　ここに眠る。",""]
        elif self.obj_no == 22: ### 宝石
            if (self.scene_no == C_SCENE_GOLD) :
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["あら。","どこから　入り込んだの？","","まあいいわ。　ちょうど退屈してたのよ。","あなた　なにか面白いもの　持ってない？",""]
                if self.rtn_txt_no == 1:
                    return ["見ての通り　ここって何もないでしょ。","暇なのよ。",""]
        elif self.obj_no == 23: ### 剣
            if (self.scene_no == C_SCENE_GOLD) :
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["ん？","だれだ？","","ここは時折　砂塵が吹き荒ぶ！","命惜しくば　早々に　立ち去るがよい！",""]
                if self.rtn_txt_no == 1:
                    return ["言っておくが　あの宝石・・・　なんの価値もないぞ。","あいつは、　常に騒がしいだけだ。",""]
        elif self.obj_no == 24: ###灯籠
            if (self.scene_no == C_SCENE_MOON) :
                if self.rtn_txt_no == 0:
                    return ["光が　揺らめいている。"]
        elif self.obj_no == 25: ###神棚
            if (self.scene_no == C_SCENE_HOME) :
                if self.rtn_txt_no == 0:
                    return ["塀の上に・・・　これ神棚か？","なんで　こんなところに？",""] 
            if (self.scene_no == C_SCENE_MOON) :
                if self.rtn_txt_no == 0:
                    return ["空中に　神棚が浮いている・・・。","","","榊、水、酒、塩、味噌、米が供えられている。",""]
            if (self.scene_no == C_SCENE_FIRE) :
                if self.rtn_txt_no == 0:
                    return ["ここにも　神棚がある。","榊の葉は　ピンと張っている。",""]
            if (self.scene_no == C_SCENE_WATER) :
                if self.rtn_txt_no == 0:
                    return ["神棚がある。","どこにも　水滴はかかっていない。","榊の葉が、　水の音に合わせて揺れている。"]
            if (self.scene_no == C_SCENE_WOOD) :
                if self.rtn_txt_no == 0:
                    return ["当然のように　神棚がある。","風を受け、　榊がわずかに揺れている。",""]
            if (self.scene_no == C_SCENE_GOLD) :
                if self.rtn_txt_no == 0:
                    return ["神棚だ。","砂を弾いているのか、　チリひとつ落ちてない。",""]
            if (self.scene_no == C_SCENE_SOIL) :
                if self.rtn_txt_no == 0:
                    return ["神棚が　光を受けている。","心なしか　周辺の空気が　和らいで見える。",""]
            if (self.scene_no == C_SCENE_SUN) :
                if self.rtn_txt_no == 0:
                    return ["神棚だ。","屋内にある　ってだけで　しっくり感じるな。",""]
        elif self.obj_no == 26: ###さざれ石
            if (self.scene_no == C_SCENE_FIRE) :
                if self.rtn_txt_no == 0:
                    return ["苔に覆われた　大きな石が　鎮座している。",""]
                
        elif self.obj_no == 27: ### 水ステージ探しもの用（ハズレ）
            if (self.scene_no == C_SCENE_WATER) :
                if self.rtn_txt_no == 0:
                    return ["ほんのりと冷たい水に　手を差し込み、　水底をさらってみた。","","",
                            "・・・　・・・　・・・。","","何も　見つからない。"]
        elif self.obj_no == 28: ### 水ステージ探しもの用（ハズレ：体力減）
            if (self.scene_no == C_SCENE_WATER) :
                if self.rtn_txt_no == 0:
                    return ["ほんのりと冷たい水に　手を差し込み、　水底をさらってみた。","","",
                            "・・・　・・・　・・・。","！！！！！！","・・・指先を　切ってしまった。"]
        elif self.obj_no == 29: ### 水ステージ探しもの用（クラゲずかん）
            if (self.scene_no == C_SCENE_WATER) :
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["ほんのりと冷たい水に　手を差し込み、　水底をさらってみた。","","",
                            "・・・　・・・　・・・。","","なにかのカドが　手に当たった！"]
                if self.rtn_txt_no == 2:
                    return ["「クラゲずかん」が　沈んでいた場所だ。","",""]
        elif self.obj_no == 30: ### 水ステージ探しもの用（古い手鏡）
            if (self.scene_no == C_SCENE_WATER) :
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["ほんのりと冷たい水に　手を差し込み、　水底をさらってみた。","","",
                            "・・・　・・・　・・・。","","なにかが　手に当たった！"]
                if self.rtn_txt_no == 2:
                    return ["「古い手鏡」が　沈んでいた場所だ。","",""]
        elif self.obj_no == 31: ### 水ステージ探しもの用（サファイアのイヤリング）
            if (self.scene_no == C_SCENE_WATER) :
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["ほんのりと冷たい水に　手を差し込み、　水底をさらってみた。","","",
                            "・・・　・・・　・・・。","","なにか　小さなものが　手に当たった！"]
                if self.rtn_txt_no == 2:
                    return ["「サファイアのイヤリング」が　沈んでいた場所だ。","",""]
        elif self.obj_no == 32: ### 水ステージ探しもの用（小さなガラス瓶）
            if (self.scene_no == C_SCENE_WATER) :
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["ほんのりと冷たい水に　手を差し込み、　水底をさらってみた。","","",
                            "・・・　・・・　・・・。","","なにか　つるりとしたものが　手に当たった！"]
                if self.rtn_txt_no == 2:
                    return ["「小さなガラス瓶」が　沈んでいた場所だ。","",""]
        elif self.obj_no == 33: ### 水ステージ食べ物（甘い水の実）
            if (self.scene_no == C_SCENE_WATER) :
                if self.rtn_txt_switch == False :
                    return ["木の幹に　甘い香りを放つ　水滴が実っている。","","",
                            "ひとつ　持っていくことにした。","","",
                            "【甘い水の実】を　手に入れた。","",""]
                if self.rtn_txt_switch == True :
                    return ["これ以上は　必要ないだろう。","",""]
