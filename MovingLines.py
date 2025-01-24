import pyxel
import random
import math

class MovingLines:
    def __init__(self, start_x, start_y, center_x, center_y, a, b, n, colors, min_frame_range, max_frame_range):
        self.start_x = start_x
        self.start_y = start_y
        self.center_x = center_x
        self.center_y = center_y
        self.a = a  # 長径の半分
        self.b = b  # 短径の半分
        self.n = n
        self.colors = colors
        self.min_frame_range = min_frame_range
        self.max_frame_range = max_frame_range
        self.lines = self._generate_lines()

    def _generate_lines(self):
        lines = []
        for _ in range(self.n):
            end_x, end_y = self._random_point_in_ellipse()
            color_index = random.randint(0, len(self.colors) - 1)
            color_frame_range = random.randint(self.min_frame_range, self.max_frame_range)
            move_frame_range = random.randint(self.min_frame_range, self.max_frame_range)
            width = random.randint(1, 3)
            lines.append({
                "start_x": self.start_x,
                "start_y": self.start_y,
                "end_x": end_x,
                "end_y": end_y,
                "color_index": color_index,
                "color_frame_range": color_frame_range,
                "move_frame_range": move_frame_range,
                "current_color_frame": 0,
                "current_move_frame": 0,
                "width": width
            })
        return lines

    def _random_point_in_ellipse(self):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, 1)
        r = math.sqrt(r)  # 均一な分布にするために平方根を取る
        x = r * self.a * math.cos(angle)
        y = r * self.b * math.sin(angle)
        return self.center_x + x, self.center_y + y

    def _is_within_ellipse(self, x, y):
        return ((x - self.center_x) ** 2 / self.a ** 2 + (y - self.center_y) ** 2 / self.b ** 2) <= 1

    def update(self):
        for line in self.lines:
            line["current_color_frame"] += 1
            line["current_move_frame"] += 1

            if line["current_color_frame"] >= line["color_frame_range"]:
                line["color_index"] = (line["color_index"] + 1) % len(self.colors)
                line["color_frame_range"] = random.randint(self.min_frame_range, self.max_frame_range)
                line["current_color_frame"] = 0

            if line["current_move_frame"] >= line["move_frame_range"]:
                dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
                new_end_x = line["end_x"] + dx
                new_end_y = line["end_y"] + dy

                if self._is_within_ellipse(new_end_x, new_end_y):
                    line["end_x"] = new_end_x
                    line["end_y"] = new_end_y
                    line["width"] = random.randint(1, 3)  # ランダムに太さを変更

                line["move_frame_range"] = random.randint(self.min_frame_range, self.max_frame_range)
                line["current_move_frame"] = 0

    def draw(self, x_offset=0, draw_border=0, draw_border_point=0):
        for line in self.lines:
            color = self.colors[line["color_index"]]
            width = line["width"]
            if draw_border == 0:
                ###指定y値より上のみ描画
                if line["end_y"] <= draw_border_point:
                    if width == 1:
                        pyxel.line(line["start_x"] -x_offset, line["start_y"], line["end_x"] -x_offset, line["end_y"], color)
                    if width == 2:
                        pyxel.tri(line["start_x"] -x_offset, line["start_y"], line["end_x"]    -x_offset, line["end_y"], line["end_x"] +1 -x_offset, line["end_y"], color)
                    if width == 3:
                        pyxel.tri(line["start_x"] -x_offset, line["start_y"], line["end_x"] -1 -x_offset, line["end_y"], line["end_x"] +1 -x_offset, line["end_y"] +1, color)
            if draw_border == 1:
                ###指定y値より下のみ描画
                if line["end_y"] > draw_border_point:
                    if width == 1:
                        pyxel.line(line["start_x"] -x_offset, line["start_y"], line["end_x"] -x_offset, line["end_y"], color)
                    if width == 2:
                        pyxel.tri(line["start_x"] -x_offset, line["start_y"], line["end_x"]    -x_offset, line["end_y"], line["end_x"] +1 -x_offset, line["end_y"], color)
                    if width == 3:
                        pyxel.tri(line["start_x"] -x_offset, line["start_y"], line["end_x"] -1 -x_offset, line["end_y"], line["end_x"] +1 -x_offset, line["end_y"] +1, color)



# # Pyxelの初期化
# pyxel.init(160, 120)

# # MovingLinesクラスのインスタンス生成
# moving_lines = MovingLines(
#     start_x=80,
#     start_y=60,
#     center_x=80,
#     center_y=60,
#     a=40,  # 長径の半分
#     b=20,  # 短径の半分
#     n=10,
#     colors=[pyxel.COLOR_RED, pyxel.COLOR_GREEN, pyxel.COLOR_BLUE, pyxel.COLOR_YELLOW],
#     min_frame_range=20,
#     max_frame_range=50
# )

# # Pyxelのアップデート関数
# def update():
#     moving_lines.update()

# # Pyxelの描画関数
# def draw():
#     pyxel.cls(pyxel.COLOR_BLACK)
#     moving_lines.draw()

# # Pyxelのメインループ開始
# pyxel.run(update, draw)
