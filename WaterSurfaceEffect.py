import pyxel
import random

class WaterSurfaceEffect:
    def __init__(self, x_start, y_start, width, height):
        self.x_start = x_start
        self.y_start = y_start
        self.width = width
        self.height = height
        self.reflection_data = [self.generate_reflection() for _ in range(30)]
        self.sparkle_data = [self.generate_sparkle() for _ in range(50)]
        
        # 新たに追加する変数
        self.stretch_frame_count = 0
        self.stretch_direction = 1  # 1: 伸びる, -1: 縮む

        # 新たに追加する変数
        self.pattern_state = 0
        self.current_pattern = random.choice([1, 2, 3])  # 初期パターンをランダムに設定

        self.stretch_increment = random.choice([0.2, 0.3, 0.4]) # 伸縮の変化量

    def generate_reflection(self):
        x = random.randint(self.x_start, self.x_start + self.width)
        y = random.randint(self.y_start, self.y_start + self.height)
        length = random.randint(1, 5)
        return (x, y, length)

    def generate_sparkle(self):
        x = random.randint(self.x_start, self.x_start + self.width)
        y = random.randint(self.y_start, self.y_start + self.height)
        sparkle_type = random.choice(['dot', 'x', 'circle'])
        return (x, y, sparkle_type)

    def update(self):
        ###reflection_data(水面の模倣)の更新        
        if pyxel.frame_count % 10 == 0: # より高い頻度で伸縮を更新
            self.pattern_state += self.stretch_increment * self.stretch_direction

            if self.pattern_state > 4 or self.pattern_state < 1: 
                self.stretch_direction *= -1 # 伸縮の方向を逆転
                self.pattern_state = max(1, min(self.pattern_state, 4)) # 状態を範囲内に保つ

            # 水面の模倣を更新
            self.reflection_data = [self.generate_reflection() for _ in range(30)]
        
        ###sparkle_data(煌めき)の更新
        if pyxel.frame_count % 6 == 0:
            self.sparkle_data = [self.generate_sparkle() for _ in range(50)]

    def draw(self, scroll_x):
        reflect_color1 = 1
        reflect_color2 = 5
        
        sparkle_color1 = 7
        sparkle_color2 = 13

        # pattern_state を四捨五入して整数として扱う
        int_pattern_state = round(self.pattern_state)

        for x, y, length in self.reflection_data:
            # パターン1の描画
            if self.current_pattern == 1:
                if int_pattern_state == 1:
                    pyxel.line(x - scroll_x, y,   x + length + 2 - scroll_x, y,   reflect_color1)
                    pyxel.line(x - scroll_x -5, y-3, x + length + 3 - scroll_x -5, y-3, reflect_color2)
                elif int_pattern_state == 2:
                    pyxel.line(x - scroll_x, y,   x + length - 1 - scroll_x, y, reflect_color1)
                    pyxel.line(x - scroll_x -5, y-3, x + length - scroll_x - 2 -5, y-3, reflect_color2)
                    pyxel.line(x + length - scroll_x + 2 -2, y-3, x + length + 3 - scroll_x -5, y-3, reflect_color2)
                elif int_pattern_state == 3:
                    pyxel.line(x - scroll_x, y, x + length + 3 - scroll_x, y, reflect_color1)
                    pyxel.line(x - scroll_x - 2 -5, y-3, x + length - 2 - scroll_x -5, y-3, reflect_color2)
                    pyxel.line(x + length - scroll_x -2, y-3, x + length + 2 - scroll_x -5, y-3, reflect_color2)
                elif int_pattern_state == 4:
                    pyxel.line(x - scroll_x, y, x + length - 2 - scroll_x, y, reflect_color1)
                    pyxel.line(x - scroll_x -5, y-3, x + length - scroll_x -5, y-3, reflect_color2)
            # パターン2の描画
            elif self.current_pattern == 2:
                if int_pattern_state == 1:
                    pyxel.line(x - scroll_x, y,   x + length - 3 - scroll_x, y,   reflect_color1)
                    pyxel.line(x - scroll_x -7, y-3, x + length + 2 - scroll_x -7, y-3, reflect_color2)
                elif int_pattern_state == 2:
                    pyxel.line(x - scroll_x, y,   x + length + 1 - scroll_x, y,   reflect_color1)
                    pyxel.line(x - scroll_x -7, y-3, x + length - 1 - scroll_x -7, y-3, reflect_color2)
                elif int_pattern_state == 3:
                    pyxel.line(x - scroll_x, y,   x + length - 2 - scroll_x, y,   reflect_color1)
                    pyxel.line(x - scroll_x -7, y-3, x + length + 3 - scroll_x -7, y-3, reflect_color2)
                elif int_pattern_state == 4:
                    pyxel.line(x - scroll_x, y,   x + length + 2 - scroll_x, y,   reflect_color1)
                    pyxel.line(x - scroll_x -7, y-3, x + length - 2 - scroll_x -7, y-3, reflect_color2)
                
            # パターン3の描画
            elif self.current_pattern == 3:
                if int_pattern_state == 1:
                    pyxel.line(x - scroll_x, y, x + length + 3 - scroll_x, y, reflect_color1)
                    pyxel.line(x - scroll_x -6, y-3,   x + length - 3 - scroll_x -6, y-3,   reflect_color2)
                elif int_pattern_state == 2:
                    pyxel.line(x - scroll_x, y, x + length - scroll_x - 2, y, reflect_color1)
                    pyxel.line(x + length - scroll_x + 2, y, x + length + 3 - scroll_x -2, y, reflect_color1)
                    pyxel.line(x - scroll_x -6, y-3,   x + length + 1 - scroll_x -6, y-3,   reflect_color2)
                elif int_pattern_state == 3:
                    pyxel.line(x - scroll_x - 2, y, x + length - 2 - scroll_x, y, reflect_color1)
                    pyxel.line(x + length - scroll_x, y, x + length + 2 - scroll_x -2, y, reflect_color1)
                    pyxel.line(x - scroll_x -6, y-3,   x + length - 2 - scroll_x -6, y-3,   reflect_color2)
                elif int_pattern_state == 4:
                    pyxel.line(x - scroll_x, y, x + length - scroll_x, y, reflect_color1)
                    pyxel.line(x - scroll_x -6, y-3,   x + length + 2 - scroll_x -6, y-3,   reflect_color2)

        ###ゲーム本体からのスクロール量を引いて描画
        for x, y, s_type in self.sparkle_data:
            if s_type == 'dot':
                pyxel.pset(x -scroll_x, y, sparkle_color1)
            elif s_type == 'circle':
                pyxel.circb(x -scroll_x, y, 1, sparkle_color1)
            else:  # x型の煌めき
                pyxel.line(x-1 -scroll_x, y-1, x+1 -scroll_x, y+1, sparkle_color2)
                pyxel.line(x+1 -scroll_x, y-1, x-1 -scroll_x, y+1, sparkle_color2)


# class App:
#     def __init__(self):
#         pyxel.init(160, 120, caption="Water Surface Reflection and Sparkle")
#         self.effect = WaterSurfaceEffect(10, 50, 140, 20)  # エリアを指定してインスタンス生成
#         pyxel.run(self.update, self.draw)

#     def update(self):
#         self.effect.update()

#     def draw(self):
#         pyxel.cls(0)
#         self.effect.draw()

# App()
