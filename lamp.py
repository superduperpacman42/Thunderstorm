from sprite import Sprite
from util import *


class Lamp(Sprite):
    def __init__(self, pos=(0, 0)):
        super().__init__(pos, "Lamp")
        self.lights = [Pose(-40, -40)]


class House(Sprite):
    def __init__(self, pos=(0, 0)):
        super().__init__(pos, "House")
        self.lights = [Pose(-200, 83), Pose(-66, 128), Pose(92, 128)]
