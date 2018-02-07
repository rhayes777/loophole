import input
import pygame
import sys
import os
from random import randint
import state
import signal

dirname = os.path.dirname(os.path.realpath(__file__))

# Set up pygame
pygame.init()
pygame.display.init()
# create screen for pygame to draw to
# screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

track_names = filter(lambda s: ".mid" in s, os.listdir("{}/media".format(dirname)))

track_number = randint(0, len(track_names) - 1)

track_path = "{}/media/song_pc.mid".format(dirname)

configuration_path = '{}/configurations/examples.json'.format(dirname)

for arg in sys.argv:
    if '.mid' in arg:
        track_path = arg
    elif '.json' in arg:
        configuration_path = arg

controller = input.Controller(pygame)

current_mode = state.Accelerate(configuration_path=configuration_path, track_names=track_names)
current_mode.change_to_track_with_name(track_names[track_number])
controller.set_button_listener(current_mode.did_receive_status_dict)
current_mode.start()

play = True


def stop(*args):
    global play
    play = False
    current_mode.stop()


signal.signal(signal.SIGINT, stop)

# Keep reading forever
while play:
    controller.read()
    clock.tick(40)
