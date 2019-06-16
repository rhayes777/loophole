import time

import mido


def set_time(new_time):
    time.time = lambda: new_time


class TimeMessage(object):
    def __init__(self, mido_message):
        self.mido_message = mido_message
        self.creation_time = time.time()

    @property
    def play_time(self):
        return self.creation_time + self.mido_message.time

    @classmethod
    def from_mido(cls, mido_message):
        return cls(mido_message)


class NoteQueue(object):
    def __init__(self):
        self.queued_notes = []

    def append(self, message):
        self.queued_notes.append(message)

    @property
    def late_notes(self):
        return [note for note in self.queued_notes if note.play_time <= time.time()]

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
        time_message = TimeMessage.from_mido(mido_message)
        assert time_message.play_time == 1.1
        assert time_message.creation_time == 1.0

    def test_note_queue(self):
        note_queue = NoteQueue()
        set_time(0.0)

        mido_0 = mido.Message(type="note_on", time=0.0)
        mido_1 = mido.Message(type="note_on", time=1.0)
        mido_15 = mido.Message(type="note_on", time=1.5)

        time_0 = TimeMessage(mido_0)
        time_1 = TimeMessage(mido_1)
        time_15 = TimeMessage(mido_15)

        note_queue.append(time_0)
        note_queue.append(time_1)
        note_queue.append(time_15)

        assert note_queue.late_notes == [time_0]
        set_time(1.0)
        assert note_queue.late_notes == [time_0, time_1]

        late_notices = note_queue.pop_late_notes()
        assert late_notices == [time_0, time_1]
        assert note_queue.queued_notes == [time_15]

        set_time(2.0)
        late_notices = note_queue.pop_late_notes()
        assert late_notices == [time_15]
        assert note_queue.queued_notes == []
