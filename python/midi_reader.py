import mido
import os
import pygame
import random



#pygame setup
pygame_Status = pygame.init()

#for the 'game loop'
done = False
clock = pygame.time.Clock()

#indicates pygame has set up:
#(6,0) = all good
print(pygame_Status)

#create screen for pygame to draw to
screen = pygame.display.set_mode((800,600))

#timer
timer = 0

#pygame gfx constants
BLACK = (0,0,0)
BLUE = (30,48,180)
RED = (180,60,30)
circle_x = 200
circle_y = 200

all_Dots = []

#basic gfx class
class Dot():

    def __init__(self, pos_x, pos_y, colour_r, colour_g, colour_b, time):
        all_Dots.append(self)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.colour_r = colour_r
        self.colour_g = colour_g
        self.colour_b = colour_b
        self.time = time
        self.size = 50

    def __call__(self, *args, **kwargs):
        all_Dots.append(self)
        self.pos_x = 100
        self.pos_y = 100
        self.colour_r = 250
        self.colour_g = 250
        self.colour_b = 250
        self.time = 50
        self.size = 50

    def update(self):
        print "Dot instance update"
        #if timer>self.time:
        #    self.size = 100


    def show(self):
        print "Dot instance show"
        pygame.draw.ellipse(screen, [self.colour_r, self.colour_g, self.colour_b], [self.pos_x, self.pos_y, self.size, self.size], 3)
        #pygame.draw.ellipse(screen, BLUE, [30,30,300,300], 3)

path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
mid = mido.MidiFile("{}/media/bicycle-ride.mid".format(dir_path))

#all_Dots.append(Dot(50,50,255,255,255,50))



while not done:

    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(10)
    timer = timer + 1
    print(timer)

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

    for message in mid.play():
        print(message)

        Dot(random.randint(0, 500), random.randint(0, 500), 255, 255, 255, 50)

        pygame.display.update()

        for Dot in all_Dots:
            Dot.show()
            Dot.update()
            print(all_Dots.__sizeof__())


pygame.quit()