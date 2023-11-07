
import pyxel
import random
import math

class Point:
    def __init__(self, x, y, z, center_x, center_y, center_z, speed_low, speed_high, life_low, life_high, pallete, cacheflg, scene):
        self.x = x
        self.y = y
        self.z = z
        self.center_x = center_x
        self.center_y = center_y
        self.center_z = center_z
        self.dx = random.uniform(speed_low, speed_high)
        self.dy = random.uniform(speed_low, speed_high)
        self.dz = random.uniform(speed_low, speed_high)
        self.life = random.randint(life_low, life_high)
        self.trail = []
        self.pallete = pallete
        self.coordinates_cache = []  # 座標を保存するためのリスト
        self.cache_index = 0  # 現在利用しているキャッシュのインデックス
        self.cache_ON = cacheflg
        self.scene = scene ###木の戸の中で葉の位置情報として使う場合はキャッシュ利用の値に制限をかけたい。

        self.draw_x = self.x
        self.draw_y = self.y
        self.draw_z = self.z

    def update(self, center, radius):

        # もし必要分座標がキャッシュされていれば、キャッシュから座標を取得して使用
        num_points = 0
        if self.scene == 4: ### 木の戸
            num_points = 3 # キャッシュする座標の数
        else:
            num_points = 5 # キャッシュする座標の数
        if self.cache_ON and len(self.coordinates_cache) == num_points:
            self.x, self.y, self.z = self.coordinates_cache[self.cache_index]
            self.cache_index = (self.cache_index + 1) % num_points  # 次のインデックスに移動、もしくは0に戻る
            self.draw_x, self.draw_y, self.draw_z = self.x, self.y, self.z
            return
            
        # # 通常の座標更新処理
        self.x += self.dx * random.randint(-1, 1)
        self.y += self.dy * random.randint(-1, 1)
        self.z += self.dz * random.randint(-1, 1)

        # golden_angle = math.pi * (3 - math.sqrt(5))
        # theta = golden_angle * self.life  # lifeをインデックスとして使用
        # phi = math.acos(1 - 2 * (self.life / 100.0))  # lifeを0-100の範囲と仮定
        # self.x = center[0] + radius * math.sin(theta) * math.cos(phi)
        # self.y = center[1] + radius * math.sin(theta) * math.sin(phi)
        # self.z = center[2] + radius * math.cos(theta)

        self.draw_x, self.draw_y, self.draw_z = self.x, self.y, self.z

        distance = math.sqrt((self.x - center[0]) ** 2 + (self.y - center[1]) ** 2 + (self.z - center[2]) ** 2)
        if distance > radius:
            nx, ny, nz = (self.x - center[0]) / distance, (self.y - center[1]) / distance, (self.z - center[2]) / distance
            self.x = center[0] + nx * radius
            self.y = center[1] + ny * radius
            self.z = center[2] + nz * radius
            self.dx = -self.dx
            self.dy = -self.dy
            self.dz = -self.dz
            self.draw_x, self.draw_y, self.draw_z = self.x, self.y, self.z

        # キャッシュが有効の場合のみ座標をキャッシュに保存
        if self.cache_ON:
            #　キャッシュがnum_points未満の場合は、座標をキャッシュに追加。それ以上の場合は、何もしない。
            if len(self.coordinates_cache) <= num_points:
                self.coordinates_cache.append((self.draw_x, self.draw_y, self.draw_z))
                # self.coordinates_cache.pop(0)  # 既定値以上キャッシュされている場合、最初の要素を削除 

        ###木ノ戸では葉の位置情報として使うので、軌跡情報の更新やライフの減少計算を行わない。
        if self.scene in(0,1,2,3,5,6,7,8,9): ### 木の戸(4)以外で実施する。
            # 軌跡情報の更新
            self.trail.append((self.draw_x, self.draw_y, self.draw_z))
            if len(self.trail) > num_points:
                self.trail.pop(0)
        
            # ライフを減少
            if self.life > 0:
                self.life -= 1

    def is_alive(self):
        return self.life > 0

    def draw(self, x_offset=0):        
        # 軌跡のポイントを描画
        prev_x, prev_y = self.draw_x, self.draw_y
        index = len(self.trail) - 1
        for trail_x, trail_y, _ in reversed(self.trail):  # 逆順で軌跡をループ
            color = 0
            if self.pallete == 0:
                if index == 4:
                    color = 9
                elif index == 3:
                    color = 12
                elif index == 2:
                    color = 5
                elif index == 1:
                    color = 1
            elif self.pallete == 1:
                if index == 4:
                    color = 14
                elif index == 3:
                    color = 15
                elif index == 2:
                    color = 8
                elif index == 1:
                    color = 2
            elif self.pallete == 2:
                if index == 4:
                    color = 11
                elif index == 3:
                    color = 10
                elif index == 2:
                    color = 9
                elif index == 1:
                    color = 4
            pyxel.line(prev_x -x_offset, prev_y, trail_x -x_offset, trail_y, color)  # 軌跡のラインを描画
            prev_x, prev_y = trail_x, trail_y
            index -= 1
        if self.pallete == 0:        
            pyxel.pset(self.draw_x -x_offset, self.draw_y, 7)  # 主点を描画
        elif self.pallete == 1:
            pyxel.pset(self.draw_x -x_offset, self.draw_y, 10)  # 主点を描画
        elif self.pallete == 2:
            pyxel.pset(self.draw_x -x_offset, self.draw_y, 3) 

class Point3D:
    def __init__(self, center_x, center_y, center_z, radius, num_points, speed_low, speed_high, life_low, life_high, randini, pallete, cacheflg, scene):
        self.x = center_x
        self.y = center_y
        self.center = (center_x, center_y, center_z)
        self.radius = radius
        self.points = [self._create_point(speed_low, speed_high, life_low, life_high, randini, pallete, cacheflg, scene) for _ in range(num_points)]
        # self.pallete = pallete
        self.draw_x = self.x
        self.draw_y = self.y

    def _create_point(self, speed_low, speed_high, life_low, life_high, randini, pallete, cacheflg, scene):
        if randini:
            phi = random.uniform(0, 2 * math.pi)
            theta = random.uniform(0, math.pi)
            r = random.uniform(0, self.radius)  # 球の中心からのランダムな距離
            
            x = r * math.sin(theta) * math.cos(phi) + self.center[0]
            y = r * math.sin(theta) * math.sin(phi) + self.center[1]
            z = r * math.cos(theta) + self.center[2]
            self.draw_x, self.draw_y = x, y
        else:
            x, y, z = self.center
            self.draw_x, self.draw_y = x, y
        
        return Point(x, y, z, self.center[0], self.center[1], self.center[2], speed_low, speed_high, life_low, life_high, pallete, cacheflg, scene)

    def update(self):
        for point in self.points:
            point.update(self.center, self.radius)
        
        # ライフが0以下の座標セットを除去
        self.points = [point for point in self.points if point.is_alive()]

    def draw(self, x_offset=0):
        for point in self.points:
            point.draw(x_offset)

