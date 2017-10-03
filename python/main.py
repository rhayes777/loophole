import midi_player
import dancemat
from time import sleep
import signal

mat = dancemat.DanceMat()
track = midi_player.Song(is_looping=True)

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
    playing_channels = []
    if status_dict[dancemat.Button.triangle]:
        playing_channels.append(0)
    if status_dict[dancemat.Button.down]:
        playing_channels.append(1)
    if status_dict[dancemat.Button.square]:
        playing_channels.append(8)
    if status_dict[dancemat.Button.circle]:
        playing_channels.append(9)
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

    if status_dict[dancemat.Button.left]:
        track.send_command(midi_player.Command.tempo_change, value=0.5)
    elif status_dict[dancemat.Button.right]:
        track.send_command(midi_player.Command.tempo_change, value=2)
    else:
        track.send_command(midi_player.Command.tempo_change, value=1)


# Attach that listener function to the dancemat
mat.set_button_listener(listener)

track.start()

# Keep reading forever
while play:
    mat.read()
    sleep(0.05)
