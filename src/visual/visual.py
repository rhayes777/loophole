# To Do

# Set media/img directory and use os.path.join to avoid cross-platform issue with directory address. done
# Wrap this into a function
# Load images into sprites eg. minim.Sprite
# Display sprites with brightness

# invert sprite BMPs so they are white

import math
import os
from random import randint

import pygame

import font


class Color(object):
    # Basic colours

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (123, 123, 123)
    GREY_DARK = (30, 30, 50)

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (0, 255, 255)

    # Palette colours

    PURPLE_DARK = (48, 0, 15)
    PURPLE_MID = (73, 0, 45)
    PURPLE_LIGHT = (194, 0, 174)

    PINK_DARK = (100, 34, 80)
    PINK_MID = (100, 62, 100)
    PINK_LIGHT = (100, 87, 100)

    TEAL_DARK = (13, 70, 86)
    TEAL_MID = (44, 92, 100)
    TEAL_LIGHT = (177, 90, 200)

    BLUE_DARK = (20, 40, 100)
    BLUE_MID = (50, 68, 100)
    BLUE_LIGHT = (177, 90, 200)

    GREEN_DARK = (15, 52, 34)
    GREEN_MID = (45, 77, 62)
    GREEN_LIGHT = (174, 96, 186)

    ORANGE_DARK = (72, 30, 0)
    ORANGE_MID = (94, 58, 0)
    ORANGE_LIGHT = (200, 184, 0)


SCREEN_SHAPE = (1080, 800)

pygame.init()
# init pygame display
pygame.display.init()
clock = pygame.time.Clock()

# screen setup
screen = pygame.display.set_mode(SCREEN_SHAPE)

# Image directory stuff

# find the directory the application is in, applying path.dirname to avoid problems with slashes etc
directory_name = os.path.dirname(os.path.realpath(__file__))

# set where image directory is in relation to visual directory
image_directory_name = "../media/images"

# join the above two together with path.join to avoid problems again
image_directory = os.path.join(directory_name, image_directory_name)

# Load Images

# background
image_background = pygame.image.load(os.path.join(image_directory, "background.bmp"))

# load note images, prepare it for alpha functions (transparency)
image_minim = pygame.image.load(os.path.join(image_directory, "minim.bmp"))
image_crotchet = pygame.image.load(os.path.join(image_directory, "crotchet.bmp"))
image_quaver = pygame.image.load(os.path.join(image_directory, "quaver.bmp"))
image_semiquaver = pygame.image.load(os.path.join(image_directory, "semiquaver.bmp"))
image_crotchet_rotation = pygame.image.load(os.path.join(image_directory, "crotchet_glow_rotation.bmp"))

# load energy glow
image_energy_glow = pygame.image.load(os.path.join(image_directory, "energy_glow.bmp"))

# load player
image_player = pygame.image.load(os.path.join(image_directory, "player_cursor.bmp"))


# Image Dictionary - stores images, mapped to integers (0 to 3 currently)
# 0 = Half Note (Minim)
# 1 = Quarter Note (Crotchet)
# 2 = Eighth Note (Quaver)
# 3 = Sixteenth note (Semiquaver)


class Style(object):
    Minim = 0
    Crotchet = 1
    Quaver = 2
    SemiQuaver = 3


images_dict = {
    0: image_minim,
    1: image_crotchet,
    2: image_quaver,
    3: image_semiquaver
}

color_dict = {
    0: Color.PURPLE_LIGHT,
    1: Color.ORANGE_LIGHT,
    2: Color.PINK_LIGHT,
    3: Color.TEAL_LIGHT
}

sprite_group_player = pygame.sprite.Group()
sprite_group_notes = pygame.sprite.Group()
sprite_group_energy_glows = pygame.sprite.Group()


class PlayerCursor(pygame.sprite.Sprite):

    def __init__(self, image, position=(SCREEN_SHAPE[0] / 2, SCREEN_SHAPE[1] / 2), alpha=255):
        pygame.sprite.Sprite.__init__(self, sprite_group_player)

        self.image = image.copy()

        self.rect = position

        self.alpha = alpha

        self.image.set_colorkey(Color.BLACK)

    def draw(self, pos):
        new_x = pos[0] - 25
        new_y = pos[1] - 25

        self.rect = (new_x, new_y)


player_cursor_instance = PlayerCursor(image_player)

circle_effects_list = []


class CircleEffect(object):

    def __init__(self, color=Color.WHITE, position=(SCREEN_SHAPE[0] / 2, SCREEN_SHAPE[1] / 2), size=1, scale_rate=4,
                 max_size=randint(250, 550)):
        self.position = position

        self.color = color

        self.scale_rate = scale_rate

        self.max_size = max_size

        self.size = size

        circle_effects_list.append(self)

    def draw(self, surface):
        self.size += self.scale_rate

        self.scale_rate *= 1.1

        self.color = scale_rgb(Color.WHITE, Color.GREY_DARK, self.size / self.max_size)

        pygame.draw.ellipse(surface, self.color, [self.position[0] - self.size / 2, self.position[1] - self.size / 2,
                                                  self.size, self.size], 1)


def make_circle_explosion(color=Color.GREY, number=randint(2, 6), position=(SCREEN_SHAPE[0] / 2, SCREEN_SHAPE[1] / 2)):
    for i in range(number):
        CircleEffect(color, position, (i + 1) / 2, randint(3, 6))


def render_circle_effects(surface):
    for circle_effect in list(circle_effects_list):
        circle_effect.draw(surface)
        if circle_effect.size > circle_effect.max_size:
            circle_effects_list.remove(circle_effect)


energy_img_size = image_energy_glow.get_rect()
image_energy_width = energy_img_size.width
image_energy_height = energy_img_size.height

GLOW_POS_LEFT = (0 - image_energy_width / 2, SCREEN_SHAPE[1] / 2 - image_energy_height / 2)
GLOW_POS_UP = [SCREEN_SHAPE[0] / 2 - image_energy_width / 2, 0 - image_energy_height / 2]
GLOW_POS_RIGHT = [SCREEN_SHAPE[0] - image_energy_width / 2, SCREEN_SHAPE[1] / 2 - image_energy_height / 2]
GLOW_POS_DOWN = [SCREEN_SHAPE[0] / 2 - image_energy_width / 2, SCREEN_SHAPE[1] - image_energy_height / 2]


class EnergyGlow(pygame.sprite.Sprite):

    def __init__(self, position=GLOW_POS_LEFT, style=Style.Minim, alpha=255):
        pygame.sprite.Sprite.__init__(self, sprite_group_energy_glows)

        self.image = image_energy_glow.copy()

        px = position[0]
        py = position[1]

        newx = px - 300
        newy = py - 300

        self.rect = (newx, newy)

        self.color = color_dict[style]

        self.image.fill(self.color + (alpha,), None, pygame.BLEND_RGBA_MULT)

        energy_glows.append(self)

    def set_alpha(self, alpha):
        self.image = image_energy_glow.copy()

        self.image.fill(self.color + (alpha,), None, pygame.BLEND_RGBA_MULT)


energy_glows = []


class Note(pygame.sprite.Sprite):

    def __init__(self, image, position=(SCREEN_SHAPE[0] / 2, SCREEN_SHAPE[1] / 2), style=Style.Minim, alpha=255):
        pygame.sprite.Sprite.__init__(self, sprite_group_notes)

        self.rect = position

        # 0 = Half Note (Minim)
        # 1 = Quarter Note (Crotchet)
        # 2 = Eighth Note (Quaver)
        # 3 = Sixteenth note (Semiquaver)
        self.style = style

        self.alpha = alpha

        self.image = image

        # self.image.set_colorkey(Color.WHITE)

        color = color_dict[style]

        self.image.fill(color + (self.alpha,), None, pygame.BLEND_RGBA_MULT)


test_notes_list = []


class SpriteSheet(object):

    def __init__(self, image, shape, total_frames, key=(255, 255, 255)):
        self.image = image
        self.shape = shape
        self.total_frames = total_frames
        self.key = key

    def get_image(self, frame_number):
        frame = frame_number % self.total_frames
        surface = pygame.Surface(self.shape, depth=24)
        surface.fill(self.key, surface.get_rect())
        surface.set_colorkey(self.key)
        surface.blit(self.image, (0, 0), (0, frame * self.shape[1], self.shape[0], self.shape[1]))
        surface.set_alpha(255)

        return surface

    def frame_number_for_angle(self, angle):
        return int((angle / (2 * math.pi)) * self.total_frames) % self.total_frames

    def image_for_angle(self, angle):
        return self.get_image(self.frame_number_for_angle(angle))


sprite_sheet = SpriteSheet(image_crotchet_rotation, (65, 65), 15, Color.BLACK)


def make_score_notice(text, position, life, style):
    font.Score(text, position, tuple(min(val + 50, 255) for val in color_dict[style]), 40, font.font_arcade, life)


def fill_gradient(surface, color, gradient, rect=None, vertical=True, forward=True):
    """fill a surface with a gradient pattern
    Parameters:
    color -> starting color
    gradient -> final color
    rect -> area to fill; default is surface's rect
    vertical -> True=vertical; False=horizontal
    forward -> True=forward; False=reverse

    Pygame recipe: http://www.pygame.org/wiki/GradientCode
    """
    if rect is None:
        rect = surface.get_rect()
    x1, x2 = rect.left, rect.right
    y1, y2 = rect.top, rect.bottom
    if vertical:
        h = y2 - y1
    else:
        h = x2 - x1
    if forward:
        a, b = color, gradient
    else:
        b, a = color, gradient
    rate = (
        float(b[0] - a[0]) / h,
        float(b[1] - a[1]) / h,
        float(b[2] - a[2]) / h
    )
    fn_line = pygame.draw.line
    if vertical:
        for line in range(y1, y2):
            color = (
                min(max(a[0] + (rate[0] * (line - y1)), 0), 255),
                min(max(a[1] + (rate[1] * (line - y1)), 0), 255),
                min(max(a[2] + (rate[2] * (line - y1)), 0), 255)
            )
            fn_line(surface, color, (x1, line), (x2, line))
    else:
        for col in range(x1, x2):
            color = (
                min(max(a[0] + (rate[0] * (col - x1)), 0), 255),
                min(max(a[1] + (rate[1] * (col - x1)), 0), 255),
                min(max(a[2] + (rate[2] * (col - x1)), 0), 255)
            )
            fn_line(surface, color, (col, y1), (col, y2))


def scale_rgb(original_rgb, target_rgb, scalar):
    range__r = original_rgb[0] - target_rgb[0]
    range__g = original_rgb[1] - target_rgb[1]
    range__b = original_rgb[2] - target_rgb[2]

    return__r = original_rgb[0] - (range__r * scalar)
    return__g = original_rgb[1] - (range__g * scalar)
    return__b = original_rgb[2] - (range__b * scalar)

    if return__r >= 255:
        return__r = 255
    if return__g >= 255:
        return__g = 255
    if return__b >= 255:
        return__b = 255

    calculated__r_g_b = [int(return__r), int(return__g), int(return__b)]

    return calculated__r_g_b


def draw():
    # screen.blit(image_background, image_background.get_rect())
    screen.fill(Color.GREY_DARK)

    sprite_group_energy_glows.draw(screen)

    sprite_group_notes.draw(screen)

    sprite_group_player.draw(screen)

    print(player_cursor_instance.rect)

    timer = 0

    timer += 1

    render_circle_effects(screen)

    font.render_notices(screen)

    pygame.display.update()


if __name__ == "__main__":
    while True:
        clock.tick(40)
        draw()
        pygame.event.get()

    # pygame.quit()
