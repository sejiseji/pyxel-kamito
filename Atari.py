import pyxel
import math as Math
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
#
#

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
        ###表示順序の基準になる、Door足元の座標
        self.position_x = self.x + C_ATARI_WIDTH/2
        self.position_y = self.y + C_ATARI_HEIGHT

        self.flg_reaction = False
        self.is_playing = False

        self.obj_no = obj

        ###シーンごとに表示するテキストを変えるための変数
        self.scene_no = scene # 0:home 1:door1 2:door2 3:door3 4:door4 5:door5 6:door6 7:door7 8:ending

        self.is_visible = is_visible

        self.draw_x = 0
        self.draw_y = 0

    def update(self):
        ###表示順序の基準となる、足元の座標情報を更新する
        self.position_x = self.x + C_ATARI_WIDTH/2
        self.position_y = self.y + C_ATARI_HEIGHT

    def draw(self):
        if self.is_visible:
            self.frames01 = Math.floor(pyxel.frame_count/8) % 7
            self.frames02 = Math.floor(pyxel.frame_count/5) % 12
            self.frames03 = Math.floor((pyxel.frame_count + 11)/5) % 12
            self.frames04 = Math.floor((pyxel.frame_count + 2)/5) % 12
            
            pyxel.blt(self.draw_x,    self.draw_y +4,  2, 160, 0 + self.frames01 * 16, 16, 16, 0)

    def is_colliding_with(self, other):
        range_x = self.width
        range_y = C_PX_AROUND_ATARI

        if self.position_x + range_x > other.position_x:
            if self.position_x < other.position_x + range_x:
                if self.position_y + range_y > other.position_y:
                    if self.position_y < other.position_y + range_y:
                        return True
        return False

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
        if (self.scene_no == C_SCENE_HOME):
            if self.obj_no == 0: ### 歩行者用信号の付いた電柱
                return ["歩行者用信号だ。","押しボタンは機能してない。"]
            elif self.obj_no == 1: ### バス停
                return ["バス停だ。","停留所名に「とかくし」とある。","所々錆びており、随分古く見える。","朝夕に各２本、日中に１本、夜は１本で運行しているようだ。"]
            elif self.obj_no == 2: ### 立て看板
                return ["”とかくし海浜公園/第54回夏まつり (8/6-8/8)","＊花火(第２夜)…有料観覧席：実行委員迄ご連絡下さい。","＊期間中は公共交通機関の混雑が見込まれます。”"]
            elif self.obj_no == 3: ### 猫
                if ((self.scenario_no == 0) and (self.branch_no == 0)):
                    if self.rtn_txt_no == 0:
                        self.rtn_txt_no += 1
                        return ["やあ。","","","ここが何処だか、今回は覚えてる？","",""]
                    if self.rtn_txt_no == 1:
                        ###月の戸を開放する。
                        self.door_open_array[1] = True
                        self.rtn_txt_no += 1
                        return ["今度は助けられるといいね。","",""]
                    if self.rtn_txt_no == 2:
                        ###panningを変更する。
                        self.panning_switch = True
                        return ["最初の戸を開いておいたよ。","","頑張ってね。"]
        if (self.scene_no == C_SCENE_WOOD) :
            if self.obj_no == 4: ### 木の幹１
                return ["やや小振りな枝に葉が茂っている。",""]
            elif self.obj_no == 5: ### 木の幹２
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["どこからか風が吹いている。","揺れた葉が擦れ、心地よい音がする。","","なんとなく、足元にある葉から一枚を持っていくことにした。","","","【きれいな葉】を手に入れた。","",""]
                # if self.rtn_txt_no == 1のとき、ゲーム本体側でアイテムを取得の処理を行い、 rtn_txt_no += 1 される。   
                if self.rtn_txt_no == 2:
                    return ["風に葉がさざめき、心地よい音がする。","",""]
