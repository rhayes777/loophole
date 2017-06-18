# Outputs a short chord sequence to available MIDI port
# 
#

import time
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")


# Defining a list for each note...
#
# Each list contains the MIDI message for that note
#
# note_Xx = [MIDI CHANNEL, MIDI NOTE, VELOCITY]
#
# Notes Middle C -> B#
# note_C = Middle C, note_Cs = Middle C# etc

note_C = [0x90, 60, 112]
note_Cs = [0x90, 61, 112]
note_D = [0x90, 62, 112]
note_Ds = [0x90, 63, 112]
note_E = [0x90, 64,112]

note_F = [0x90, 65, 112]
note_Fs = [0x90, 66, 112]
note_G = [0x90, 67,112]
note_Gs = [0x90, 68, 112]

note_A = [0x90, 69, 112]
note_As = [0x90, 70, 112]
note_B = [0x90, 71, 112]

# Defining a list for each chord...
#
# Each chord is itself a list of notes
#
# chord_cMaj = C Major, chord_eMin = E Minor etc

chord_cMaj = [note_C, note_E, note_G]
chord_cMajAdd7 = [note_C, note_E, note_G, note_B]
chord_dMin = [note_D, note_F, note_A]
chord_eMin = [note_E, note_G, note_B]
chord_gMaj = [note_D, note_G, note_B]
chord_fMaj = [note_C, note_F, note_C]
chord_csMin = [note_Cs, note_E, note_Gs]

# playChord function. Does what it says on the tin...
# Calls "midiout.send_message" for list passed into "chord" argument
#

def playChord(chord):
    
    i = 0

    while i < len(chord):
        midiout.send_message(chord[i])
        i += 1


# stopChord function. Uses while loop to scan through all 12 notes in
# Middle C Octave and sets all of their velocities to zero

def stopChord():

    i = 60
    
    while i<71 :
        notes_off = (0x90, i, 0)
        midiout.send_message(notes_off)
        i += 1

# Shockingly ugly main loop
# Just cycles throgh all the chords in the sequence until the counter reaches 999

counter = 0

while counter < 1000:

    print(counter)

    playChord(chord_dMin)
    time.sleep(0.8)
    stopChord()
    time.sleep(0.3)
    playChord(chord_cMaj)
    time.sleep(0.8)
    stopChord()
    time.sleep(0.3)
    playChord(chord_fMaj)
    time.sleep(0.8)
    stopChord()
    time.sleep(0.3)
    playChord(chord_cMajAdd7)
    time.sleep(0.8)
    stopChord()
    time.sleep(0.3)

    counter += 1


del midiout

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
