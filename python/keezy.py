import dancemat
import sample


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


# Function to listen for changes to button state
def listener(status_dict):
    for button in status_dict.keys():
        is_pressed = status_dict[button]
        # Check if button is in the dictionary
        if button in position_dict:
            number = position_dict[button]
            sample.queues[number].put(1 if is_pressed else 0)

# Attach that listener function to the dancemat
mat.set_button_listener(listener)
sample.play_track("white", 4)

# Keep reading forever
while 1:
    mat.read()