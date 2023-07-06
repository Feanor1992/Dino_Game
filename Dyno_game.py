from __future__ import annotations

import os
import sys
import pygame
from pygame import *
import random

pygame.init()

# display parameters
screen_size_display = (width_screen, height_screen) = (600, 150)
FPS = 60
gravity = 0.6

# colors
black = (0, 0, 0)
white = (255, 255, 255)
bg_color = (235, 235, 235)

highest_score = 0

# create a visible image surface on the monitor
screen_layout_display = pygame.display.set_mode(screen_size_display)
time_clock = pygame.time.Clock()
# Return the title and icon title for the display window
pygame.display.set_caption('Dino Run Game')

# sound that we will use in gameplay
jump_sound = pygame.mixer.Sound('resources/jump.wav')
checkpoint_sound = pygame.mixer.Sound('resources/checkPoint.wav')
die_sound = pygame.mixer.Sound('resources/die.wav')


# load image and colors function
def load_image(name: str, sx: int | float = -1, sy: int | float = -1, colorkey=None):
    # path to the image
    image_path = os.path.join('resources', name)
    img = pygame.image.load(image_path)
    img = img.convert()

    if colorkey is not None:
        if colorkey == -1:
            colorkey = img.get_at((0, 0))
        img.set_colorkey(colorkey, RLEACCEL)

    if sx != -1 or sy != -1:
        img = pygame.transform.scale(img, (sx, sy))

    return (img, img.get_rect())


def load_spriter_sheet(s_name: str, namex: int | float, namey: int | float, scx: int | float = -1,
                       scy: int | float = -1, c_key=None):
    sh_path = os.path.join('resources', s_name)
    sh = pygame.image.load(sh_path)
    sh = sh.convert()

    sh_rect = sh.get_rect()

    sprites = list()

    sx = sh_rect.width / namex
    sy = sh_rect.height / namey

    for i in range(0, namey):
        for j in range(0, namex):
            rectangle = pygame.Rect(j * sx, i * sy, sx, sy)
            # pygame object for representing images
            img = pygame.Surface(rectangle.size)
            img = img.convert()
            # draw many images onto another
            img.blit(sh, (0, 0), rectangle)

            if c_key is not None:
                if c_key == -1:
                    c_key = img.get_at((0, 0))
                img.set_colorkey(c_key, RLEACCEL)

            if scx != -1 or scy != -1:
                img = pygame.transform.scale(img, (scx, scy))

            sprites.append(img)
    sprite_rect = sprites[0].get_rect()

    return sprites, sprite_rect


# function of game over massage and replay button in screen window
def game_over_display_message(replay_button_image: Surface, game_over_image: Surface):
    replay_button_rect = replay_button_image.get_rect()

    # replay button position on the screen
    replay_button_rect.centerx = width_screen / 2
    replay_button_rect.top = height_screen * 0.52

    game_over_rect = game_over_image.get_rect()

    # game over message position on the screen
    game_over_rect.centerx = width_screen / 2
    game_over_rect.top = height_screen * 0.35

    # blit replay button and game over message on the screen
    screen_layout_display.blit(replay_button_image, replay_button_rect)
    screen_layout_display.blit(game_over_image, game_over_rect)


def extract_digits(num: int | float) -> list:
    if num > -1:
        d = list()
        i = 0

        while num / 10 != 0:
            d.append(num % 10)
            num = int(num / 10)

        d.append(num % 10)
        for i in range(len(d), 5):
            d.append(0)
        d.reverse()

        return d


class Dino:
    """Dino's init and actions in the screen window"""

    def __init__(self, sx: int = -1, sy: int = -1):
        self.imgs, self.rectangle = load_spriter_sheet('dino.png', 5, 1, sx, sy, -1)
        self.imgs_upd, self.rectangle_upd = load_spriter_sheet('dino_ducking.png', 2, 1, 59, sy, -1)
        self.rectangle.bottom = int(0.98 * height_screen)
        self.rectangle.left = width_screen / 15
        self.image = self.imgs[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.jumping = False
        self.dead = False
        self.duking = False
        self.blinking = False
        self.movement = [0, 0]
        self.jump_speed = 11.5
        self.stand_position_width = self.rectangle.width
        self.duck_position_width = self.rectangle_upd.width

    # function for drawing Dino
    def draw(self):
        screen_layout_display.blit(self.image, self.rectangle)

    def check_bounds(self):
        if self.rectangle.bottom > int(0.98 * height_screen):
            self.rectangle.bottom = int(0.98 * height_screen)
            self.jumping = False

    # function for moving Dino on the screen
    def update(self):
        if self.jumping:
            self.movement[1] = self.movement[1] + gravity

        if self.jumping:
            self.index = 0
        elif self.blinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1) % 2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1) % 2
        elif self.duking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2

        if self.dead:
            self.index = 4

        if not self.duking:
            self.image = self.imgs[self.index]
            self.rectangle.width = self.stand_position_width
        else:
            self.image = self.imgs_upd[self.index % 2]
            self.rectangle.width = self.duck_position_width

        self.rectangle = self.rectangle.move(self.movement)
        self.check_bounds()

        if not self.dead and self.counter % 7 == 6 and self.blinking == False:
            self.score += 1
            if self.score % 100 == 0 and self.score != 0:
                if pygame.mixer.get_init() != None:
                    checkpoint_sound.play()

        self.counter = (self.counter + 1)


class Cactus(pygame.sprite.Sprite):
    """class for drawing and moving cactus on the screen"""

    def __init__(self, speed: int = 5, sx: int = -1, sy: int = -1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.imgs, self.rectangle = load_spriter_sheet('cactus-small.png', 3, 1, sx, sy, -1)
        self.rectangle.bottom = int(0.98 * height_screen)
        self.rectangle.left = width_screen + self.rectangle.width
        self.image = self.imgs[random.randrange(0, 3)]
        self.movement = [-1 * speed, 0]

    # function for Cactus drawing
    def draw(self):
        screen_layout_display.blit(self.image, self.rectangle)

    # function for moving cactus on the screen
    def update(self):
        self.rectangle = self.rectangle.move(self.movement)

        if self.rectangle.right < 0:
            self.kill()


class birds(pygame.sprite.Sprite):
    """class for drawing and moving birds on the screen"""

    def __init__(self, speed: int = 5, sx: int = -1, sy: int = -1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.imgs, self.rectangle = load_spriter_sheet('birds.png', 2, 1, sx, sy, -1)
        self.birds_height = [height_screen * 0.82, height_screen * 0.75, height_screen * 0.6]
        self.rectangle.centery = self.birds_height[random.randrange(0, 3)]
        self.rectangle.left = width_screen + self.rectangle.width
        self.image = self.imgs[0]
        self.movement = [-1 * speed, 0]
        self.index = 0
        self.counter = 0

    # function for birds drawing
    def draw(self):
        screen_layout_display.blit(self.image, self.rectangle)

    # function for birds moving
    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index + 1) % 2

        self.image = self.imgs[self.index]
        self.rectangle = self.rectangle.move(self.movement)
        self.counter = self.counter + 1

        if self.rectangle.right < 0:
            self.kill()


class ground():
    def __init__(self, speed : int = -5):
        self.image, self.rectangle = load_image('ground.png', -1, -1, -1)
        self.image_1, self.rectangle_1 = load_image('ground.png', -1, -1, -1)
        self.rectangle.bottom = height_screen
        self.rectangle_1.bottom = height_screen
        self.rectangle_1.left = self.rectangle.right
        self.speed = speed

    # function for drawing ground on the screen
    def draw(self):
        screen_layout_display.blit(self.image, self.rectangle)
        screen_layout_display.blit(self.image_1, self.rectangle_1)

    # function for grond moving
    def update(self):
        self.rectangle.left += self.speed
        self.rectangle_1.left += self.speed

        if self.rectangle < 0:
            self.rectangle.left = self.rectangle_1.right

        if self.rectangle_1 < 0:
            self.rectangle_1.left = self.rectangle.right
























