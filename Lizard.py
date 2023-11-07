import pyxel
import random
import math

class Lizard:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.footprints = []  # 保存された足跡の座標
        self.footprint_limit = 10  # 保存する足跡の最大数
    
    def update(self):
        # 画面内でランダムな方向に移動、または停止
        if random.choice([True, False]):  # ランダムで動くか静止するか選択
            angle = random.uniform(0, 2 * math.pi)  # ランダムな方向を選択
            dx = self.speed * math.cos(angle)
            dy = self.speed * math.sin(angle)

            # 新しい座標が画面内に収まるようにする
            new_x = min(max(0, self.x + dx), pyxel.width - 1)
            new_y = min(max(0, self.y + dy), pyxel.height - 1)
            
            self.move(new_x, new_y)
    
    def move(self, x, y):
        self.x = x
        self.y = y
        self.footprints.append((x, y))  # 新しい足跡を追加
        
        # 足跡の最大数を超えた場合、古い足跡を削除
        if len(self.footprints) > self.footprint_limit:
            self.footprints.pop(0)
    
    def draw(self):
        # トカゲを描画
        pyxel.circ(self.x, self.y, 3, 8)
        
        # 足跡を描画
        for x, y in self.footprints:
            pyxel.circ(x, y, 1, 7)

# class App:
#     def __init__(self):
#         pyxel.init(160, 120)
#         self.lizard = Lizard(80, 60, 2)  # スピード2でリザードを初期化
#         pyxel.run(self.update, self.draw)
    
#     def update(self):
#         self.lizard.update()
    
#     def draw(self):
#         pyxel.cls(0)
#         self.lizard.draw()

# App()
