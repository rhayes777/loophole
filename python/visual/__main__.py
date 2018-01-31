import mido
from Queue import Queue
from threading import Thread
import logging
import sys
import pygame
import signal
from .. import messaging

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (180, 60, 30)
GREEN = (46, 190, 60)
BLUE = (30, 48, 180)
PINK_MASK = (255, 0, 255)

logging.basicConfig()

logger = logging.getLogger(__name__)

# pygame clock init
clock = pygame.time.Clock()

# pygame init
pygame.display.init()

# pygame setup
# (6,0) = all good
print(pygame.init())

import background
import foreground
import font
import util

# create screen for pygame to draw to
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h))

all_dots = []

# Create an instance of Grid
the_grid = background.Grid(info.current_w / 2, info.current_h / 2, 10, 5)

my_message = font.Wave("Welcome to the MidiZone", RED, 30, font.font_arcade, True)

test_pixel = foreground.Pixel(5, 5, True, 20, 1)


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

        self.flash = foreground.Flash(15)
        self.flashing_now = False

        self.draw_foreground = True
        self.draw_text = True

    def new_row(self):
        """
        Created a new row
        :return: A list of blue pixels at the top of the screen of length num_pixels_x
        """
        row = []
        for i in range(self.num_pixels_x):
            row.append(
                foreground.Pixel((self.grid_size_x / 2) + self.grid_size_x * i, (self.grid_size_y / 2),
                                 False, self.grid_size_x, i))
        return row

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
                message = self.queue.get()

                if isinstance(message, messaging.MidiMessage):
                    mido_message = message.mido_message
                    if mido_message.type == 'note_on':
                        # Use your function to convert to screen cooordinates
                        x_position = util.get_new_range_value(1, 128, mido_message.note, 1, self.num_pixels_x)
                        # Set the "pixel" at that position in this row to red
                        row[x_position].colour = RED

                elif isinstance(message, messaging.ButtonMessage):
                    display.flash.make_flash()
                    display.flashing_now = display.flash.is_flashing()

                    if message.button == "up":
                        # up buttons pressed
                        pass
                    elif message.button == "circle":
                        # circle pressed
                        pass

            # Add the newly created row to the queue
            self.row_queue.put(row)

            # If there are so many rows that it's going off screen, remove the row that was added first
            if len(self.row_queue.queue) > self.num_pixels_y:
                self.row_queue.get()

            screen.fill(BLACK)

            # render grid
            mouse_x, mouse_y = pygame.mouse.get_pos()
            the_grid.render(screen, (mouse_x, mouse_y))

            if self.flashing_now is False:
                self.flash.make_flash()
                self.flashing_now = self.flash.is_flashing()

            self.flash.render(screen)

            if self.timer >= 1:
                self.timer -= 1
            else:
                self.timer = 6

            # Draw all those objects
            if self.draw_foreground is True:
                self.draw_objects()

            test_pixel.show(screen)

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
                pixel.show(screen)

        foreground.all_sprites.draw(screen)

        test_pixel.show(screen)

        # Draw text
        if self.draw_text is True:
            my_message.blit_text(screen, screen.get_width() / 2, screen.get_height() / 2, self.timer)


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

        for message in messaging.read():
            pygame.event.get()

            display.queue.put(message)

    pygame.quit()


def run_for_mido():
    import os
    global done
    dirname = os.path.dirname(os.path.realpath(__file__))
    filename = '../media/mute-city.mid'
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
