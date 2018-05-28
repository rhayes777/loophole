import pygame
import math
from os import path

# Init pygame font module
pygame.font.init()

dirname = path.dirname(path.realpath(__file__))

# Loading font
font_arcade = pygame.font.Font("{}/fonts/arcadeclassic.ttf".format(dirname), 46)

# Colour Constants

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (180, 60, 30)
GREEN = (46, 190, 60)
BLUE = (30, 48, 180)
PINK_MASK = (255, 0, 255)


# notice class handles messages displayed to screen using fonts
class Notice(object):
    def __init__(self, words, colour, size, this_font):
        self.words = words
        self.char_list = []  # Character list - to store Letter instances
        self.colour = colour
        self.size = size  # size (Font size)
        self.this_font = this_font  # font

        # append each Letter instance to char_list
        for i in range(len(self.words)):
            self.char_list.append(Letter(self.words[i], self.colour, self.size, self.this_font))

    # draw text
    def blit_text(self, this_surface, xpos, ypos, drop=False):

        # iterate through each Letter in char_list
        for i in range(len(self.char_list) - 1):
            char_size_x, char_size_y = self.this_font.size("a")  # get size of characters in string

            text_width, text_height = self.this_font.size(self.words)  # get size of text
            start_x = text_width / 2  # get x-offset (coordinate to start drawing Letters from)

            this_surface.blit(self.char_list[i].char_render,
                              (xpos - start_x + (i * char_size_x),
                               ypos))


# Letter class stores individual characters in strings in Notices
class Letter(object):
    def __init__(self, char, colour, size, this_font):
        self.colour = colour
        self.size = size
        self.this_font = this_font
        self.char = char

        self.char_render = self.this_font.render(self.char, True, self.colour)  # Actual raster render of the character


class Wave(Notice, object):
    def __init__(self, words, colour, size, this_font, shrink=False):
        super(Wave, self).__init__(words, colour, size, this_font)
        self.char_list = []
        self.wave_timer = 0
        self.shrink = shrink  # shrinking effect

        if self.shrink is False:

            for i in range(len(self.words)):
                self.char_list.append(
                    Letter(self.words[i], self.colour, self.size, self.this_font))  # Use normal letters

        else:

            for i in range(len(self.words)):
                self.char_list.append(
                    ShrinkLetter(self.words[i], self.colour, self.size, self.this_font))  # Use ShrinkLetters

    def blit_text(self, this_surface, xpos, ypos, drop=False):

        self.wave_timer = + 1  # timer

        if self.wave_timer > 10:
            self.wave_timer = 0  # max is 10 so go back to 0

        for i in range(len(self.char_list)):
            char_size_x, char_size_y = self.this_font.size("a")

            text_width, text_height = self.this_font.size(self.words)
            start_x = text_width / 2

            wave_add = 10 * (math.sin((i * 10) + self.wave_timer))  # multiply by sin to get wavy variable

            if self.shrink is False:  # if shrink effect is off just do the wavy effect

                this_surface.blit(self.char_list[i].char_render,
                                  (xpos - start_x + (i * char_size_x),
                                   ypos + wave_add))  # wav_add determines oscillation in the y-direction

            elif self.shrink is True:  # if shrink effect is on do the wavy effect and the shrink effect

                less = self.wave_timer

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
        self.timer = 0

        for i in range(len(self.words)):
            self.char_list.append(ShrinkLetter(self.words[i], self.colour, self.size, self.this_font))

    def blit_text(self, this_surface, xpos, ypos, drop=False):

        self.timer += 1

        for i in range(len(self.char_list)):

            text_width, text_height = self.this_font.size(self.words)
            start_x = text_width / 2

            for j in range(len(self.char_list[i].anim_list) - self.timer):
                char_size_x = self.char_list[i].anim_list[j].img.get_width

                this_surface.blit(self.char_list[i].anim_list[j].img,
                                  (xpos - start_x) - (j * (char_size_x * 2)) + (i * char_size_x),
                                  ypos - (j * 15))

            print(self.timer)

            for j in range(len(self.char_list[i].anim_list) - self.timer):
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
