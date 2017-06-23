import dancemat
import music

mat = dancemat.DanceMat()

scale = music.Scale(music.Scale.major)

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
        chord = scale.chord(position_dict[button])
        chord.set_should_play(is_on)
    elif is_on:
        scale.change_octave(-1 if button == dancemat.Button.select else 1)


mat.set_button_listener(listener)

while 1:
    mat.read()
    scale.update()
