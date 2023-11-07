import pyxel
from GameObject import GameObject

###くらげ
C_JERRY_WIDTH = 16 * 2
C_JERRY_HEIGHT = 16 * 2 + 8
C_JERRY_SPEED = 2

##########-----------------------------------------------------------------------
# くらげ
class Jerry(GameObject):
    def __init__(self, x=0, y=0):
        super().__init__(x,y)
        self.width = C_JERRY_WIDTH
        self.height = C_JERRY_HEIGHT
        ###表示順序の基準になる、JERRY足元の座標
        self.position_x = self.x + C_JERRY_WIDTH/2
        self.position_y = self.y + C_JERRY_HEIGHT

        ###
        self.is_playing = False

        self.draw_x = 0
        self.draw_y = 0
        

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

    def is_colliding_with(self, other):
        range_x = self.width
        range_y = C_JERRY_WIDTH

        if self.x + range_x > other.x:
            if self.x < other.x + range_x:
                if self.y + range_y > other.y:
                    if self.y < other.y + range_y:
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

        ### ◆シーン１　ー　シナリオ１
        if((self.scene_no == 0) and (self.scenario_no == 0) and (self.branch_no == 0)):
            return ["クラゲのような生き物だ。","表面が透きとおっていて、触るとツヤツヤしている。"]
        
    # def getReactionText(self):
    #     return ["クラゲのような生き物だ。","表面が透きとおっていて、触るとツヤツヤしている。"]