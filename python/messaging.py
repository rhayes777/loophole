import unittest
import sys
import mido


class ProcessMessage(object):
    def send(self):
        print self
        sys.stdout.flush()

    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def from_string(cls, as_string):
        as_array = as_string.split(",")
        class_name = as_array[0]
        return globals()[class_name](*as_array[1:])


class MidiMessage(ProcessMessage, object):
    def __init__(self, mido_message):
        if isinstance(mido_message, str):
            self.mido_message = mido.Message.from_str(mido_message)
        else:
            self.mido_message = mido_message

    def __repr__(self):
        return "{},{}".format(super(MidiMessage, self).__repr__(), self.mido_message)

    def __eq__(self, other):
        return self.mido_message == other.mido_message


class MidiTestCase(unittest.TestCase):
    def setUp(self):
        self.as_string = "MidiMessage,note_on channel=0 note=0 velocity=64 time=0"
        self.as_message = MidiMessage(mido.Message(type="note_on"))

    def test_midi_to_string(self):
        self.assertEqual(self.as_string, str(self.as_message))

    def test_from_string(self):
        self.assertEqual(self.as_message, ProcessMessage.from_string(self.as_string))


if __name__ == "__main__":
    unittest.main()
