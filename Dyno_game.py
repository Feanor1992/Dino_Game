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







