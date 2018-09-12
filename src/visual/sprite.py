# To Do

# Set media/img directory and use os.path.join to avoid cross-platform issue with directory address. done
# Wrap this into a function
# Load images into sprites eg. minim.Sprite
# Display sprites with brightness

# invert sprite BMPs so they are white

import pygame
import os


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


SCREEN_SHAPE = (1080, 1240)

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
    0: Color.BLUE,
    1: Color.RED,
    2: Color.YELLOW,
    3: Color.GREEN
}

sprite_group_notes = pygame.sprite.Group()


class Note(pygame.sprite.Sprite):

    def __init__(self, position=(SCREEN_SHAPE[0] / 2, SCREEN_SHAPE[1] / 2), style=Style.Minim, alpha=255):
        pygame.sprite.Sprite.__init__(self, sprite_group_notes)

        self.rect = position

        # 0 = Half Note (Minim)
        # 1 = Quarter Note (Crotchet)
        # 2 = Eighth Note (Quaver)
        # 3 = Sixteenth note (Semiquaver)
        self.style = style

        self.__alpha = alpha

        self.image = images_dict[style].copy()
        color = color_dict[style]
        self.image.fill(color + (self.alpha,), None, pygame.BLEND_RGBA_MULT)

    @property
    def alpha(self):
        return self.__alpha

    @alpha.setter
    def alpha(self, new_value):
        self.__alpha = new_value


test_notes_list = []
#
# for i in range(1, 20):
#
#     for j in range(0, 4):
#         test_notes_list.append(Note((30 * i, 45 * j), j, Color.GREEN, i * 12))


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
