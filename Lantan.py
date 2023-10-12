import pyxel
import random

C_LANTAN_WIDTH = 16 * 1
C_LANTAN_HEIGHT = 21 * 1

###pyxelのLantanクラスを作成
class Lantan:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.width = C_LANTAN_WIDTH
        self.height = C_LANTAN_HEIGHT
        self.position_x = self.x + self.width/2
        self.position_y = self.y + self.height
        ###灯籠の移動速度
        self.speed = speed
        ###particlesys紐づけ済みかどうかのフラグ
        self.is_attached = False
        ###アニメーションのスタートフレーム
        self.start_frame = random.randint(0, 7)

    def update(self):
        ###ランタンの移動
        self.x -= self.speed
        self.position_x = self.x + self.width/2

    def draw(self, x_offset=0, min_x=0, max_x=300):
        ###x_offsetを加味して画面内(min_x〜max_x)にある場合のみ描画処理を行う
        if self.x - x_offset > min_x -16 and self.x - x_offset < max_x + 16:
            ###灯籠の描画
            pyxel.blt(self.x - x_offset, self.y, 1, 128, 0 + 21*(((pyxel.frame_count + self.start_frame)//10)%8), 16, 21, 0)

    def getLantanpositionX(self):
        return self.position_x

    def getLantanpositionY(self):
        return self.position_y
    
