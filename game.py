from lamp import Lamp, House
from monster import *
from player import Player
from util import *
from wall import Wall, Bridge


class Game:

    def reset(self, respawn=False):
        """ Resets the game state """
        # self.t = 0
        self.x = 0
        self.y = 0
        self.ground = []
        self.pause = False
        self.victory = False
        self.house = None
        self.sprites = []
        self.thunder = False
        self.walls = []
        self.checkpoints = []
        self.game_over = False
        if not respawn:
            self.respawn = None
        self.monsters = []
        # self.walls.append(Wall((-WIDTH/2, WIDTH/2, 0, HEIGHT)))
        # self.walls.append(Wall((-WIDTH/2, -WIDTH/2+100, -100, 0)))
        self.load_world()
        if self.respawn:
            self.player = Player(Pose(self.respawn.x, self.respawn.y))
        self.x = self.player.pos.x
        self.y = self.player.pos.y - 50
        self.chaser = Chaser(self, Pose(self.player.pos.x - GRID*5, self.player.pos.y-20))
        self.monsters.append(self.chaser)

    def load_world(self):
        j0 = 0 if not self.respawn else (self.respawn.x - WIDTH)/GRID
        with open("images/Layout.txt") as file:
            for i, line in enumerate(file):
                y = i * GRID
                for j, c in enumerate(line[:-1]):
                    if len(self.ground) <= j:
                        self.ground.append(12)
                    if j < j0:
                        continue
                    x = j * GRID
                    if c == "0":  # wall
                        self.walls.append(Wall((x-GRID/2, x+GRID/2, y-GRID/2, y+GRID/2+HEIGHT*5)))
                        if i < self.ground[j]:
                            self.ground[j] = i
                    elif c == ".":  # fake wall
                        self.sprites.append(Wall((x-GRID/2, x+GRID/2, y-GRID/2, y+GRID/2)))
                    elif c == "_":  # platform
                        self.walls.append(Wall((x-GRID/2, x+GRID/2, y-GRID/2, y-GRID/4)))
                    elif c == "b":  # bridge
                        self.walls.append(Bridge(Pose(x, y)))
                        for dj in range(-2, 3):
                            if i < self.ground[j+dj]:
                                self.ground[j+dj] = i
                    elif c == "*" and not self.respawn:  # player
                        self.player = Player(Pose(x, y))
                    elif c == '"' and not self.respawn:  # warning
                        self.warning = Sprite(Pose(x, y-150), "Warning")
                    elif c == "L":  # lamp
                        self.checkpoints.append(Lamp(Pose(x, y-50)))
                    elif c == "t":  # lamp
                        self.sprites.append(Sprite(Pose(x, y-112), "Tree"))
                    elif c == "l":  # lurker
                        self.monsters.append(Lurker(Pose(x+GRID/2, y-75)))
                    elif c == "m":  # small pit monster
                        self.monsters.append(Monster(Pose(x+GRID/2, y)))
                    elif c == "M":  # big pit monster
                        self.monsters.append(Monster(Pose(x, y-15), "BigPit"))
                    elif c == "c":  # crawler
                        self.monsters.append(Crawler(Pose(x, y+6)))
                    elif c == "C":  # big crawler
                        self.monsters.append(BigCrawler(Pose(x, y-70)))
                    elif c == "f":  # crawler
                        self.monsters.append(Flyer(Pose(x, y)))
                    elif c == "h":  # home
                        self.house = House(Pose(x, y-212))
                        self.sprites.append(self.house)

    def ui(self, surface):
        """ Draws the user interface overlay """
        if self.victory and self.t - self.victory > 1000:
            caption = self.font.render("YOU ARE SAFE", True, (255, 255, 255))
            surface.blit(caption, (WIDTH/2 - caption.get_width()/2, HEIGHT*3/4))
            if self.t - self.victory > 4000 and (self.t - self.victory) % 2000 > 1000:
                caption = self.font2.render("Press Enter to Play Again", True, (255, 255, 255))
                surface.blit(caption, (WIDTH / 2 - caption.get_width() / 2, HEIGHT * 0.9))
        elif self.splash:
            caption = self.font2.render("Use Arrow Keys or WASD to Move", True, (255, 255, 255))
            surface.blit(caption, (WIDTH / 2 - caption.get_width() / 2, HEIGHT * 0.75))
            caption = self.font2.render("Press Escape to Toggle Full-Screen", True, (255, 255, 255))
            surface.blit(caption, (WIDTH / 2 - caption.get_width() / 2, HEIGHT * 0.82))
            caption = self.font2.render("Press Enter to Begin", True, (255, 255, 255))
            surface.blit(caption, (WIDTH / 2 - caption.get_width() / 2, HEIGHT * 0.89))

    def update(self, dt, keys):
        """ Updates the game by a timestep and redraws graphics """
        # Update player
        if dt > 100:
            return
        if self.game_over and self.t - self.game_over > 2000:
            self.reset(respawn=True)
        self.t += dt
        self.update_keys(keys)
        self.x += CAMERA_KP * (self.player.pos.x - self.x)
        if abs(self.x - self.player.pos.x) < 1:
            self.x = self.player.pos.x
        self.y += CAMERA_KP * (self.player.pos.y - self.y - 50)
        if abs(self.y - self.player.pos.y) < 1:
            self.y = self.player.pos.y
        if self.player.pos.x > self.house.pos.x - self.house.imw/2:
            if not self.victory:
                pygame.mixer.music.fadeout(2000)

                play_sound("Lamp.wav")
                self.victory = self.t
            self.player.lights = []
            if self.player.pos.x < self.house.pos.x:
                self.player.update("r", dt, self.splash)
            else:
                self.player.update("", dt, self.splash)
        else:
            self.player.update(self.input[-1] if not self.game_over else "", dt, self.splash)
        self.player.grounded = False
        if self.player.pos.y > GRID*15:
            if not self.game_over:
                self.game_over = self.t

        # Draw
        surface = pygame.Surface((WIDTH, HEIGHT))
        lights = pygame.Surface((WIDTH, HEIGHT))
        self.screen.fill((0, 0, 0))
        surface.fill((0, 0, 0))
        lights.fill((0, 0, 0))
        self.sprites = sorted(self.sprites, key=lambda sp: sp.layer)
        for s in self.sprites:
            if s.onscreen(self.x, self.y, WIDTH, HEIGHT):
                s.draw(surface, lights, self.x, self.y, self.t)
        if not self.splash:
            self.warning.draw(surface, lights, self.x, self.y, self.t)
        for m in self.monsters:
            if m.onscreen(self.x, self.y, WIDTH, HEIGHT) or m is self.chaser:
                m.update(dt)
                if m.collide(self.player):
                    if not self.game_over:
                        self.game_over = self.t
                m.draw(surface, lights, self.x, self.y, self.t)
        self.chaser.sanctuary = False
        for c in self.checkpoints:
            if c.onscreen(self.x, self.y, WIDTH, HEIGHT):
                if c.collide(self.player, buffer=-20):
                    self.chaser.sanctuary = True
                    if not self.respawn or self.respawn.x < c.pos.x:
                        self.respawn = c.pos
                        play_sound("Lamp.wav")
                c.draw(surface, lights, self.x, self.y, self.t)
        if self.victory:
            self.chaser.sanctuary = True
        for w in self.walls:
            if w.onscreen(self.x, self.y, WIDTH, HEIGHT):
                w.draw(surface, lights, self.x, self.y, self.t)
                w.collide(self.player)
        if not self.player.grounded:
            if self.player.v.y >= 0:
                self.player.image = self.player.fall
            else:
                self.player.image = self.player.jumping
        self.player.draw(surface, lights, self.x, self.y, self.t)
        if self.game_over:
            shadow = pygame.Surface((WIDTH, HEIGHT)).convert()
            shadow.set_alpha(min(255, int((self.t - self.game_over) * 255 / 500)))
            surface.blit(shadow, (0, 0))

        if not self.splash and \
                (self.t % LIGHTNING_PERIOD < 100 or 200 < self.t % LIGHTNING_PERIOD < 400):  # lightning
            surface.blit(self.lightning[0], (0, 0))
            self.screen.fill((255, 255, 255), (0, 0, WIDTH, HEIGHT))
            self.screen.blit(surface, (0, 0), None, pygame.BLEND_RGB_SUB)
            if not self.thunder:
                self.thunder = True
                play_sound("Thunder.wav")
                play_sound("Rain.wav", False)
                play_sound("Rain.wav")
        else:
            self.screen.blit(surface, (0, 0))
            self.screen.blit(lights, (0, 0), None, pygame.BLEND_RGB_MIN)
            if not self.splash and self.t % LIGHTNING_PERIOD < 400:
                self.screen.blit(self.lightning[0], (0, 0))
            self.thunder = False
        self.ui(self.screen)
        if self.t > self.wind and not self.splash:
            play_sound("Wind.wav", True)
            self.wind = self.t + 5000 + random.random()*(LIGHTNING_PERIOD - 5000)

    def key_pressed(self, key):
        """ Respond to a key press event """
        if key == pygame.K_RETURN:
            if self.splash:
                self.splash = False
                play_music("A_Dark_and_Stormy_Night.wav")
                self.t = 0
            elif self.victory and self.t - self.victory > 2000:
                self.reset(respawn=False)
                self.t = 0
                play_music("A_Dark_and_Stormy_Night.wav")
        if key == pygame.K_ESCAPE:
            self.full_screen = not self.full_screen
            if self.full_screen:
                self.screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            if "R" in self.input:
                self.input.remove("R")
            self.input.append("R")
        elif key == pygame.K_LEFT or key == pygame.K_a:
            if "L" in self.input:
                self.input.remove("L")
            self.input.append("L")
        elif key == pygame.K_UP or key == pygame.K_w or key == pygame.K_SPACE:
            if not self.game_over and not self.victory:
                self.player.jump()

    def update_keys(self, keys):
        """ Respond to a key press event """
        if "R" in self.input and not (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            self.input.remove("R")
        if "L" in self.input and not (keys[pygame.K_LEFT] or keys[pygame.K_a]):
            self.input.remove("L")

    ################################################################################

    def __init__(self, name):
        """ Initialize the game """
        self.pause = False
        self.t = 0
        self.x = 0
        self.y = 0
        self.player = None
        self.warning = None
        self.respawn = None
        self.sprites = []
        self.monsters = []
        self.ground = []
        self.walls = []
        self.house = None
        self.victory = False
        self.splash = True
        self.wind = 5000
        self.thunder = False
        self.checkpoints = []
        self.input = [""]
        self.game_over = False
        self.chaser = None
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0, 30'
        pygame.display.set_caption(name)
        self.full_screen = False
        if not self.full_screen:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT])
        else:
            self.screen = pygame.display.set_mode([WIDTH, HEIGHT], pygame.FULLSCREEN)
        icon = load_image("Icon.png", scale=1)[0]
        icon.set_colorkey((255, 0, 0))
        pygame.display.set_icon(icon)
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.font = pygame.font.SysFont("Calibri", 80)
        self.font2 = pygame.font.SysFont("Calibri", 40)
        self.lightning = load_image("Lightning.png", number=1, flip=False, scale=1)
        play_sound("Thunder.wav", False, 0.05)
        play_sound("Wind.wav", False, 0.1)
        play_sound("Lamp.wav", False, 0.1)
        play_sound("Rain.wav", False, 0.0)
        set_volume(0.05)

        self.reset()
        self.run()

    def run(self):
        """ Iteratively call update """
        clock = pygame.time.Clock()
        self.pause = False
        while not self.pause:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.key_pressed(event.key)
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
            dt = clock.tick(TIME_STEP)
            self.update(dt, pygame.key.get_pressed())
            pygame.display.update()


if __name__ == '__main__':
    game = Game("Thunderstorm")
