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


# Background stuff

# Grid class draws a "3D" grid as a background
class Grid(object):
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
                red = util.get_new_range_value(0, 4500, self.segment_list[i].size, 20, 230)
                green = util.get_new_range_value(0, 4500, self.segment_list[i].size, 20, 230)
                blue = util.get_new_range_value(0, 4500, self.segment_list[i].size, 50, 230)

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

            red = util.get_new_range_value(0, 4500, self.size * mult, 20, 230)
            green = util.get_new_range_value(0, 4500, self.size * mult, 20, 230)
            blue = util.get_new_range_value(0, 4500, self.size * mult, 50, 230)

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
