import pyxel

C_TITLE = "newgame"
###操作キャラクタ用固定パラメタ
C_PLAYER_WIDTH = 16
C_PLAYER_HEIGHT = 48
C_PLAYER_MOVE_SPEED = 3
###各GameObjectが利用可能なPlayer座標
player_axis = []

#--------------------------

#--------------------------



#####--------------------------------------------------------------------
# ゲームオブジェクト
class GameObject:
	def __init__(self):
        # パラメタ初期化（存在フラグ、機体座標、移動時座標増分、機体サイズ、機体体力）
		self.exists = False
		self.x = 0
		self.y = 0
		self.vx = 0
		self.vy = 0
		self.width = 0
		self.height = 0
		self.checkable = False
		self.message = ""
		self.message_created = False

	def init(self, x, y):
        # インスタンス生成時の引数に基づく初期化
        # 座標
		self.x, self.y = x, y

	def create_message_window(self, message):
		self.message_box = MessageBox(message)
        # ここでMessageBoxはメッセージウィンドウオブジェクトを生成するための任意のクラスです。
        # MessageBoxクラスの実装により、この部分は適宜調整してください。

	def update_btnprss(self, message):
		if((self.checkable)and(not(self.message_created))):
			if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                # プレイヤー座標との距離がXでないならcontinue
                # プレイヤーが向いてる方向に自分がいなければcontinue
                # メッセージウィンドウを生成する
				self.create_message_window(message)
				self.message_created = True


class BDFRenderer:
    BORDER_DIRECTIONS = [
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1),
    ]

    def __init__(self, bdf_filename):
        self.font_bounding_box = [0, 0, 0, 0]
        self.fonts = self._parse_bdf(bdf_filename)
        self.screen_ptr = pyxel.screen.data_ptr()
        self.screen_width = pyxel.width

    def _parse_bdf(self, bdf_filename):
        fonts = {}
        code = None
        bitmap = None
        dwidth = 0
        with open(bdf_filename, "r") as f:
            for line in f:
                if line.startswith("FONTBOUNDINGBOX"):
                    self.font_bounding_box = list(map(int, line.split()[1:]))
                elif line.startswith("ENCODING"):
                    code = int(line.split()[1])
                elif line.startswith("DWIDTH"):
                    dwidth = int(line.split()[1])
                elif line.startswith("BBX"):
                    bbx = tuple(map(int, line.split()[1:]))
                elif line.startswith("BITMAP"):
                    bitmap = []
                elif line.startswith("ENDCHAR"):
                    fonts[code] = (
                        dwidth,
                        bbx,
                        bitmap,
                    )
                    bitmap = None
                elif bitmap is not None:
                    hex_string = line.strip()
                    bin_string = bin(int(hex_string, 16))[2:].zfill(len(hex_string) * 4)
                    bitmap.append(int(bin_string[::-1], 2))
        return fonts

    def _draw_font(self, x, y, font, color):
        dwidth, bbx, bitmap = font
        screen_ptr = self.screen_ptr
        screen_width = self.screen_width
        x = x + self.font_bounding_box[2] + bbx[2]
        y = y + self.font_bounding_box[1] + self.font_bounding_box[3] - bbx[1] - bbx[3]
        for j in range(bbx[1]):
            for i in range(bbx[0]):
                if (bitmap[j] >> i) & 1:
                    screen_ptr[(y + j) * screen_width + x + i] = color

    def draw_text(self, x, y, text, color=7, border_color=None, spacing=0):
        for char in text:
            code = ord(char)
            if code not in self.fonts:
                continue
            font = self.fonts[code]
            if border_color is not None:
                for dx, dy in self.BORDER_DIRECTIONS:
                    self._draw_font(
                        x + dx,
                        y + dy,
                        font,
                        border_color,
                    )
            self._draw_font(x, y, font, color)
            x += font[0] + spacing

class MessageBox:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.message = ""
        self.umplus10 = BDFRenderer("assets/umplus_j10r.bdf")
        self.umplus12 = BDFRenderer("assets/umplus_j12r.bdf")

    def __init__(self, message):
        self.message = message

    def draw(self):
        self.drawtext()

    def drawtext(self):
        self.umplus10.draw_text(24, 8, self.message, 0)
        self.umplus12.draw_text( 4, 98, self.message, 0, 5)
        self.umplus12.draw_text( 4, 113, self.message, 0, 5)


#####--------------------------------------------------------------------
# 操作キャラ
class Girl(GameObject):
    def __init__(self):
        super().__init__()
        self.x = (pyxel.width / 2)  - C_PLAYER_WIDTH/2
        self.y = (pyxel.height / 2) - C_PLAYER_HEIGHT/2    
        self.width = C_PLAYER_WIDTH
        self.height = C_PLAYER_HEIGHT
        self.player_direction = 0
        self.player_direction_RF = 1
        self.player_face = 0
        self.frame = 0  # 追加：アニメーションのためのフレーム数
        self.frame_count_wk = 0
        self.animation_frame = 0
        self.is_alive = True
        self.moving = False   

    def update(self):
        move_speed = C_PLAYER_MOVE_SPEED
        # キャラクターが移動しているかどうか
        # キー入力と指定動作スピードに応じて座標を増減させる。
        self.arrow_input_check(move_speed)

        if self.moving:
            self.frame += 1  # キャラクターが移動しているときはフレーム数を増やす
        else:
            self.frame = 0  # キャラクターが静止しているときはフレーム数をリセットする

        self.x = max(min(self.x, pyxel.width  - C_PLAYER_WIDTH), 0)
        self.y = max(min(self.y, pyxel.height - C_PLAYER_HEIGHT), 0)

    def draw(self):
        self.frame_count_wk = pyxel.frame_count
        self.animation_frame = self.frame_count_wk // 6 % 4  # フレーム数を6で割り、その後4で割った余りを取ることでアニメーションフレームを0, 1, 2, 3の範囲に制限する

        ### TEST ★player_faceパラメタで表示切替　★　　　###
        self.player_face = self.frame_count_wk // 6 % 8
        ### TEST ★player_faceパラメタで表示切替　★　　　###

        #　キャラクター画像の描画
        ### キー押下による移動中かストップ中かで大きく描画パターン分け。
        ### また、胴体と頭部の画像リソースを分けているのでそれぞれをセットで描画するようにする。
        if (self.moving):
            # walking
            if (self.player_direction == 0):
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 3 * 48, 16, 48, 3) # 上移動中
                pyxel.blt(self.x, self.y, 0, 48, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 1):
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 2 * 48, 16, 48, 3) # 下移動中
                pyxel.blt(self.x, self.y, 0, 32, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 2):
                self.player_direction_RF = -1 # 左移動途中
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 1 * 48, -16, 48, 3) # 左移動中
                self.draw_head() # 頭部を描画
            if (self.player_direction == 3):
                self.player_direction_RF =  1 # 右移動途中
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 1 * 48, 16, 48, 3) # 右移動中
                self.draw_head() # 頭部を描画
        else:
            # standing
            if (self.player_direction == 0):
                pyxel.blt(self.x, self.y, 0, 48, 3 * 48, 16, 48, 3) # 上移動途中
                pyxel.blt(self.x, self.y, 0, 48, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 1):
                pyxel.blt(self.x, self.y, 0, 48, 2 * 48, 16, 48, 3) # 下移動途中
                pyxel.blt(self.x, self.y, 0, 32, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 2):
                self.player_direction_RF = -1 # 左移動途中
                pyxel.blt(self.x, self.y + 16, 0, 0,   16, self.player_direction_RF * 16, 32, 3) # 左右移動途中
                self.draw_head() # 頭部を描画
            if (self.player_direction == 3):
                self.player_direction_RF =  1 # 右移動途中
                pyxel.blt(self.x, self.y + 16, 0, 0,   16, self.player_direction_RF * 16, 32, 3) # 左右移動途中
                self.draw_head() # 頭部を描画
        
        self.moving = False

    def draw_head(self):
        # 横向きか正面かで使用する画像リソース位置が異なる
        if((self.player_direction == 2)or(self.player_direction == 3)):
            ### Player_direction_RFで右向き画像を左反転して対応
            pyxel.blt(self.x, self.y, 0, self.player_face * 16, 0, self.player_direction_RF * 16, 16, 3) # 通常表情


    def draw_parts(self):
        # 各部位を個別に描画
        ##pyxel.blt(self.x, self.y + 36, 2, animation_frame * 16, 0 * 48, 16, 12, 3)  # 奥の腕
        pyxel.blt(self.x, self.y + 32, 0,  0, 32, 16, 16, 3)  # 下半身
        pyxel.blt(self.x, self.y + 16, 0,  0, 16, 16, 16, 3)  # 胴体
        #pyxel.blt(self.x, self.y + 16, 2, animation_frame * 16, 3 * 48, 16, 16, 3)   # 手前の腕
        pyxel.blt(self.x, self.y +  0, 0, (pyxel.frame_count // 6 % 7) * 16, 0, 16, 16, 3)  # 頭部


    def arrow_input_check(self, move_speed):
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= move_speed
            self.player_direction = 0
            self.moving = True
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += move_speed
            self.player_direction = 1
            self.moving = True
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= move_speed
            self.player_direction = 2
            self.moving = True
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += move_speed
            self.player_direction = 3
            self.moving = True

        if pyxel.btn(pyxel.KEY_W):
            self.y -= move_speed
            self.player_direction = 0
            self.moving = True
        if pyxel.btn(pyxel.KEY_Z):
            self.y += move_speed
            self.player_direction = 1
            self.moving = True
        if pyxel.btn(pyxel.KEY_A):
            self.x -= move_speed
            self.player_direction = 2
            self.moving = True
        if pyxel.btn(pyxel.KEY_S):
            self.x += move_speed
            self.player_direction = 3
            self.moving = True


#####--------------------------------------------------------------------
# 操作キャラ
class Wolf(GameObject):
    def __init__(self):
        super().__init__()
        self.x = (pyxel.width / 2)  - C_PLAYER_WIDTH/2
        self.y = (pyxel.height / 2) - C_PLAYER_HEIGHT/2    
        self.width = C_PLAYER_WIDTH
        self.height = C_PLAYER_HEIGHT
        self.player_direction = 0
        self.player_direction_RF = 1
        self.player_face = 0
        self.frame = 0  # 追加：アニメーションのためのフレーム数
        self.frame_count_wk = 0
        self.animation_frame = 0
        self.is_alive = True
        self.moving = False
        self.checkable = True

    def update(self):
        move_speed = C_PLAYER_MOVE_SPEED
        # キャラクターが移動しているかどうか
        # キー入力と指定動作スピードに応じて座標を増減させる。
        self.arrow_input_check(move_speed)

        if self.moving:
            self.frame += 1  # キャラクターが移動しているときはフレーム数を増やす
        else:
            self.frame = 0  # キャラクターが静止しているときはフレーム数をリセットする

        self.x = max(min(self.x, pyxel.width  - C_PLAYER_WIDTH), 0)
        self.y = max(min(self.y, pyxel.height - C_PLAYER_HEIGHT), 0)

        ###
        self.update_btnprss("試しにメッセージ表示")

    def draw(self):
        self.frame_count_wk = pyxel.frame_count
        self.animation_frame = 4 + self.frame_count_wk // 6 % 4  # フレーム数を6で割り、その後4で割った余りを取ることでアニメーションフレームを0, 1, 2, 3の範囲に制限する

        ### TEST ★player_faceパラメタで表示切替　★　　　###
        self.player_face = self.frame_count_wk // 6 % 8
        ### TEST ★player_faceパラメタで表示切替　★　　　###

        #　キャラクター画像の描画
        ### キー押下による移動中かストップ中かで大きく描画パターン分け。
        ### また、胴体と頭部の画像リソースを分けているのでそれぞれをセットで描画するようにする。
        if (self.moving):
            # walking
            if (self.player_direction == 0):
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 9 * 16, 16, 48, 3) # 上移動中
                ###pyxel.blt(self.x, self.y, 0, 48, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 1):
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 6 * 16, 16, 48, 3) # 下移動中
                ###pyxel.blt(self.x, self.y, 0, 32, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 2):
                self.player_direction_RF = -1 # 左移動途中
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 1 * 48, -16, 48, 3) # 左移動中
            if (self.player_direction == 3):
                self.player_direction_RF =  1 # 右移動途中
                pyxel.blt(self.x, self.y, 0, self.animation_frame * 16, 1 * 48, 16, 48, 3) # 右移動中
            self.draw_head() # 頭部を描画
        else:
            # standing
            if (self.player_direction == 0):
                pyxel.blt(self.x, self.y, 0, 7 * 16, 9 * 16, 16, 48, 3) # 上移動途中
                ###pyxel.blt(self.x, self.y, 0, 48, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 1):
                pyxel.blt(self.x, self.y, 0, 7 * 16, 6 * 16, 16, 48, 3) # 下移動途中
                ###pyxel.blt(self.x, self.y, 0, 32, 32, 16, 16, 3) # 頭部
            if (self.player_direction == 2):
                self.player_direction_RF = -1 # 左移動途中
                pyxel.blt(self.x, self.y + 16, 0, 14 * 16,   16, self.player_direction_RF * 16, 32, 3) # 左右移動途中
            if (self.player_direction == 3):
                self.player_direction_RF =  1 # 右移動途中
                pyxel.blt(self.x, self.y + 16, 0, 14 * 16,   16, self.player_direction_RF * 16, 32, 3) # 左右移動途中
            self.draw_head() # 頭部を描画
        
        self.moving = False

    def draw_head(self):
        if(self.player_direction == 0):
            if(self.animation_frame == 5)and(self.moving):
                ### 2枚目歩きモーション時は頭部を1px上に浮かせる。
                pyxel.blt(self.x, self.y - 1, 0, 10 * 16, 4 * 16, 16, 16, 3)
            else:
                ### Player_direction_RFで右向き画像を左反転して対応
                pyxel.blt(self.x, self.y, 0, 10 * 16, 4 * 16, 16, 16, 3)
        if(self.player_direction == 1):
            if(self.animation_frame == 5)and(self.moving):
                ### 2枚目歩きモーション時は頭部を1px上に浮かせる。
                pyxel.blt(self.x, self.y - 1, 0, 9 * 16, 4 * 16, 16, 16, 3)
            else:
                ### Player_direction_RFで右向き画像を左反転して対応
                pyxel.blt(self.x, self.y, 0, 9 * 16, 4 * 16, 16, 16, 3)
        # 横向きか正面かで使用する画像リソース位置が異なる
        if((self.player_direction == 2)or(self.player_direction == 3)):
            if(self.animation_frame == 5)and(self.moving):
                ### Player_direction_RFで右向き画像を左反転して対応、2枚目歩きモーション時は頭部を1px上に浮かせる。
                pyxel.blt(self.x, self.y - 1, 0, 8 * 16, 4 * 16, self.player_direction_RF * 16, 16, 3) # 通常表情
            else:
                ### Player_direction_RFで右向き画像を左反転して対応
                pyxel.blt(self.x, self.y, 0, 8 * 16, 4 * 16, self.player_direction_RF * 16, 16, 3) # 通常表情

    def draw_parts(self):
        # 各部位を個別に描画
        ##pyxel.blt(self.x, self.y + 36, 2, animation_frame * 16, 0 * 48, 16, 12, 3)  # 奥の腕
        pyxel.blt(self.x, self.y + 32, 0,  0, 32, 16, 16, 3)  # 下半身
        pyxel.blt(self.x, self.y + 16, 0,  0, 16, 16, 16, 3)  # 胴体
        #pyxel.blt(self.x, self.y + 16, 2, animation_frame * 16, 3 * 48, 16, 16, 3)   # 手前の腕
        pyxel.blt(self.x, self.y +  0, 0, (pyxel.frame_count // 6 % 7) * 16, 0, 16, 16, 3)  # 頭部


    def arrow_input_check(self, move_speed):
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= move_speed
            self.player_direction = 0
            self.moving = True
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += move_speed
            self.player_direction = 1
            self.moving = True
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= move_speed
            self.player_direction = 2
            self.moving = True
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += move_speed
            self.player_direction = 3
            self.moving = True

        if pyxel.btn(pyxel.KEY_W):
            self.y -= move_speed
            self.player_direction = 0
            self.moving = True
        if pyxel.btn(pyxel.KEY_Z):
            self.y += move_speed
            self.player_direction = 1
            self.moving = True
        if pyxel.btn(pyxel.KEY_A):
            self.x -= move_speed
            self.player_direction = 2
            self.moving = True
        if pyxel.btn(pyxel.KEY_S):
            self.x += move_speed
            self.player_direction = 3
            self.moving = True

##########-----------------------------------------------------------------------
class MyApp:
    def __init__(self):
        pyxel.init(300, 300, title=C_TITLE, fps=40, quit_key=pyxel.KEY_NONE, capture_scale=4, capture_sec=0)
        pyxel.load("newgame.pyxres")  


        #プレイヤーオブジェクトを準備
        ###self.player = Girl()
        self.player = Wolf()
        

        pyxel.run(self.update, self.draw)

    def update(self):
        self.player.update()

    def draw(self):
        pyxel.cls(3)  
        self.player.draw()







#----------------------------
MyApp()
