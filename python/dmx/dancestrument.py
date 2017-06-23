import dancemat
import chord

mat = dancemat.DanceMat()

scale = chord.scale_dict['minor_blues']

position_dict = {dancemat.Button.triangle: 0,
                 dancemat.Button.down: 1,
                 dancemat.Button.square: 2,
                 dancemat.Button.left: 3,
                 dancemat.Button.right: 4,
                 dancemat.Button.x: 5,
                 dancemat.Button.up: 6,
                 dancemat.Button.circle: 7}


def listener(button, is_on):
    print "{} is_on = {}".format(button, is_on)
    if button in position_dict:
        note = scale[position_dict[button]]
        if is_on:
            chord.play_note(note)
        else:
            chord.stop_note(note)


mat.set_button_listener(listener)

while 1:
    mat.read()
