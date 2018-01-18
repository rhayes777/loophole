import unittest
import sys
import mido
import json


def read():
    while True:
        line = sys.stdin.readline()
        if line is None:
            break
        yield Message.from_string(line)


def write(message):
    print message
    sys.stdout.flush()


class Message(object):
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{},{}".format(self.__class__.__name__,
                              json.dumps({key: str(value) for key, value in self.__dict__.iteritems()}))

    @classmethod
    def from_string(cls, as_string):
        as_array = as_string.split(",")
        class_name = as_array[0]
        return globals()[class_name](**json.loads(as_array[1]))


class MidiMessage(Message, object):
    def __init__(self, mido_message):
        if isinstance(mido_message, str) or isinstance(mido_message, unicode):
            self.mido_message = mido.Message.from_str(mido_message)
        else:
            self.mido_message = mido_message

    def __eq__(self, other):
        return self.mido_message == other.mido_message


class ButtonMessage(Message, object):
    def __init__(self, button):
        self.button = button

    def __eq__(self, other):
        return self.button == other.button


class MidiTestCase(unittest.TestCase):
    def setUp(self):
        self.as_string = 'MidiMessage,{"mido_message": "note_on channel=0 note=0 velocity=64 time=0"}'
        self.as_message = MidiMessage(mido.Message(type="note_on"))

    def test_midi_to_string(self):
        self.assertEqual(self.as_string, str(self.as_message))

    def test_from_string(self):
        self.assertEqual(self.as_message, Message.from_string(self.as_string))


class ButtonTestCase(unittest.TestCase):
    def setUp(self):
        self.as_string = 'ButtonMessage,{"button": "up"}'
        self.as_message = ButtonMessage("up")

    def test_midi_to_string(self):
        self.assertEqual(self.as_string, str(self.as_message))

    def test_from_string(self):
        self.assertEqual(self.as_message, Message.from_string(self.as_string))


if __name__ == "__main__":
    unittest.main()
