import mido
import os
import random
from Queue import Queue

# pygame gfx constants
BLACK = (0, 0, 0)
RED = (180, 60, 30)
GREEN = (46, 190, 60)
BLUE = (30, 48, 180)

circle_x = 200
circle_y = 200

all_dots = []


# basic gfx class
class Dot:
    def __init__(self, colour, size, pos_x, pos_y, life):
        self.colour = colour
        self.time = 1
        self.size = size
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.life = life

    def show(self, pygame,
             screen):  # TODO: pygame and screen are passed about rather than being visible to the whole module. I've passed them in as arguments here but that probably isn't the most elegant solution

        if self.size > 7:
            pygame.draw.ellipse(screen, self.colour,
                                [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 2)

    def update(self):

        self.size *= self.time  # TODO: this is a more concise way of saying self.size = self.size * self.time

        if self.size > 5:
            self.time -= 0.001
        else:
            self.size = 5
            self.die()

    def die(self):

        all_dots.remove(self)


class Pixel:
    def __init__(self, pos_x, pos_y, is_on, size, colour=BLUE):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.is_on = is_on
        self.size = size
        self.colour = colour

    def show(self, pygame, screen):
        pygame.draw.ellipse(screen, self.colour,
                            [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 2)

    def update(self):
        if self.is_on == False:
            self.colour = BLUE
        elif self.is_on:
            self.colour = RED


class Display:  # TODO: This class basically wraps the functionality you defined. It allows us to pass in references the pygame module and a screen
    def __init__(self, pygame, screen):
        self.pygame = pygame
        self.screen = screen
        self.queue = Queue()

        self.pixel_grid = [[]]  # numpi later maybe

        grid_size_y = self.screen.get_height() / 128
        grid_size_x = grid_size_y  # self.screen.get_width()

        for i in range(grid_size_x):

            row = []

            for j in range(grid_size_y):
                row.append(Pixel(grid_size_x * i, grid_size_y * j, False, grid_size_x))

            self.pixel_grid.append(row)

    def process_message(self, msg):  # TODO: the response to a new message should be implemented here
        if msg.type == 'note_on':

            # print(msg)


            this_channel = msg.channel  # getattr(msg, 'channel')

            this_colour = BLUE

            if this_channel == 0:
                this_colour = BLUE
            elif this_channel == 1:
                this_colour = RED
            elif this_channel == 2:
                this_colour = GREEN

            this_size = (msg.velocity - 70) / 30

            all_dots.append(Dot(this_colour,
                                (random.randint(30, 70)),
                                (random.randint(0, self.screen.get_width())),
                                (msg.note * 10) - 300,
                                this_size))

            self.pygame.display.update()

            # print len(all_dots)

            self.screen.fill(BLACK)

            for dot in all_dots:
                dot.show(self.pygame, self.screen)
                dot.update()

            for row in self.pixel_grid:
                for pixel in row:
                    pixel.show(self.pygame, self.screen)
                    pixel.update()

    def update(self):
        while not self.queue.empty():
            self.process_message(self.queue.get())

    def on_message_received(self, msg):
        self.queue.put(msg)


def run_example():  # TODO: this runs the example you've already programmed
    import pygame
    # timer
    timer = 0
    # for the 'game loop'
    done = False

    dir_path = os.path.dirname(os.path.realpath(__file__))
    mid = mido.MidiFile("{}/media/mute-city.mid".format(dir_path))

    # pygame setup
    # (6,0) = all good
    print(pygame.init())
    clock = pygame.time.Clock()

    # create screen for pygame to draw to
    screen = pygame.display.set_mode((1000, 700))

    display = Display(pygame, screen)

    while not done:

        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        clock.tick(10)
        timer += 1
        # print(timer)

        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

        for message in mid.play():
            pygame.event.get()

            display.process_message(message)

    pygame.quit()


if __name__ == '__main__':  # TODO: This will only be true if this file is called directly rather than imported (e.g. python display.py)
    run_example()
