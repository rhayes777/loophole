import mido
from Queue import Queue
from threading import Thread
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
pygame.display.init()
# create screen for pygame to draw to
screen = pygame.display.set_mode((1000, 700))


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
        pass
        # self.pos_y = self.pos_y - 1
        # print(".")


class Display(Thread):
    def __init__(self):
        super(Display, self).__init__()
        self.queue = Queue()

        self.grid_size_x = 20
        self.grid_size_y = self.grid_size_x  # self.screen.get_width()

        self.row_queue = Queue()

        self.num_pixels_x = screen.get_width() / self.grid_size_x
        self.num_pixels_y = screen.get_height() / self.grid_size_y

        self.is_stopping = False

    def new_row(self):
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
            row = self.new_row()
            while not self.queue.empty():
                msg = self.queue.get()
                if msg.type == 'note_on':
                    recent_note = get_new_range_value(1, 128, msg.note, 1, self.num_pixels_x)
                    row[recent_note].colour = RED

            self.row_queue.put(row)

            if len(self.row_queue.queue) > self.num_pixels_y:
                self.row_queue.get()

            screen.fill(BLACK)
            self.draw_objects()
            pygame.display.update()

            # Break if should stop
            if self.is_stopping:
                break

            clock.tick(5)

    def stop(self):
        self.is_stopping = True

    def draw_objects(self):
        for j, row in enumerate(self.row_queue.queue):
            y_position = j * self.grid_size_y
            for pixel in row:
                print pixel
                pixel.pos_y = y_position
                pixel.show()


def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    old_range = old_range_max - old_range_min
    new_range = new_range_max - new_range_min
    new_value = (float(((old_value - old_range_min) * new_range) / old_range)) + new_range_min

    return int(new_value)


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
    filename = 'media/song_pc.mid'
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
