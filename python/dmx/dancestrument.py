import dancemat
import chord

mat = dancemat.DanceMat()

note_dict = {dancemat.Button.triangle: 0,
             dancemat.Button.down: 2,
             dancemat.Button.square: 4,
             dancemat.Button.left: 5,
             dancemat.Button.right: 7,
             dancemat.Button.x: 9,
             dancemat.Button.up: 11,
             dancemat.Button.circle: 12}


def listener(button):
    print "{} pressed".format(button)
    chord.play_note(note_dict[button])


mat.set_button_listener(listener)

while 1:
    mat.read()
