import pyxel
import math


class PyxelExtended:
    def __init__(self):
        self.angle = 0.0
    #     self.particles = []

    def draw_moving_circle(self, x, y, img, u, v, w, h, r):
        for i in range(w):
            for j in range(h):
                if (i - w/2)**2 + (j - h/2)**2 <= r**2:
                    offset = math.sin(self.angle + j * 0.05) * r
                    pyxel.pset(x + i, y + j, pyxel.image(img).pget(u + int(i + offset) % w, v + j))
                else:
                    pyxel.pset(x + i, y + j, pyxel.image(img).pget(u + i, v + j))

    def update_angle(self, increment=0.05):
        self.angle += increment

    def draw_wavy_rect(self, x, y, img, u, v, w, h, amplitude=5, frequency=0.05, trans_color=None):
        # 歪みの最大および最小のオフセットを計算
        offsets = [int(amplitude * math.sin(self.angle + j * frequency)) for j in range(h)]
        max_abs_offset = max([abs(offset) for offset in offsets])
        
        # 一時的な画像領域を確保
        temp_width = w + 2 * max_abs_offset
        temp_image = [[-1 for _ in range(temp_width)] for _ in range(h)]  # 初期値を-1として透過を示す
        
        # 元の画像を一時的な画像領域の中央にコピー
        for j in range(h):
            for i in range(w):
                color = pyxel.image(img).pget(u + i, v + j)
                if color != trans_color:
                    temp_image[j][i + max_abs_offset] = color

        # 一時的な画像領域を歪ませて描画
        for j in range(h):
            offset = offsets[j]
            for i in range(temp_width):  # 一時的な画像の全幅で描画
                src_i = i - offset
                if 0 <= src_i < temp_width and temp_image[j][src_i] != -1:  # 色が-1（透過）でない場合のみ描画
                    pyxel.pset(x + i - max_abs_offset, y + j, temp_image[j][src_i])


    ### 円形クリッピングを適用する。trans_colorで指定した色は透過として扱う
    def draw_clipped_circle(self, x, y, img, u, v, w, h, r, trans_color=None):
        flip_horizontal = w < 0  # Check if w is negative
        w = abs(w)  # Ensure w is positive for the loop
        
        for i in range(w):
            for j in range(h):
                dx, dy = i - w // 2, j - h // 2  # Offset from the center
                if dx ** 2 + dy ** 2 <= r ** 2:
                    src_x = u + (w - 1 - i) if flip_horizontal else u + i  # Flip horizontally if flip_horizontal is True
                    color = pyxel.image(img).pget(src_x, v + j)
                    if color != trans_color:  # Skip if the color is the specified transparent color
                        pyxel.pset(x + i, y + j, color)

    def warp_drawn_content(self, x, y, w, h, amplitude=5, frequency=0.05):
        # オフセットの計算
        offsets = [int(amplitude * math.sin(self.angle + j * frequency)) for j in range(h)]
        max_abs_offset = max([abs(offset) for offset in offsets])
        
        # 一時的な画像領域を確保
        temp_width = w + 2 * max_abs_offset
        temp_image = [[-1 for _ in range(temp_width)] for _ in range(h)]  # 初期値を-1として透過を示す
        
        # 現在の描画内容を一時的な画像領域の中央にコピー
        for j in range(h):
            for i in range(w):
                color = pyxel.pget(x + i, y + j)
                temp_image[j][i + max_abs_offset] = color
        
        # 一時的な画像領域を歪ませて描画
        for j in range(h):
            offset = offsets[j]
            for i in range(temp_width):  # 一時的な画像の全幅で描画
                src_i = i - offset
                if 0 <= src_i < temp_width and temp_image[j][src_i] != -1:  # 色が-1（透過）でない場合のみ描画
                    pyxel.pset(x + i - max_abs_offset, y + j, temp_image[j][src_i])



    def warp_drawn_content_with_simple_convolution(self, x, y, w, h, amplitude=5, frequency=0.05):
        # 現在の描画内容をリストにコピー
        image = [[pyxel.pget(x + i, y + j) for i in range(w)] for j in range(h)]
        
        # 新しい描画内容を保存するための空のリストを作成
        new_image = [[0 for _ in range(w)] for _ in range(h)]
        
        # オフセットの計算を用いて新しい画像を生成
        for j in range(h):
            for i in range(w):
                offset = int(amplitude * math.sin(self.angle + j * frequency))
                new_value = 0
                count = 0
                for k in range(-offset, offset + 1):
                    if 0 <= i + k < w:
                        new_value += image[j][i + k]
                        count += 1
                new_image[j][i] = new_value // count if count != 0 else image[j][i]
        
        # 新しい画像を描画
        for j in range(h):
            for i in range(w):
                pyxel.pset(x + i, y + j, new_image[j][i])

