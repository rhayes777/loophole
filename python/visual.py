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
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (180, 60, 30)
GREEN = (46, 190, 60)
BLUE = (30, 48, 180)
PINK_MASK = (255, 0, 255)

#pygame Font setup

#Init pygame font module
pygame.font.init()

#Loading font
font_arcade = pygame.font.Font("media/arcadeclassic.ttf", 56)

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
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h))

all_sprites = pygame.sprite.Group()

#notice class handles messages displayed to screen using fonts

class Notice():
    def __init__(self, words, colour, drop_colour, size, this_font):
        self.words = words
        self.colour = colour
        self.drop_colour = drop_colour
        self.size = size
        self.this_font = this_font

        self.main_render = self.this_font.render(self.words, True, self.colour)

        self.drop_render = self.this_font.render(self.words, True, self.drop_colour)

    def blit_text(self, this_surface, xpos, ypos, shadow = False):
        if shadow is True:
            this_surface.blit(self.drop_render,
                              (xpos - (self.drop_render.get_width() / 2) + 8,
                               ypos - (self.drop_render.get_height() / 2) + 8))

        this_surface.blit(self.main_render,
                    (xpos - (self.main_render.get_width() / 2),
                     ypos - (self.main_render.get_height() / 2)))

my_message = Notice("Hello! This is a test!", RED, BLUE, 56, font_arcade)


class Quaver(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("media/quaver.bmp")
        self.image.convert()
        self.image.set_colorkey(PINK_MASK)
        self.image = pygame.transform.scale(self.image, (100,100))
        self.rect = self.image.get_rect()
        self.rect.center = (screen.get_width() /2, screen.get_height() / 2)


class Pixel:
    def __init__(self, pos_x, pos_y, is_on, size, ref, colour=BLUE):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.is_on = is_on
        self.size = size
        self.ref = ref
        self.colour = colour

    def show(self):

        if self.colour == BLUE:
            pygame.draw.ellipse(screen, self.colour,
                            [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 2)

        #Gradually shifts colour of 'RED' (On) Pixels as they move up the screen
        #Get_new_range_value scales y position to a 0-255 RGB range

        if self.colour == RED:
            pygame.draw.ellipse(screen,
                                [
                                get_new_range_value(0, 800, self.pos_y, 30, 255), #Red
                                get_new_range_value(0, 800, self.pos_y, 20, 140), #Green
                                get_new_range_value(0, 800, self.pos_y, 255, 120) #Blue
                                ],
                            [self.pos_x - (self.size / 2), self.pos_y - (self.size / 2), self.size, self.size], 2)


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

            screen.fill(BLACK)
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

        my_message.blit_text(screen, screen.get_width() / 2 , screen.get_height() / 2, shadow = True)


def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    old_range = old_range_max - old_range_min
    new_range = new_range_max - new_range_min
    new_value = (float(((old_value - old_range_min) * new_range) / old_range)) + new_range_min

    return int(new_value)

def draw_text(text_render, xpos, ypos, shadow = False):

    if shadow is False:
        screen.blit(text_render,
                    (xpos - (my_text.get_width() / 2),
                     ypos - (my_text.get_height() / 2)))



done = False
display = Display()
my_quaver = Quaver()
#all_sprites.add(my_quaver)

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
