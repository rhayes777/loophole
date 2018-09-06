from control import input, state
import pygame
import sys
import os
import signal
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

dirname = os.path.dirname(os.path.realpath(__file__))

# Set up pygame
pygame.init()
pygame.display.init()
# create screen for pygame to draw to
# screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

# track_names = filter(lambda s: ".mid" in s, os.listdir("{}/media".format(dirname)))

# logger.info(track_names)
#
# track_number = randint(0, len(track_names) - 1)

media_path = "{}/media".format(dirname)

configuration_path = '{}/configurations/switch_examples.json'.format(dirname)

for arg in sys.argv:
    if '.json' in arg:
        configuration_path = arg

controller = input.Controller(pygame)

current_mode = state.Normal(configuration_path=configuration_path, media_path=media_path, track_names=['lull.mid'])
current_mode.change_to_track_with_name('lull.mid')
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
