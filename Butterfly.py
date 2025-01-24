import pyxel
import random

C_BUTTERFLY_WIDTH = 8
C_BUTTERFLY_HEIGHT = 8

class Butterfly:
    def __init__(self, x1, y1, x2, y2, col=0, move_distance='short'):
        self.x_min = min(x1, x2)
        self.x_max = max(x1, x2)
        self.y_min = min(y1, y2)
        self.y_max = max(y1, y2)
        self.x = random.randint(self.x_min, self.x_max)
        self.y = random.randint(self.y_min, self.y_max)
        self.sprite_index = 0
        self.col = col

        ###
        self.is_playing = False
        self.draw_x = 0
        self.draw_y = 0

        self.width = C_BUTTERFLY_WIDTH
        self.height = C_BUTTERFLY_HEIGHT

        ###表示順序の基準になる、JERRY足元の座標
        self.position_x = self.x + self.width/2
        self.position_y = self.y + self.height

        # 移動距離の設定
        self.move_distance = move_distance  # 'short', 'long'

        # スプライトのx軸の向きの設定
        self.direction = 1
        
    def update(self):
        # ランダムにスピードを選択
        move_frequency = random.choice(['low', 'medium', 'high'])
        frequency_map = {'low': 20, 'medium': 10, 'high': 5}
        # move_frequency = random.choice(['low', 'medium', 'high', 'none'])
        # frequency_map = {'low': 20, 'medium': 10, 'high': 5, 'none': 1000}

        if pyxel.frame_count % frequency_map[move_frequency] != 0:
            return
        
        # 一定間隔で方向転換
        if random.random() < 0.1:
            self.direction = random.choice([-1, 1])

        # 移動距離に基づいた移動量
        distance_map = {'short': 1, 'long': 2}
        move_amount = distance_map[self.move_distance]

        # 8方向ランダム移動
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)])
        new_x = self.x + dx * move_amount
        new_y = self.y + dy * move_amount
        
        # 範囲を超えないように調整
        self.x = max(self.x_min, min(self.x_max, new_x))
        self.y = max(self.y_min, min(self.y_max, new_y))

        self.draw_x = self.x
        self.draw_y = self.y

        ###表示順序の基準となる、足元の座標情報を更新する
        self.position_x = self.x + C_BUTTERFLY_WIDTH/2
        self.position_y = self.y + C_BUTTERFLY_HEIGHT

        # スプライトのインデックスを更新
        self.sprite_index = (self.sprite_index + 1) % 6

    def draw(self, x_offset=0):
        #pyxel.blt(self.x, self.y, 0, 0, 8 * self.sprite_index, 8, 8)
        pyxel.blt(self.draw_x -x_offset, self.draw_y, 2, 176 + self.col * 8, 184 + self.sprite_index * C_BUTTERFLY_HEIGHT, self.direction * C_BUTTERFLY_WIDTH, C_BUTTERFLY_HEIGHT, 3)


# # Pyxelアプリの初期化
# pyxel.init(160, 120, caption="Random Walking Butterfly")
# butterfly = Butterfly(50, 50, 100, 100, move_distance='long')
# pyxel.run(update, draw)
