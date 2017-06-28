import music
import rhythm

# Create a midi instrument
instrument = music.MidiInstrument()
# Create a scale
scale = music.Scale(music.Scale.minor, key=music.Key.A)

clock = rhythm.SongClock(60)

note_position = 0
current_note = None


def next_note():
    global note_position
    global current_note
    note = scale.note(note_position)
    note_position += 1
    if current_note is not None:
        instrument.stop(current_note)
    instrument.play(note)
    current_note = note
    instrument.update()


clock.add_function(next_note)
clock.run()
