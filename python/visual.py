import mido
import os
from Queue import Queue
from threading import Thread
from time import sleep

# pygame gfx constants
BLACK = (0, 0, 0)
RED = (180, 60, 30)
GREEN = (46, 190, 60)
BLUE = (30, 48, 180)

circle_x = 200
circle_y = 200

all_dots = []

"""
I've made a couple of changes that I've pointed out below. The main problem is that iterating through every
pixel every single frame consumes a lot of processing power and causes the music to jitter.

What I've done is to move the loop that makes every pixel in the Display constructor. Then, when you want to change
the colour of a pixel you can just call a function to do that e.g. self.change_pixel_colour(10, 20, BLUE)

One problem we might have is with how you wanted to update the display. If you check the status of every single pixel
that will be really time consuming. A better way might be to keep track of pixel colour combinations in some tuple or
class and then use and change that list to make the dots move.

e.g. [((5, 10), RED), ((7, 11), YELLOW)]

You could take each item from that last and colour the pixel (i, j) the specified colour. Then you'd have to manage
the objects in the list. Like, you'd add one to each y value each time:

e.g. the list becomes [((5, 11), RED), ((7, 12), YELLOW)]
"""


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
             screen):

        if self.size > 7:
            pygame.draw.ellipse(screen, self.colour,
                                [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 2)

    def update(self):

        self.size *= self.time

        if self.size > 5:
            self.time -= 0.001
        else:
            self.size = 5
            self.die()

    def die(self):

        all_dots.remove(self)


class Pixel:
    def __init__(self, pos_x, pos_y, is_on, size, ref, colour=BLUE):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.is_on = is_on
        self.size = size
        self.ref = ref
        self.colour = colour

    def show(self, pygame, screen):
        pygame.draw.ellipse(screen, self.colour,
                            [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 2)

    def update(self):
        if self.is_on is False:
            self.colour = BLUE
        elif self.is_on:
            self.colour = RED


class Display(Thread):
    def __init__(self, pygame, screen):
        super(Display, self).__init__()
        self.pygame = pygame
        self.screen = screen
        self.queue = Queue()
        self.pixel_grid = []  # numpy later maybe

        grid_size_x = 20
        grid_size_y = grid_size_x  # self.screen.get_width()

        self.num_pixels_x = self.screen.get_width() / grid_size_x
        self.num_pixels_y = self.screen.get_height() / grid_size_y

        self.is_stopping = False

        for j in range(self.num_pixels_y):

            row = []

            for i in range(self.num_pixels_x):
                row.append(Pixel((grid_size_x / 2) + grid_size_x * i, (grid_size_y / 2) + (grid_size_y * j), False,
                                 grid_size_x, i))

                self.pixel_grid.append(row)

        self.pygame.draw.ellipse(self.screen, RED, [50, 50, 200, 200])

        # TODO: This was being called in the update function. The problem is that updating every pixel every fraction
        # TODO: of a second takes a lot of processing power. I figured we can make them all appear at first here and
        # TODO: then update them individually.
        for row in self.pixel_grid:

            for pixel in row:
                pixel.show(self.pygame, self.screen)

    def change_pixel_colour(self, i, j, colour):
        pixel = self.pixel_grid[i][j]
        pixel.colour = colour
        pixel.show(self.pygame, self.screen)

    def process_message(self, msg):
        if msg.type == 'note_on':
            recent_note = get_new_range_value(1, 128, msg.note, 1, len(self.pixel_grid[0]))

            # TODO: I wrote this method to get a pixel by it's i and j position and set it's colour. You can use it to
            # TODO: switch pixels on and off by setting different colours.
            self.change_pixel_colour(0, recent_note, RED)

            self.pygame.display.update()

            # print("Incoming note value: ", msg.note)
            # print("Scaled value: ", recent_note)

            # TODO: The below code doesn't do anything. It seems to be about selecting a colour for a channel. I'd
            # TODO: delete it if you're not using it. Unused code makes it harder to see what's going on.

            # this_channel = msg.channel  # getattr(msg, 'channel')
            #
            # this_colour = BLUE
            #
            # if this_channel == 0:
            #     this_colour = BLUE
            # elif this_channel == 1:
            #     this_colour = RED
            # elif this_channel == 2:
            #     this_colour = GREEN
            #
            # this_size = (msg.velocity - 70) / 30



            # all_dots.append(Dot(this_colour,
            #                     (random.randint(30, 70)),
            #                     (random.randint(0, self.screen.get_width())),
            #                     (msg.note * 10) - 300,
            #                     this_size))



            # print len(all_dots)

            # self.screen.fill(BLACK)

    def run(self):
        self.is_stopping = False
        while True:
            while not self.queue.empty():
                msg = self.queue.get()
                self.process_message(msg)

            # Break if should stop
            if self.is_stopping:
                break

            sleep(0.2)

            # TODO: there was a loop going through all the ixj pixels here. It slows down the song! I may have made a
            # TODO: mistake with threading but I recommend trying to avoid iterating through every pixel all the time.
            # TODO: Instead you could keep track of the coordinates of "on" pixels and use them to get a pixel by the
            # TODO: index in the pixel matrix e.g. self.pixel_grid[i][j]

    def stop(self):
        self.is_stopping = True


def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    old_range = old_range_max - old_range_min
    new_range = new_range_max - new_range_min
    new_value = (float(((old_value - old_range_min) * new_range) / old_range)) + new_range_min

    return int(new_value)


def run_example():
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

    display.start()

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

            display.queue.put(message)

    pygame.quit()


if __name__ == '__main__':
    run_example()
