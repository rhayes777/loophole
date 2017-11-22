import player
import dancemat
from time import sleep
import pygame
import signal
import effect
import sys
import os

dirname = os.path.dirname(os.path.realpath(__file__))

# Set up pygame
pygame.init()
pygame.display.init()
# create screen for pygame to draw to
# screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

# Popen([executable, 'visual.py'])

mat = dancemat.DanceMat(pygame)
track = player.Track(filename=filename, is_looping=True)

combinator = effect.Combinator(configuration, track)

play = True


# noinspection PyUnusedLocal
def stop(*args):
    global play
    track.stop()
    play = False


signal.signal(signal.SIGINT, stop)

channels = track.channels


def note_on_listener(msg):
    print str(msg)
    sys.stdout.flush()


# TODO: Test whether this message passing mechanism is causing the jitter
for channel in channels:
    channel.note_on_listener = note_on_listener


# Function to listen for changes to button state
def listener(status_dict):
    on_buttons = [button for (button, is_on) in status_dict.iteritems() if is_on]
    combinator.apply_for_buttons(on_buttons)


# Attach that listener function to the dancemat
mat.set_button_listener(listener)

track.start()

# Keep reading forever
while play:
    mat.read()
    sleep(0.05)
