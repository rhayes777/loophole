import midi_player
import dancemat

mat = dancemat.DanceMat()
midi_player.play_midi_file_on_new_thread(name='bicycle-ride.mid')

# Relate button names to positions in the scale
position_dict = {dancemat.Button.triangle: 0,
                 dancemat.Button.down: 1,
                 dancemat.Button.square: 2,
                 dancemat.Button.left: 3,
                 dancemat.Button.right: 4,
                 dancemat.Button.x: 5,
                 dancemat.Button.up: 6,
                 dancemat.Button.circle: 7}


# Function to listen for changes to button state
def listener(status_dict):
    pressed_positions = [position_dict[button] for button in status_dict.keys() if status_dict[button]]
    midi_player.set_included_channels(pressed_positions)


# Attach that listener function to the dancemat
mat.set_button_listener(listener)

# Keep reading forever
while 1:
    mat.read()
