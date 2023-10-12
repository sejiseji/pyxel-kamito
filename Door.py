import pyxel
import math as Math
from GameObject import GameObject

###戸
C_DOOR_WIDTH = 16 * 1
C_DOOR_HEIGHT = 16 * 3
C_DOOROPEN_SPEED = 2
C_PX_AROUND_ATARI = 6 #当たり判定用のy軸不可侵エリア幅


##########-----------------------------------------------------------------------
# ドア
class Door(GameObject):
    def __init__(self, x=0, y=0, roomnumber=0, scene=0):
        super().__init__(x,y)
        self.width = C_DOOR_WIDTH
        self.height = C_DOOR_HEIGHT
        ###開き状態はデフォルトではない
        self.is_opened = False
        self.is_opening = False
        ###閉じ状態をデフォルトとする
        self.is_closed = True
        self.is_closing = False
        ###開き幅
        self.open_width = 0 ##デフォルトでは閉じている
        ###表示順序の基準になる、Door足元の座標
        self.position_x = self.x + C_DOOR_WIDTH/2 + 4
        self.position_y = self.y + C_DOOR_HEIGHT

        self.flg_reaction = False
        self.is_playing = False

        self.room_no = roomnumber

        self.belong_scene = scene

    def update(self):
        ###closing状態で開き幅が0になったら、closingを終了し、closed状態を開始する
        if self.is_closing and (self.open_width == 0):
            self.is_closing = False
            self.is_closed = True
        ###opening状態で開き幅が16になったら、openingを終了し、opened状態を開始する
        if self.is_opening and (self.open_width == 16):
            self.is_opening = False
            self.is_opened = True
        ###openingフラグ下におけるopen動作
        if (self.is_opening) and (self.open_width < 16):
            self.open_width += 2
        ###closingフラグ下におけるclose動作
        if (self.is_closing) and (self.open_width > 0):
            self.open_width -= 2

        ###表示順序の基準となる、足元の座標情報を更新する
        self.position_x = self.x + C_DOOR_WIDTH/2 + 4
        self.position_y = self.y + C_DOOR_HEIGHT

    def draw(self):
        ###鳥居部分
        pyxel.blt(self.x -10, self.y -16, 2, 112, 0, 44, 64, 3)
        ###開いた領域部分
        if self.is_opening or self.is_opened or self.is_closing:
            pyxel.blt(self.x, self.y, 2, 40, 64, self.open_width, 48, 3)
        ###ドア部分
        pyxel.blt(self.x + self.open_width, self.y, 2, 56, 64, 24, 48, 3)

        ###重ね表示(暗闇に重ねる光)
        if self.is_opened:
            # self.frames01 = Math.floor(pyxel.frame_count / 10) % 15
            # self.frames02 = Math.floor((pyxel.frame_count + 3) / 10) % 15
            # self.frames03 = Math.floor((pyxel.frame_count +11) / 10) % 15
            # self.frames04 = Math.floor((pyxel.frame_count + 7) / 10) % 15
            # self.frames05 = Math.floor((pyxel.frame_count +12) / 10) % 15
            # self.frames06 = Math.floor((pyxel.frame_count + 9) / 10) % 15
            # self.frames07 = Math.floor((pyxel.frame_count + 2) / 10) % 15
            base_frame = Math.floor(pyxel.frame_count / 10)
            offsets = [0, 3, 11, 7, 12, 9, 2]
            self.frames01, self.frames02, self.frames03, self.frames04, self.frames05, self.frames06, self.frames07 = [(base_frame + offset) % 15 for offset in offsets]

            if self.room_no == 0: # 0:暗闇の戸
                pyxel.pal(7, 0)
            if self.room_no == 1: # 1:宵の戸
                pyxel.pal(7, 7)
            if self.room_no == 2: # 2:灯の戸
                pyxel.pal(7, 8)
            if self.room_no == 3: # 3:波紋の戸
                pyxel.pal(7, 12)
            if self.room_no == 4: # 4:刻時の戸
                pyxel.pal(7, 11)
            if self.room_no == 5: # 5:静寂の戸
                pyxel.pal(7, 10)
            if self.room_no == 6: # 6:記憶の戸
                pyxel.pal(7, 15)
            if self.room_no == 7: # 7:日輪の部屋
                pyxel.pal(7, 7)
            pyxel.blt(self.x + 5,  self.y + 4, 2, 88, self.frames01 * 5, 5, 5, 0)
            pyxel.blt(self.x + 9,  self.y +22, 2, 88, self.frames04 * 5, 5, 5, 0)
            pyxel.blt(self.x + 5,  self.y +40, 2, 88, self.frames07 * 5, 5, 5, 0)
            pyxel.pal()

            if self.room_no == 0: # 0:暗闇の戸
                pyxel.pal(7, 0)
            if self.room_no == 1: # 1:宵の戸
                pyxel.pal(7, 13)
            if self.room_no == 2: # 2:灯の戸
                pyxel.pal(7, 2)
            if self.room_no == 3: # 3:波紋の戸
                pyxel.pal(7, 5)
            if self.room_no == 4: # 4:刻時の戸
                pyxel.pal(7, 3)
            if self.room_no == 5: # 5:静寂の戸
                pyxel.pal(7, 9)
            if self.room_no == 6: # 6:記憶の戸
                pyxel.pal(7, 4)
            if self.room_no == 7: # 7:日輪の部屋
                pyxel.pal(7, 15)
            pyxel.blt(self.x +10,  self.y +10, 2, 88, self.frames02 * 5, 5, 5, 0)
            pyxel.blt(self.x + 4,  self.y +16, 2, 88, self.frames03 * 5, 5, 5, 0)
            pyxel.blt(self.x + 6,  self.y +28, 2, 88, self.frames05 * 5, 5, 5, 0)
            pyxel.blt(self.x +10,  self.y +34, 2, 88, self.frames06 * 5, 5, 5, 0)
            pyxel.pal()


    def openStart(self):
        ###閉鎖状態を終了してopen動作を開始する
        self.is_closed = False
        self.is_opening = True

    def closeStart(self):
        ###開放状態を終了してclose動作を開始する
        self.is_opened = False
        self.is_closing = True

    def is_colliding_with(self, other):
        range_x = self.width
        # range_y = C_DOOR_WIDTH + self.open_width
        range_y = C_PX_AROUND_ATARI

        if self.position_x + range_x > other.position_x:
            if self.position_x < other.position_x + range_x:
                if self.position_y + range_y > other.position_y:
                    if self.position_y < other.position_y + range_y:
                        return True
        return False

    # def getReactionText(self):
    def getReactionText(self, scene_no, scenario_no, branch_no, conversation_with, response_no):
        ###当該シーン・シナリオ配下でcharacter_noがプレイヤーconversation_withに話しかけられた場合の発話
        #----------------------------------------------------------- 
        ###シーン番号、シナリオ番号、返却テキスト番号（進行に合わせて返却のたびにカウントアップ、ただし質問中はそのまま）、質問中フラグ、返答結果番号
        self.scene_no = scene_no ### シーン番号
        self.scenario_no = scenario_no ### シナリオ番号
        self.branch_no = branch_no ### シナリオ分岐番号
        self.conversation_with = conversation_with ### 誰と会話中か
        #----------------------------------------------------------- 
        self.responce_no = response_no ### 返答結果番号

        if(self.room_no == 0):
            if(self.belong_scene == 0) :
                return ["何もない空間に障子戸がある。","中は真っ暗で何も見えない。"]
            else:
                return ["何もない空間に障子戸がある。","鴨居と敷居を繋ぐ薄い面が、波のように揺らいでいる。","暗闇の先から、波の打ち寄せる音が響いてくる…。"]
        if(self.room_no == 1): ## 月　：　宵の戸
            return ["何もない空間に障子戸がある。","鴨居と敷居を繋ぐ薄い面が、白く揺らいでいる。","暗闇の先に、一筋の光が差して見えた気がした。"]
        if(self.room_no == 2): ## 火　：　灯の戸
            return ["何もない空間に障子戸がある。","鴨居と敷居を繋ぐ薄い面が、紅く揺らいでいる。","暗闇の先で、幾つもの揺らめく光が流れた気がした。"]
        if(self.room_no == 3): ## 水　：　波紋の戸
            return ["何もない空間に障子戸がある。","鴨居と敷居を繋ぐ薄い面が、青く揺らいでいる。","暗闇の先で、水の滴る音が重なって聞こえた気がした。"]
        if(self.room_no == 4): ## 木　：　刻時の戸
            return ["何もない空間に障子戸がある。","鴨居と敷居を繋ぐ薄い面が、緑に揺らいでいる。","暗闇の先から、木の香りが風に乗って届いた気がした。"]
        if(self.room_no == 5): ## 金　：　静寂の戸
            return ["何もない空間に障子戸がある。","鴨居と敷居を繋ぐ薄い面が、輝き揺らいでいる。","暗闇の先から、冷気を纏う砂粒が吹き込んだ気がした。"]
        if(self.room_no == 6): ## 土　：　記憶の戸
            return ["何もない空間に障子戸がある。","鴨居と敷居を繋ぐ薄い面が、暗く揺らいでいる。","暗闇の先へ、体が引き摺り込まれるような気がした。"]
        if(self.room_no == 7): ## 日　：　日輪の戸
            return ["何もない空間に障子戸がある。","鴨居と敷居を繋ぐ薄い面が、霞んで揺らいでいる。","暗闇の先を、温かな光を含んだ霧が覆い隠している。"]