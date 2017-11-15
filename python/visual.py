import mido
import os
import signal
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
        if self.is_on is False:  # TODO: This was == False whereas it should be is False
            self.colour = BLUE
        elif self.is_on:
            self.colour = RED


class Display:  # TODO: This class basically wraps the functionality you defined. It allows us to pass in references the pygame module and a screen
    def __init__(self, pygame, screen):
        self.pygame = pygame
        self.screen = screen
        self.queue = Queue()
        self.pixel_grid = [[]]  # numpy later maybe

        grid_size_x = 20
        grid_size_y = grid_size_x  # self.screen.get_width()

        self.num_pixels_x = self.screen.get_width() / grid_size_x
        self.num_pixels_y = self.screen.get_height() / grid_size_y

        for j in range(self.num_pixels_y):

            row = []

            for i in range(self.num_pixels_x):
                row.append(Pixel((grid_size_x / 2) + grid_size_x * i, (grid_size_y / 2) + (grid_size_y * j), False,
                                 grid_size_x, i))

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

            recent_note = get_new_range_value(1, 128, msg.note, 1, 20)

            print("Incoming note value: ", msg.note)
            print("Scaled value: ", recent_note)

            # all_dots.append(Dot(this_colour,
            #                     (random.randint(30, 70)),
            #                     (random.randint(0, self.screen.get_width())),
            #                     (msg.note * 10) - 300,
            #                     this_size))

            self.pygame.display.update()

            # print len(all_dots)

            self.screen.fill(BLACK)

            for dot in all_dots:
                dot.show(self.pygame, self.screen)
                dot.update()

            for row in self.pixel_grid:

                for pixel in row:

                    if get_new_range_value(1, 128, msg.note, 1, self.num_pixels_x) == pixel.ref:
                        pixel.is_on = True
                    else:
                        pixel.is_on = False

                    pixel.show(self.pygame, self.screen)
                    pixel.update()

    def on_message_received(self, msg):
        self.queue.put(msg)

    # Stop this display
    # noinspection PyUnusedLocal
    def stop(self, *args):
        print "stop2"
        self.queue.put("STOP")

    def update(self):
        print "delete me"
        # TODO update the display

    def loop(self):
        is_looping = True
        while is_looping:
            while not self.queue.empty():
                msg = self.queue.get()
                print msg
                if isinstance(msg, str) and "STOP" == msg:
                    print "stop3"
                    is_looping = False
                self.process_message(msg)

            self.update()

            sleep(0.2)

    def start(self):
        t = Thread(target=self.loop)
        t.start()


def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    old_range = old_range_max - old_range_min
    new_range = new_range_max - new_range_min
    new_value = (float(((old_value - old_range_min) * new_range) / old_range)) + new_range_min

    return int(new_value)


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

    # noinspection PyUnusedLocal
    def stop(*args):
        print "stop1"
        global done
        display.stop()
        done = True

    signal.signal(signal.SIGINT, stop)

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

            display.on_message_received(message)

    pygame.quit()


if __name__ == '__main__':  # TODO: This will only be true if this file is called directly rather than imported (e.g. python display.py)
    run_example()
