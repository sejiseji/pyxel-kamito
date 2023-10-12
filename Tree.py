import pyxel
import random
import math

C_TREE_WIDTH = 16 * 5
C_TREE_HEIGHT = 16 * 4 + 16

def pseudo_perlin_noise(t):
    # 振幅を小さく調整
    return math.sin(t) * random.uniform(0.05, 0.35)
    # return math.sin(t) * random.uniform(0.01, 0.1)

class Tree:
    def __init__(self, x, y, num_leaves, leaves_area_radius):
        self.x = x
        self.y = y
        self.leaves = [(x + random.randint(-leaves_area_radius, leaves_area_radius),
                        y + random.randint(-leaves_area_radius, leaves_area_radius))
                       for _ in range(num_leaves)]
        self.time = 0
        self.leaves_area_radius = leaves_area_radius

        ###動的設定パラメタ
        self.delta_time = 0.1
        self.coefficient = 1
        self.noise_min = 0.01
        self.noise_max = 0.1

        self.leaves_history = []  # 各葉の座標の履歴を保存するリスト
        self.update_count = 0  # 追加: 更新回数をカウントする変数

        self.position_x = self.x + C_TREE_WIDTH/2
        self.position_y = self.y + C_TREE_HEIGHT
        
        self.is_playing = False
        self.position_back = True
        self.position_front = False

    def update(self, min_x=0, max_x=300):
        ###x_offsetを加味して画面内(min_x〜max_x)にある粒子のみ処理
        if min_x <= self.x <= max_x:
            self.time += self.delta_time
            new_leaves = []  # 新しい座標のリスト
            
            if len(self.leaves_history) < 3:  # 3回までの場合、新しい座標を計算
                for i, (x, y) in enumerate(self.leaves):

                    ### sin関数によるノイズ
                    # dx = (math.sin(self.time + i) * random.uniform(self.noise_min, self.noise_max)) * self.coefficient
                    # dy = (math.sin(self.time + i + 10) * random.uniform(self.noise_min, self.noise_max)) * self.coefficient
                    ###  pseudo_perlin_noise関数によるノイズ               
                    dx = pseudo_perlin_noise(self.time + i) * self.coefficient
                    dy = pseudo_perlin_noise(self.time + i + 10) * self.coefficient

                    new_x, new_y = x + dx, y + dy
                    
                    # 座標が半径内に収まるように調整
                    distance = math.sqrt((new_x - self.x)**2 + (new_y - self.y)**2)
                    if distance > self.leaves_area_radius:
                        angle = math.atan2(new_y - self.y, new_x - self.x)
                        new_x = self.x + self.leaves_area_radius * math.cos(angle)
                        new_y = self.y + self.leaves_area_radius * math.sin(angle)
                    
                    new_leaves.append((new_x, new_y))
                self.leaves_history.append(new_leaves)  # 新しい座標のリストを履歴に追加
            else:  # 3回以上の場合、履歴から座標を取得
                history_index = self.update_count % 3
                new_leaves = self.leaves_history[history_index].copy()  # .copy()を使用して新しいリストを作成

            self.update_count += 1  #　更新回数をカウント
            self.leaves = new_leaves

    def parameta_update(self, delta_time, coefficient, noise_min, noise_max):
        self.delta_time = delta_time
        self.coefficient = coefficient
        self.noise_min = noise_min
        self.noise_max = noise_max
    
    def parameta_reset(self):
        self.delta_time = 0.1
        self.coefficient = 1
        self.noise_min = 0.01
        self.noise_max = 0.1

