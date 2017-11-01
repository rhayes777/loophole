import unittest
from Queue import Queue


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

    @classmethod
    def all(cls):
        return range(12)


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

    @classmethod
    def all_positions(cls, scale, key):
        s = Scale(scale, key, base_octave=0)
        interval = -7
        positions = []
        while True:
            pos = s.interval_to_position(interval)
            if pos > 127:
                break
            if pos >= 0:
                positions.append(pos)
            interval += 1
        return positions

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


keys_array = [set() for _ in range(128)]
for k in Key.all():
    for pos in Scale.all_positions(Scale.major, k):
        keys_array[pos].add(k)


def possible_keys(positions):
    key_set = set(range(12))
    for position in positions:
        key_set = key_set.intersection(keys_array[position])
    return key_set


class KeyTracker:
    def __init__(self, capacity=16):
        self.queue = Queue()
        self.key_queue = Queue()
        self.capacity = capacity

    def add_note(self, note):
        self.queue.put(note)
        if len(self.queue.queue) > self.capacity:
            self.queue.get()
        self.key_queue.put(self.keys)
        if len(self.key_queue.queue) > self.capacity:
            self.key_queue.get()

    @property
    def key(self):
        counts = {key: 0 for key in range(12)}
        for key_set in list(self.key_queue.queue):
            for key in key_set:
                counts[key] += 1
        return sorted(counts.iteritems(), key=lambda item: item[1])[-1][0]

    @property
    def keys(self):
        if len(self.queue.queue) == 0:
            return Key.C
        keys = []
        note_list = list(self.queue.queue)
        while len(keys) == 0:
            keys = possible_keys(note_list)
            note_list = note_list[1:]
        return keys


class KeySelectionTestCase(unittest.TestCase):
    def test_keys_array(self):
        self.assertTrue(Key.C in keys_array[0])
        self.assertTrue(Key.C not in keys_array[1])

    def test_positions(self):
        self.assertTrue(0 in Scale.all_positions(Scale.major, Key.C))
        self.assertTrue(1 not in Scale.all_positions(Scale.major, Key.C))
        self.assertTrue(1 in Scale.all_positions(Scale.major, Key.C_Sharp))

    def test_possible_keys(self):
        self.assertTrue(Key.C in possible_keys([0, 2, 4]))
        self.assertTrue(Key.C_Sharp not in possible_keys([0, 2, 4]))

        self.assertTrue(Key.C not in possible_keys([1, 3, 5]))
        self.assertTrue(Key.C_Sharp in possible_keys([1, 3, 5]))

    def test_key_tracker(self):
        key_tracker = KeyTracker()
        key_tracker.add_note(0)
        key_tracker.add_note(2)
        self.assertTrue(Key.C in key_tracker.keys)
        self.assertTrue(Key.G in key_tracker.keys)
        self.assertTrue(Key.C_Sharp not in key_tracker.keys)
        self.assertTrue(Key.D not in key_tracker.keys)

        key_tracker = KeyTracker(capacity=1)
        key_tracker.add_note(0)
        self.assertTrue(Key.C in key_tracker.keys)
        self.assertTrue(Key.D not in key_tracker.keys)

        key_tracker.add_note(2)
        self.assertTrue(Key.C in key_tracker.keys)
        self.assertTrue(Key.D in key_tracker.keys)

    def test_key_change(self):
        key_tracker = KeyTracker()
        key_tracker.add_note(0)
        self.assertTrue(Key.C in key_tracker.keys)
        self.assertTrue(Key.D not in key_tracker.keys)

        key_tracker.add_note(1)
        key_tracker.add_note(2)
        self.assertTrue(Key.C not in key_tracker.keys)
        self.assertTrue(Key.D in key_tracker.keys)


if __name__ == "__main__":
    unittest.main()
