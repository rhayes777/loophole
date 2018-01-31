import pygame
import util

# Colour Constants

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (180, 60, 30)
GREEN = (46, 190, 60)
BLUE = (30, 48, 180)
PINK_MASK = (255, 0, 255)

# Get display info

info = pygame.display.Info()

# Create pygame group for sprites
all_sprites = pygame.sprite.Group()


class Flash(object):
    def __init__(self, time):
        self.time = time
        self.blit_surface = pygame.Surface((info.current_w, info.current_h))

        self.blit_surface.fill((255, 255, 255))
        self.timer = -2

    def make_flash(self):
        self.timer = self.time

    def render(self, this_screen):
        self.this_screen = this_screen

        if self.timer >= 0:
            alpha = util.get_new_range_value(1, self.time, self.timer, 0, 255)
            print(alpha)
            self.timer -= 1
            self.blit_surface.set_alpha(alpha)
            self.this_screen.blit(self.blit_surface, (0, 0))

    def is_flashing(self):
        return self.timer > 1  # if timer is greater than 1, is_flashing is true


class Pixel(object):
    def __init__(self, pos_x, pos_y, is_on, size, ref, colour=BLUE):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.is_on = is_on
        self.size = size
        self.ref = ref
        self.colour = colour

    def show(self, this_screen):
        self.this_screen = this_screen
        if self.colour == RED:
            self.size += 1

            # determine colour based on position
            color = [
                util.get_new_range_value(0, info.current_w, self.pos_x, 30, 255),  # Red
                util.get_new_range_value(0, info.current_h, self.pos_y, 20, 140),  # Green
                util.get_new_range_value(0, info.current_h, self.pos_y, 120, 255)  # Blue
            ]

            pygame.draw.ellipse(this_screen, color,
                                [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 0)

            pygame.draw.ellipse(this_screen,
                                [
                                    util.get_new_range_value(0, info.current_w, self.pos_x, 120, 255),  # Red
                                    util.get_new_range_value(0, info.current_h, self.pos_y, 30, 255),  # Green
                                    util.get_new_range_value(0, info.current_h, self.pos_y, 20, 140)  # Blue
                                ],
                                [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 4)
