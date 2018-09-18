# To Do

# Set media/img directory and use os.path.join to avoid cross-platform issue with directory address. done
# Wrap this into a function
# Load images into sprites eg. minim.Sprite
# Display sprites with brightness

# invert sprite BMPs so they are white

import pygame
import os
import math


class Color(object):
    # Basic colours

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (0, 255, 255)

    # Palette colours

    PURPLE_DARK = (48, 0, 15)
    PURPLE_MID = (73, 0, 45)
    PURPLE_LIGHT = (94, 0, 74)

    PINK_DARK = (100, 34, 80)
    PINK_MID = (100, 62, 100)
    PINK_LIGHT = (100, 87, 100)

    TEAL_DARK = (13, 70, 86)
    TEAL_MID = (44, 92, 100)
    TEAL_LIGHT = (77, 90, 100)

    BLUE_DARK = (20, 40, 100)
    BLUE_MID = (50, 68, 100)
    BLUE_LIGHT = (77, 90, 100)

    GREEN_DARK = (15, 52, 34)
    GREEN_MID = (45, 77, 62)
    GREEN_LIGHT = (74, 96, 86)

    ORANGE_DARK = (72, 30, 0)
    ORANGE_MID = (94, 58, 0)
    ORANGE_LIGHT = (100, 84, 0)


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

# load minim image, prepare it for alpha functions (transparency)
image_minim = pygame.image.load(os.path.join(image_directory, "minim.bmp"))
image_crotchet = pygame.image.load(os.path.join(image_directory, "crotchet.bmp"))
image_quaver = pygame.image.load(os.path.join(image_directory, "quaver.bmp"))
image_semiquaver = pygame.image.load(os.path.join(image_directory, "semiquaver.bmp"))
image_crotchet_rotation = pygame.image.load(os.path.join(image_directory, "crotchet_glow_rotation.bmp"))


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

sprite_group_notes = pygame.sprite.Group()


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

        color = color_dict[style]
        self.image.fill(color + (self.alpha,), None, pygame.BLEND_RGBA_MULT)


test_notes_list = []


class SpriteSheet(object):

    def __init__(self, filename, shape, total_frames, key=(255, 255, 255)):
        self.filename = filename
        self.shape = shape
        self.total_frames = total_frames
        self.key = key

    def get_image(self, frame_number):
        frame = frame_number % self.total_frames
        surface = pygame.Surface(self.shape, depth=24)
        surface.fill(self.key, surface.get_rect())
        surface.set_colorkey(self.key)
        surface.blit(self.filename, (0, 0), (0, frame * self.shape[1], self.shape[0], self.shape[1]))
        surface.set_alpha(128)

        return surface

    def frame_number_for_angle(self, angle):
        return int((angle / (2 * math.pi)) * self.total_frames) % self.total_frames

    def image_for_angle(self, angle):
        return self.get_image(self.frame_number_for_angle(angle))


sprite_sheet = SpriteSheet(image_crotchet_rotation, (65, 65), 15)


def draw():
    screen.fill(Color.BLACK)

    sprite_group_notes.draw(screen)

    pygame.display.flip()


if __name__ == "__main__":
    while True:
        clock.tick(40)
        draw()
        pygame.event.get()

    pygame.quit()
