from sprite import Sprite
from util import *
import random


class Monster(Sprite):
    def __init__(self, pos=Pose(0, 0), image="Pit", frames=1):
        super().__init__(pos, image, frames)

    def update(self, dt):
        pass


class Crawler(Monster):
    def __init__(self, pos=Pose(0, 0)):
        super().__init__(pos, "Crawler", frames=4)
        self.dx = 0
        self.direction = 1 if random.random() > 0.5 else -1

    def update(self, dt):
        self.dx += CRAWLER_SPEED * self.direction * dt / 1000
        self.pos.x += CRAWLER_SPEED * self.direction * dt / 1000
        if self.dx > GRID * 2:
            self.direction = -1
        if self.dx < -GRID * 2:
            self.direction = 1


class BigCrawler(Monster):
    def __init__(self, pos=Pose(0, 0)):
        super().__init__(pos, "Spider", frames=8)
        self.dx = 0
        self.direction = 1 if random.random() > 0.5 else -1

    def update(self, dt):
        self.dx += BIG_CRAWLER_SPEED * self.direction * dt / 1000
        self.pos.x += BIG_CRAWLER_SPEED * self.direction * dt / 1000
        if self.dx > GRID * 3:
            self.direction = -1
        if self.dx < -GRID * 3:
            self.direction = 1


class Flyer(Monster):
    def __init__(self, pos=Pose(0, 0)):
        super().__init__(pos, "Flyer", frames=6)
        self.dx = 0
        self.direction = 1

    def update(self, dt):
        self.dx += FLYER_SPEED * self.direction * dt / 1000
        self.pos.x += FLYER_SPEED * self.direction * dt / 1000
        if self.dx > GRID * 3:
            self.direction = -1
        if self.dx < -GRID * 3:
            self.direction = 1


class Lurker(Monster):
    def __init__(self, pos=Pose(0, 0)):
        super().__init__(pos, "Lurker", frames=1)
        self.lights = [Pose(-15, -80)]

    def collide(self, sprite, buffer=BUFFER):
        h = 75
        y = self.pos.y + self.imh / 2 - h / 2
        return self.pos.x - self.imw / 2 < sprite.pos.x + sprite.imw / 2 - buffer and \
               self.pos.x + self.imw / 2 > sprite.pos.x - sprite.imw / 2 + buffer and \
               y - h / 2 < sprite.pos.y + sprite.imh / 2 - buffer and \
               y + h / 2 > sprite.pos.y - sprite.imh / 2 + buffer


class Chaser(Monster):
    def __init__(self, game, pos=Pose(0, 0)):
        super().__init__(pos, "Chaser", frames=5)
        self.forward = self.image
        self.reverse = load_image("Chaser.png", number=5, flip=True)
        self.game = game
        self.sanctuary = False

    def update(self, dt):
        # if self.sanctuary or self.game.game_over or self.game.splash:
        if self.game.game_over or self.game.splash or self.game.victory:
            self.t0 = self.game.t
        else:
            if self.game.player.pos.x > self.pos.x+1:
                self.image = self.forward
                self.pos.x += CHASER_SPEED * dt / 1000
            elif self.game.player.pos.x < self.pos.x-1:
                self.image = self.reverse
                self.pos.x -= CHASER_SPEED * dt / 1000
            else:
                self.t0 = self.game.t
            if self.game.player.pos.x - self.pos.x > WIDTH/2 + 100:
                self.pos.x = self.game.player.pos.x - WIDTH/2 - 100
        g1 = GRID * self.game.ground[int(self.pos.x / GRID)] - self.imh / 2 - GRID / 2
        g2 = GRID * self.game.ground[int(self.pos.x / GRID + 0.3)] - self.imh / 2 - GRID / 2
        self.pos.y += 0.5 * (min(g1, g2) - self.pos.y)

    def collide(self, sprite, buffer=BUFFER):
        return self.pos.x - self.imw/4 < sprite.pos.x + sprite.imw/2 - buffer and \
               self.pos.x + self.imw/4 > sprite.pos.x - sprite.imw/2 + buffer and \
               self.pos.y - self.imh / 2 < sprite.pos.y + sprite.imh / 2 - buffer and \
               self.pos.y + self.imh / 2 > sprite.pos.y - sprite.imh / 2 + buffer
