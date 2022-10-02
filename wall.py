import pygame.draw

from sprite import Sprite
from util import *
import random


class Wall:
    def __init__(self, lims, layer=0):
        self.x0 = lims[0]
        self.x1 = lims[1]
        self.y0 = lims[2]
        self.y1 = lims[3]
        self.pos = Pose((self.x0 + self.x1)/2, (self.y0 + self.y1)/2)
        self.w = lims[1] - lims[0]
        self.h = lims[3] - lims[2]
        self.rect = (self.x0, self.y0, self.w, self.h)
        self.layer = layer

    def draw(self, surface, lights, x, y, t):
        rect = (self.x0 + WIDTH/2 - x, self.y0 + HEIGHT/2 - y, self.w, self.h)
        pygame.draw.rect(surface, (255, 255, 255), rect)

    def update(self, dt):
        pass

    def collide(self, sprite):
        right = sprite.pos.x - sprite.imw/2 - self.x1 + 2
        left = -sprite.pos.x - sprite.imw/2 + self.x0 + 2
        down = sprite.pos.y - sprite.imh/2 - self.y1 + 2
        up = -sprite.pos.y - sprite.imh/2 + self.y0 + 2
        if not sprite.grounded:
            up -= 2
            down -= 2
        if up > 0 or down > 0 or left > 0 or right > 0:
            return False
        if up > down and up > left and up > right:
            sprite.grounded = True
            sprite.pos.y += up
            sprite.v.y = min(0, sprite.v.y)
        elif left > down and left > up and left > right:
            sprite.pos.x += left
            sprite.v.x = min(0, sprite.v.x)
        elif right > down and right > up and right > left:
            sprite.pos.x -= right
            sprite.v.x = max(0, sprite.v.x)
        else:
            sprite.pos.y -= down
            sprite.v.y = max(0, sprite.v.y)
        return True

    def onscreen(self, x, y, w, h):
        return self.x0 < w/2 + x and self.x1 > -w/2 + x and self.y0 < h/2 + y and self.y1 > -h/2 + y


class Bridge(Wall):
    def __init__(self, pos):
        self.image = load_image("Bridge.png", number=1)
        self.imw = self.image[0].get_width()
        self.imh = self.image[0].get_height()
        lims = (pos.x - self.imw/2, pos.x + self.imw/2, pos.y - GRID/2, pos.y - GRID/2 + self.imh)
        super().__init__(lims)

    def draw(self, surface, lights, x, y, t):
        surface.blit(self.image[0], (self.x0 + WIDTH/2 - x, self.y0 + HEIGHT/2 - y, self.imw, self.imh))
