import pygame
import util
import math
import random

# Colour Constants

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (180, 60, 30)
GREEN = (46, 190, 60)
BLUE = (30, 48, 180)
PINK_MASK = (255, 0, 255)

# Get display info

info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h))

# Create pygame group for sprites
all_sprites = pygame.sprite.Group()

# Camera - this is the (abstract) point from which we are viewing the scene
#
# Z = 0 is the furthest away from the camera/viewer we will render
# as an object's Z value becomes larger, the object is closer to the viewer
# and will be rendered larger, giving a sense of perspective and scale

# For now, camera is fixed at dead centre of screen...

CAM_x = screen.get_width() / 2
CAM_y = screen.get_height() / 2

# ...and is placed 500px back from the scene

CAM_z = 500

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


class Sprite3D(object):
    def __init__(self, pos_x, pos_y, pos_z, angle_xy=math.radians(random.randint(0, 360)),
                 angle_zx=math.radians(random.randint(0, 180)), velocity=2.5):
        """ x, y, z co-ordinates """
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z

        """ angle_zx is the angle at which the object is moving along the Z-X axis... """
        """ So it's the 'bird's eye view' angle of movement of the object """
        """ 0 will be fully "left" as you're looking at it, with object not moving towards viewer at all """
        """ 180 would be fully "right" so the opposite direction, still no Z axis movement - """
        """ 90 is exactly towards the viewer (so no x-axis movement) """

        self.angle_zx = angle_zx

        """ angle_xy is along the 'normal' 2D plane ie. x and y """
        """ so 0 is directly up the screen, 180 is directly down etc """

        self.angle_xy = angle_xy
        self.velocity = velocity

        """ This is the 'original' size of the object: The size it has when rendered at Z = 0 """

        self.size = 10
        self.size_render = self.size
        self.this_screen = None

    def update(self):
        """ Do movement calculations """

        x_add = self.velocity * math.cos(self.angle_xy)
        y_add = self.velocity * math.sin(self.angle_xy)
        z_add = self.velocity * math.sin(self.angle_zx)

        """ Update position """

        self.pos_x = self.pos_x + x_add
        self.pos_y = self.pos_y + y_add
        self.pos_z = self.pos_z + z_add

        print("3D Obj pos_z: ", self.pos_z)
        print("3D Obj pos_x: ", self.pos_x)

        """ Figuring out scale """

        max_scale = screen.get_width() / self.size
        z_scale = util.get_new_range_value(0, CAM_z, self.pos_z, 1, max_scale)

        x_distance_to_cam = self.pos_x - CAM_x
        y_distance_to_cam = self.pos_y - CAM_y

        xtimesy = x_distance_to_cam * y_distance_to_cam
        max_xtimesy = screen.get_width() * screen.get_height()

        print("x_distance_to_cam: ", x_distance_to_cam)
        print("y_distance_to_cam: ", y_distance_to_cam)
        print("x times y: ", xtimesy)

        xy_scale = util.get_new_range_value(0, max_xtimesy, xtimesy, 1, max_scale)

        scale = z_scale + xy_scale / 2

        if scale <= 1:
            scale = 1
        if scale >= 100:
            scale = 100

        print("3D Obj scale: ", scale)

        self.size_render = self.size * scale

    def show(self, this_screen):

        self.this_screen = this_screen

        color = [200, 100, 130]

        pygame.draw.ellipse(this_screen, color,
                            [self.pos_x - (self.size_render / 2), self.pos_y - (self.size_render / 2),
                             self.size_render, self.size_render], 1)



class NoteSprite(object):
    def __init__(self, pos_x, pos_y, size, ref, velocity=0, angle_pitch=0, growth_rate=1, is_on=False, colour=RED):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = 0
        self.origin_x, self.origin_y = pygame.mouse.get_pos()
        self.size = size
        self.ref = ref
        self.velocity = velocity
        self.angle_pitch = angle_pitch
        self.angle_yaw = 1
        self.growth_rate = growth_rate / self.velocity
        self.is_on = is_on
        self.colour = colour
        self.size_multiplier = 1

    def update(self):
        """ Do movement calculations """

        """ Find Origin x, y """
        self.origin_x, self.origin_y = 650, 500

        dist_scale_x = util.get_new_range_value(self.pos_x, 500, self.origin_x, 2, 300)
        dist_scale_y = util.get_new_range_value(self.pos_y, 500, self.origin_y, 2, 300)
        self.size_multiplier = util.get_new_range_value(2, 90000, dist_scale_x * dist_scale_y, 1, 1.7)

        """ Calculate how much to move each frame """
        x_add = self.velocity * math.sin(self.angle_pitch)
        y_add = self.velocity * math.cos(self.angle_pitch)

        z_add = self.velocity * math.cos(self.angle_yaw)

        """ Update position """
        self.pos_x = self.pos_x + x_add
        self.pos_y = self.pos_y + y_add
        self.pos_z = self.pos_z + z_add

        print("Pos_z = ", self.pos_z)

    def show(self, this_screen):

        if self.size <= 250:
            self.size = self.size * self.size_multiplier

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
