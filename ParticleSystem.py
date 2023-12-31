import pyxel
import math
import random as Random

class ParticleSystem:

    def __init__(self):
        self.particles = []
        self.is_active = False  # 初期状態は非アクティブ
        self.timer = 0
        self.spawn_timer = 0
        self.active_duration = 0
        self.spawn_interval = 0
        self.spawn_args = None
        self.angle = 0.0
        self.current_spawns = 0
        self.total_spawns = 0
        self.speed_ranges = {0: (0.5, 2), 1: (1, 3), 2: (2, 5), 3: (3, 6)} #速度範囲のdict
        ###particle放出点の初期座標
        self.x = 0
        self.y = 0

    def activate(self, active_duration, spawn_interval, total_spawns, x, y, width, height, num_particles, pattern, size, color, speed_range, direction=0):
        """インスタンスのシステムをアクティブにし、タイマーと生成間隔をリセットする"""
        self.x = x
        self.y = y
        self.is_active = True
        self.timer = 0
        self.spawn_timer = 0
        self.active_duration = active_duration ###active_duration: アクティブになる期間（フレーム数）。この期間が経過すると、is_activeがFalseになります。
        self.spawn_interval = spawn_interval ###spawn_interval: パーティクルを生成する間隔（フレーム数）。この間隔ごとにspawn_particles_in_rectangleが呼び出されます。
        self.total_spawns = total_spawns
        self.current_spawns = 0
        self.spawn_args = (x, y, width, height, num_particles, pattern, size, color, speed_range, direction)
        self.spawn_rotate_args = (x, y, num_particles, pattern, size, color, speed_range)

    def update_particles(self,scroll_x=0,spawn_ptn=0):
        if self.is_active:
            ###現在のself.x,self.yでargsを更新
            self.spawn_args = (self.x, self.y, self.spawn_args[2], self.spawn_args[3], self.spawn_args[4], self.spawn_args[5], self.spawn_args[6], self.spawn_args[7], self.spawn_args[8], self.spawn_args[9])
            self.spawn_rotate_args = (self.x, self.y, self.spawn_rotate_args[2], self.spawn_rotate_args[3], self.spawn_rotate_args[4], self.spawn_rotate_args[5], self.spawn_rotate_args[6])
            ###タイマーを更新
            self.timer += 1
            self.spawn_timer += 1
            if self.spawn_timer % self.spawn_interval == 0:
                self.spawn_timer = 0
                if spawn_ptn == 0:
                    self.spawn_rotating_particles(*self.spawn_rotate_args)
                elif spawn_ptn == 1:
                    self.spawn_particles_in_rectangle(*self.spawn_args)
                self.current_spawns += 1
                if self.current_spawns >= self.total_spawns:
                    self.is_active = False
            ###active_durationを超えたら、非アクティブにする
            if self.timer > self.active_duration:
                self.is_active = False
            ###粒子の更新
            for particle in self.particles:
                particle.update(scroll_x)
            ### lifeが0以下の粒子を削除
            self.particles = [particle for particle in self.particles if particle.is_alive()]

    ###円形にパーティクルを生成する
    def spawn_rotating_particles(self, center_x, center_y, num_particles, pattern, size, color, specified_speed, angle_rotation_rate=0.01):
        # 現在の放射角度を更新
        self.angle += angle_rotation_rate

        for _ in range(num_particles):
            # パーティクルの放出位置と角度を計算
            self.spawn_x = center_x + math.cos(self.angle)
            self.spawn_y = center_y + math.sin(self.angle)
            ###directionが0以外の場合は、指定された方向に向かって生成する            
            self.base_angle = math.pi/2 * (math.pi/6)  # 12時を基準にするための変換
            self.angle += Random.uniform(self.base_angle - math.pi/24, self.base_angle + math.pi/24)  # 指定された方向の±15度
            ###スピードの範囲を指定
            self.speed_min, self.speed_max = self.speed_ranges[specified_speed]
            # self.speed = Random.uniform(self.speed_min, self.speed_max)
            self.speed = self.speed_min
            ###particleの寿命（フレーム数）
            self.lifespan = 20
            # パーティクルの生成
            if pattern == 0:
                self.particles.append(DotParticle(self.spawn_x, self.spawn_y, self.angle, self.speed, self.lifespan, color))       
            elif pattern == 1:
                self.particles.append(CircleParticle(self.spawn_x, self.spawn_y, self.angle, self.speed, self.lifespan, color, size))
            elif pattern == 2:
                self.particles.append(CircleParticleLine(self.spawn_x, self.spawn_y, self.angle, self.speed, self.lifespan, color, size))         
            elif pattern == 3:
                self.rotation_angle_deg = Random.uniform(0, 360)
                self.particles.append(StarParticle(self.spawn_x, self.spawn_y, size, self.angle, self.speed, self.lifespan, color, self.rotation_angle_deg))

    ###指定方向（時）の±30度の範囲でパーティクルを生成する
    def spawn_particles_in_rectangle(self, x, y, width, height, num_particles, pattern, size, color, specified_speed, direction=0):
        for _ in range(num_particles):
            # ランダムな位置と速度で星を生成
            self.spawn_x = Random.uniform(x, x + width)
            self.spawn_y = Random.uniform(y, y + height)
            self.angle = Random.uniform(0, 2 * math.pi)
            ###directionが0以外の場合は、指定された方向に向かって生成する            
            if direction != 0:
                self.base_angle = math.pi/2 - direction * (math.pi/6)  # 12時を基準にするための変換
                self.angle = Random.uniform(self.base_angle - math.pi/6, self.base_angle + math.pi/6)  # 指定された方向の±30度
            ###スピードの範囲を指定
            self.speed_min, self.speed_max = self.speed_ranges[specified_speed]
            self.speed = Random.uniform(self.speed_min, self.speed_max)
            ###particleの寿命（フレーム数）
            self.lifespan = 100
            self.rotation_angle_deg = Random.uniform(0, 360)
            self.pattern = pattern
            if self.pattern == 0:
                self.particles.append(DotParticle(self.spawn_x, self.spawn_y, self.angle, self.speed, self.lifespan, color))       
            elif self.pattern == 1:
                self.particles.append(CircleParticle(self.spawn_x, self.spawn_y, self.angle, self.speed, self.lifespan, color, size))
            elif self.pattern == 2:
                self.particles.append(CircleParticleLine(self.spawn_x, self.spawn_y, self.angle, self.speed, self.lifespan, color, size))         
            elif self.pattern == 3:
                self.particles.append(StarParticle(self.spawn_x, self.spawn_y, size, self.angle, self.speed, self.lifespan, color, self.rotation_angle_deg))

    def draw_particles(self, x_offset=0, min_x=0, max_x=0):
        for particle in self.particles:
            ###x_offsetを加味して画面内(min_x〜max_x)にある粒子のみ描画
            if particle.x - x_offset > min_x and particle.x - x_offset < max_x:
                if (isinstance(particle, DotParticle) or isinstance(particle, CircleParticle) or isinstance(particle, CircleParticleLine)):
                    particle.draw(x_offset)  
                elif isinstance(particle, StarParticle):
                    particle.draw_filled_star(particle.x -x_offset, particle.y, particle.size, particle.color, rotation_angle_deg=particle.rotation_angle_deg)


    def update_angle(self, increment=0.05):
        self.angle += increment

    def update_rotation_angle(self, increment=0.05):
        self.angle += increment


###ドット型パーティクル
class DotParticle:
    def __init__(self, x, y, angle, speed, lifespan, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.lifespan = lifespan
        self.age = 0
        self.color = color
        #self.color = Random.choice([pyxel.COLOR_ORANGE, pyxel.COLOR_YELLOW, pyxel.COLOR_RED])

    def update(self, scroll_x=0):
        self.x += self.speed * math.cos(self.angle)
        self.y -= self.speed * math.sin(self.angle)
        self.age += 1
    def is_alive(self):
        return self.age < self.lifespan
    def draw(self, x_offset=0):
        pyxel.pset(self.x -x_offset, self.y, self.color)

###円型パーティクル
class CircleParticle:
    def __init__(self, x, y, angle, speed, lifespan, color, size):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.lifespan = lifespan
        self.age = 0
        self.color = color
        self.size = size
    def update(self, scroll_x=0):
        self.x += self.speed * math.cos(self.angle)
        self.y -= self.speed * math.sin(self.angle)
        self.age += 1
    def is_alive(self):
        return self.age < self.lifespan
    def draw(self, x_offset=0):
        pyxel.circ(self.x -x_offset, self.y, self.size, self.color)

###円型パーティクル（線のみ）
class CircleParticleLine:
    def __init__(self, x, y, angle, speed, lifespan, color, size):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.lifespan = lifespan
        self.age = 0
        self.color = color
        self.size = size
    def update(self, scroll_x=0):
        self.x += self.speed * math.cos(self.angle)
        self.y -= self.speed * math.sin(self.angle)
        self.age += 1
    def is_alive(self):
        return self.age < self.lifespan
    def draw(self, x_offset=0):
        pyxel.circb(self.x -x_offset, self.y, self.size, self.color)

###星型パーティクル
class StarParticle:
    def __init__(self, x, y, size, angle, speed, lifespan, color, rotation_angle_deg):
        self.x = x
        self.y = y
        self.size = size
        self.angle = angle  # 移動の方向を指定する角度
        self.rotation_angle_deg = rotation_angle_deg  # 星を回転させる角度
        self.speed = speed
        self.lifespan = lifespan
        self.age = 0
        self.color = color
        self.new_x = 0
        self.new_y = 0
        self.angles_deg_outer = []
        self.points_outer = []
        self.r_inner = 0
        self.angles_deg_inner = []
        self.points_inner = []

    def update(self, scroll_x=0):
        self.x += self.speed * math.cos(self.angle)
        self.y -= self.speed * math.sin(self.angle)  # 上向きに移動するため、yを減少させる
        self.age += 1
    def is_alive(self):
        return self.age < self.lifespan
    
    def rotate_point(self, x, y, angle_rad):
        """座標を指定された角度で回転させる"""
        self.new_x = x * math.cos(angle_rad) - y * math.sin(angle_rad)
        self.new_y = x * math.sin(angle_rad) + y * math.cos(angle_rad)
        return self.new_x, self.new_y

    def draw_filled_star(self, x, y, r, color, rotation_angle_deg=0):
        # 五芒星の外周の頂点を計算
        self.angles_deg_outer = [72 * i - 90 for i in range(5)]
        self.points_outer = [(x + r * math.cos(math.radians(ang)), y + r * math.sin(math.radians(ang))) for ang in self.angles_deg_outer]
        
        # 五芒星の内周の頂点を計算
        self.r_inner = r * (3 - math.sqrt(5)) / 2
        self.angles_deg_inner = [72 * i - 54 for i in range(5)]
        self.points_inner = [(x + self.r_inner * math.cos(math.radians(ang)), y + self.r_inner * math.sin(math.radians(ang))) for ang in self.angles_deg_inner]
        
        # 五芒星の全頂点
        self.points_star = [self.points_outer[i] for i in range(5)]
        for i in range(5):
            self.points_star.insert(2 * i + 1, self.points_inner[i])
        
        # 全頂点を指定された角度で回転させる
        self.rotation_angle_rad = math.radians(rotation_angle_deg)
        self.points_star = [self.rotate_point(px - x, py - y, self.rotation_angle_rad) for px, py in self.points_star]
        self.points_star = [(px + x, py + y) for px, py in self.points_star]
        
        # 全頂点を指定された角度で回転させる
        self.rotation_angle_rad = math.radians(rotation_angle_deg)
        self.points_star = [self.rotate_point(px - x, py - y, self.rotation_angle_rad) for px, py in self.points_star]
        self.points_star = [(px + x, py + y) for px, py in self.points_star]
        
        # アウトラインを描画
        for i in range(10):
            start_point = self.points_star[i]
            end_point = self.points_star[(i + 1) % 10]
            pyxel.line(int(start_point[0]), int(start_point[1]), int(end_point[0]), int(end_point[1]), color)
