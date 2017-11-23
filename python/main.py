import player
import dancemat
import pygame
import signal
import effect
import sys
import os
from random import randint

dirname = os.path.dirname(os.path.realpath(__file__))

# Set up pygame
pygame.init()
pygame.display.init()
# create screen for pygame to draw to
# screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

track_names = filter(lambda s: ".mid" in s, os.listdir("media"))

track_number = randint(0, len(track_names) - 1)

default_filename = "media/song_pc.mid"

configuration = 'configurations/examples.json'

for arg in sys.argv:
    if '.mid' in arg:
        default_filename = arg
    elif '.json' in arg:
        configuration = arg

mat = dancemat.DanceMat(pygame)

play = True


def start_track_with_name(track_name):
    global track_number
    global play
    filename = "media/{}".format(track_name)
    track = player.Track(filename=filename, is_looping=True)

    combinator = effect.Combinator(configuration, track)

    # noinspection PyUnusedLocal
    def stop(*args):
        track.stop()
        play = False

    signal.signal(signal.SIGINT, stop)

    channels = track.channels

    def note_on_listener(msg):
        print msg
        sys.stdout.flush()

    for channel in channels:
        channel.note_on_listener = note_on_listener

    # Function to listen for changes to button state
    def listener(status_dict):
        global track_number
        on_buttons = [button for (button, is_on) in status_dict.iteritems() if is_on]
        if dancemat.Button.start in on_buttons:
            track_number += 1
            start_track_with_name(track_names[track_number % len(track_names)])
        elif dancemat.Button.select in on_buttons:
            track_number -= 1
            start_track_with_name(track_names[track_number % len(track_names)])
        else:
            combinator.apply_for_buttons(on_buttons)

    # Attach that listener function to the dancemat
    mat.set_button_listener(listener)

    track.start()


start_track_with_name(track_names[track_number])

# Keep reading forever
while play:
    mat.read()
    clock.tick(5)
