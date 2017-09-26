import midi_player
import dancemat
from time import sleep
import signal

mat = dancemat.DanceMat()
track = midi_player.Song(filename="bicycle-ride.mid", is_looping=True)

play = True


def stop(*args):
    global play
    track.stop()
    play = False


signal.signal(signal.SIGINT, stop)

channels = track.channels

chord_channel = channels[0]
drum_channel = channels[8]

bass_channel = midi_player.BassChannel(2, chord_channel, drum_channel)
channels[2] = bass_channel

# Relate button names to positions in the scale
position_dict = {dancemat.Button.triangle: 0,
                 dancemat.Button.down: 1,
                 dancemat.Button.square: 2,
                 dancemat.Button.left: 3,
                 dancemat.Button.right: 4,
                 dancemat.Button.x: 5,
                 dancemat.Button.up: 6,
                 dancemat.Button.circle: 7}

channel_numbers_with_fifth = set()


# Function to listen for changes to button state
def listener(status_dict):
    playing_channels = [position_dict[button] for button in status_dict.keys() if
                        status_dict[button] and position_dict[button] in [0, 1, 2]]
    track.set_included_channels(playing_channels)

    def check_fifth(button_name, channel_number):
        if status_dict[button_name] and channel_number not in channel_numbers_with_fifth:
            channels[channel_number].add_effect(midi_player.fifth)
            channel_numbers_with_fifth.add(channel_number)
        elif channel_number in channel_numbers_with_fifth:
            channels[channel_number].remove_effect(midi_player.fifth)
            channel_numbers_with_fifth.remove(channel_number)

    check_fifth(dancemat.Button.x, 0)
    check_fifth(dancemat.Button.up, 1)
    check_fifth(dancemat.Button.circle, 2)


# Attach that listener function to the dancemat
mat.set_button_listener(listener)

track.start()

# Keep reading forever
while play:
    mat.read()
    sleep(0.05)
