import dancemat
import music

mat = dancemat.DanceMat()
instrument = music.MidiInstrument()
scale = music.Scale(music.Scale.major)

position_dict = {dancemat.Button.triangle: 0,
                 dancemat.Button.down: 1,
                 dancemat.Button.square: 2,
                 dancemat.Button.left: 3,
                 dancemat.Button.right: 4,
                 dancemat.Button.x: 5,
                 dancemat.Button.up: 6,
                 dancemat.Button.circle: 7}

playing_notes = {}


def listener(button, is_on):
    if button in position_dict:
        note = playing_notes[button] if button in playing_notes else scale.chord(position_dict[button])
        if is_on:
            print "{} pressed".format(button)
            instrument.play(note)
            playing_notes[button] = note
        else:
            instrument.stop(note)
            if button in playing_notes:
                del playing_notes[button]
    elif is_on:
        instrument.stop_all()
        scale.change_octave(-1 if button == dancemat.Button.select else 1)
    instrument.update()


mat.set_button_listener(listener)

while 1:
    mat.read()
