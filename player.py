from sprite import Sprite
from util import *
import random


class Player(Sprite):
    def __init__(self, pos=Pose(0, 0)):
        self.idle = load_image("PlayerIdle.png", number=1, flip=False, scale=1)
        super().__init__(pos, "PlayerIdle")
        self.right = load_image("PlayerRun.png", number=10, flip=False, scale=1)
        self.left = load_image("PlayerRun.png", number=10, flip=True, scale=1)
        self.light = load_image("Light2.png", scale=2.2)[0]
        self.glow = load_image("Glow2.png", scale=2.2)[0]
        self.lights = [Pose(0, 0)]
        self.grounded = True
        self.fall = load_image("PlayerJump.png", number=1, flip=False, scale=1)
        self.jumping = load_image("PlayerJump.png", number=1, flip=False, scale=1)

    def update(self, user_input, dt, splash=False):
        if user_input == "R":
            self.v.x = PLAYER_SPEED
            self.image = self.right
        elif user_input == "r":
            self.v.x = PLAYER_SPEED/2
            self.image = self.right
        elif user_input == "L":
            self.v.x = -PLAYER_SPEED
            self.image = self.left
        else:
            self.image = self.idle
            self.v.x -= self.v.x * PLAYER_FRICTION
            if abs(self.v.x) < PLAYER_SPEED/10:
                self.v.x = 0
        self.v.y += PLAYER_GRAVITY * dt/1000
        if self.v.y > PLAYER_MAX_FALL:
            self.v.y = PLAYER_MAX_FALL
        if splash:
            self.pos.y += self.v.y * dt/1000
        else:
            self.pos += self.v * dt / 1000

    def jump(self):
        if self.grounded:
            self.v.y = -PLAYER_JUMP
            self.grounded = False
