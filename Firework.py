import math as Math
from cmath import exp as Exp
import random as Random

def radial_burst(z, num_particles, expansion_rate):
    return [z + Exp(1j * 2 * Math.pi * i / num_particles) * expansion_rate for i in range(num_particles)]

def spiral_burst(z, num_particles, expansion_rate, num_turns):
    return [z + Exp(1j * 2 * Math.pi * i * num_turns / num_particles) * expansion_rate for i in range(num_particles)]

###三角波放射状: 放射状に火花を放出するが、三角波の形状を模倣します。
def triangular_burst(z, expansion_rate, num_particles, num_rings=2):
    particles = []
    for i in range(num_particles):
        factor = i % num_rings + 1
        angle = 2 * Math.pi * i / num_particles
        distance = expansion_rate * factor
        particles.append(z + distance * Exp(1j * angle))
    return particles

###ランダム放射状: 放射の角度をランダムにします。
def random_burst(z, expansion_rate, num_particles):
    return [z + Exp(1j * Random.uniform(0, 2*Math.pi)) * expansion_rate for _ in range(num_particles)]

###ハート形状: ハートの形状で火花を放出します。
def heart_shape(z, expansion_rate):
    particles = []
    for t in [i * 2 * Math.pi / 100 for i in range(101)]:
        x = 16 * Math.sin(t)**3
        y = -(13*Math.cos(t) - 5*Math.cos(2*t) - 2*Math.cos(3*t) - Math.cos(4*t)) ##pyxel描画用に符号を反転
        particles.append(z + complex(x, y) * expansion_rate)
    return particles

###五芒星: 火花を五芒星の形状で放出します。
def star_burst(z, expansion_rate):
    particles = []    
    # ランダムなオフセット角度を0から2πの範囲で生成
    random_offset = Random.uniform(0, 2*Math.pi)
    # 外側の五芒星の座標を計算
    for i in range(5):
        angle = i * 2 * Math.pi * 2/5 + random_offset
        particles.append(z + complex(Math.cos(angle), Math.sin(angle)) * expansion_rate)
    # 内側の反転させた五芒星の座標を計算
    inner_expansion_rate = expansion_rate * 0.5  # この値は適宜調整してください
    for i in range(5):
        angle = i * 2 * Math.pi * 2/5 + Math.pi/5 + random_offset  # π/5を加えることで角度を半分にして反転させます
        particles.append(z + complex(Math.cos(angle), Math.sin(angle)) * inner_expansion_rate)
    return particles

###螺旋の三次分岐: 火花が再帰的に3つの螺旋で分岐します。
def spiral_recursive_burst(z, depth, expansion_rate, spiral_factor, rotation_offset, branch_count):
    if depth == 0:
        return [z]
    particles = [z]
    for i in range(branch_count):
        angle = i * 2 * Math.pi / branch_count + spiral_factor + rotation_offset
        delta_z = Exp(1j * angle) * expansion_rate
        new_z = z + delta_z
        particles.extend(spiral_recursive_burst(new_z, depth-1, expansion_rate, spiral_factor, rotation_offset, branch_count))
    return particles


###ファイボナッチ放射状: ファイボナッチ数列に基づいて火花を放出します。
def fibonacci_burst(z, expansion_rate, num_particles):
    phi = (1 + 5**0.5) / 2  # Golden ratio
    # zの位置からの相対座標を計算
    relative_coordinates = [Exp(1j * 2 * Math.pi * phi * i) * expansion_rate for i in range(num_particles)]
    # zを中心にした放射の座標を返す
    return [z + rc for rc in relative_coordinates]

###ファイボナッチ放射状　ーN次
def fibonacci_burst_multiple(z, expansion_rates, num_particles, life):
    phi = (1 + 5**0.5) / 2  # Golden ratio
    coordinates = []
    adjusted_rates = [rate * life for rate in expansion_rates]  # lifeに基づいて放射の広がりを調整
    for rate in adjusted_rates:
        # 各リングのzの位置からの相対座標を計算
        relative_coordinates = [Exp(1j * 2 * Math.pi * phi * i) * rate for i in range(num_particles)]
        # zを中心にした放射の座標を結合
        coordinates.extend([z + rc for rc in relative_coordinates])
    return coordinates

###リング爆発: 火花をリング状に放出します。
def ring_burst(z, expansion_rate, num_particles, width):
    particles = []
    base_angle = Random.uniform(0, 2*Math.pi)
    for i in range(num_particles):
        angle = 2 * Math.pi * i / num_particles
        # distance = expansion_rate + Random.uniform(-width, width) ###ランダムでゆらぎを表現
        distance = expansion_rate + (i % 10) + width ###らせん状にプロットが行われる
        particles.append(z + Exp(1j * (base_angle + angle)) * distance)
    return particles

def ring_burst2(z, expansion_rate, num_particles, width):
    particles = []
    base_angle = Random.uniform(0, 2*Math.pi)
    for i in range(2 * num_particles):  # パーティクルの数を2倍に
        angle = 2 * Math.pi * i / num_particles
        distance = expansion_rate + (i % 20) + width
        # 奇数のパーティクルは左巻きの螺旋、偶数のパーティクルは右巻きの螺旋になるように設定
        if i % 2 == 0:
            particles.append(z + Exp(1j * (base_angle + angle)) * distance)
        else:
            particles.append(z + Exp(1j * (base_angle - angle)) * distance)  # angleの方向を反転
    return particles

###複数リング爆発: 複数のリングで火花を放出します。
def multi_ring_burst(z, expansion_rate, num_rings, num_particles):
    particles = []
    base_angle = Random.uniform(0, 2*Math.pi)
    for j in range(num_rings):
        for i in range(num_particles):
            angle = 2 * Math.pi * i / num_particles
            distance = expansion_rate * (j + 1)
            particles.append(z + Exp(1j * (base_angle + angle)) * distance)
    return particles

###ハロー爆発: 一定の距離を保ちつつ放射する。
def halo_burst(z, expansion_rate, width, num_particles):
    particles = []
    for i in range(num_particles):
        angle = 2 * Math.pi * i / num_particles
        # distance = expansion_rate + Random.uniform(-width, width)
        distance = expansion_rate + Math.sin(i * Math.pi/3) + width
        particles.append(z + complex(Math.cos(angle) * distance, Math.sin(angle) * distance))
    return particles

###球面放射するパーティクルを複素平面上に射影する花火関数（必ず放射の中心座標を(x,y,0)平面上に生成）、framecountに応じて回転する
def radiating_sphere_projection_burst(z, r, num_particles, expansion_rate, life):
    particles = []
    # lifeに基づいてランダムな角度を生成
    random_angle = life * Random.random() * 2 * Math.pi
    for i in range(num_particles):
        theta = Math.acos(1 - 2 * i / num_particles)  # 緯度を均等に分布
        phi = Math.sqrt(num_particles * Math.pi) * theta  # 経度を均等に分布
        # 放射による拡大を考慮して距離を調整
        dist = r + expansion_rate
        # 放射を考慮した球面上の座標を計算
        x_relative = dist * Math.sin(theta) * Math.cos(phi)
        y_relative = dist * Math.sin(theta) * Math.sin(phi)
        z_relative = dist * Math.cos(theta)
        # X軸を中心にalphaだけ回転させる
        y_rotated = y_relative * Math.cos(random_angle) - z_relative * Math.sin(random_angle)
        z_rotated = y_relative * Math.sin(random_angle) + z_relative * Math.cos(random_angle)
        # 放射の中心点として与えられたz（x, y）を加味して座標を調整
        x_final = z.real + x_relative
        y_final = z.imag + y_rotated
        # 複素数として追加
        particles.append(complex(x_final, y_final))
    return particles

###双曲線螺旋: 双曲線を用いた螺旋放射。
def hyperbolic_spiral_burst(z, a, b, num_particles):
    return [z + complex(a * Math.cos(t) - b * Math.sin(t), a * Math.sin(t) + b * Math.cos(t)) for t in range(num_particles)]

###ベジエ曲線放射: ベジエ曲線に沿った放射。
from cmath import exp, phase
def bezier_curve_burst(z, control_point, t, expansion_rate, num_particles):
    b = (1 - t) * z + t * control_point
    # return [z + exp(1j * phase(b)) * expansion_rate for _ in range(num_particles)]
    return [z * expansion_rate for _ in range(num_particles)]

###Sierpińskiの三角形: Sierpińskiの三角形に基づく放射。
def rotate_point(point, angle, center):
    return exp(1j * angle) * (point - center) + center
def sierpinski_triangle_burst(z, expansion_rate, depth, angle=None):
    if angle is None:
        angle = Random.uniform(0, 2 * Math.pi)  # ランダムな回転角を生成
    if depth == 0:
        return [rotate_point(z, angle, z)]
    top = z + complex(0, expansion_rate)
    left = z + complex(-expansion_rate * Math.cos(Math.pi/6), -expansion_rate * Math.sin(Math.pi/6))
    right = z + complex(expansion_rate * Math.cos(Math.pi/6), -expansion_rate * Math.sin(Math.pi/6))
    return sierpinski_triangle_burst(rotate_point(top, angle, z), expansion_rate / 2, depth - 1, angle) + \
           sierpinski_triangle_burst(rotate_point(left, angle, z), expansion_rate / 2, depth - 1, angle) + \
           sierpinski_triangle_burst(rotate_point(right, angle, z), expansion_rate / 2, depth - 1, angle)

###楕円放射: 楕円軌道に沿った放射。
def elliptical_burst(z, a, b, num_particles):
    angle = Random.uniform(0, 2 * Math.pi)  # ランダムな回転角を生成
    return [rotate_point(z + complex(a * Math.cos(2 * Math.pi * i / num_particles), b * Math.sin(2 * Math.pi * i / num_particles)),angle,z) for i in range(num_particles)]

###ルーカス数列: ルーカス数列に基づき相対距離を計算し放射。
def lucas_firework(z, n):
    lucas_numbers = [2, 1]
    for _ in range(2, n):
        lucas_numbers.append(lucas_numbers[-1] + lucas_numbers[-2])
    particles = []
    for l in lucas_numbers:
        angle = 8 * Math.pi * l / max(lucas_numbers) * 15
        particles.append(z * Exp(1j * angle))
    return particles

###パスカルの三角形: パスカルの三角形に基づく放射。
def pascal_firework(z, layers):
    triangle = [[1]]
    particles = [z]
    for i in range(1, layers):
        row = [sum(pair) for pair in zip([0] + triangle[-1], triangle[-1] + [0])]
        triangle.append(row)
        for j in row:
            angle = 2 * Math.pi * j / sum(row)
            particles.append(z * Exp(1j * angle))
    return particles

###ハーシャッド数の約数の数に基づく放射のブロックを生成
def harshad_firework(z, r, n):
    divisors = [i for i in range(1, n + 1) if n % i == 0]
    particles = []
    for divisor in divisors:
        angle = 2 * Math.pi * divisor / n
        # オフセットを計算
        offset = Exp(1j * angle)
        particles.append((r * z + offset) * Exp(1j * angle))
    return particles

###モーザーズ数に基づいて円周上に均等にパーティクルを放出
def moser_firework(z, r, n):
    particles = []
    for i in range(n):
        angle = 2 * Math.pi * i / n
        # 半径 r を考慮したオフセットを計算
        offset = r * Exp(1j * angle)
        particles.append((z + offset))
    return particles

###ハッピー数: ハッピー数に基づく放射。放射角度をハッピー数にする。
def is_happy(num):
    seen = set()
    while num != 1 and num not in seen:
        seen.add(num)
        num = sum(int(i)**2 for i in str(num))
    return num == 1
def happy_firework(z, r, n):
    happy_numbers = [i for i in range(1, n+1) if is_happy(i)]
    particles = []
    for h in happy_numbers:
        angle = 2 * Math.pi * h / n
        # 半径 r を考慮したオフセットを計算
        offset = r * Exp(1j * angle)
        particles.append(z + offset)
    return particles

###魔法陣定数:nxnのグリッドに基づく放射
def magic_square_firework(z, r, n):
    particles = []
    angle = Random.uniform(0, 2 * Math.pi)  # ランダムな回転角を生成
    for i in range(n):
        for j in range(n):
            offset = r * (complex(i, j) - complex(n/2, n/2)) * Exp(1j * angle)
            particles.append(z + offset)
    return particles

###ペル数列:ペル数に基づくスパイラル放射
def pell_firework(z, n):
    pell_numbers = [0, 1]
    for i in range(2, n):
        pell_numbers.append(2 * pell_numbers[-1] + pell_numbers[-2])
    particles = []
    for p in pell_numbers:
        angle = 2 * Math.pi * p / max(pell_numbers)
        particles.append(z * Exp(1j * angle))
    return particles

###シルヴェスター数列: 各シルヴェスター数の位置に基づく放射。
def sylvester_firework(z, n):
    sylvester = [2]
    for _ in range(1, n):
        sylvester.append(sylvester[-1] * (sylvester[-1] - 1) + 1)
    particles = []
    for s in sylvester:
        angle = 2 * Math.pi * s / max(sylvester)
        particles.append(z * Exp(1j * angle))
    return particles

##-----------

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.draw_x = self.x
        self.draw_y = self.y
        self.peak = self.draw_y - Random.randrange(70, 140)  # 最大高度（鉛直投射の軌跡）
        self.vy = Random.randrange(1, 3)  # 上昇速度
        self.active = True
        self.burst = None
        self.life = 100 # 花火の寿命
        self.rotation_angle = 0  # 花火の回転角度　。。。３次元球面花火用
        self.multi_color_num = 1

        # すべての花火関数をリストに追加
        # self.burst_funcs = [radial_burst, spiral_burst, triangular_burst, random_burst, heart_shape, star_burst, 
        #                     spiral_recursive_burst, fibonacci_burst, fibonacci_burst_multiple, ring_burst, ring_burst2, 
        #                     multi_ring_burst, halo_burst, radiating_sphere_projection_burst, hyperbolic_spiral_burst, sierpinski_triangle_burst, elliptical_burst,
        #                     lucas_firework, pascal_firework, harshad_firework, moser_firework, happy_firework,
        #                     magic_square_firework, pell_firework, sylvester_firework]
        self.burst_funcs = [radial_burst, spiral_burst, triangular_burst, random_burst, heart_shape, star_burst, 
                            spiral_recursive_burst, fibonacci_burst, fibonacci_burst_multiple, ring_burst, ring_burst2, 
                            multi_ring_burst, halo_burst, radiating_sphere_projection_burst, hyperbolic_spiral_burst, sierpinski_triangle_burst, elliptical_burst,
                            moser_firework, magic_square_firework]
        
        self.burst_funcs_maxindex = len(self.burst_funcs) - 1
        # self.burst_func = self.burst_funcs[17] 垂れる花火をリストから除外。#20231231
        self.burst_func = self.burst_funcs[Random.randrange(0,self.burst_funcs_maxindex)]

    def update(self):
        if self.life > 0:
            if self.y > self.peak and self.active:
                self.y -= self.vy  # 上昇
                self.draw_y = self.y                
            elif self.active:
                if self.burst_func   == radial_burst: ###No.00調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 100, 25)
                elif self.burst_func == spiral_burst: ###No.01調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 100, 20, Random.randrange(1, 4))
                elif self.burst_func == triangular_burst: ###No.02調整済 
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), Random.uniform(10, 20), 100, Random.randrange(2, 5))
                elif self.burst_func == random_burst: ###No.03調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 60, 100)
                elif self.burst_func == heart_shape: ###No.04調整済 ハート状放射
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 2)
                elif self.burst_func == star_burst: ###No.05調整済　星型放射
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), Random.randrange(15, 30))
                elif self.burst_func == spiral_recursive_burst: ###No.06調整済
                    rotation_offset = Random.uniform(-0.5, 0.5)
                    branch_count = Random.choice([5, 6, 8, 10])
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 2, 12, 8.0, rotation_offset, branch_count)
                elif self.burst_func == fibonacci_burst: ###No.07調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 42, 100)
                elif self.burst_func == fibonacci_burst_multiple: ###No.08調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), [0.25, 0.375, 0.5], 100, self.life)
                elif self.burst_func == ring_burst: ###No.09調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), Random.choice([8, 12, 15]), 100, 5)
                elif self.burst_func == ring_burst2: ###No.10調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), Random.choice([8, 12, 15]), 100, 5)
                elif self.burst_func == multi_ring_burst: ###No.11調整済
                    index = Random.randrange(0, 3)
                    radius = [4, 6, 8]
                    particle_num = [18, 20, 26]
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), radius[index], 4, particle_num[index])
                elif self.burst_func == halo_burst:  ###No.12調整済 ハロー放射三次元球面
                    index = Random.randrange(0, 3)
                    radius = [15, 20, 30]
                    particle_num = [40, 60, 80]
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 2, radius[index], particle_num[index])
                elif self.burst_func == radiating_sphere_projection_burst: ###No.13調整済 三次元球面花火
                    index = Random.randrange(0, 3)
                    radius = [40, 50, 65]
                    particle_num = [100, 150, 250]
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), radius[index], particle_num[index], 1.2, self.life)
                elif self.burst_func == hyperbolic_spiral_burst: ###No.14調整済 円状放射
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), Random.choice([8, 12, 15]), 30, 20)
                elif self.burst_func == sierpinski_triangle_burst: ###No.15調整済 シェルピンスキーの三角形
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 20, 4)
                elif self.burst_func == elliptical_burst: ###No.16 調整済 楕円状放射
                    major_axis = Random.randrange(35, 45)
                    minor_axis = Random.randrange(20, 30)
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), major_axis, minor_axis, 40)
                # elif self.burst_func == lucas_firework: ###No.17調整済.　左下へと流れる花火
                #     self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 200)
                # elif self.burst_func == pascal_firework: ###No.18調整済。　左下へと流れる花火
                #     self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 10)
                # elif self.burst_func == harshad_firework: ###No.19調整済。　左下へと流れる花火
                #     self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 0.8, 100)
                elif self.burst_func == moser_firework: ###No.20調整済。　円状放射
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 45, 36)
                elif self.burst_func == happy_firework: ###No.21調整済。
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 30, 50)
                elif self.burst_func == magic_square_firework: ###No.22調整済。
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 6, 8)
                elif self.burst_func == pell_firework: ###No.23調整済。
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 100)
                # ... 同様に、他の関数も条件分岐して引数を設定 ...
                else:
                    # 未対応の関数についてはエラーが発生しないようにデフォルトの動作を設定
                    self.burst = []
                self.active = False  # 花火の動きを停止
            else:
                self.expand_burst()  # ピークに達した後は放射を拡大
                self.life -= 1 # 花火の寿命を減らす

    def expand_burst(self):
        expansion_factor = 1.0028  # 拡大率を設定
        # 元の中心からの相対的な位置に放射座標を移動
        relative_burst = [complex(pt.real - self.draw_x, pt.imag - self.draw_y) for pt in self.burst]
        # 相対的な位置で放射座標を拡大
        expanded_burst = [complex(pt.real * expansion_factor, pt.imag * expansion_factor) for pt in relative_burst]
        # 拡大した放射座標を元の中心に戻す
        self.burst = [complex(pt.real + self.draw_x, pt.imag + self.draw_y) for pt in expanded_burst]

    def expand_and_rotate_burst(self, angle):
        expansion_factor = 1.0028
        # 拡大
        expanded_burst = [complex(pt.real * expansion_factor, pt.imag * expansion_factor) for pt in self.burst]
        # 拡大した放射座標をFireworkの中心座標を中心に回転させる
        rotated_burst = [self.rotate_point(pt, complex(self.draw_x, self.draw_y), angle) for pt in expanded_burst]
        self.burst = rotated_burst

    def rotate_point(self, point, center, angle):
        """
        与えられた複素数座標を指定された中心座標を中心に指定された角度で回転させます。
        """
        # 中心を原点に移動
        translated_point = complex(point.real - center.real, point.imag - center.imag)
        # 移動した点を回転
        rotated_real = translated_point.real * Math.cos(angle) - translated_point.imag * Math.sin(angle)
        rotated_imag = translated_point.real * Math.sin(angle) + translated_point.imag * Math.cos(angle)
        rotated_point = complex(rotated_real, rotated_imag)
        # 回転した点を元の中心に戻す
        return complex(rotated_point.real + center.real, rotated_point.imag + center.imag)
