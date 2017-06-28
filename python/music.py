import pygame.midi

pygame.init()

pygame.midi.init()

print pygame.midi.get_default_output_id()
print pygame.midi.get_device_info(1)

midi_Output = pygame.midi.Output(1)
midi_Output.set_instrument(0)


# Class that represents a midi instrument.
class MidiInstrument:
    def __init__(self, no_of_positions=120):
        self.no_of_positions = no_of_positions
        self.playing_notes = set()
        self.stopping_notes = set()

    # Call this to dispatch midi messages
    def update(self):
        messages_dict = {}
        for note in self.stopping_notes:
            messages_dict[str(note.position)] = [note.position, 0, 0]
        for note in self.playing_notes:
            if str(note.position) in messages_dict:
                messages_dict[str(note.position)][1] += note.volume
            else:
                messages_dict[str(note.position)] = [note.position, note.volume, 0]
            if messages_dict[str(note.position)][2] > 112:
                messages_dict[str(note.position)][2] = 112
        for message in messages_dict.values():
            if message[1] > 0:
                print "note on {}".format(message)
                midi_Output.note_on(message[0], velocity=message[1], channel=message[2])
            else:
                print "note off {}".format(message)
                midi_Output.note_off(message[0], velocity=0, channel=message[2])
        self.stopping_notes = set()

    # Adds a chord or note to start playing. Will play once update called and until stop called.
    def play(self, obj):
        if isinstance(obj, Chord):
            for note in obj.notes:
                self.play(note)
        else:
            self.playing_notes.add(obj)

    # Stop playing a note or chord. Will take effect once update called.
    def stop(self, obj):
        if isinstance(obj, Chord):
            for note in obj.notes:
                self.stop(note)
        elif obj in self.playing_notes:
            self.playing_notes.remove(obj)
            self.stopping_notes.add(obj)

    # Stop playing everything
    def stop_all(self):
        self.stopping_notes.update(self.playing_notes)
        self.playing_notes = set()


# noinspection PyClassHasNoInit
class Key:
    C = 0
    C_Sharp = 1
    D = 2
    D_Sharp = 3
    E = 4
    F = 5
    F_Sharp = 6
    G = 7
    G_Sharp = 8
    A = 9
    A_Sharp = 10
    B = 11


# Represents a note
class Note:
    def __init__(self, position, volume=112):
        self.position = position
        self.volume = volume


# Represents a chord
class Chord:
    # These lists are positions within a scale. [0, 2, 4] is first, third and fifth which is a regular triad
    triad = [0, 2, 4]
    triad_octave = [0, 2, 4, 7]
    suspended_second = [0, 2, 3]
    suspended_fourth = [0, 2, 5]
    seventh = [0, 2, 4, 7]
    seventh_octave = [0, 2, 4, 6, 7]
    sixth = [0, 2, 4, 5, 7]

    all = [triad, triad_octave, suspended_second, suspended_fourth, seventh, seventh_octave, sixth]

    def __init__(self, notes):
        self.notes = notes

    def add_stress(self, note):
        self.notes.append(note)


# Represents a scale
class Scale:
    major = [0, 2, 4, 5, 7, 9, 11]
    minor = [0, 2, 3, 5, 7, 8, 10]
    minor_pentatonic = [0, 3, 5, 7, 10]
    minor_blues = [0, 3, 5, 6, 7, 10]

    all = [major, minor, minor_pentatonic, minor_blues]

    # Make a new scale with a scale passed to it (e.g. scale = Scale(minor_blues))
    def __init__(self, scale, key=Key.C, base_octave=3):
        self.scale = scale
        self.length = len(scale)
        self.base_octave = base_octave
        self.key = key

    def interval_to_position(self, interval):
        return self.key + self.scale[interval % self.length] + 12 * (interval / self.length + self.base_octave)

    # Get a note from this scale starting with a given interval from the root (0, 1, 2, 3 etc.)
    def note(self, interval):
        position = self.interval_to_position(interval)
        return Note(position)

    # Get a chord from this scale starting with a given interval from the root (0, 1, 2, 3 etc.) Set the chord type
    # using intervals (e.g. chord = scale.chord(0, intervals=Chord.triad) gives the root triad. Chords always in key!)
    def chord(self, interval, intervals=Chord.triad):
        positions = map(lambda i: self.interval_to_position(interval + i), intervals)
        return Chord(map(Note, positions))

    # Go up by number of octaves
    def change_octave(self, by):
        self.base_octave = self.base_octave + by
