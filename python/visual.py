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

from pygame.locals import *

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

# Init pygame font module
pygame.font.init()

# Loading font
font_arcade = pygame.font.Font("media/arcadeclassic.ttf", 46)

all_dots = []

# pygame setup
# (6,0) = all good
print(pygame.init())
clock = pygame.time.Clock()
pygame.display.init()
# create screen for pygame to draw to
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h))

all_sprites = pygame.sprite.Group()

main_timer = 0

# Fullscreen 'flash' effect

class Flash():
    def __init__(self, time):

        self.time = time
        self.blit_surface = pygame.Surface((info.current_w, info.current_h))

        self.blit_surface.fill((255,255,255))
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
        return self.timer > 1 # if timer is greater than 1, is_flashing is true


# Background stuff

# Grid class draws a "3D" grid as a background

class Grid():
    def __init__(self, start_x, start_y, start_size, end_center, end_size, gap):
        self.start_x = start_x
        self.start_y = start_y
        self.start_size = start_size
        self.end_center = end_center
        self.end_size = end_size
        self.gap = gap
        self.this_timer = 0

        self.segment_list = []

        segment = GridSegment(self.start_x, self.start_y, 1, 20)

        self.segment_list.append(segment)

    def render(self, this_surface):

        if self.this_timer <= 10:
            self.this_timer +=1
        else:
            self.this_timer = 0

        if self.this_timer is 5:
            segment = GridSegment(self.start_x, self.start_y, 1, 20)

            self.segment_list.append(segment)

        for i in range(len(self.segment_list)):

            self.segment_list[i].render(this_surface)



class GridSegment():
    def __init__(self, xpos, ypos, zpos, size):
        self.xpos = xpos
        self.ypos = ypos
        self.zpos = zpos # zpos determines Z value ie. Segment's 'depth into the screen'
        self.size = size

    def render(self, this_surface):

        red = 230
        green = 230
        blue = 240

        if self.size < 1600:
            self.size = self.size * 1.15  # Increase size over time


        # draw rect boundary line
        pygame.draw.rect(this_surface, (red, green, blue), (self.xpos - (self.size/2), self.ypos - (self.size/2), self.size, self.size), 3)

        # count = 10
        #
        # for i in range(0, count):
        #     start_pos_x = self.xpos - (self.size / 2)
        #     end_pos_x = self.xpos + (self.size / 2)
        #     start_pos_y = self.ypos - (self.size / 2)
        #     end_pos_y = self.ypos + (self.size / 2)
        #     gap = (self.size / count)
        #     pygame.draw.line(this_surface, (red, green, blue),
        #                      (start_pos_x + gap * i, start_pos_y),(end_pos_x + gap * i, start_pos_y + gap * i), 1)
        #     pygame.draw.line(this_surface, (red, green, blue),
        #                      (start_pos_y + gap * i, start_pos_x + gap * i),(end_pos_y + gap * i, start_pos_x + gap * i), 1)


        # # draw lines to next rect
        # pygame.draw.line(this_surface,
        #                  (red, green, blue),
        #                  ((self.xpos - (self.size/2)),(self.ypos - (self.size/2)),
        #                   ))

        # if xpos is outside os screen, delete instance
        if self.xpos - (self.size / 2) < 0 or self.size > 1590:
            del self

# Create an instance of Grid
the_grid = Grid(info.current_w/2, info.current_h/2,20,info.current_w/2, info.current_h/2, 40)

# notice class handles messages displayed to screen using fonts
class Notice():
    def __init__(self, words, colour, size, this_font):
        self.words = words
        self.char_list = [] # Character list - to store Letter instances
        self.colour = colour
        self.size = size # size (Font size)
        self.this_font = this_font # font

        # append each Letter instance to char_list
        for i in range(len(self.words)):
            self.char_list.append(Letter(self.words[i], self.colour, self.size, self.this_font))

    # draw text
    def blit_text(self, this_surface, xpos, ypos, drop=False):

        #iterate through each Letter in char_list
        for i in range(len(self.char_list) - 1):
            char_size_x, char_size_y = self.this_font.size("a") # get size of characters in string

            text_width, text_height = self.this_font.size(self.words) # get size of text
            start_x = text_width / 2 # get x-offset (coordinate to start drawing Letters from)

            mouse_shake = get_new_range_value(0, screen.get_height(), mouse_y, 15, 0)

            this_surface.blit(self.char_list[i].char_render,
                              (xpos - start_x + (i * char_size_x),
                               ypos + random.randint(0, mouse_shake)))

# Letter class stores individual characters in strings in Notices
class Letter:
    def __init__(self, char, colour, size, this_font):
        self.colour = colour
        self.size = size
        self.this_font = this_font
        self.char = char

        self.char_render = self.this_font.render(self.char, True, self.colour) # Actual raster render of the character

class Wave(Notice, object):
    def __init__(self, words, colour, size, this_font, shrink=False):
        super(Wave, self).__init__(words, colour, size, this_font)
        self.char_list = []
        self.wave_timer = 0
        self.shrink = shrink # shrinking effect

        if self.shrink is False:

            for i in range(len(self.words)):
                self.char_list.append(Letter(self.words[i], self.colour, self.size, self.this_font)) # Use normal letters

        else:

            for i in range(len(self.words)):
                self.char_list.append(ShrinkLetter(self.words[i], self.colour, self.size, self.this_font)) # Use ShrinkLetters

    def blit_text(self, this_surface, xpos, ypos, drop=False):

        self.wave_timer = + 1 # timer

        if self.wave_timer > 10:
            self.wave_timer = 0 # max is 10 so go back to 0

        for i in range(len(self.char_list)):
            char_size_x, char_size_y = self.this_font.size("a")

            text_width, text_height = self.this_font.size(self.words)
            start_x = text_width / 2

            wave_add = 10 * (math.sin((i * 10) + display.timer)) # multiply by sin to get wavy variable

            if self.shrink is False: # if shrink effect is off just do the wavy effect

                this_surface.blit(self.char_list[i].char_render,
                                  (xpos - start_x + (i * char_size_x),
                                   ypos + wave_add)) # wav_add determines oscillation in the y-direction

            elif self.shrink is True: # if shrink effect is on do the wavy effect and the shrink effect

                less = display.timer

                for j in range(len(self.char_list[i].anim_list) - less):
                    this_surface.blit(self.char_list[i].anim_list[j].img,
                                      ((xpos - start_x) + (i * char_size_x * 1.5),
                                       (ypos + wave_add) - (j * 25)))


class Shrink(Notice):

    def __init__(self, words, colour, size, this_font, is_shrinking=True, drop_colour=BLUE):
        Notice.__init__(self, words, colour, size, this_font)
        self.drop_colour = drop_colour
        self.is_shrinking = is_shrinking
        self.char_list = []

        for i in range(len(self.words)):
            self.char_list.append(ShrinkLetter(self.words[i], self.colour, self.size, self.this_font))

    def blit_text(self, this_surface, xpos, ypos, drop=False):

        for i in range(len(self.char_list)):

            text_width, text_height = self.this_font.size(self.words)
            start_x = text_width / 2

            less = display.timer

            for j in range(len(self.char_list[i].anim_list) - less):
                char_size_x = self.char_list[i].anim_list[j].img.get_width

                this_surface.blit(self.char_list[i].anim_list[j].img,
                                  (xpos - start_x) - (j * (char_size_x * 2)) + (i * char_size_x),
                                  ypos - (j * 15))


            for j in range(len(self.char_list[i].anim_list) - less):
                char_size_x = self.char_list[i].anim_list[j].img.get_width

                this_surface.blit(self.char_list[i].anim_list[j].img,
                                  (xpos - start_x - (j * 25) + (i * char_size_x),
                                   ypos - (j * 15)))


class ShrinkLetter(object):
    def __init__(self, char, colour, size, this_font):
        self.colour = colour
        self.size = size
        self.this_font = this_font
        self.char = char

        self.anim_list = []

        self.char_render = self.this_font.render(self.char, True, self.colour)

        for i in range(1, 7):
            frame = FontFrame(self.size, self.this_font, self.char_render, i)
            self.anim_list.append(frame)


class FontFrame(object):
    def __init__(self, size, this_font, img, icount=1):
        self.size = size
        self.this_font = this_font
        self.icount = icount
        self.img = pygame.transform.scale(img, (self.size / icount, self.size / icount))

        char_size_x, char_size_y = self.this_font.size("a")

        img_w = char_size_x / self.icount
        img_h = char_size_y / self.icount

        pygame.transform.smoothscale(img, (img_w, img_h))

my_message = Wave("Welcome to the MidiZone", RED, 30, font_arcade, True)

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


class Display(Thread):
    def __init__(self):
        super(Display, self).__init__()
        self.queue = Queue()

        self.grid_size_x = 20
        self.grid_size_y = self.grid_size_x  # self.screen.get_width()

        # This is a queue to keep rows of "pixels" in. You put things in one end and get them out the other which is
        # what we need to make scrolling notes.
        self.row_queue = Queue()

        self.num_pixels_x = screen.get_width() / self.grid_size_x
        self.num_pixels_y = screen.get_height() / self.grid_size_y

        self.is_stopping = False

        self.timer = 0

        self.flash = Flash(15)
        self.flashing_now = False

    def new_row(self):
        """
        Created a new row
        :return: A list of blue pixels at the top of the screen of length num_pixels_x
        """
        row = []
        for i in range(self.num_pixels_x):
            row.append(
                Pixel((self.grid_size_x / 2) + self.grid_size_x * i, (self.grid_size_y / 2), False, self.grid_size_x,
                      i))
        return row


        # + (self.grid_size_y * j)

    def run(self):
        """
        Runs the game loop
        """
        self.is_stopping = False
        while True:
            # Make a new row each time the loop runs
            row = self.new_row()
            # Keep grabbing messages from the incoming message queue until it's empty
            while not self.queue.empty():
                msg = self.queue.get()
                if msg.type == 'note_on':
                    # Use your function to convert to screen cooordinates
                    x_position = get_new_range_value(1, 128, msg.note, 1, self.num_pixels_x)
                    # Set the "pixel" at that position in this row to red
                    row[x_position].colour = RED

            # Add the newly created row to the queue
            self.row_queue.put(row)

            # If there are so many rows that it's going off screen, remove the row that was added first
            if len(self.row_queue.queue) > self.num_pixels_y:
                self.row_queue.get()

            main_timer =+1

            screen.fill(BLACK)

            #render grid
            the_grid.render(screen)

            if self.flashing_now is False:
                self.flash.make_flash()
                self.flashing_now = self.flash.is_flashing()

            self.flash.render(screen)

            # mouse_x, mouse_y = pygame.mouse.get_pos()
            # the_grid.start_x = mouse_x
            # the_grid.start_y = mouse_y

            if self.timer >= 1:
                self.timer -= 1
            else:
                self.timer = 6


            # Draw all those objects
            self.draw_objects()

            # Actually update the display
            pygame.display.update()

            # Break if should stop
            if self.is_stopping:
                break

            clock.tick(10)

    def stop(self):
        self.is_stopping = True

    def draw_objects(self):
        """
        Draws all the objects in the queue
        """
        # This function goes through each line in the queue. It gets that row of pixels (row) and also what number it is
        # is in queue (j)
        for j, row in enumerate(self.row_queue.queue):
            # We can work out what the y position should be from the position in the list
            y_position = j * self.grid_size_y
            # Now we individually draw each pixel
            for pixel in row:
                # We have to update the y position of the pixels here.
                pixel.pos_y = y_position
                pixel.show()

        all_sprites.draw(screen)

        # Draw text
        my_message.blit_text(screen, screen.get_width() / 2, screen.get_height() / 2)







def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    if old_value > old_range_max:
        old_value = old_range_max
    if old_value < old_range_min:
        old_value = old_range_min
    return (old_value - old_range_min) * (new_range_max - new_range_min) / (
        old_range_max - old_range_min) + new_range_min


done = False
display = Display()

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

        while True:
            message = sys.stdin.readline()
            if message is None:
                break
            pygame.event.get()

            try:
                display.queue.put(mido.Message.from_str(message))
            except IndexError as e:
                logger.exception(e)

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
