import unittest
import sys
import mido


class ProcessMessage(object):
    def send(self):
        print self
        sys.stdout.flush()

    def __repr__(self):
        return self.__class__.__name__


class MidiMessage(ProcessMessage, object):
    def __init__(self, mido_message):
        self.mido_message = mido_message

    def __repr__(self):
        return "{},{}".format(super(MidiMessage, self).__repr__(), self.mido_message)


class TestCase(unittest.TestCase):
    def test_midi_to_string(self):
        self.assertEqual("MidiMessage,note_on channel=0 note=0 velocity=64 time=0",
                         str(MidiMessage(mido.Message(type="note_on"))))


if __name__ == "__main__":
    unittest.main()
