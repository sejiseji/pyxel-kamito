import pyxel
from GameObject import GameObject

###くらげ
C_JERRY_WIDTH = 16 * 2
C_JERRY_HEIGHT = 16 * 2 + 8
C_JERRY_SPEED = 2

C_SCENE_WATER = 3

##########-----------------------------------------------------------------------
# くらげ
class Jerry(GameObject):
    def __init__(self, x=0, y=0, obj_no=0):
        super().__init__(x,y)
        self.width = C_JERRY_WIDTH
        self.height = C_JERRY_HEIGHT
        self.collision_width = C_JERRY_WIDTH
        self.collision_height = C_JERRY_HEIGHT
        ###表示順序の基準になる、JERRY足元の座標
        self.position_x = self.x + self.width/2
        self.position_y = self.y + self.height

        ###
        self.is_playing = False
        self.draw_x = 0
        self.draw_y = 0

        self.obj_no = obj_no

        self.panning_switch = False

        ###シーンごとに表示するテキストを変えるための変数
        self.scene_no = 3 # 0:home 1:door1 2:door2 3:door3 4:door4 5:door5 6:door6 7:door7 8:ending
        self.scenario_no = 3
        self.branch_no = 0
        self.conversation_with = 0
        self.responce_no = 0
        self.rtn_txt_no = 0
        self.face_disp = True
        self.name_disp = False
        self.door_open_array = list()

    def update(self):
        ###表示順序の基準となる、足元の座標情報を更新する
        self.position_x = self.x + C_JERRY_WIDTH/2
        self.position_y = self.y + C_JERRY_HEIGHT

    def draw(self):
        ###
        self.frame_count_wk = pyxel.frame_count
        self.animation_frame = self.frame_count_wk // 10 % 4  
        ###
        pyxel.blt(self.draw_x, self.draw_y, 1, 80, self.animation_frame * C_JERRY_HEIGHT, C_JERRY_WIDTH, C_JERRY_HEIGHT, 0)

    # def is_colliding_with(self, other):
    #     range_x = self.width
    #     range_y = C_JERRY_WIDTH

    #     if self.x + range_x > other.x:
    #         if self.x < other.x + range_x:
    #             if self.y + range_y > other.y:
    #                 if self.y < other.y + range_y:
    #                     return True
    #     return False

    def is_colliding_with(self, other):
        range_x_self = 16
        range_y_self = 8
        range_x_other = 16
        range_y_other = 8

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

        ### ◆シーン１　ー　シナリオ１
        if ((self.scene_no == C_SCENE_WATER) and (self.scenario_no == C_SCENE_WATER) and (self.branch_no == 0)):
            if self.rtn_txt_no == 0:
                self.rtn_txt_no += 1
                self.setFlgWaitingResponce()
                return ["・・・・・え？","だ　だれ・・・？　あなた達・・・。","",
                        "こんなところ　ほかにだれかいるわけ・・・。","え・・・　でも・・・　え？","",
                        "ううん、　だめ、　ちがう。","これは幻覚、　これも幻覚、　幻覚よ・・・・。"]
            if self.rtn_txt_no == 1:
                self.rtn_txt_no = 0
                self.setFlgWaitingResponce()
                self.branch_no += 1
                return ["ま、迷い込んだ？　ウソ、そんなこと・・・。", "","",
                        "だめだめだめだめ。　だいじょうぶ、　すぐ消える。","きっと。　すぐ。　すぐ消える。　大丈夫。","だいじょうぶ・・・・・・。"]
        if ((self.scene_no == C_SCENE_WATER) and (self.scenario_no == 3) and (self.branch_no == 1)):
            if self.rtn_txt_no == 0:
                self.rtn_txt_no += 1
                self.cancelFlgWaitingResponce()
                return ["と、扉なら　奥に　あるけど・・・。", "ど、どうせ、　あ　あかないよ！。","",
                        "いちども　開いたことなんか　ないんだから！","","",
                        "は、はやく　探さないと。。。","もう、　どこ・・・？","あ　あなたたち、　幻覚なら　早く　消えてよね！"]
            if self.rtn_txt_no == 1:
                self.setFlgWaitingResponce()
                self.branch_no += 1
                self.rtn_txt_no = 0
                return ["しつこい　幻覚ね・・・。", "ねえ　わ、私の幻覚ならさ　手伝ってよ。","私の手じゃ　探し回るのも　大変でさ・・・。"]
        if ((self.scene_no == C_SCENE_WATER) and (self.scenario_no == 3) and (self.branch_no == 2)):
            if self.rtn_txt_no == 0:
                self.cancelFlgWaitingResponce()
                return ["え？　このすがた？","いつから・・・？","・・・・・・。　どれぐらい　経ったんだろう・・・。",
                        "木が　見えるでしょ？　あの枝や幹に　なる実を食べたの。","ある日起きたら　触手がひとつ生えてて・・・。","だんだん増えて　水が冷たく　感じなくなったの・・・。"]
        if ((self.scene_no == C_SCENE_WATER) and (self.scenario_no == 3) and (self.branch_no == 3)):
            if self.rtn_txt_no == 0:
                self.cancelFlgWaitingResponce()
                return ["どこ　いっちゃったんだろう・・・。","",""]
        ### ◆シーン１　ー後続シナリオ
        if ((self.scene_no == C_SCENE_WATER) and (self.scenario_no >= 4) and (self.branch_no >= 0)):
            if self.rtn_txt_no == 0:
                self.cancelFlgWaitingResponce()
                return ["あっ　あ　","ここっこ　こんにちわ・・・","お手伝いできること　あれば　な、なんでも　言ってね。"]
