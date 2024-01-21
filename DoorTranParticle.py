import pyxel
import random
import math

class DoorTranParticle:
    def __init__(self):
        self.x = pyxel.width / 2
        self.y = pyxel.height / 2
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * random.randint(2, 4)
        self.vy = math.sin(angle) * random.randint(2, 4)
        self.size = random.randint(1, 2)
        self.type = random.choice(['+', '*', 'dot', 'circle'])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # 画面外に出たパーティクルをリセット
        if self.x < 0 or self.x > pyxel.width or self.y < 0 or self.y > pyxel.height:
            self.__init__()

    def draw(self):
        if self.type == '+':
            pyxel.line(self.x, self.y - self.size, self.x, self.y + self.size, 7)
            pyxel.line(self.x - self.size, self.y, self.x + self.size, self.y, 7)
        elif self.type == '*':
            pyxel.line(self.x - self.size, self.y - self.size, self.x + self.size, self.y + self.size, 7)
            pyxel.line(self.x + self.size, self.y - self.size, self.x - self.size, self.y + self.size, 7)
        elif self.type == 'dot':
            pyxel.pset(self.x, self.y, 7)
        elif self.type == 'circle':
            pyxel.circb(self.x, self.y, self.size, 7)

