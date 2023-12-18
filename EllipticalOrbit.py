import pyxel
import math

class EllipticalOrbit:
    def __init__(self, center_x, center_y, a, b, alpha, speed, color, parent=None):
        self.center_x = center_x
        self.center_y = center_y
        self.prev_center_x = center_x  # 前回の中心座標X
        self.prev_center_y = center_y  # 前回の中心座標Y
        self.a = a
        self.b = b
        self.alpha = alpha
        self.angle = 0
        self.speed = speed
        self.color = color
        self.parent = parent  # 追加：親となるオブジェクトを参照
        self.x, self.y, self.z = 0, 0, 0
        self.draw_x, self.draw_y = 0, 0
        self.pjtx, self.pjty = 0, 0
        self.update()  # Initialize the position

    def update(self):
        # 親オブジェクトが存在する場合、その座標を中心座標として更新
        if self.parent:
            dx = self.parent.x - self.prev_center_x  # X方向の移動増分
            dy = self.parent.y - self.prev_center_y  # Y方向の移動増分

            self.center_x, self.center_y = self.parent.x, self.parent.y
            self.prev_center_x, self.prev_center_y = self.center_x, self.center_y

        self.angle += self.speed
        x = self.a * math.cos(self.angle)
        y = self.b * math.sin(self.angle) * math.cos(self.alpha)
        z = self.b * math.sin(self.angle) * math.sin(self.alpha)

        # 親オブジェクトが存在する場合、移動増分を加える
        if self.parent:
            self.x, self.y, self.z = self.center_x + x + dx, self.center_y + y + dy, z
        else:
            self.x, self.y, self.z = self.center_x + x, self.center_y + y, z

    # def update(self):
    #     # 親オブジェクトが存在する場合、その座標を中心座標として更新
    #     if self.parent:
    #         self.parent.update()  # これを追加：親の位置を最新のものに更新
    #         self.center_x, self.center_y = self.parent.x, self.parent.y

    #     self.angle += self.speed
    #     x = self.a * math.cos(self.angle)
    #     y = self.b * math.sin(self.angle) * math.cos(self.alpha)
    #     z = self.b * math.sin(self.angle) * math.sin(self.alpha)
    #     self.x, self.y, self.z = self.center_x + x, self.center_y + y, z



    def project(self, f):
        X = f * self.x / (self.z + f) + pyxel.width // 2
        Y = f * self.y / (self.z + f) + pyxel.height // 2
        return X, Y

    def draw(self, scroll_x, framecount):
        X, Y = self.project(200)
        # pyxel.pset(X -scroll_x, Y, self.color)
        # pyxel.circb(X -scroll_x, Y, 3, self.color)
        self.pjtx, self.pjty = X, Y
        frames = framecount // 7 % 8
        pyxel.blt(X -scroll_x, Y, 1, 32, frames * 16, 16, 16, 0)

###呼び出し状況
    # def generateObjects(self):
    ###〜略〜
                    # ###象徴するオブジェクトを生成
                    # if (self.gamestate.scene == C_SCENE_GOLD):
                    #     point_a_x, point_a_y = 0, 0  # This is just the center of the screen
                    #     point_b = EllipticalOrbit(point_a_x, point_a_y, 40, 30, Math.radians(45), 0.03, pyxel.COLOR_RED)
                    #     point_c = EllipticalOrbit(point_b.x, point_b.y, 20, 20, 0, 0.05, pyxel.COLOR_GREEN)
                    #     self.elliptical_orbits.append(point_b)
                    #     self.elliptical_orbits.append(point_c)

###更新
        # if (self.gamestate.scene == C_SCENE_GOLD):
        #     # オブジェクトのupdateメソッドを呼び出す
        #     for point in self.elliptical_orbits:
        #         point.update()

###描画
    # def drawGoldBG(self):
    #     ###reset(Bk)
    #     pyxel.cls(0)
    #     ###EllipticalOrbitを描画
    #     for point in self.elliptical_orbits:
    #         point.draw()