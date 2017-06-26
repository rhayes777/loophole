import music
import rhythm

import time, random

import rtmidi

#Creating a MidiInstrument() called chord_player

chord_player = music.MidiInstrument()

#creating a scale

scale = music.Scale(music.Scale.major, key=music.Key.A)

#creating a note from scale

note_A = music.Note(40, 112)

#create a clock

chord_clock = rhythm.SongClock(60, 0, 0)

timer = 0


playing_notes = {}

sequence_time = 0

chord_player.play(note_A)

chord_player.update()

while timer<1000:

    chord_clock.update()
