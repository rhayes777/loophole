import player
import dancemat
from time import sleep
import pygame
import signal
import effect
import sys
import message_passer

filename = 'media/bicycle-ride.mid'
configuration = 'configurations/effects_1.json'

for arg in sys.argv:
    if '.mid' in arg:
        filename = arg
    elif '.json' in arg:
        configuration = arg

# Set up pygame
pygame.init()
pygame.display.init()
# create screen for pygame to draw to
screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

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

writer = message_passer.Writer()


def note_on_listener(msg):
    writer.write(str(msg))


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
