
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






###双曲線螺旋: 双曲線を用いた螺旋放射。
def hyperbolic_spiral_burst(z, a, b, num_particles):
    return [z + complex(a * Math.cos(t) - b * Math.sin(t), a * Math.sin(t) + b * Math.cos(t)) for t in range(num_particles)]

###正n星形: n角形の星形を形成する放射状。
def star_polygon_burst(z, n, expansion_rate):
    skip = n // 2  # for simple star patterns
    return [z * Exp(1j * 2 * Math.pi * i * skip / n) * expansion_rate for i in range(n)]

###アーチメデスの螺旋: アーチメデスの螺旋を用いた放射。
def star_polygon_burst(z, n, expansion_rate):
    skip = n // 2  # for simple star patterns
    return [z * Exp(1j * 2 * Math.pi * i * skip / n) * expansion_rate for i in range(n)]

###モビウス変換: モビウス変換を用いた放射。
def mobius_transform(z, a, b, c, d):
    return (a * z + b) / (c * z + d)

###ベジエ曲線放射: ベジエ曲線に沿った放射。
from cmath import exp, phase
def bezier_curve_burst(z, control_point, t, expansion_rate, num_particles):
    b = (1 - t) * z + t * control_point
    return [z + exp(1j * phase(b)) * expansion_rate for _ in range(num_particles)]


###カンターセット放射: カンターセットを用いた放射。
def cantor_set_burst(z, expansion_rate, num_particles, depth=0):
    if depth >= num_particles:
        return []
    cantor_distance = expansion_rate / (3 ** (depth + 1))
    left = z - complex(cantor_distance, 0)
    right = z + complex(cantor_distance, 0)
    return [left, right] + cantor_set_burst(left, expansion_rate, num_particles, depth + 1) + cantor_set_burst(right, expansion_rate, num_particles, depth + 1)


###Sierpińskiの三角形: Sierpińskiの三角形に基づく放射。
def sierpinski_triangle_burst(z, expansion_rate, depth):
    if depth == 0:
        return [z]
    top = z + complex(0, expansion_rate)
    left = z + complex(-expansion_rate * Math.cos(Math.pi/3), -expansion_rate * Math.sin(Math.pi/3))
    right = z + complex(expansion_rate * Math.cos(Math.pi/3), -expansion_rate * Math.sin(Math.pi/3))
    return sierpinski_triangle_burst(top, expansion_rate / 2, depth - 1) + \
           sierpinski_triangle_burst(left, expansion_rate / 2, depth - 1) + \
           sierpinski_triangle_burst(right, expansion_rate / 2, depth - 1)

###楕円放射: 楕円軌道に沿った放射。
def elliptical_burst(z, a, b, num_particles):
    return [z + complex(a * Math.cos(2 * Math.pi * i / num_particles), b * Math.sin(2 * Math.pi * i / num_particles)) for i in range(num_particles)]

###ユークリッドの互除法: ユークリッドの互除法に基づく放射。
def euclid_burst(z, a, b, expansion_rate):
    angles = []
    while b != 0:
        angles.append(a)
        a, b = b, a % b
    # anglesリストの値を放射の角度として用いる
    particles = [z + Exp(1j * 2 * Math.pi * angle / sum(angles)) * expansion_rate for angle in angles]    
    return particles

###ルーカス数列: ルーカス数列に基づき相対距離を計算し放射。
def lucas_firework(z, n):
    lucas_numbers = [2, 1]
    for _ in range(2, n):
        lucas_numbers.append(lucas_numbers[-1] + lucas_numbers[-2])
    particles = []
    for l in lucas_numbers:
        angle = 2 * Math.pi * l / max(lucas_numbers)
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
def harshad_firework(z, n):
    divisors = [i for i in range(1, n + 1) if n % i == 0]
    particles = []
    for divisor in divisors:
        angle = 2 * Math.pi * divisor / n
        particles.append(z * Exp(1j * angle))
    return particles

###モーザーズ数に基づいて円周上に均等にパーティクルを放出
def moser_firework(z, n):
    particles = []
    for i in range(n):
        angle = 2 * Math.pi * i / n
        particles.append(z * Exp(1j * angle))
    return particles

###ハッピー数: ハッピー数に基づく放射。放射角度をハッピー数にする。
def is_happy(num):
    seen = set()
    while num != 1 and num not in seen:
        seen.add(num)
        num = sum(int(i)**2 for i in str(num))
    return num == 1
def happy_firework(z, n):
    happy_numbers = [i for i in range(1, n+1) if is_happy(i)]
    particles = []
    for h in happy_numbers:
        angle = 2 * Math.pi * h / n
        particles.append(z * Exp(1j * angle))
    return particles

###魔法陣定数:nxnのグリッドに基づく放射
def magic_square_firework(z, n):
    particles = []
    for i in range(n):
        for j in range(n):
            offset = complex(i, j) - complex(n/2, n/2)
            particles.append(z + offset)
    return particles


###四角形数に基づく相対距離
def square_number_firework(z, n):
    square_numbers = [i**2 for i in range(1, int(n**0.5)+1)]
    particles = []
    for s in square_numbers:
        angle = 2 * Math.pi * s / max(square_numbers)
        particles.append(z * Exp(1j * angle))
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

###パドヴァン数列：3つ前のパーティクルの位置に基づく放射
def padovan_firework(z, n):
    padovan = [1, 1, 1]
    for _ in range(3, n):
        padovan.append(padovan[-2] + padovan[-3])
    particles = []
    for p in padovan:
        angle = 2 * Math.pi * p / max(padovan)
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
# ###球面放射するパーティクルを複素平面上に射影する花火関数（必ず放射の中心座標を(x,y,0)平面上に生成）
# def radiating_sphere_projection_burst(z, r, num_particles, expansion_rate):
#     particles = []
#     for i in range(num_particles):
#         theta = Math.acos(1 - 2 * i / num_particles)  # 緯度を均等に分布
#         phi = Math.sqrt(num_particles * Math.pi) * theta  # 経度を均等に分布
#         # 放射による拡大を考慮して距離を調整
#         dist = r + expansion_rate
#         # 放射を考慮した球面上の座標を計算
#         x = dist * Math.sin(theta) * Math.cos(phi) + z.real  # 放射中心のx座標を足す
#         y = dist * Math.sin(theta) * Math.sin(phi) + z.imag  # 放射中心のy座標を足す
#         # 複素数として追加
#         particles.append(complex(x, y))
#     return particles
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
        self.burst_funcs = [radial_burst, spiral_burst, triangular_burst, random_burst, heart_shape, star_burst, 
                            spiral_recursive_burst, fibonacci_burst, fibonacci_burst_multiple, ring_burst, ring_burst2, 
                            multi_ring_burst, halo_burst, radiating_sphere_projection_burst, hyperbolic_spiral_burst, star_polygon_burst, 
                            mobius_transform, bezier_curve_burst, cantor_set_burst, sierpinski_triangle_burst, elliptical_burst,
                            euclid_burst, lucas_firework, pascal_firework, harshad_firework, moser_firework, happy_firework,
                            magic_square_firework, square_number_firework, pell_firework, padovan_firework, sylvester_firework]
        self.burst_funcs_maxindex = len(self.burst_funcs) - 1
        # self.burst_func = Random.choice(self.burst_funcs)
        # self.burst_func = self.burst_funcs[2]
        # self.burst_func = self.burst_funcs[self.burst_funcs_maxindex]
        # self.burst_func = self.burst_funcs[13] # 13: radiating_sphere_projection_burstまで調整完了済みです. 20230905
        self.burst_func = self.burst_funcs[Random.randrange(0,14)]

        # self.update()


    def update(self):
        if self.life > 0:
            if self.y > self.peak and self.active:
                self.y -= self.vy  # 上昇
                self.draw_y = self.y                
            elif self.active:
                if self.burst_func   == radial_burst: ###調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 100, 25)
                elif self.burst_func == spiral_burst: ###調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 100, 20, Random.randrange(1, 4))
                elif self.burst_func == triangular_burst: ###調整済 
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), Random.uniform(10, 20), 100, Random.randrange(2, 5))
                elif self.burst_func == random_burst: ###調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 60, 100)
                elif self.burst_func == heart_shape: ###調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 2)
                elif self.burst_func == star_burst: ###調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), Random.randrange(15, 30))
                elif self.burst_func == spiral_recursive_burst: ###調整済
                    rotation_offset = Random.uniform(-0.5, 0.5)
                    branch_count = Random.choice([5, 6, 8, 10])
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 2, 12, 8.0, rotation_offset, branch_count)
                elif self.burst_func == fibonacci_burst: ###調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 42, 100)
                elif self.burst_func == fibonacci_burst_multiple: ###調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), [0.25, 0.375, 0.5], 100, self.life)
                elif self.burst_func == ring_burst: ###調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), Random.choice([8, 12, 15]), 100, 5)
                elif self.burst_func == ring_burst2: ###調整済
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), Random.choice([8, 12, 15]), 100, 5)
                elif self.burst_func == multi_ring_burst: ###調整済
                    index = Random.randrange(0, 3)
                    radius = [4, 6, 8]
                    particle_num = [18, 20, 26]
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), radius[index], 4, particle_num[index])
                elif self.burst_func == halo_burst: 
                    index = Random.randrange(0, 3)
                    radius = [15, 20, 30]
                    particle_num = [40, 60, 80]
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), 2, radius[index], particle_num[index])

                elif self.burst_func == radiating_sphere_projection_burst:
                    index = Random.randrange(0, 3)
                    radius = [40, 50, 65]
                    particle_num = [100, 150, 250]
                    self.burst = self.burst_func(complex(self.draw_x, self.draw_y), radius[index], particle_num[index], 1.2, self.life)

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

