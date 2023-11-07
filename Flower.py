import pyxel
import math
import random


class Flower:
    def __init__(self, x, y, stem):
        self.x = x
        self.y = y
        self.stem = stem
        self.core_radius = random.randint(2, 4)
        self.core_color = random.choice([pyxel.COLOR_RED, pyxel.COLOR_YELLOW, pyxel.COLOR_PINK, pyxel.COLOR_WHITE, pyxel.COLOR_ORANGE, pyxel.COLOR_PEACH])
        self.num_petals = random.randint(4, 8)
        self.petal_length = random.randint(5, 10)
        self.petal_width = random.randint(3, 5)
        self.petal_color = random.choice([pyxel.COLOR_RED, pyxel.COLOR_YELLOW, pyxel.COLOR_PINK, pyxel.COLOR_WHITE, pyxel.COLOR_ORANGE, pyxel.COLOR_PEACH])
        self.petal_coordinates_outer = [[] for _ in range(6)]  # For memoizing outer coordinates of petals
        self.petal_coordinates_inner = [[] for _ in range(6)]  # For memoizing inner coordinates of petals
        self.memoize_petal_coordinates()

        self.draw_x = 0
        self.draw_y = 0

    def memoize_petal_coordinates(self):
        for count in range(5):
            for i in range(self.num_petals):
                angle = i * (360 / self.num_petals)
                outer_coords = []
                inner_coords = []
                for j in range(self.petal_width + 1):
                    offset_angle_outer = angle + j * 2  # 2-degree offset to adjust the width of the petal
                    petal_x_offset_outer = self.petal_length * math.cos(math.radians(offset_angle_outer))
                    petal_y_offset_outer = self.petal_length * math.sin(math.radians(offset_angle_outer))
                    outer_coords.append((petal_x_offset_outer, petal_y_offset_outer))

                    offset_angle_inner = angle - j * 2  # 2-degree offset to adjust the width of the petal
                    petal_x_offset_inner = self.petal_length * math.cos(math.radians(offset_angle_inner))
                    petal_y_offset_inner = self.petal_length * math.sin(math.radians(offset_angle_inner))
                    inner_coords.append((petal_x_offset_inner, petal_y_offset_inner))

                self.petal_coordinates_outer[count].append(outer_coords)
                self.petal_coordinates_inner[count].append(inner_coords)

    def draw(self, x_offset=0):
        numpoins = 4 # Number of points to cache
        x = self.stem.new_tip_x - x_offset
        y = self.stem.new_tip_y
        cycle_index = int(self.stem.new_tip_y) % numpoins  # Converting to int to avoid TypeError

        # Draw the flower core
        pyxel.circ(x, y, self.core_radius, self.core_color)

        # Use memoized coordinates to draw petals
        for i in range(self.num_petals):
            angle = i * (360 / self.num_petals)
            outer_coords = self.petal_coordinates_outer[cycle_index][i]
            inner_coords = self.petal_coordinates_inner[cycle_index][i]
            for (outer_x, outer_y), (inner_x, inner_y) in zip(outer_coords, inner_coords):
                pyxel.line(x + outer_x, y + outer_y, x + inner_x, y + inner_y, self.petal_color)

            # 幅を追加して花びらを太くする
            for j in range(1, self.petal_width + 1):
                offset_angle = angle + j * 2  # 2度のオフセットで花びらの幅を調整
                petal_x_offset = x + self.petal_length * math.cos(math.radians(offset_angle))
                petal_y_offset = y + self.petal_length * math.sin(math.radians(offset_angle))
                pyxel.line(x, y, petal_x_offset, petal_y_offset, self.petal_color)

                offset_angle = angle - j * 2  # 2度のオフセットで花びらの幅を調整
                petal_x_offset = x + self.petal_length * math.cos(math.radians(offset_angle))
                petal_y_offset = y + self.petal_length * math.sin(math.radians(offset_angle))
                pyxel.line(x, y, petal_x_offset, petal_y_offset, self.petal_color)

class Stem:
    def __init__(self, x, base_y, height):
        self.x = x
        self.y = base_y
        self.base_y = base_y
        self.height = height
        self.max_width = random.randint(2, 5)  # 草の最大幅
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
        # self.flower = Flower(self.control_points[2][0], self.control_points[2][1],self)
        self.flower = None
        self.tip_cache = []  # tipの座標をキャッシュするためのリスト
        self.tip_cache_index = 0  # 使用中のキャッシュのインデックス

        self.draw_x = 0
        self.draw_y = 0

    def generate_control_points(self):
        self.mid_x = random.uniform(self.x - 10, self.x + 10)
        self.mid_y = self.base_y - (self.height / 2) + random.uniform(-10, 10)
        self.tip_x = self.x + random.uniform(-10, 10)
        self.tip_y = self.base_y - self.height

        return [(self.x, self.base_y), (self.mid_x, self.mid_y), (self.tip_x, self.tip_y)]

    def update_tip(self, min_x=0, max_x=300):
        ### Flowerがない場合は生成する
        if self.flower is None:
            ###茎が画面外にある場合は花の初期生成位置が画面外へ飛ばしておく
            if self.x > 300:
                self.flower = Flower(-100, -100, self)
            else:
                self.flower = Flower(-100, -100, self)
                # self.flower = Flower(self.control_points[2][0], self.control_points[2][1],self)

        ###x_offsetを加味して画面内(min_x〜max_x)にある　または　tipの座標がキャッシュされていない場合は座標更新を行う
        if (min_x <= self.x <= max_x) or (len(self.tip_cache)==0):
            numpoints = 4
            if len(self.tip_cache) == numpoints: # tipの座標でキャッシュされている数
                self.new_tip_x, self.new_tip_y = self.tip_cache[self.tip_cache_index]
                self.tip_cache_index = (self.tip_cache_index + 1) % numpoints
                self.control_points[2] = (self.new_tip_x, self.new_tip_y)
                self.flower.x, self.flower.y = self.new_tip_x, self.new_tip_y
                return
            else:            
                # 通常のtip更新処理
                self.angle = random.uniform(0, 2 * math.pi)
                self.distance = random.uniform(0, 3)
                self.new_tip_x = self.initial_tip_x - 3 + self.distance * math.cos(self.angle)
                self.new_tip_y = self.initial_tip_y + 3 + self.distance * math.sin(self.angle)
                
                self.control_points[2] = (self.new_tip_x, self.new_tip_y)
                self.flower.x, self.flower.y = self.new_tip_x, self.new_tip_y
                
                # tipの座標をキャッシュに保存
                self.tip_cache.append((self.new_tip_x, self.new_tip_y))
                if len(self.tip_cache) > numpoints:
                    self.tip_cache.pop(0)  # 既定値以上キャッシュされている場合、最初の要素を削除

    def bezier_curve(self, t):
        self.bx = (1-t)**2 * self.control_points[0][0] + 2 * (1-t) * t * self.control_points[1][0] + t**2 * self.control_points[2][0]
        self.by = (1-t)**2 * self.control_points[0][1] + 2 * (1-t) * t * self.control_points[1][1] + t**2 * self.control_points[2][1]
        return self.bx, self.by


    def draw(self, x_offset=0, scroll_x=0,min_x=0,max_x=300):
        segments = 20
        if self.x - x_offset > min_x -16 and self.x - x_offset < max_x + 16:
            for i in range(segments):
                self.x1, self.y1 = self.bezier_curve(i/segments)
                self.x2, self.y2 = self.bezier_curve((i+1)/segments)
                
                ###offset調整
                self.x1 -= x_offset
                self.x2 -= x_offset

                # 中心線を描画
                pyxel.line(int(self.x1) -scroll_x, int(self.y1), int(self.x2) -scroll_x, int(self.y2), pyxel.COLOR_GREEN)

                # 幅を追加 (交点に近づくにつれて幅を減少)
                for j in range(1, int(self.max_width * (1 - i/segments)) + 1):
                    angle = math.atan2(self.y2 - self.y1, self.x2 - self.x1) + math.pi/2
                    self.dx = j * math.cos(angle)
                    self.dy = j * math.sin(angle)
                    pyxel.line(int(self.x1 + self.dx) -scroll_x, int(self.y1 + self.dy), int(self.x2 + self.dx) -scroll_x, int(self.y2 + self.dy), pyxel.COLOR_GREEN)
        ###花の描画
        if self.flower is not None:
            self.flower.draw(x_offset -scroll_x)

