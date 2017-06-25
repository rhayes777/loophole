import music

import time, random

chord_player = music.MidiInstrument()

scale = music.Scale(music.Scale.major, key=music.Key.A)

note_A = music.Note(1, 112)

playing_notes = {}

sequence_time = 0

chord_player.play(note_A)

chord_player.update()

time.sleep(5)