import player
import dancemat
from time import sleep
import pygame
import signal
import visual
import effect
import sys

filename = 'media/bicycle-ride.mid' if len(sys.argv) == 1 else sys.argv[1]

# Set up pygame
pygame.init()
pygame.display.init()
# create screen for pygame to draw to
screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

mat = dancemat.DanceMat(pygame)
track = player.Track(filename=filename, is_looping=True)

combinator = effect.Combinator("configurations/effects_1.json", track)

play = True

display = visual.Display(pygame, screen)


# noinspection PyUnusedLocal
def stop(*args):
    global play
    track.stop()
    display.stop()
    play = False


signal.signal(signal.SIGINT, stop)

channels = track.channels

# TODO: Test whether this message passing mechanism is causing the jitter
channels[0].message_send_listener = display.on_message_received


# Function to listen for changes to button state
def listener(status_dict):
    on_buttons = [button for (button, is_on) in status_dict.iteritems() if is_on]
    combinator.apply_for_buttons(on_buttons)


# Attach that listener function to the dancemat
mat.set_button_listener(listener)

track.start()
display.start()

# Keep reading forever
while play:
    mat.read()
    sleep(0.05)
