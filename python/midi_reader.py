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

all_Dots = []  # TODO this should be all_dots


"""
In Bash type:
git log

Then copy the hash by this commit and then type:

git show i3rio3hfwifh904oirgosnfwpfnweffwep

(With a hash instead of the random text)
...that will show you what was added (green) and what was removed (red) in this commit.
"""


# basic gfx class
class Dot():  # TODO: this doesn't need brackets
    def __init__(self, colour, time):
        # all_Dots.append(self) TODO: I removed this because it feels more flexible to decide outside of the constructor whether to add the instance to a list or not
        self.colour = colour # TODO: I've made this colour a tuple (red, green, blue) instead because that's how you've defined colours above and that's how they work with the pygame library
        self.time = time
        self.size = 50

    # def __call__(self, *args, **kwargs):  TODO: this code isn't being used. __call__ it a weird think that makes an instance of a class callable like a function. I haven't really seen it used before!
    #     all_Dots.append(self)
    #     self.pos_x = 100
    #     self.pos_y = 100
    #     self.colour_r = 250
    #     self.colour_g = 250
    #     self.colour_b = 250
    #     self.time = 50
    #     self.size = 50

    # def update(self):  TODO: this bit wasn't doing anything
    #     print "Dot instance update"
    #     # if timer>self.time:
    #     #    self.size = 100

    def show(self, pos_x=random.randint(0, 500), pos_y=random.randint(0,
                                                                      500)):  # TODO: it seems to make sense to let us draw a dot more than once so we can define the style and put it in multiple places. I might be wrong (I'm still not sure how you remove/move dots?)
        print "Dot instance show"
        pygame.draw.ellipse(screen, self.colour,
                            [pos_x, pos_y, self.size, self.size], 3)


path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
mid = mido.MidiFile("{}/media/bicycle-ride.mid".format(dir_path))

all_Dots.append(Dot(50, BLUE))

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

        # Dot(random.randint(0, 500), random.randint(0, 500), 255, 255, 255, 50)

        pygame.display.update()

        print len(all_Dots)

        for Dot in all_Dots:  # TODO: Dot should be dot (variables_are_lower_dashed_case)
            Dot.show()  # TODO: enter changing coordinates here for where ever you want to put a dot
            # Dot.update()  # TODO: this method wasn't doing anything
            # print(all_Dots.__sizeof__())  TODO: I think you wanted print len(all_dots)


pygame.quit()
