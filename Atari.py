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
# 6 : ストーブ&ヤカン
# 7 : girls
# 8 : 木の幹3
# 9 : 木の幹4
#10 : ボウボウ



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

        ###シーンごとに表示するテキストを変えるための変数
        self.scene_no = scene # 0:home 1:door1 2:door2 3:door3 4:door4 5:door5 6:door6 7:door7 8:ending
        self.scenario_no = 0
        self.branch_no = 0
        self.conversation_with = 0
        self.responce_no = 0
        self.rtn_txt_no = 0
        self.face_disp = True

        self.is_visible = is_visible

        self.draw_x = 0
        self.draw_y = 0

        self.flg_waiting_responce = False

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
            if Math.floor(pyxel.frame_count/8) % 7 != 6:
                pyxel.blt(self.draw_x,    self.draw_y +4,  2, 160, 0 + self.frames01 * 16, 16, 16, 0)

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
        range_x_other = 8
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
        self.panning_switch = False

        ### ◆シーン１　ー　シナリオ１
        if self.obj_no == 0: ### 歩行者用信号の付いた電柱
            return ["歩行者用信号だ。","押しボタンは機能してない。"]
        elif self.obj_no == 1: ### バス停
            return ["バス停だ。","停留所名に「とかくし」とある。","所々錆びており　随分古く見える。","朝夕に各２本　日中に１本　夜は１本で運行しているようだ。"]
        elif self.obj_no == 2: ### 立て看板
            return ["”とかくし海浜公園/第54回夏まつり (8/6-8/8)","＊花火(第２夜)…有料観覧席：実行委員迄ご連絡下さい。","＊期間中は公共交通機関の混雑が見込まれます。”"]
        elif self.obj_no == 3: ### 猫
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 0) and (self.branch_no == 0)):
                if self.rtn_txt_no == 0:
                    return ["まずは彼女から話を聞くといいよ。"]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 0) and (self.branch_no == 1)):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce()
                    return ["ぼくはクロエ。ここで扉の管理をしてる。","おはなし終わった？","",
                            "他の人の扉を探してるんでしょ？","聞こえてたよ。",""]
                if self.rtn_txt_no == 1:
                    self.rtn_txt_no += 1
                    self.door_open_array[1] = True ## 月の戸を開放する。
                    self.cancelFlgWaitingResponce()
                    return ["いいよ。","ちょっと待ってて。","",
                            "・・・　・・・　・・・　・・・","","",
                            "ＯＫ。"]
                if self.rtn_txt_no == 2:
                    self.rtn_txt_no = 0            ## 返却テキスト番号の初期化
                    self.panning_switch = True     ## panningを変更する。
                    self.branch_no += 1            ## branch_noのup
                    self.cancelFlgWaitingResponce()
                    return ["最初の戸を開いておいたよ。","","頑張ってね。"]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no == 0) and (self.branch_no == 2)):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["ここのこと、すこしだけ教えてあげる。","","",
                            "水域に集まるのは、打ち捨てられた願いなんだ。","基本的にはね。","",
                            "戸の先で願いはあらゆる形を成すんだけど・・・","特に強い願いは、願う者の形を得るんだ。","もちろん、中には歪んじゃう人もいる。",
                            "待ち人や、恋慕の相手、後悔に沈む人・・・とかかな。","負の感情に囚われて願った思いは、変な空間になるんだ。","",
                            "会話自体はできると思うけど、","なかにはややこしい相手も居るかもしれないよ。","気をつけてね。"]
                if self.rtn_txt_no == 1:
                    self.rtn_txt_no += 1
                    self.setFlgWaitingResponce()
                    return ["ちなみに。","僕が管理してるのは、鍵のかかってない部屋だけだよ。","",
                            "錠のかかった扉を開くことはできないんだ。","いま施錠されてないのは、さっき開いた月の扉だけだね。","",]
                if self.rtn_txt_no == 2:
                    self.rtn_txt_no += 1
                    self.cancelFlgWaitingResponce()
                    return ["なぜってそりゃあ・・・。","","おもしろいからさ。ニヒヒ・・・。",
                            "やだなあ、そんな顔しないでよ。","",""]
                if self.rtn_txt_no == 3:
                    return ["良い報告、期待してるよ。","",""]
            if ((self.scene_no == C_SCENE_HOME) and (self.scenario_no >= 1)):
                return ["やあ。","","","自分の願い、思い出せたのかな？","",""]
        elif self.obj_no == 8: ### 木の幹3
            if (self.scene_no == C_SCENE_MOON):
                return ["大きな樹が佇んでいる。"]
        elif self.obj_no == 9: ### 木の幹4
            if (self.scene_no == C_SCENE_MOON):
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["大きなうろがある。","中を覗き込むと、小さなリスが住み着いているようだ。","",
                            "リスはじっとこちらを見ていたが途中で興味を失くし、","物陰へと戻っていった。",""]
                if self.rtn_txt_no == 1:
                    self.rtn_txt_no = 0
                    return ["リスの興味を引けるものが何かないだろうか・・・",""]    
        elif self.obj_no == 4: ### 木の幹１
            if (self.scene_no == C_SCENE_WOOD) :
                return ["やや小振りな枝に葉が茂っている。",""]
        elif self.obj_no == 5: ### 木の幹２
            if (self.scene_no == C_SCENE_WOOD) :
                if self.rtn_txt_no == 0:
                    self.rtn_txt_no += 1
                    return ["どこからか風が吹いている。","揺れた葉が擦れ、心地よい音がする。","","なんとなく、足元にある葉から一枚を持っていくことにした。","","","【きれいな葉】を手に入れた。","",""]
                # if self.rtn_txt_no == 1のとき、ゲーム本体側でアイテムを取得の処理を行い、 rtn_txt_no += 1 される。   
                if self.rtn_txt_no == 2:
                    return ["風に葉がさざめき、心地よい音がする。","",""]
        elif self.obj_no == 7: ### girls
            if (self.scene_no == C_SCENE_GOLD) :
                if self.rtn_txt_no == 0:
                    return ["あはははははは！くるくるーー！","","","おにーちゃんだーれ？？？","",""]
        elif self.obj_no == 6: ### ストーブ&ヤカン
            if (self.scene_no == C_SCENE_SUN) :
                if self.rtn_txt_no == 0:
                    return ["ストーブが暖かい。","ヤカンにはたっぷりのお湯が沸いている。",""]
        elif self.obj_no == 10: ### ボウボウ
            if (self.scene_no == C_SCENE_FIRE) :
                if self.rtn_txt_no == 0:
                    return ["お！","きいてるぞ！","扉の中の人を探してんだろ？","俺ぁボウボウってんだ！","よろしくな、あんちゃん！",""]
        
