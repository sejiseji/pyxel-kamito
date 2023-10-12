import pyxel
import math
import random

class EchoChamberVisualizer:
    GOLDEN_RATIO = 1.6180339887
    SILVER_RATIO = 2.4142135623

    def __init__(self, x_center, y_center, r, treeangle, max_depth, polygon_sides=6, external=False, firstlength=None):
        self.x_center = x_center
        self.y_center = y_center
        self.r = r
        self.tree_angle = treeangle
        # firstlengthが指定されていなければ、rの75%をデフォルト値として使用
        self.max_depth = max_depth
        self.polygon_sides = polygon_sides
        self.external = external
        self.use_golden_ratio = True  # 初期設定として黄金比を使用
        if firstlength:
            self.starting_length_golden = firstlength
            self.starting_length_silver = firstlength * 1.5
        else:
            self.starting_length_golden = r * 0.75
            self.starting_length_silver = r * 1.125
        self.angle_offset = 360/self.polygon_sides   # 新しいインスタンス変数の追加
        pyxel.mouse(True)

        self.frame_count = 0
        self.max_frame_count = 80
        # self.max_frame_count = random.randint(50, 150)

        self.x_new = 0
        self.y_new = 0
        self.r_new = 0
        self.tree_angle_new = 0
        self.max_depth_new = 0
        self.polygon_sides_new = 0
        self.external_new = False
        self.firstlength_new = 0


    def update(self):
        ###frame_countをインクリメントし、max_frame_countに達したらburst()を呼び出す
        self.frame_count += 1
        ###self.x_newが0の場合はburst()を呼び出す=1回だけ実行
        if (self.frame_count >= self.max_frame_count) and (self.x_new == 0):
            self.burst()

        if pyxel.btnp(pyxel.KEY_T):
            # Tキーが押された場合、angle_offsetを15度増加させる
            self.angle_offset += 15  
 

        if pyxel.btnp(pyxel.KEY_E):
            # externalを切り替える
            # self.external = not self.external
            self.angle_offset = (self.angle_offset + 180) % 360  # 180度変更


        if pyxel.btnp(pyxel.KEY_R):
            # 黄金比と白銀比を切り替える
            self.use_golden_ratio = not self.use_golden_ratio

    def burst(self):
        max_distance = 30  # x_center, y_centerからの最大の距離
        while True:
            angle = random.uniform(0, 2 * math.pi)  # ランダムな角度を取得
            distance = random.uniform(0, max_distance)  # ランダムな距離を取得
            
            x_new_potential = self.x_center + math.cos(angle) * distance
            y_new_potential = self.y_center + math.sin(angle) * distance
            
            # x_new, y_newが画面内に収まるか確認
            if 0 < x_new_potential < pyxel.width and 0 < y_new_potential < pyxel.height:
                self.x_new = x_new_potential
                self.y_new = y_new_potential
                break  # 画面内に収まる座標が見つかった場合、whileループを抜ける
        
        self.r_new = random.randint(10, 30)
        self.tree_angle_new = random.randint(15, 35)
        self.max_depth_new = random.randint(8, 14)
        self.polygon_sides_new = random.randint(3, 16)
        self.external_new = random.choice([True, False])
        self.firstlength_new = random.randint(20, 50)


    def draw_tree(self, x, y, branch_length, angle, current_depth=0, max_current_depth=None):
        if max_current_depth is None:
            max_current_depth = self.max_depth
        
        if current_depth >= max_current_depth:
            return

        x2 = x + branch_length * math.sin(math.radians(angle))
        y2 = y - branch_length * math.cos(math.radians(angle))
        pyxel.line(x, y, x2, y2, pyxel.COLOR_GREEN)

        ratio = self.GOLDEN_RATIO if self.use_golden_ratio else self.SILVER_RATIO

        # 白銀比を使用する場合の枝の角度の調整
        adjusted_tree_angle = self.tree_angle * 0.8 if not self.use_golden_ratio else self.tree_angle

        next_length = branch_length / ratio
        if next_length > 1:
            self.draw_tree(x2, y2, next_length, angle + adjusted_tree_angle, current_depth+1, max_current_depth)
            self.draw_tree(x2, y2, next_length, angle - adjusted_tree_angle, current_depth+1, max_current_depth)




    def draw_polygon(self, x, y, r, max_current_depth=None):
        angle_increment = 360 / self.polygon_sides
        for i in range(self.polygon_sides):
            x2 = x + r * math.sin(math.radians(i * angle_increment))
            y2 = y - r * math.cos(math.radians(i * angle_increment))
            pyxel.line(x, y, x2, y2, pyxel.COLOR_RED)

            internal_angle = ((self.polygon_sides - 2) * 180) / self.polygon_sides
            half_internal_angle = internal_angle / 2

            # 頂点から樹形図を描画
            if self.external:
                start_angle = (i * angle_increment) - half_internal_angle + self.angle_offset  # angle_offsetの追加
            else:
                start_angle = (i * angle_increment) + half_internal_angle + self.angle_offset  # angle_offsetの追加

            starting_length = self.starting_length_golden if self.use_golden_ratio else self.starting_length_silver
            self.draw_tree(x2, y2, starting_length, start_angle, max_current_depth=max_current_depth)
            
            x, y = x2, y2

    def draw(self, scroll_x):
        # loop_duration = 10 * (self.max_depth + 1)  # 深さが最大値に達するまでのフレーム数
        current_max_depth = (pyxel.frame_count // 5) % (self.max_depth + 1)
        # current_max_depth = (pyxel.frame_count // 10) % (self.max_depth + 1)
        self.draw_polygon(self.x_center - scroll_x, self.y_center, self.r, current_max_depth)

        if self.x_new > 0:
            ###ランダムな頂点座標から新たなインスタンス座標へラインを1本描画する
            pyxel.line(self.x_center, self.y_center, self.x_new, self.y_new, pyxel.COLOR_WHITE)
