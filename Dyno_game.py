from __future__ import annotations

import os
import sys
import pygame
from pygame import *
import random

pygame.init()

# display parameters
screen_size_display = (width_screen, height_screen) = (900, 950)
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
    """class for drawing and moving ground on the screen"""

    def __init__(self, speed: int = -5):
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


class clouds(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rectangle = load_image('cloud.png', int(90 * 30 / 42), 30, -1)
        self.speed = 1
        self.rectangle.left = x
        self.rectangle.top = y
        self.movement = [-1 * self.speed, 0]

    # function for drawing clouds on the screen
    def draw(self):
        screen_layout_display.blit(self.image, self.rectangle)

    # function for clouds moving
    def update(self):
        self.rectangle = self.rectangle.move(self.movement)
        if self.rectangle.right < 0:
            self.kill()


class scoreboard():
    """add scoreboard to the screen"""

    def __init__(self, x: int = -1, y: int = -1):
        self.score = 0
        self.scoreboard_image, self.scoreboard_rectangle = load_spriter_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5),
                                                                              -1)
        self.image = pygame.Surface((55, int(11 * 6 / 5)))
        self.rectangle = self.image.get_rect()

        if x == -1:
            self.rectangle.left = width_screen * 0.89
        else:
            self.rectangle.left = x

        if y == -1:
            self.rectangle.top = height_screen * 0.1
        else:
            self.rectangle.top = y

    # function for drawing scoreboard on the screen
    def draw(self):
        screen_layout_display.blit(self.image, self.rectangle)

    # function for update score in scoreboard
    def update(self, score: int):
        score_digits = extract_digits(score)
        self.image.fill(bg_color)

        for digit in score_digits:
            self.image.blit(self.scoreboard_image[digit], self.scoreboard_rectangle)
            self.scoreboard_rectangle.left += self.scoreboard_rectangle.width

        self.scoreboard_rectangle.left = 0


# function for start position of all stuff and moving Dino
def introduction_screen():
    dino_position = Dino(44, 47)
    dino_position.blinking = True
    starting_game = False

    t_ground, t_ground_rectangle = load_spriter_sheet('ground.png', 15, 1, -1, -1, -1)
    t_ground_rectangle.left = width_screen / 20
    t_ground_rectangle.bottom = height_screen

    # logo place in the screen
    logo, logo_rectangle = load_image('logo.png', 300, 400, -1)
    logo_rectangle.centerx = width_screen * 0.6
    logo_rectangle.centery = height_screen * 0.6

    # add event for Quit the game and keys for moving Dino
    while not starting_game:
        if pygame.display.get_surface() is None:
            print("Couldn't load display surface")
            return True
        else:
            if event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        dino_position.jumping = True
                        dino_position.blinking = False
                        dino_position.movement[1] = -1 * dino_position.jump_speed

        dino_position.update()

        if pygame.display.get_surface() is not None:
            screen_layout_display.fill(bg_color)
            screen_layout_display.blit(t_ground[0], t_ground_rectangle)

            if dino_position.blinking:
                screen_layout_display.blit(logo, logo_rectangle)

            dino_position.draw()

            pygame.display.update()

        time_clock.tick(FPS)

        if dino_position.jumping == False and dino_position.blinking == False:
            starting_game = True


# gameplay function
def gameplay():
    global highest_score

    gp= 4
    start_menu = False
    game_over = False
    game_exit = False

    gamer_dino = Dino(44, 47)
    new_ground = ground(-1 * gp)
    score_board = scoreboard()
    high_score = scoreboard(width_screen * 0.78)
    counter = 0

    npc_cactus = pygame.sprite.Group()
    npc_bird = pygame.sprite.Group()
    npc_cloud = pygame.sprite.Group()
    last_end_obs = pygame.sprite.Group()

    Cactus.containers = npc_cactus
    birds.containers = npc_bird
    clouds.containers = npc_cloud

    replay_button_image, replay_button_rectangle = load_image('replay_button.png', 35, 31, -1)
    game_over_image, game_over_rectangle = load_image('game_over.png', 190, 11, -1)

    # add time counter on display
    time_images, time_rectangle = load_spriter_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
    time_counter_image = pygame.Surface((22, int(11 * 6 / 5)))
    time_counter_rectangle = time_counter_image.get_rect()
    time_counter_image.fill(bg_color)
    time_counter_image.blit(time_images[10], time_rectangle)
    time_rectangle.left += time_rectangle.width
    time_counter_image.blit(time_images[11], time_rectangle)
    time_counter_rectangle.top = height_screen * 0.1
    time_counter_rectangle.left = width_screen * 0.73

    # game loop
    while not  game_exit:
        while start_menu:
            pass

        while not game_over:
            if pygame.display.get_surface() is None:
                print("Couldn't load display surface")
                game_over = True
                game_exit = True
            else:
                for event in pygame.event.get():
                    # quit the game
                    if event.type == pygame.QUIT:
                        game_over = True
                        game_exit = True

                    # moving Dino
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if gamer_dino.rectangle.bottom == int(0.98 * height_screen):
                                gamer_dino.jumping = True

                                # Initialize the mixer module for jump sound
                                if pygame.mixer.get_init() is not None:
                                    jump_sound.play()

                                gamer_dino.movement[1] = -1 * gamer_dino.jump_speed

                        if event.key == pygame.K_DOWN:
                            if not (gamer_dino.jumping and gamer_dino.dead):
                                gamer_dino.duking = True

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_DOWN:
                            gamer_dino.duking = False

            # cactus moving in gameplay
            for cactus in npc_cactus:
                cactus.movement[0] = -1 * gp

                # add game over = True and sound of Dino dying when he faced a cactus
                if pygame.sprite.collide_mask(gamer_dino, cactus):
                    gamer_dino.dead = True

                    if pygame.mixer.get_init() is not None:
                        die_sound.play()

            # birds moving gameplay
            for bird in npc_bird:
                bird.movement[0] = -1 * gp

                # add game over = True and sound of Dino dying when he faced a bird
                if pygame.sprite.collide_mask(gamer_dino, bird):
                    gamer_dino.dead = True

                    if pygame.mixer.get_init() is not None:
                        die_sound.play()

            if len(npc_cactus) < 2:
                if len(npc_cactus) == 0:
                    last_end_obs.empty()
                    last_end_obs.add(Cactus(gp, 40, 40))
                else:
                    for l in last_end_obs:
                        if l.rect.right < width_screen * 0.7 and random.randrange(0, 50) == 10:
                            last_end_obs.empty()
                            last_end_obs.add(Cactus(gp, 40, 40))

            if len(npc_bird) == 0 and random.randrange(0, 200) == 10 and counter > 500:
                for l in last_end_obs:
                    if l.rect.right < width_screen * 0.8:
                        last_end_obs.empty()
                        last_end_obs.add(birds(gp, 46, 40))

            if len(npc_cloud) < 5 and random.randrange(0, 300) == 10:
                clouds(width_screen, random.randrange(height_screen / 5, height_screen / 2))

            # update dino and others on screen
            gamer_dino.update()
            npc_cactus.update()
            npc_bird.update()
            npc_cloud.update()
            new_ground.update()
            score_board.update(gamer_dino.score)
            high_score.update(highest_score)

            # draw updating screen
            if pygame.display.get_surface() is not None:
                screen_layout_display.fill(bg_color)
                new_ground.draw()
                npc_cloud.draw(screen_layout_display)
                score_board.draw()

                if highest_score != 0:
                    high_score.draw()
                    screen_layout_display.blit(time_counter_image, time_counter_rectangle)

                npc_cactus.draw(screen_layout_display)
                npc_bird.draw(screen_layout_display)
                gamer_dino.draw()

                pygame.display.update()

            time_clock.tick(FPS)

            # game over true if Dino died and add new highest score if it is highest
            if gamer_dino.dead:
                game_over = True

                if gamer_dino.score > highest_score:
                    highest_score = gamer_dino.score

            # increase speed each 700 points
            if counter % 700 == 699:
                new_ground.speed -= 1
                gp += 1

            # increase counter
            counter = counter + 1

        # exit game
        if game_exit:
            break

        # game over options
        while game_over:
            if pygame.display.get_surface() is None:
                print("Couldn't load display surface")
                game_over = True
                game_exit = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = False
                        game_exit = True

                    if event.type == pygame.KEYDOWN:
                        if event.key  == pygame.K_ESCAPE:
                            game_over = False
                            game_exit = True

                        if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            game_over = False
                            gameplay()

            high_score.update(highest_score)

            if pygame.display.get_surface() is not None:
                game_over_display_message(replay_button_image, game_over_image)

                if highest_score != 0:
                    high_score.draw()
                    screen_layout_display.blit(time_counter_image, time_counter_rectangle)

                pygame.display.update()

            time_clock.tick(FPS)

    pygame.quit()
    quit()


def main():
    isGameQuit = introduction_screen()
    if not isGameQuit:
        gameplay()

main()
























