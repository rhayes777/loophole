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
screen = pygame.display.set_mode((800, 600))

# timer
timer = 0

# pygame gfx constants
BLACK = (0, 0, 0)
BLUE = (30, 48, 180)
RED = (180, 60, 30)
circle_x = 200
circle_y = 200

all_dots = []

"""
In Bash type:
git log

Then copy the hash by this commit and then type:

git show i3rio3hfwifh904oirgosnfwpfnweffwep

(With a hash instead of the random text)
...that will show you what was added (green) and what was removed (red) in this commit.
"""


# basic gfx class
class Dot:
    def __init__(self, colour, size, pos_x, pos_y):
        self.colour = colour
        self.time = 5000
        self.size = size
        self.pos_x = pos_x
        self.pos_y = pos_y

    def show(self):
        pygame.draw.ellipse(screen, self.colour, [self.pos_x, self.pos_y, self.size, self.size], 3)


path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
mid = mido.MidiFile("{}/media/bicycle-ride.mid".format(dir_path))

all_dots.append(Dot(BLUE, 50, 50, 50))

while not done:

    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)
    timer = timer + 1  # TODO could be timer += 1
    print(timer)

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

    for message in mid.play():
        print(message)

        all_dots.append(Dot(BLUE, 50, random.randint(0, 400), random.randint(0, 400)))

        pygame.display.update()

        print len(all_dots)

        for Dot in all_dots:  # TODO: Dot should be dot (variables_are_lower_dashed_case)
            Dot.show()  # TODO: enter changing coordinates here for where ever you want to put a dot
            # Dot.update()  # TODO: this method wasn't doing anything
            # print(all_Dots.__sizeof__())  TODO: I think you wanted print len(all_dots)

pygame.quit()
