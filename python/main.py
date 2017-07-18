import music
import rhythm

# Create a midi instrument
instrument = music.MidiInstrument()
# Create a scale
scale = music.Scale(music.Scale.minor, key=music.Key.A)

clock = rhythm.SongClock(60)


def add_note(note, length=1.0):
    def play():
        instrument.play(note)
        instrument.update()

    def stop():
        instrument.stop(note)
        instrument.update()
    clock.add_action(play, stop, length=length)


instrument.play(scale.note(0))


def add_bend(value):
    def bend():
        instrument.midi_output.write_short(0xb0, 77, value)

    clock.add_action(bend)

add_bend(0)
add_bend(1)
add_bend(2)
add_bend(4)
add_bend(16)
add_bend(50)
add_bend(100)
add_bend(200)
add_bend(300)
add_bend(400)
add_bend(1000)
add_bend(2000)

# add_note(scale.note(0))
# add_note(scale.note(3))
# add_note(scale.note(2))
# add_note(scale.note(5))
# add_note(scale.note(0), length=0.5)
# add_note(scale.note(3), length=0.5)
# add_note(scale.note(2), length=0.5)
# add_note(scale.note(5), length=0.5)

clock.start()
