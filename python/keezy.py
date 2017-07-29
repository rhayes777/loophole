import dancemat
import sample
from time import sleep

# Create a dancemat
mat = dancemat.DanceMat()

# Relate button names to positions in the scale
position_dict = {dancemat.Button.triangle: 0,
                 dancemat.Button.down: 1,
                 dancemat.Button.square: 2,
                 dancemat.Button.left: 3,
                 }
# dancemat.Button.right: 4,
# dancemat.Button.x: 5,
# dancemat.Button.up: 6,
# dancemat.Button.circle: 7}

tracks = [sample.WHITE_atmos, sample.WHITE_guitar, sample.WHITE_percnsub, sample.WHITE_sitar]


# Function to listen for changes to button state
def listener(status_dict):
    for button in status_dict.keys():
        is_pressed = status_dict[button]
        # Check if button is in the dictionary
        if button in position_dict and is_pressed:
            number = position_dict[button]
            sample.loop_wav_on_new_thread(tracks[number], no_of_times_to_loop=1)


# Attach that listener function to the dancemat
mat.set_button_listener(listener)
# sample.play_track("white", 4)

# Keep reading forever
while 1:
    mat.read()
    sleep(0.05)
