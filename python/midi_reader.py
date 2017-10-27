import mido
import os
import pygame
import random

# pygame setup
pygame_Status = pygame.init()

# for the 'game loop'
done = False
clock = pygame.time.Clock()

# indicates pygame has set up:
# (6,0) = all good
print(pygame_Status)

# create screen for pygame to draw to
screen = pygame.display.set_mode((1000, 700))

# timer
timer = 0

# pygame gfx constants
BLACK = (0, 0, 0)
BLUE = (30, 48, 180)
RED = (180, 60, 30)
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

    def show(self):

        if self.size > 7:
            pygame.draw.ellipse(screen, self.colour, [self.pos_x-(self.size/2), self.pos_y-(self.size/2), self.size, self.size], 2)

    def update(self):

        self.size = self.size * self.time

        if self.size > 5:
            self.time -= 0.001
        else:
            self.size = 5
            self.die()

    def die(self):

        all_dots.remove(self)


path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
mid = mido.MidiFile("{}/media/big-blue.mid".format(dir_path))


while not done:



    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)
    timer +=1
    print(timer)

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

    for message in mid.play():

        if message.type == 'note_on':

            print(message)

            all_dots.append(Dot(BLUE,
                                (random.randint(30,70)),
                                (random.randint(0,screen.get_width())),
                                (getattr(message, 'note')*10)-300,
                                0.85))

            pygame.display.update()

            print len(all_dots)

            screen.fill(BLACK)

            for dot in all_dots:
                dot.show()
                dot.update()
                # print len(all_dots)

pygame.quit()
