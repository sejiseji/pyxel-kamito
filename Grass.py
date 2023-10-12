import pyxel
import random
import math

class Blade:
    def __init__(self, x, base_y, height):
        self.x = x
        self.base_y = base_y
        self.height = height
        self.max_width = random.randint(2, 5)  # 草の最大幅
        self.color = random.choice([pyxel.COLOR_GREEN, pyxel.COLOR_GREEN, pyxel.COLOR_LIME])  # 色のバリエーション
        self.control_points = self.generate_control_points()
        self.initial_tip_x = self.control_points[2][0]
        self.initial_tip_y = self.control_points[2][1]
        self.mid_x = 0
        self.mid_y = 0
        self.tip_x = 0
        self.tip_y = 0
        self.angle = 0
        self.distance = 0
        self.new_tip_x = 0
        self.new_tip_y = 0
        self.bx = 0
        self.by = 0
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.dx = 0
        self.dy = 0
        self.cached_tips = []  # ここに7回分の頂点を格納
        self.update_count = 0  # 何回頂点が更新されたかをトラック


    def generate_control_points(self):
        self.mid_x = random.uniform(self.x - 10, self.x + 10)
        self.mid_y = self.base_y - (self.height / 2) + random.uniform(-10, 10)
        self.tip_x = self.x + random.uniform(-10, 10)
        self.tip_y = self.base_y - self.height

        return [(self.x, self.base_y), (self.mid_x, self.mid_y), (self.tip_x, self.tip_y)]


    def update_tip(self):
        # 既に7回更新されている場合、キャッシュから座標を取得
        if self.update_count >= 7:
            index = self.update_count % 7  # キャッシュのインデックス
            self.new_tip_x, self.new_tip_y = self.cached_tips[index]
        else:
            self.angle = random.uniform(0, 2 * math.pi)
            self.distance = random.uniform(0, 3)
            self.new_tip_x = self.initial_tip_x - 3 + self.distance * math.cos(self.angle)
            self.new_tip_y = self.initial_tip_y + 3 + self.distance * math.sin(self.angle)
            
            # キャッシュに新しい座標を追加
            self.cached_tips.append((self.new_tip_x, self.new_tip_y))
        
        self.update_count += 1
        self.control_points[2] = (self.new_tip_x, self.new_tip_y)


    def bezier_curve(self, t):
        self.bx = (1-t)**2 * self.control_points[0][0] + 2 * (1-t) * t * self.control_points[1][0] + t**2 * self.control_points[2][0]
        self.by = (1-t)**2 * self.control_points[0][1] + 2 * (1-t) * t * self.control_points[1][1] + t**2 * self.control_points[2][1]
        return self.bx, self.by

    def draw(self, x_offset=0):
        segments = 20
        for i in range(segments):
            self.x1, self.y1 = self.bezier_curve(i/segments)
            self.x2, self.y2 = self.bezier_curve((i+1)/segments)
            
            ###offset調整
            self.x1 -= x_offset
            self.x2 -= x_offset

            # 中心線を描画
            pyxel.line(int(self.x1), int(self.y1), int(self.x2), int(self.y2), self.color)  # 色を指定
            # pyxel.line(int(self.x1), int(self.y1), int(self.x2), int(self.y2), pyxel.COLOR_GREEN)

            # 幅を追加 (交点に近づくにつれて幅を減少)
            for j in range(1, int(self.max_width * (1 - i/segments)) + 1):
                angle = math.atan2(self.y2 - self.y1, self.x2 - self.x1) + math.pi/2
                self.dx = j * math.cos(angle)
                self.dy = j * math.sin(angle)
                pyxel.line(int(self.x1 + self.dx), int(self.y1 + self.dy), int(self.x2 + self.dx), int(self.y2 + self.dy), self.color)  # 色を指定
                # pyxel.line(int(self.x1 + self.dx), int(self.y1 + self.dy), int(self.x2 + self.dx), int(self.y2 + self.dy), pyxel.COLOR_GREEN)

class Grass:
    def __init__(self, x, y, distance, min_height, max_height, num_blades):
        self.blades = [Blade(x + random.uniform(0, distance), y, random.uniform(min_height, max_height)) for _ in range(num_blades)]

    def update(self, min_x=0, max_x=300):
        for blade in self.blades:
            if min_x <= blade.x <= max_x:
                blade.update_tip()

    def draw(self, x_offset=0, min_x=0, max_x=300):
        for blade in self.blades:
            if blade.x - x_offset > min_x -16 and blade.x - x_offset < max_x + 16:
                blade.draw(x_offset)
