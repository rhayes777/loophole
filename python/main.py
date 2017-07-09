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


add_note(scale.note(0))
add_note(scale.note(3))
add_note(scale.note(2))
add_note(scale.note(5))
add_note(scale.note(0), length=0.5)
add_note(scale.note(3), length=0.5)
add_note(scale.note(2), length=0.5)
add_note(scale.note(5), length=0.5)

clock.start()
