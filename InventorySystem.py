import pyxel
from font.bdfrenderer import BDFRenderer

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

class Item:
    def __init__(self):
        self.item_dict = {
            'おにぎり': '艷やかな真っ白いおにぎり。おいしそうだ。',
            'まんじゅう': '白い薄皮に包まれたあんが透けて見える。',
            'クッキー': '真ん中にグミが埋め込まれており、花の形をしている。',
            'チョコレート': '星型のチョコレート。甘い香りがする。',
            'ぽんぽこペパロニピザ': '個包装されたピザ。ふざけた顔のたぬきマークがついている。裏側には「製造元：奥山パン株式会社」と書かれたシールが貼ってある。',
        }
        self.Valuable_dict = {
            '金のコイン': '気づくとポケットに入っていたコイン。金色に輝いている。',
            '囁く葉': '葉を模したブローチ。葉脈の部分には細かい文字が刻まれている。',
            '冷たい小瓶': '中で光が打ち上がっている。ガラスに触るとひんやりとして霜がつく。小さな蓋に耳を当てると、遠く喧騒が聞こえる。',
            '煤けた灰': '麻袋に詰めた灰。握りしめるとほんのりと温かい。目を閉じると光の川が見える。',
            '歌う花': '茎をくすぐると、花が歌い始める。歌詞は聞き取れないが、気持ちが落ち着く。',
            'きれいな葉' : '大きな木の根元に落ちていた。羽のように軽く、暗がりで葉脈が光って見える。'
        }
        self.thought_dict_WOLF = {
            'おにぎり': '梅干しが好きだな。あとツナマヨと肉味噌。海苔はしっとり派。',
            'まんじゅう': 'こしあんがいい。',
            'クッキー': 'グミが歯にくっつく。コーヒーもほしいところ。',
            'チョコレート': '甘いもんはちょっと苦手なんだよな。いや、美味いけど。',
            'ぽんぽこペパロニピザ': 'もっとくれ。',
            '金のコイン': '手に取ると必ず表面に砂粒がついてる。湧いて出てるみたいに…。',
            '囁く葉': '俺の名前も書いてある。文字が小さくて目がしょぼしょぼする。',
            '冷たい小瓶': 'あのとき、花火の音でかき消えた声があったはずなんだ。彼女はこちらを向いて、口が動いていたから…。',
            '煤けた灰': '夜、ずっと眺めてられるな。',
            '歌う花': '俺には知らない言葉でスロージャズ歌ってくれるんだけど、コイツ見た目からの決めつけが過ぎないか？',
            'きれいな葉': 'まるで工芸品みたいだな。触るとしっとりと濡れてる。',
        }
    
    def get_description(self, item_name):
        ###item_dictにアイテム名があれば、説明文を返す
        if item_name in self.item_dict:
            return self.item_dict[item_name]
        
    def get_valuable_description(self, valuable_name):
        ###Valuable_dictにアイテム名があれば、説明文を返す
        if valuable_name in self.Valuable_dict:
            return self.Valuable_dict[valuable_name]
    
    def get_allitem_nums(self):
        return len(self.item_dict)
    
    def get_allvaluable_nums(self):
        return len(self.Valuable_dict)


class InventorySystem:
    def __init__(self):
        self.items = {} ##アイテム名と個数の辞書型配列
        self.valuables = {} ##貴重品名と個数の辞書型配列
        self.items_and_valuables = {} ##アイテム名・貴重品名の辞書型配列合計
        self.selected_index = 0
        self.subwindow_open = False  # サブウィンドウが開いているかどうかのフラグ
        self.subwindow_selected_index = 0  # サブウィンドウ内の選択肢インデックス
        self.bdf1 = BDFRenderer("font/umplus_j10r.bdf")
        self.bdf2 = BDFRenderer("font/umplus_j12r.bdf")
        ###全アイテムのアイテム名と説明文を取得するためのインスタンス
        self.itemdict = Item()
        ###アイテム取得フラグ配列
        self.itemgetflgs = [False] * self.itemdict.get_allitem_nums()
        ###アイテム取得個数配列
        self.itemgetnums = [0] * self.itemdict.get_allitem_nums()
        ###貴重品取得フラグ配列
        self.valuablegetflgs = [False] * self.itemdict.get_allvaluable_nums()
        ###貴重品取得個数配列
        self.valuablegetnums = [0] * self.itemdict.get_allvaluable_nums()

    def update_items(self):
        self.items = {}
        for i, key in enumerate(self.itemdict.item_dict.keys()):
            if(self.itemgetflgs[i] == True):
                self.items[key] = self.itemgetnums[i]
    
    def update_valuables(self):
        self.valuables = {}
        for i, key in enumerate(self.itemdict.Valuable_dict.keys()):
            if(self.valuablegetflgs[i] == True):
                self.valuables[key] = self.valuablegetnums[i]
    
    def update_items_and_valuables(self):
        self.items_and_valuables = self.items.copy()
        self.items_and_valuables.update(self.valuables)

    def add_item(self, itemname):
        index = 0
        ###受け取ったアイテム名に対応する位置を探す
        for key in self.itemdict.item_dict.keys():
            if(key == itemname):
                break
            index += 1
        ###捕捉したインデックス位置のフラグを確認し、未取得なら取得フラグを立てる
        ###取得済みなら取得数を増やす
        if(self.itemgetflgs[index] == False):
            self.itemgetflgs[index] = True
            self.itemgetnums[index] += 1
        else:
            self.itemgetnums[index] += 1
        ###itemsを更新する
        self.update_items()
        ###items_and_valuablesを更新する
        self.update_items_and_valuables()

    def add_valuable(self, valuablename):
        index = 0
        ###受け取った貴重品名に対応する位置を探す
        for key in self.itemdict.Valuable_dict.keys():
            if(key == valuablename):
                break
            index += 1
        ###捕捉したインデックス位置のフラグを確認し、未取得なら取得フラグを立てる
        if(self.valuablegetflgs[index] == False):
            self.valuablegetflgs[index] = True
            self.valuablegetnums[index] += 1
        ###valuablesを更新する
        self.update_valuables()
        ###items_and_valuablesを更新する
        self.update_items_and_valuables()

    def subtract_item(self, itemname):
        index = 0
        ###受け取ったアイテム名に対応する位置を探す
        for key in self.itemdict.item_dict.keys():
            if(key == itemname):
                break
            index += 1
        ###捕捉したインデックス位置のフラグを確認し、取得済みなら取得数を減らす
        ###取得数が0になったら取得フラグを下ろす
        if(self.itemgetflgs[index] == True):
            self.itemgetnums[index] -= 1
            if(self.itemgetnums[index] == 0):
                self.itemgetflgs[index] = False
        ###itemsを更新する
        self.update_items()
        ###items_and_valuablesを更新する
        self.update_items_and_valuables()

    def subtract_valuable(self, valuablename):
        index = 0
        ###受け取った貴重品名に対応する位置を探す
        for key in self.itemdict.Valuable_dict.keys():
            if(key == valuablename):
                break
            index += 1
        ###捕捉したインデックス位置のフラグを確認し、取得済みなら取得数を減らす
        ###取得数が0になったら取得フラグを下ろす
        if(self.valuablegetflgs[index] == True):
            self.valuablegetnums[index] -= 1
            if(self.valuablegetnums[index] == 0):
                self.valuablegetflgs[index] = False
        ###valuablesを更新する
        self.update_valuables()
        ###items_and_valuablesを更新する
        self.update_items_and_valuables()

    def draw(self):
        ###アイテムの取得フラグ配列が１つでも立っていたら、アイテム名と個数を描画する。続けて、貴重品の取得フラグ配列が１つでも立っていたら、貴重品名を描画する
        x = 40
        y = 30
        if len(self.items_and_valuables)>0:
            ###items_and_valuablesをenumerateで回す
            for i, (key, value) in enumerate(self.items_and_valuables.items()):
                color = 7 if i == self.selected_index else 5
                if(self.items_and_valuables[key] > 0):
                    self.bdf1.draw_text(x, y, key, color)
                    ###アイテムの場合、個数を描画する
                    if key in self.items:
                        self.bdf1.draw_text(x + 120, y, str(value), color)
                    y += 12
        else:
            self.bdf1.draw_text(40, 30, "（何も持ってない）", 7)
        
    def drawSubWindow(self):
        # サブウィンドウの表示
        if self.subwindow_open:
            sw_x, sw_y = 243, 245  # サブウィンドウの位置
            pyxel.rect(sw_x, sw_y, 50, 40, 0)  # サブウィンドウの背景
            pyxel.rectb(sw_x, sw_y, 50, 40, 7)  # サブウィンドウの枠
            
            options = ['つかう', 'やめる']
            for i, option in enumerate(options):
                color = 7 if i == self.subwindow_selected_index else 5
                self.bdf1.draw_text(sw_x + 10, sw_y + 6 + i * 17, option, color)

    def execute_option(self):
        ###アイテムがなければ、何もしない
        if not self.items_and_valuables:
            print("No items to use.")
            return
        
        ###選択された選択肢に応じたアクションを実行
        selected_item_name = list(self.items_and_valuables.keys())[self.selected_index]
        if self.subwindow_selected_index == 0:  # つかう
            pyxel.play(3,10) #SE再生(アイテム使用)
            print("Used the item")
            ###アイテム（消耗品）の場合、個数を減らす（貴重品は使っても減らないようにする）
            if selected_item_name in self.items:
                self.subtract_item(selected_item_name)
                # selected_indexに該当するアイテムがなくなったらselected_indexを調整
                if self.selected_index >= len(self.items_and_valuables):
                    self.selected_index = len(self.items_and_valuables) - 1
        else:  # やめる
            pyxel.play(3,12) #SE再生(キャンセル)
            print("Canceled")

    def get_selected_description(self):
        ###items_and_valuablesの中で選択中のアイテム名をもとに、説明文を取得する
        if len(self.items_and_valuables)>0:
            selected_item_name = list(self.items_and_valuables.keys())[self.selected_index]
            ###itemの中に選択中のアイテム名があれば、説明文を返す
            if selected_item_name in self.itemdict.item_dict:
                return self.itemdict.get_description(selected_item_name)
            ###valuableの中に選択中のアイテム名があれば、説明文を返す
            elif selected_item_name in self.itemdict.Valuable_dict:
                return self.itemdict.get_valuable_description(selected_item_name)
        else:
            return ""

    def getThoughtOnMenu(self, scenario, branch, character_no):
        ###scenario, branch, character_noに応じた思考を返す
        if character_no == C_CHARA_WOLF:
            return [self.itemdict.thought_dict_WOLF[list(self.items_and_valuables.keys())[self.selected_index]]]
