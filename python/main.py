import player
import dancemat
import pygame
import signal
import effect
import sys
import os
from random import randint
import messaging

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

track = None
combinator = None

last_on_buttons = []


# Function to listen for changes to button state
def listener(status_dict):
    global last_on_buttons
    global track_number
    on_buttons = [button for (button, is_on) in status_dict.iteritems() if is_on]
    new_on_buttons = filter(lambda b: b not in last_on_buttons, on_buttons)
    last_on_buttons = on_buttons

    for button in new_on_buttons:
        messaging.write(messaging.ButtonMessage(button))

    if len(new_on_buttons) > 0 and track is not None:
        player.set_program(15, program=116)
        player.note_on(15, velocity=127)

    if dancemat.Button.start in on_buttons:
        track_number += 1
        track.stop()
        start_track_with_name(track_names[track_number % len(track_names)])
    elif dancemat.Button.select in on_buttons:
        track_number -= 1
        track.stop()
        start_track_with_name(track_names[track_number % len(track_names)])
    else:
        combinator.apply_for_buttons(on_buttons)


def start_track_with_name(track_name):
    global play
    global track
    global combinator
    filename = "media/{}".format(track_name)
    track = player.Track(filename=filename, is_looping=True)

    combinator = effect.Combinator(configuration, track)

    # noinspection PyUnusedLocal
    def stop(*args):
        global play
        track.stop()
        combinator.stop()
        play = False

    signal.signal(signal.SIGINT, stop)

    channels = track.channels

    def note_on_listener(msg):
        messaging.write(messaging.MidiMessage(msg))

    for channel in channels:
        channel.note_on_listener = note_on_listener

    track.start()


start_track_with_name(track_names[track_number])
mat.set_button_listener(listener)

# Keep reading forever
while play:
    mat.read()
    clock.tick(40)
