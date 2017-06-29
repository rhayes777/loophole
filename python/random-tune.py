import music, rhythm, math, random

# Create a midi instrument
instrument = music.MidiInstrument()
# Create a scale
scale = music.Scale(music.Scale.major, key=music.Key.B)

clock = rhythm.SongClock(70)

note_position = 0
current_note = None

tune = [random.randrange(0,12) for _ in range (999)]

def next_note():
    global note_position
    global current_note
    note = scale.note(tune[note_position])
    note_position += 1
    if current_note is not None:
        instrument.stop(current_note)
    instrument.play(note)
    current_note = note
    instrument.update()


clock.add_function(next_note)
clock.run()
