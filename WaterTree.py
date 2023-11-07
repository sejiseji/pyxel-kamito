import pyxel
import math
import random

class WaterTree:
    def __init__(self, x, num_branch):
        self.x = x
        self.y = 0
        self.num_branch = num_branch  # 枝の数
        # self.width = 8  # 基本の幹の太さ
        self.width = random.randint(6,9)  # 基本の幹の太さ
        #誤差
        self.rnddeg1 = random.randint(-3, 3)
        self.rnddeg2 = random.randint(-3, 3)
        #色
        self.color = random.choice([1,5])  # 色のバリエーション

    def draw_branch(self, x, y, angle, length, width):
        # 枝の終点の座標を計算
        end_x = x + length * math.cos(math.radians(angle))
        end_y = y - length * math.sin(math.radians(angle))

        # 枝を描画
        for i in range(width):
            offset = i - width // 2
            pyxel.line(x + offset, y, end_x + offset, end_y, self.color)

        return end_x, end_y

    def draw(self, camera_x=0):
        # 幹の描画
        trunk_height = pyxel.height
        for i in range(self.width -1):
            pyxel.line(self.x - camera_x + i +self.width -4, trunk_height -130, self.x - camera_x + i +self.width -4, trunk_height, self.color)
        
        # 1世代目の枝のパラメータ
        branches = [(self.x - camera_x + self.width - 1, trunk_height -120, 90, 50, self.width - 1)]
        
        # 各世代の枝を描画
        for _ in range(self.num_branch):
            new_branches = []
            for x, y, angle, length, width in branches:
                end_x, end_y = self.draw_branch(x, y, angle, length, width)
                # 新しい世代の枝のパラメータを計算
                gen_length = length * 0.75
                gen_width = max(width - 1, 1)
                new_branches.append((end_x, end_y, angle + 30 +self.rnddeg1, gen_length, gen_width))
                new_branches.append((end_x, end_y, angle - 25 +self.rnddeg2, gen_length, gen_width))
            branches = new_branches  # 次の世代の枝に更新






# import pyxel
# import math

# class WaterTree:
#     def __init__(self, x, num_branch):
#         self.x = x
#         self.y = 0
#         self.num_branch = num_branch  # 枝の数
#         self.width = 8  # 基本の幹の太さ

#     def draw_branch(self, x, y, angle, length, width):
#         # 枝の終点の座標を計算
#         end_x = x + length * math.cos(math.radians(angle))
#         end_y = y - length * math.sin(math.radians(angle))  # PyxelのY座標は下が大きいので、引き算

#         # 枝を描画
#         for i in range(width):
#             offset = i - width // 2
#             pyxel.line(
#                 x + offset, y,  # 始点は幹の中心からずらす
#                 end_x + offset, end_y,  # 終点も同様にずらす
#                 1  # 色
#             )

#         return end_x, end_y  # 次の枝の描画のために終点座標を返す

#     def draw(self, camera_x=0):
#         # 幹の描画
#         trunk_height = pyxel.height - 100  # トランクの高さを設定
#         for i in range(self.width):
#             pyxel.line(self.x - camera_x + i, 0, self.x - camera_x + i, trunk_height, 1)
        
#         # 1世代目の枝のパラメータ
#         branch_length = 50
#         branch_width = self.width - 1
#         branch_angle = 90
#         # 1世代目の枝を描画
#         end_x, end_y = self.draw_branch(self.x - camera_x + self.width - 1, trunk_height, branch_angle, branch_length, branch_width)
#         # 2世代目の枝のパラメータ
#         gen2_length = branch_length * 0.75
#         gen2_width = branch_width - 1
#         # 2世代目の枝を描画（左側）
#         end_x_left, end_y_left = self.draw_branch(end_x, end_y, branch_angle + 30, gen2_length, gen2_width)
#         # 2世代目の枝を描画（右側）
#         end_x_right, end_y_right = self.draw_branch(end_x, end_y, branch_angle - 30, gen2_length, gen2_width)
#         # 3世代目の枝のパラメータ
#         gen3_length = gen2_length * 0.75
#         gen3_width = gen2_width - 1
#         # 3世代目の枝を描画（左枝から左右に）
#         self.draw_branch(end_x_left, end_y_left, branch_angle + 45, gen3_length, gen3_width)
#         self.draw_branch(end_x_left, end_y_left, branch_angle + 15, gen3_length, gen3_width)
#         # 3世代目の枝を描画（右枝から左右に）
#         self.draw_branch(end_x_right, end_y_right, branch_angle - 45, gen3_length, gen3_width)
#         self.draw_branch(end_x_right, end_y_right, branch_angle - 15, gen3_length, gen3_width)
#         # 4世代目の枝のパラメータ
#         gen4_length = gen3_length * 0.75
#         gen4_width = max(gen3_width - 2, 1)  # 幅は1以上を保つ
#         # 4世代目の枝を描画（左枝の左側から左右に）
#         end_x_ll, end_y_ll = self.draw_branch(end_x_left, end_y_left, branch_angle + 60, gen4_length, gen4_width)
#         self.draw_branch(end_x_ll, end_y_ll, branch_angle + 70, gen4_length * 0.75, gen4_width - 1)
#         self.draw_branch(end_x_ll, end_y_ll, branch_angle + 50, gen4_length * 0.75, gen4_width - 1)
#         # 4世代目の枝を描画（左枝の右側から左右に）
#         end_x_lr, end_y_lr = self.draw_branch(end_x_left, end_y_left, branch_angle, gen4_length, gen4_width)
#         self.draw_branch(end_x_lr, end_y_lr, branch_angle + 10, gen4_length * 0.75, gen4_width - 1)
#         self.draw_branch(end_x_lr, end_y_lr, branch_angle - 10, gen4_length * 0.75, gen4_width - 1)
#         # 4世代目の枝を描画（右枝の左側から左右に）
#         end_x_rl, end_y_rl = self.draw_branch(end_x_right, end_y_right, branch_angle, gen4_length, gen4_width)
#         self.draw_branch(end_x_rl, end_y_rl, branch_angle + 10, gen4_length * 0.75, gen4_width - 1)
#         self.draw_branch(end_x_rl, end_y_rl, branch_angle - 10, gen4_length * 0.75, gen4_width - 1)
#         # 4世代目の枝を描画（右枝の右側から左右に）
#         end_x_rr, end_y_rr = self.draw_branch(end_x_right, end_y_right, branch_angle - 60, gen4_length, gen4_width)
#         self.draw_branch(end_x_rr, end_y_rr, branch_angle - 70, gen4_length * 0.75, gen4_width - 1)
#         self.draw_branch(end_x_rr, end_y_rr, branch_angle - 50, gen4_length * 0.75, gen4_width - 1)



# import pyxel
# import math

# class WaterTree:
#     def __init__(self, x, num_branch):
#         self.x = x
#         self.y = 0
#         self.num_branch = num_branch
#         self.draw_x = x
#         self.draw_y = 0
#         ##幹の太さ
#         self.width = 7

#     def draw(self, camera_x=0):
#         ##幹の描画
#         for i in range(self.width):
#             pyxel.line(self.x -camera_x +i, 0, self.x -camera_x +i, pyxel.height, 1)
        
#         ##枝の描画
#         #右側１段階目の枝の太さ
#         branch_width01 = self.width - 2
#         #右側１段階目の枝の描画
#         for i in range(branch_width01):
#             yi = math.floor(i/2)
#             pyxel.line(self.x -camera_x +self.width -1, 200 + i, self.x -camera_x +self.width -1 + 50, 200 - 50 +yi, 1)
