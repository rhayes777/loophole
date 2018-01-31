##
## TO DO
##
## Background -
# Vector mountains method (midpoint algorhythm)
# Grid

import mido
from Queue import Queue
from threading import Thread
import logging
import sys
import pygame
import signal
import random
import math
import messaging

logging.basicConfig()

logger = logging.getLogger(__name__)

# pygame gfx constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (180, 60, 30)
GREEN = (46, 190, 60)
BLUE = (30, 48, 180)
PINK_MASK = (255, 0, 255)

mouse_x, mouse_y = (400, 400)

# pygame Font setup









main_timer = 0


# Fullscreen 'flash' effect

class Flash():
    def __init__(self, time):
        self.time = time
        self.blit_surface = pygame.Surface((info.current_w, info.current_h))

        self.blit_surface.fill((255, 255, 255))
        self.timer = -2

    def make_flash(self):
        self.timer = self.time

    def render(self, render_to):
        self.render_to = render_to

        if self.timer >= 0:
            alpha = get_new_range_value(1, self.time, self.timer, 0, 255)
            print(alpha)
            self.timer -= 1
            self.blit_surface.set_alpha(alpha)
            self.render_to.blit(self.blit_surface, (0, 0))

    def is_flashing(self):
        return self.timer > 1  # if timer is greater than 1, is_flashing is true


# Background stuff

# Grid class draws a "3D" grid as a background
class Grid():
    def __init__(self, start_x, start_y, size, gap):

        self.start_x = start_x
        self.start_y = start_y
        self.size = size
        self.gap = gap
        self.this_timer = 0

        self.segment_list = []

        segment = GridSegment(self.start_x, self.start_y, 1, self.size)

        self.segment_list.append(segment)

    def render(self, this_surface, (start_x, start_y)):
        self.start_x = start_x
        self.start_y = start_y

        offsetmax = 200
        y_offset = 0

        messaging.read()


        line_end = 1000
        if self.this_timer <= 5:
            self.this_timer += 1
        else:
            self.this_timer = 0

        if self.this_timer is 5:
            segment = GridSegment(self.start_x, self.start_y + y_offset, 1, self.size)

            self.segment_list.append(segment)

        for i in range(len(self.segment_list)):
            # render grid segment
            self.segment_list[i].render(this_surface)

            # get values for drawing lines between segments (3D effect bit):

            # first four are for the current instance in list...

            # start pos x = furthest left x value; start pos y = furthest up y value
            start_pos_x = self.segment_list[i].xpos - (self.segment_list[i].size / 2)
            start_pos_y = self.segment_list[i].ypos - (self.segment_list[i].size / 2)

            # end pos x = furthest right x value; end pos y = furthest down y value
            end_pos_x = self.segment_list[i].xpos + (self.segment_list[i].size / 2)
            end_pos_y = self.segment_list[i].ypos + (self.segment_list[i].size / 2)

            # second four access the previous instance in list...

            # next start pos x = furthest left x value; next start pos y = furthest up y value
            next_start_pos_x = self.segment_list[i - 1].xpos - (self.segment_list[i - 1].size / 2)
            next_start_pos_y = self.segment_list[i - 1].ypos - (self.segment_list[i - 1].size / 2)

            # end pos x = furthest right x value; next end pos y = furthest down y value
            next_end_pos_x = self.segment_list[i - 1].xpos + (self.segment_list[i - 1].size / 2)
            next_end_pos_y = self.segment_list[i - 1].ypos + (self.segment_list[i - 1].size / 2)

            for j in range(0, 6):

                red = get_new_range_value(0, 4500, self.segment_list[i].size, 20, 230)
                green = get_new_range_value(0, 4500, self.segment_list[i].size, 20, 230)
                blue = get_new_range_value(0, 4500, self.segment_list[i].size, 50, 230)

                # find gap in px
                gap = (self.segment_list[i].size / self.segment_list[i].count)

                # find gap in px from previous instance in list
                next_gap = (self.segment_list[i - 1].size / self.segment_list[i - 1].count)

                # draw lines from top of current instance to the previous one...
                pygame.draw.line(this_surface, (red, green, blue),
                                 (start_pos_x + (gap * j), start_pos_y),
                                 (next_start_pos_x + (next_gap * j), next_start_pos_y), 1)

                # then from the bottom...
                pygame.draw.line(this_surface, (red, green, blue),
                                 (start_pos_x + (gap * j), end_pos_y),
                                 (next_start_pos_x + (next_gap * j), next_end_pos_y), 1)

                # ...from right to left...
                pygame.draw.line(this_surface, (red, green, blue),
                                 (start_pos_x, start_pos_y + (gap * j)),
                                 (next_start_pos_x, next_start_pos_y + (next_gap * j)), 1)

                # and left to right.
                pygame.draw.line(this_surface, (red, green, blue),
                                 (end_pos_x, start_pos_y + (gap * j)),
                                 (next_end_pos_x, next_start_pos_y + (next_gap * j)), 1)


class GridSegment(object):
    def __init__(self, xpos, ypos, zpos, size):
        self.xpos = xpos
        self.ypos = ypos
        self.zpos = zpos  # zpos determines Z value ie. Segment's 'depth into the screen'
        self.size = size
        self.count = 5

    def render(self, this_surface):

        if self.size < 4500:
            self.size *= 1.15  # Increase size over time

            mult = 2

            red = get_new_range_value(0, 4500, self.size * mult, 20, 230)
            green = get_new_range_value(0, 4500, self.size * mult, 20, 230)
            blue = get_new_range_value(0, 4500, self.size * mult, 50, 230)

            # draw rect boundary line
            pygame.draw.rect(this_surface, (red, green, blue),
                             (self.xpos - (self.size / 2), self.ypos - (self.size / 2), self.size, self.size), 3)

            # draw a grid of lines to size self.size centered around (self.xpos, self.ypos)
            # self.count determines the number of lines
            for i in range(0, self.count):
                start_pos_x = self.xpos - (self.size / 2)
                end_pos_x = self.xpos + (self.size / 2)
                start_pos_y = self.ypos - (self.size / 2)
                end_pos_y = self.ypos + (self.size / 2)
                gap = (self.size / self.count)
                pygame.draw.line(this_surface, (red, green, blue),
                                 (start_pos_x + (gap * i), start_pos_y), (start_pos_x + (gap * i), end_pos_y), 1)
                pygame.draw.line(this_surface, (red, green, blue),
                                 (start_pos_x, start_pos_y + (gap * i)), (end_pos_x, start_pos_y + (gap * i)), 1)

        # if xpos is outside os screen, delete instance
        if self.xpos - (self.size / 2) < 0 or self.size > 1590:
            del self


# Create an instance of Grid
the_grid = Grid(info.current_w / 2, info.current_h / 2, 10, 5)





class Input:
    def __init__(self):
        self.pressed_up = False
        self.pressed_down = False
        self.pressed_left = False
        self.pressed_right = False

    def check_input(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_1]:
            display.draw_foreground = not display.draw_foreground
        if pressed[pygame.K_2]:
            display.draw_text = not display.draw_text
        if pressed[pygame.K_UP]:
            self.pressed_up = True
        if pressed[pygame.K_DOWN]:
            self.pressed_down = True
        elif -pressed[pygame.K_DOWN]:
            self.pressed_down = False
        if pressed[pygame.K_LEFT]:
            self.pressed_left = True
        elif -pressed[pygame.K_LEFT]:
            self.pressed_left = False
        if pressed[pygame.K_RIGHT]:
            self.pressed_right = True
        elif -pressed[pygame.K_RIGHT]:
            self.pressed_right = False

the_input = Input()




class Pixel:
    def __init__(self, pos_x, pos_y, is_on, size, ref, colour=BLUE):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.is_on = is_on
        self.size = size
        self.ref = ref
        self.colour = colour

    def show(self):
        if self.colour == RED:
            self.size += 1

            # determine colour based on position
            color = [
                get_new_range_value(0, info.current_w, self.pos_x, 30, 255),  # Red
                get_new_range_value(0, info.current_h, self.pos_y, 20, 140),  # Green
                get_new_range_value(0, info.current_h, self.pos_y, 120, 255)  # Blue
            ]

            pygame.draw.ellipse(screen, color,
                                [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 0)

            pygame.draw.ellipse(screen,
                                [
                                    get_new_range_value(0, info.current_w, self.pos_x, 120, 255),  # Red
                                    get_new_range_value(0, info.current_h, self.pos_y, 30, 255),  # Green
                                    get_new_range_value(0, info.current_h, self.pos_y, 20, 140)  # Blue
                                ],
                                [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 4)




def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    if old_value > old_range_max:
        old_value = old_range_max
    if old_value < old_range_min:
        old_value = old_range_min
    return (old_value - old_range_min) * (new_range_max - new_range_min) / (
            old_range_max - old_range_min) + new_range_min






# noinspection PyUnusedLocal
def stop(*args):
    global done
    done = True
    display.stop()
    pygame.quit()


signal.signal(signal.SIGINT, stop)
display.start()


def run_for_stdin():
    global done
    while not done:

        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        clock.tick(10)

        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

        for message in messaging.read():
            pygame.event.get()

            display.queue.put(message)

    pygame.quit()


def run_for_mido():
    import os
    global done
    dirname = os.path.dirname(os.path.realpath(__file__))
    filename = 'media/mute-city.mid'
    mid = mido.MidiFile("{}/{}".format(dirname, filename))
    while not done:

        for message in mid.play():
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    done = True  # Flag that we are done so we exit this loop
            display.queue.put(message)

    pygame.quit()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        run_for_stdin()
    else:
        run_for_mido()
