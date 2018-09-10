# To Do

# Set media/img directory and use os.path.join to avoid cross-platform issue with directory address. done
# Wrap this into a function
# Load images into sprites eg. minim.Sprite
# Display sprites with brightness

# invert sprite BMPs so they are white

import pygame
import os

BLACK = [0,0,0]
WHITE = [255, 255, 255]

pygame.init()
# init pygame display
pygame.display.init()
clock = pygame.time.Clock()

# screen setup
screen = pygame.display.set_mode((1240, 1080))

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
images_dict = {
    0 : image_minim,
    1 : image_crotchet,
    2 : image_quaver,
    3 : image_semiquaver
}

alpha = 255

image_minim.set_alpha(alpha)

image_minim_transparent = image_minim.copy()
image_minim_transparent.fill((255, 255, 255, alpha), None, pygame.BLEND_RGBA_MULT)

sprite_group_notes = pygame.sprite.Group()

class Note(pygame.sprite.Sprite):

    def __init__(self, x, y, style, brightness):

        pygame.sprite.Sprite.__init__(self, sprite_group_notes)

        self.rect = [x, y]

        # 0 = Half Note (Minim)
        # 1 = Quarter Note (Crotchet)
        # 2 = Eighth Note (Quaver)
        # 3 = Sixteenth note (Semiquaver)
        self.style = style

        self.brightness = brightness

        self.temp_image = images_dict[style]

        self.image = self.temp_image.copy()
        self.image.fill((0, 0, self.brightness, self.brightness), None, pygame.BLEND_RGBA_MULT)

    def set_brightness(self, brightness):

        self.brightness = brightness

test_notes_list = []

for i in range(1, 20):

    for j in range(0, 4):

        test_notes_list.append(Note(30 * i, 45 * j, j, i*12))


while True:
    clock.tick(40)
    screen.fill(WHITE)

    sprite_group_notes.draw(screen)

    pygame.display.flip()

    pygame.event.get()

pygame.quit()