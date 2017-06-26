import dancemat
import music

# Create a dancemat
mat = dancemat.DanceMat()
# Create a midi instrument
instrument = music.MidiInstrument()
# Create a scale
scale = music.Scale(music.Scale.minor, key=music.Key.A)

# Relate button names to positions in the scale
position_dict = {dancemat.Button.triangle: 0,
                 dancemat.Button.down: 1,
                 dancemat.Button.square: 2,
                 dancemat.Button.left: 3,
                 dancemat.Button.right: 4,
                 dancemat.Button.x: 5,
                 dancemat.Button.up: 6,
                 dancemat.Button.circle: 7}

# Keep track of notes currently playing
playing_notes = {}


# Function to listen for changes to button state
def listener(button, is_pressed):
    # Check if button is in the dictionary
    if button in position_dict:
        # See if a note is already playing for that button
        if button in playing_notes:
            # If there is a note playing, grab that
            note = playing_notes[button]
        else:
            # Otherwise, grab the position in the scale associated with the button...
            position = position_dict[button]
            # ...and create a new jazzy seventh chord for that position (this is gonna be in the scale)
            # note = scale.chord(position, intervals=music.Chord.seventh_octave)
            note = scale.chord(position)
        # Check if the button is pressed down
        if is_pressed:
            print "{} pressed".format(button)
            # If this is, play the note
            instrument.play(note)
            # Make sure the note is in the playing_notes dictionary so we can get it later
            playing_notes[button] = note
        else:
            # Otherwise, stop playing the note...
            instrument.stop(note)
            # And if the note is in the dictionary, delete it
            if button in playing_notes:
                del playing_notes[button]
    # If the button wasn't in the dictionary, it's because it's select or start
    elif is_pressed:
        # Stop the instruments
        instrument.stop_all()
        # Change octave, going down for select and up for start
        scale.change_octave(-1 if button == dancemat.Button.select else 1)
    # This is called to make changes to the instrument have effect (i.e. it sends midi messages)
    instrument.update()

# Attach that listener function to the dancemat
mat.set_button_listener(listener)

# Keep reading forever
while 1:
    mat.read()
