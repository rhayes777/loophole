import pygame
import util
import math

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


class NoteSprite(object):
    def __init__(self, pos_x, pos_y, size, ref, velocity=0, angle=0, growth_rate=1, is_on=False, colour=RED):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = 0
        self.origin_x, self.origin_y = 0, 0
        self.size = size
        self.ref = ref
        self.velocity = velocity
        self.velocity_z = 3
        self.angle = angle
        self.angle_zx = 0
        self.angle_zy = 0
        self.growth_rate = growth_rate / self.velocity
        self.is_on = is_on
        self.colour = colour

    def update(self):
        """ Do movement calculations """

        """ Find Origin x, y """
        self.origin_x, self.origin_y = pygame.mouse.get_pos()

        """ Get distance from object's x and y to origin's x and y's """
        x_distance_to_origin = (self.pos_x - self.origin_x)
        y_distance_to_origin = (self.pos_y - self.origin_y)

        """ Get angles between z -> x and z -> y """
        self.angle_zx = math.sin(x_distance_to_origin)
        self.angle_zy = math.cos(y_distance_to_origin)

        """ Calculate how much to move each frame """
        x_add = self.velocity * math.sin(self.angle)
        y_add = self.velocity * math.cos(self.angle)
        z_add = self.velocity_z

        """ Update position """
        self.pos_x = self.pos_x + x_add
        self.pos_y = self.pos_y + y_add
        self.pos_z = self.pos_z + z_add

        print("Pos_z = ", self.pos_z)

    def show(self, this_screen):
        """ Find Origin x, y """
        self.origin_x, self.origin_y = pygame.mouse.get_pos()
        size_multiplier = util.get_new_range_value(1, 50, self.pos_z, 1, 1.3)

        if self.size <= 250:
            self.size = self.size * size_multiplier

        self.this_screen = this_screen
        if self.size < 250 and self.is_on:

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
