import mido
from Queue import Queue
from threading import Thread
from time import sleep
import logging
import sys
import pygame
import signal

logging.basicConfig()

logger = logging.getLogger(__name__)

# pygame gfx constants
BLACK = (0, 0, 0)
RED = (180, 60, 30)
GREEN = (46, 190, 60)
BLUE = (30, 48, 180)

circle_x = 200
circle_y = 200

all_dots = []

timer = 0

# pygame setup
# (6,0) = all good
print(pygame.init())
clock = pygame.time.Clock()
# create screen for pygame to draw to
screen = pygame.display.set_mode((1000, 700))


# basic gfx class
class Dot:
    def __init__(self, colour, size, pos_x, pos_y, life):
        self.colour = colour
        self.time = 1
        self.size = size
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.life = life

    def show(self):

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

    def show(self):
        pygame.draw.ellipse(screen, self.colour,
                            [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 2)

    def update(self):
        # self.pos_y = self.pos_y - 1
        print(".")


class Display(Thread):
    def __init__(self):
        super(Display, self).__init__()
        self.queue = Queue()
        self.pixel_grid = []  # numpy later maybe

        grid_size_x = 20
        grid_size_y = grid_size_x  # self.screen.get_width()

        self.num_pixels_x = screen.get_width() / grid_size_x
        self.num_pixels_y = screen.get_height() / grid_size_y

        self.is_stopping = False

        for j in range(self.num_pixels_y):

            row = []

            for i in range(self.num_pixels_x):
                row.append(Pixel((grid_size_x / 2) + grid_size_x * i, (grid_size_y / 2) + (grid_size_y * j), False,
                                 grid_size_x, i))

            self.pixel_grid.append(row)

    def change_pixel_colour(self, i, j, colour):
        pixel = self.pixel_grid[i][j]
        pixel.colour = colour
        # pixel.show(self.pygame, self.screen)

    def shift_pixel_grid(self):

        for z in range(timer, timer + 1):

            for x in range(0, len(self.pixel_grid[z])):

                if self.pixel_grid[z - 1][x].colour == RED:
                    self.change_pixel_colour(z, x, self.pixel_grid[z - 1][x].colour)

                self.pixel_grid[z][x].pos_y += self.pixel_grid[z][x].size

    def process_message(self, msg):
        if msg.type == 'note_on':
            recent_note = get_new_range_value(1, 128, msg.note, 1, len(self.pixel_grid[0]))

            # TODO: I wrote this method to get a pixel by it's i and j position and set it's colour. You can use it to
            # TODO: switch pixels on and off by setting different colours.

            self.change_pixel_colour(0, recent_note, RED)
            self.shift_pixel_grid()

    def run(self):
        self.is_stopping = False
        while True:
            while not self.queue.empty():
                msg = self.queue.get()
                self.process_message(msg)

            self.draw_objects()
            self.update_objects()
            pygame.display.update()

            # Break if should stop
            if self.is_stopping:
                break

            sleep(0.2)

    def stop(self):
        self.is_stopping = True

    def draw_objects(self):
        for row in self.pixel_grid:
            for pixel in row:
                pixel.show()

    def update_objects(self):
        for row in self.pixel_grid:
            for pixel in row:
                pixel.update()


def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    old_range = old_range_max - old_range_min
    new_range = new_range_max - new_range_min
    new_value = (float(((old_value - old_range_min) * new_range) / old_range)) + new_range_min

    return int(new_value)


def run_example():
    done = False

    display = Display()

    display.start()

    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # mid = mido.MidiFile("{}/media/mute-city.mid".format(dir_path))

    # noinspection PyUnusedLocal
    def stop(*args):
        global done
        done = True
        display.stop()
        pygame.quit()
        # exit()

    signal.signal(signal.SIGINT, stop)

    while not done:

        # This limits the while loop to a max of 10 times per second.
        # Leave this out and we will use all CPU we can.
        clock.tick(10)

        screen.fill(BLACK)

        display = Display()
        display.start()

        display.update_objects()
        display.draw_objects()

        pygame.display.update()

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


if __name__ == '__main__':
    run_example()
