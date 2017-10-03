import mido
import os

path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
mid = mido.MidiFile("{}/media/bicycle-ride.mid".format(dir_path))
for message in mid.play(meta_messages=True):
    print message

    # Do stuff here
