import time

import mido


def set_time(new_time):
    time.time = lambda: new_time


class TimeMessage(object):
    def __init__(self, mido_message, message_time):
        self.mido_message = mido_message
        self.time = message_time


class Converter(object):
    def mido_to_time(self, mido_message):
        return TimeMessage(mido_message, mido_message.time + time.time())


class NoteQueue(object):
    def __init__(self):
        self.queued_notes = []

    def append(self, message):
        self.queued_notes.append(message)

    @property
    def late_notes(self):
        return [note for note in self.queued_notes if note.time <= time.time()]

    def pop_late_notes(self):
        late_notes = self.late_notes
        for note in late_notes:
            self.queued_notes.remove(note)
        return late_notes


class TestCase(object):

    def test_convert_to_time(self):
        set_time(1.0)
        mido_message = mido.Message(type="note_on", time=0.1)
        # noinspection PyTypeChecker
        time_message = Converter().mido_to_time(mido_message)
        assert time_message.time == 1.1

    def test_note_queue(self):
        note_queue = NoteQueue()
        message_0 = TimeMessage(None, message_time=0.0)
        message_1 = TimeMessage(None, message_time=1.0)
        message_15 = TimeMessage(None, message_time=1.5)

        note_queue.append(message_0)
        note_queue.append(message_1)
        note_queue.append(message_15)

        set_time(0.0)
        assert note_queue.late_notes == [message_0]
        set_time(1.0)
        assert note_queue.late_notes == [message_0, message_1]

        late_notices = note_queue.pop_late_notes()
        assert late_notices == [message_0, message_1]
        assert note_queue.queued_notes == [message_15]

        set_time(2.0)
        late_notices = note_queue.pop_late_notes()
        assert late_notices == [message_15]
        assert note_queue.queued_notes == []
