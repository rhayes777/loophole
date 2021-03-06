import math
from os import path

import pygame

from color import Color

# Init pygame font module
pygame.font.init()

dirname = path.dirname(path.realpath(__file__))

# Loading font
font_arcade = pygame.font.Font("{}/fonts/arcadeclassic.ttf".format(dirname), 46)

# Colour Constants
colors = [Color.APPLIANCE_WHITE,
          Color.FLIRT,
          Color.KEEN,
          Color.VINO,
          Color.VENOM,
          Color.SHAKA,
          Color.LIGHTNING]

notices_list = []


# notice class handles messages displayed to screen using fonts
class Notice(object):
    def __init__(self, text, position, color=Color.WHITE, size=40, this_font=font_arcade, should_blit=True, alpha=255):
        self.position = position
        self.color = color
        self.alpha = alpha
        self.size = size  # size (Font size)
        self.this_font = this_font  # font

        self.char_list = []
        self.text = text

        notices_list.append(self)

        self.should_blit = should_blit

    @property
    def text(self):
        return "".join(character.char for character in self.char_list)

    @text.setter
    def text(self, text):
        self.char_list = [Letter(character, self.color, self.size, self.this_font) for character in text]
        for char in self.char_list:
            char.char_render.fill(self.color + (self.alpha,), None, pygame.BLEND_RGBA_MULT)

    # draw text
    def blit_text(self, this_surface):
        # iterate through each Letter in char_list
        for i in range(len(self.char_list)):
            char_size_x, char_size_y = self.this_font.size("a")  # get size of characters in string

            text_width, text_height = self.this_font.size(self.text)  # get size of text
            start_x = text_width / 2  # get x-offset (coordinate to start drawing Letters from)

            char_img = self.char_list[i].char_render

            this_surface.blit(char_img,
                              (self.position[0] - start_x + (i * char_size_x),
                               self.position[1]))


class HighScoreNotice(Notice):
    def __init__(self, text, position):
        super(HighScoreNotice, self).__init__(text, position)
        self.highlighted_character = None
        self.cycle = 0

    # draw text
    def blit_text(self, this_surface):
        # iterate through each Letter in char_list
        for i in range(len(self.char_list)):
            char_size_x, char_size_y = self.this_font.size("a")  # get size of characters in string

            text_width, text_height = self.this_font.size(self.text)  # get size of text
            start_x = text_width / 2  # get x-offset (coordinate to start drawing Letters from)

            char_img = self.char_list[i].char_render.copy()

            if i == self.highlighted_character:
                color = colors[self.cycle]
                self.cycle = (self.cycle + 1) % len(colors)
            else:
                color = self.color

            char_img.fill(color + (self.alpha,), None, pygame.BLEND_RGBA_MULT)

            this_surface.blit(char_img,
                              (self.position[0] - start_x + (i * char_size_x),
                               self.position[1]))


# notice class handles messages displayed to screen using fonts
class TransientNotice(Notice):
    def __init__(self, text, position, color, size, this_font, life, rate=1):
        super(TransientNotice, self).__init__(text, position, color, size, this_font)

        self.life = life
        self.timer = self.life
        self.rate = rate
        self.alpha = 255

        notices_list.append(self)

    # draw text
    def blit_text(self, this_surface):
        alpha = self.alpha
        if self.life is not None:
            if self.timer >= 0:
                self.timer -= self.rate
            divide = float(self.timer) / float(self.life)
            alpha = 255 * divide

        # iterate through each Letter in char_list
        for i in range(len(self.char_list)):
            char_size_x, char_size_y = self.this_font.size("a")  # get size of characters in string

            text_width, text_height = self.this_font.size(self.text)  # get size of text
            start_x = text_width / 2  # get x-offset (coordinate to start drawing Letters from)

            char_img = self.char_list[i].char_render

            char_img.fill(self.color + (alpha,), None, pygame.BLEND_RGBA_MULT)

            this_surface.blit(char_img,
                              (self.position[0] - start_x + (i * char_size_x),
                               self.position[1]))


# Letter class stores individual characters in strings in Notices
class Letter(object):
    def __init__(self, char, color, size, this_font):
        self.color = color
        self.size = size
        self.this_font = this_font
        self.char = char

        self.char_render = self.this_font.render(self.char, True, self.color)  # Actual raster render of the character


# Score class for whenever player gains some points
class Score(TransientNotice):
    def __init__(self, text, position, color, size, this_font, life):
        super(Score, self).__init__(str(text), position, color, size, this_font, life)


class Wave(TransientNotice):
    def __init__(self, text, color, size, this_font, life, shrink=False):
        super(Wave, self).__init__(text, size, color, this_font, life)
        self.char_list = []
        self.wave_timer = 0
        self.shrink = shrink  # shrinking effect

        if self.shrink is False:

            for i in range(len(self.text)):
                self.char_list.append(
                    Letter(self.text[i], self.color, self.size, self.this_font))  # Use normal letters

        else:

            for i in range(len(self.text)):
                self.char_list.append(
                    ShrinkLetter(self.text[i], self.color, self.size, self.this_font))  # Use ShrinkLetters

    def blit_text(self, this_surface, drop=False):

        self.wave_timer += 1  # timer

        if self.wave_timer > 10:
            self.wave_timer = 0  # max is 10 so go back to 0

        for i in range(len(self.char_list)):
            char_size_x, char_size_y = self.this_font.size("a")

            text_width, text_height = self.this_font.size(self.text)
            start_x = text_width / 2

            wave_add = 10 * (math.sin((i * 10) + self.wave_timer))  # multiply by sin to get wavy variable

            if self.shrink is False:  # if shrink effect is off just do the wavy effect

                this_surface.blit(self.char_list[i].char_render,
                                  (self.position[0] - start_x + (i * char_size_x),
                                   self.position[1] + wave_add))  # wav_add determines oscillation in the y-direction

            elif self.shrink is True:  # if shrink effect is on do the wavy effect and the shrink effect

                less = self.wave_timer

                for j in range(len(self.char_list[i].anim_list) - less):
                    this_surface.blit(self.char_list[i].anim_list[j].img,
                                      ((self.position[0] - start_x) + (i * char_size_x * 1.5),
                                       (self.position[1] + wave_add) - (j * 25)))


class ShrinkLetter(object):
    def __init__(self, char, color, size, this_font):
        self.color = color
        self.size = size
        self.this_font = this_font
        self.char = char

        self.anim_list = []

        self.char_render = self.this_font.render(self.char, True, self.color)

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


def render_notices(surface):
    for notice in list(notices_list):
        if hasattr(notice, "timer") and notice.timer <= 0:
            notices_list.remove(notice)
        elif notice.should_blit:
            notice.blit_text(surface)
