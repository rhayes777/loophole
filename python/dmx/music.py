# Generates chords randomly from an array (List of Lists)
# 
# Plays it in realtime.
#
# change timeStep to vary spacing between chords (in seconds)
#
#

import time
import rtmidi
import random

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

# Defining chordStruct, a list of chords.
#
# Each chord is itself a list, with each integer showing its distance
# from the root note in semitones.
#


chord_dict = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7]

}


class MidiInstrument:
    def __init__(self, no_of_positions=120):
        self.no_of_positions = no_of_positions
        self.playing_notes = []
        self.stopping_notes = []

    def update(self):
        messages_dict = {}
        for note in self.stopping_notes:
            messages_dict[str(note.position)] = [0x90, note.position, 0]
        for note in self.playing_notes:
            if str(note.position) in messages_dict:
                messages_dict[str(note.position)][2] += note.volume
            else:
                messages_dict[str(note.position)] = [0x90, note.position, note.volume]
            if messages_dict[str(note.position)][2] > 112:
                messages_dict[str(note.position)][2] = 112
        for message in messages_dict.values():
            midiout.send_message(message)
        self.stopping_notes = []

    def play(self, obj):
        if isinstance(obj, Chord):
            for note in obj.notes:
                self.play(note)
        else:
            self.playing_notes.append(obj)

    def stop(self, obj):
        if isinstance(obj, Chord):
            for note in obj.notes:
                self.stop(note)
        elif obj in self.playing_notes:
            self.playing_notes.remove(obj)
            self.stopping_notes.append(obj)


class Chord:
    triad = [0, 2, 4]

    def __init__(self, notes):
        self.notes = notes


class Scale:
    major = [0, 2, 4, 5, 7, 9, 11]
    minor = [0, 2, 3, 5, 7, 8, 10]
    minor_pentatonic = [0, 3, 5, 7, 10]
    minor_blues = [0, 3, 5, 6, 7, 10]

    def __init__(self, scale, base_octave=3):
        self.scale = scale
        self.length = len(scale)
        self.note_dict = {}
        self.chord_dict = {}
        self.base_octave = base_octave

    def interval_to_position(self, interval):
        return self.scale[interval % self.length] + 12 * (interval / self.length + self.base_octave)

    def note(self, interval):
        position = self.interval_to_position(interval)
        if str(position) not in self.note_dict:
            self.note_dict[str(position)] = Note(position)
        return self.note_dict[str(position)]

    def chord(self, interval, intervals=Chord.triad):
        positions = map(lambda i: self.interval_to_position(interval + i), intervals)
        if str(positions) not in self.chord_dict:
            self.chord_dict[str(positions)] = Chord(map(Note, positions))
        return self.chord_dict[str(positions)]

    def change_octave(self, by):
        self.base_octave = self.base_octave + by


class Note:
    def __init__(self, position, volume=112):
        self.position = position
        self.volume = volume


chordStruct = [

    [0, 4, 7],

    [0, 3, 7],

    [0, 4, 7, 9],

    [0, 2, 5, 7],

    [1, 4, 7, 11],

    [2, 5, 7, 9],

    [0, 2, 7, 9]

]


# (Calls "midiout.send_message" for list passed into "chord" argument) old
#

# playChord function:
#
# 'position' is ascending from C, so:
#
# 0 = C
# 1 = C#
# 2 = D   etc...
#
# 'key' refers to a 'chord_x...' array which stores different formations
# of chords eg. Maj = 0, 4, 7  ... Min = 0, 3, 7 etc.
#
# 'octave' is the octave in which the chord is played
# Middle C is at 5 octaves in. Octave integer is multiplied by 12 to
# define the root note of the chord.
#
# So calling playChord(4, 0, 5) would send MIDI message for E major in
# the 5th Octave.


def playChord(position, key, octave):
    chord = chordStruct[key]

    root = (octave * 12) + position

    i = 0

    for note in chord:
        chordMIDI = [0x90, root + note, 112]
        midiout.send_message(chordMIDI)

        i += 1


# stopChord function. Uses while loop to scan through all notes
# and sets all of their velocities to zero

def stopChord():
    i = 0

    while i < 120:
        notes_off = (0x90, i, 0)
        midiout.send_message(notes_off)
        i += 1


# Shockingly ugly main loop
# Just cycles throgh all the chords in the sequence until the counter reaches 999

def run():
    counter = 0
    mainRoot = 0

    timeStep = 1

    while counter < 1000:

        print(counter)

        rootStep = random.randint(-5, 5)

        mainRoot = mainRoot + rootStep

        chordSelect = random.randint(0, len(chordStruct) - 1)

        if random.randint(0, 30) > 15:

            playChord(mainRoot, chordSelect, 5)

            if mainRoot > 25:
                mainRoot = 0

        else:

            if mainRoot < 1:
                mainRoot = 20

            playChord(mainRoot - 2, chordSelect, 5)

        print(chordStruct[chordSelect])

        time.sleep(timeStep)

        counter += 1

        stopChord()

    del midiout


if __name__ == "__main__":
    run()

### original code that I pilfered...
#
#
# note_on = [0x90, 60, 112] # channel 1, middle C, velocity 112
# note_off = [0x80, 60, 0]
# midiout.send_message(note_on)
# time.sleep(0.5)
# midiout.send_message(note_off)
# time.sleep(0.5)
#
