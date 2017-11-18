import player
import dancemat
from time import sleep
import pygame
import signal
import visual
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
    if status_dict[dancemat.Button.up]:
        # channels[1].instrument_type += 1
        track.tempo_shift = 2
    if status_dict[dancemat.Button.down]:
        track.tempo_shift = 0.5
    if status_dict[dancemat.Button.right]:
        channels[1].instrument_version += 1
    if status_dict[dancemat.Button.left]:
        channels[1].instrument_version -= 1

    if status_dict[dancemat.Button.triangle]:
        channels[0].intervals = player.Intervals([1])
    if status_dict[dancemat.Button.circle]:
        channels[0].intervals = player.Intervals([2])
    if status_dict[dancemat.Button.x]:
        channels[0].intervals = player.Intervals([3])
    if status_dict[dancemat.Button.square]:
        channels[0].intervals = player.Intervals([4])


# Attach that listener function to the dancemat
mat.set_button_listener(listener)

track.start()
display.start()

# Keep reading forever
while play:
    mat.read()
    sleep(0.05)
