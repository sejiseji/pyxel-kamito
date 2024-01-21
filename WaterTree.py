import pyxel
import math
import random

class WaterTree:
    def __init__(self, x, num_branch):
        self.x = x
        self.y = 0
        self.num_branch = num_branch  # 枝の数
        # self.width = 8  # 基本の幹の太さ
        self.width = random.randint(6,9)  # 基本の幹の太さ
        #誤差
        self.rnddeg1 = random.randint(-3, 3)
        self.rnddeg2 = random.randint(-3, 3)
        #色
        self.color = random.choice([1,5])  # 色のバリエーション

    def draw_branch(self, x, y, angle, length, width):
        # 枝の終点の座標を計算
        end_x = x + length * math.cos(math.radians(angle))
        end_y = y - length * math.sin(math.radians(angle))

        # 枝を描画
        for i in range(width):
            offset = i - width // 2
            pyxel.line(x + offset, y, end_x + offset, end_y, self.color)

        return end_x, end_y

    def draw(self, camera_x=0):
        # 幹の描画
        trunk_height = pyxel.height
        for i in range(self.width -1):
            pyxel.line(self.x - camera_x + i +self.width -4, trunk_height -130, self.x - camera_x + i +self.width -4, trunk_height, self.color)
        
        # 1世代目の枝のパラメータ
        branches = [(self.x - camera_x + self.width - 1, trunk_height -120, 90, 50, self.width - 1)]
        
        # 各世代の枝を描画
        for count in range(self.num_branch):
            new_branches = []
            # rndnum = random.randint(0, self.num_branch)
            for x, y, angle, length, width in branches:
                end_x, end_y = self.draw_branch(x, y, angle, length, width)
                # 枝ごとに異なるタイミングで明滅
                if (pyxel.frame_count//30 + count) % 4 == 0:
                    rndminus = random.randint(0, 1)
                    if rndminus == 0:
                        rndminus = -1
                    rndx = random.randint(0, 2) * rndminus
                    rndy = random.randint(0, 2) * rndminus
                    if count >= 5:
                        pyxel.pset(x + rndx, y + rndy, random.choice([9,10]))

                # 新しい世代の枝のパラメータを計算
                gen_length = length * 0.75
                gen_width = max(width - 1, 1)
                new_branches.append((end_x, end_y, angle + 30 +self.rnddeg1, gen_length, gen_width))
                new_branches.append((end_x, end_y, angle - 25 +self.rnddeg2, gen_length, gen_width))
            branches = new_branches  # 次の世代の枝に更新
        
