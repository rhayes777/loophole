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

# ...and is placed 300px back from the scene

CAM_z = 300


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
    """ NoteSprite object is a visual representation of a Midi note
    It's now a 3D object with the usual x and y co ordinates as well as a Z co ord
    so it can move towards the camera """

    """ Initialize with defaults for angle_xy ('2D' angle on flat plane of screen), angle_zx (Left-Right in direction
    of the camera), and Velocity"""

    def __init__(self, pos_x, pos_y, pos_z, size, ref,
                 angle_xy=math.radians(random.randint(0, 360)),
                 angle_zx=math.radians(random.randint(0, 180)),
                 velocity=random.randint(1, 6), spin_angle=90, spin_velocity=2):





        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z

        """ This is the 'original' size of the object: The size it has when rendered at Z = 0 """

        self.size = size

        self.ref = ref

        """ angle_zx is the angle at which the object is moving along the Z-X axis...
        So it's the 'bird's eye view' angle of movement of the object 
        0 will be fully "left" as you're looking at it, with object not moving towards viewer at all
        180 would be fully "right" so the opposite direction, still no Z axis movement -
        90 is exactly towards the viewer (so no x-axis movement) """

        self.angle_zx = math.radians(angle_zx)

        """ angle_xy is along the 'normal' 2D plane ie. x and y
        so 0 is directly up the screen, 180 is directly down etc.
        angle is put into radians at this stage so that Python can do trig functions on it """

        self.angle_xy = math.radians(angle_xy)

        """ General velocity of object that is applied to all axes """

        self.velocity = velocity

        """ Creates spinning movement """

        self.spin_angle = spin_angle
        self.spin_velocity = spin_velocity

        """ Start off with render size at a 1:1 ratio to its actual size 
        This will later be modified as the object moves in the z-axis (towards the camera/viewer)"""

        self.size_render = self.size

        """ Screen to draw to """

        self.this_screen = None

        self.is_on = False

    def update(self):

        """ Calculate and update movement """

        if self.pos_z >= CAM_z:

            self.pos_z = CAM_z

            self.is_on = False

        """ Calculate how much to move in each axis each frame
        Sin and cosine functions used on pre-radian'd angle variables to get correct unit to add to position
        each turn """

        x_add = self.velocity * math.sin(self.angle_xy)
        y_add = self.velocity * math.cos(self.angle_xy)
        z_add = self.velocity * math.sin(self.angle_zx)

        """ Get absolute values of x-dist to Cam's x, and z-dist to Cam's z"""

        mouse_x, mouse_y = pygame.mouse.get_pos()

        camera_x = mouse_x
        if camera_x <= 2:
            camera_x = 2
        camera_y = mouse_y

        origin_x = screen.get_width()/2
        origin_y = screen.get_height()/2

        x_distance_to_origin = abs(self.pos_x - origin_x)

        Origin_z = CAM_z
        Origin_y = CAM_y

        x_distance_to_cam = abs(camera_x - self.pos_x)
        y_distance_to_cam = abs(camera_y - self.pos_y)
        z_distance_to_cam = abs(Origin_z - self.pos_z)

        """ Parallax stuff """
        amount = 30

        amount_x = math.cos(util.get_new_range_value(1, Origin_z, z_distance_to_cam, 0, 1))*amount
        amount_y = math.sin(util.get_new_range_value(1, Origin_z, z_distance_to_cam, 0, 1))*amount

        para_x = util.get_new_range_value(1, screen.get_width(), camera_x, amount_x, -amount_x)
        para_y = util.get_new_range_value(1, screen.get_height(), camera_y, amount_y, -amount_y)

        print("Para x", para_x)

        """ Spin function """

        x_spin = self.spin_velocity*math.sin(self.spin_angle)
        y_spin = self.spin_velocity*math.cos(self.spin_angle)

        """ Update position """

        self.pos_x = self.pos_x + x_add + para_x
        self.pos_y = self.pos_y + y_add + para_y
        self.pos_z = self.pos_z + z_add

        """ Figuring out maximum scale factor based on screen size """

        max_scale = screen.get_width() / self.size







        """ Create scaling factors based on maximum scale, and distance of object from the camera along Z and X axes"""

        z_scale = util.get_new_range_value(0, CAM_z, z_distance_to_cam, max_scale/12, 1)
        x_scale = util.get_new_range_value(0, screen.get_width() / 2, x_distance_to_cam, max_scale, 1)
        y_scale = util.get_new_range_value(0, screen.get_height() / 2, y_distance_to_cam, max_scale, 1)

        """ Combine scales """

        combined_scale = z_scale

        scale = combined_scale

        """ Limit scaling factor """

        if scale <= 1:
            scale = 1
        if scale >= 2650:
            scale = 2650

        """ Set size to actually render at based on scale """

        self.size_render = self.size * scale

    def show(self, this_screen):

        """ Render object to screen """

        self.this_screen = this_screen
        if self.is_on:
            # determine colour based on position
            color = [
                util.get_new_range_value(0, info.current_w, self.pos_x, 30, 255,),  # Red
                util.get_new_range_value(0, info.current_h, self.pos_y, 20, 140),  # Green
                util.get_new_range_value(0, info.current_h, self.pos_y, 120, 255),  # Blue
            ]

            pygame.draw.ellipse(this_screen, color,
                                [self.pos_x - (self.size_render / 2),
                                 self.pos_y - (self.size_render / 2),
                                 self.size_render,
                                 self.size_render])
            color2 = [
                util.get_new_range_value(0, info.current_h, self.pos_y, 160, 155,),  # Red
                util.get_new_range_value(0, info.current_w, self.pos_x, 140, 110),  # Green
                util.get_new_range_value(0, info.current_w, self.pos_x, 120, 55),  # Blue
            ]

            pygame.draw.ellipse(this_screen, color2,
                                [self.pos_x - (self.size_render / 2),
                                 self.pos_y - (self.size_render / 2),
                                 self.size_render,
                                 self.size_render], 5)

