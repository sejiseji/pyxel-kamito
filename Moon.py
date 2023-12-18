import pyxel
import math
import random

class Moon:
    def __init__(self, center_x, center_y, radius, increment=0.001, num_seas=100, num_stars=400):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.last_framecount = pyxel.frame_count
        self.current_phase = 0.0  # 初期フェーズ
        self.increment = increment
        self.num_seas = num_seas
        self.seas = self.generate_seas()
        self.stars = self.generate_stars(num_stars)

    def generate_seas(self):
        seas = []
        for _ in range(self.num_seas):
            while True:
                r = random.uniform(0.01 * self.radius, 0.15 * self.radius)
                x = random.uniform(self.center_x - self.radius + r, self.center_x + self.radius - r)
                y = random.uniform(self.center_y - self.radius + r, self.center_y + self.radius - r)
                distance = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
                if distance + r < self.radius:
                    seas.append((x, y, r))
                    break
        return seas

    def generate_stars(self, num_stars):
        return [(random.randint(0, pyxel.width * 2), random.randint(0, pyxel.height)) for _ in range(num_stars)]
    
    def update(self):
        # framecountに基づいて月の満ち欠けを更新
        delta_time = pyxel.frame_count - self.last_framecount
        self.last_framecount = pyxel.frame_count
        phase_increment = delta_time * self.increment  # この値を調整して、満ち欠けの速度を変更
        self.current_phase = (self.current_phase + phase_increment) % 1.0

    def draw(self, camera_x=0, scroll_speeds=[0.95, 1.05, 0.90, 1.15]):
        angle = self.current_phase * 2 * math.pi

        # 星を描画
        num_stars = len(self.stars) - 1
        for i in range(num_stars):
            pllx_camera_x = 0
            if i % 4 == 0:
                pllx_camera_x = camera_x * scroll_speeds[0]
            elif i % 4 == 1:
                pllx_camera_x = camera_x * scroll_speeds[1]
            elif i % 4 == 2:
                pllx_camera_x = camera_x * scroll_speeds[2]
            elif i % 4 == 3:
                pllx_camera_x = camera_x * scroll_speeds[3]
            pyxel.pset(self.stars[i][0] -pllx_camera_x, self.stars[i][1], 7)

        # 月の本体（常に表示）
        pyxel.circ(self.center_x -camera_x, self.center_y, self.radius, 10)

        # 月の海（常に表示）
        for x, y, r in self.seas:
            pyxel.circ(x -camera_x, y, r, 9)

        if 0 < self.current_phase < 0.5:
            shadow_radius = self.radius * (1 - 2 * self.current_phase)
            pyxel.circ(self.center_x + (self.radius - shadow_radius) -camera_x, self.center_y, shadow_radius, 0)
        elif 0.5 < self.current_phase < 1:
            shadow_radius = self.radius * (2 * self.current_phase - 1)
            pyxel.circ(self.center_x - (self.radius - shadow_radius) -camera_x, self.center_y, shadow_radius, 0)







# import pyxel
# import math
# import random

# class Moon:
#     def __init__(self, center_x, center_y, radius, increment=0.001, num_seas=100):
#         self.center_x = center_x
#         self.center_y = center_y
#         self.radius = radius
#         self.last_framecount = pyxel.frame_count
#         self.current_phase = 0.0  # 初期フェーズ
#         self.increment = increment
#         self.num_seas = num_seas
#         self.seas = self.generate_seas()

#     def generate_seas(self):
#         seas = []
#         for _ in range(self.num_seas):
#             while True:
#                 r = random.uniform(0.01 * self.radius, 0.15 * self.radius)
#                 x = random.uniform(self.center_x - self.radius + r, self.center_x + self.radius - r)
#                 y = random.uniform(self.center_y - self.radius + r, self.center_y + self.radius - r)
#                 distance = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
#                 if distance + r < self.radius:
#                     seas.append((x, y, r))
#                     break
#         return seas
    
#     def update(self):
#         # framecountに基づいて月の満ち欠けを更新
#         delta_time = pyxel.frame_count - self.last_framecount
#         self.last_framecount = pyxel.frame_count
#         phase_increment = delta_time * self.increment  # この値を調整して、満ち欠けの速度を変更
#         self.current_phase = (self.current_phase + phase_increment) % 1.0

#     def draw(self):
#         angle = self.current_phase * 2 * math.pi

#         # 月の本体（常に表示）
#         pyxel.circ(self.center_x, self.center_y, self.radius, 10)

#         # 月の海（常に表示）
#         # pyxel.circ(self.center_x, self.center_y/4, self.radius/6, 9)
#         for x, y, r in self.seas:
#             pyxel.circ(x, y, r, 9)

        
#         if 0 < self.current_phase < 0.5:
#             shadow_radius = self.radius * (1 - 2 * self.current_phase)
#             pyxel.circ(self.center_x + (self.radius - shadow_radius), self.center_y, shadow_radius, 0)
#         elif 0.5 < self.current_phase < 1:
#             shadow_radius = self.radius * (2 * self.current_phase - 1)
#             pyxel.circ(self.center_x - (self.radius - shadow_radius), self.center_y, shadow_radius, 0)
