import time

import mido
import pytest


def set_time(new_time):
    time.time = lambda: new_time


@pytest.fixture(autouse=True)
def reset_last_time():
    TimeMessage.last_time = None


class TimeMessage(object):
    last_time = None

    def __init__(self, mido_message, lag=0.0):
        if TimeMessage.last_time is None or mido_message.time > 0.0:
            TimeMessage.last_time = time.time()
        self.mido_message = mido_message
        self.creation_time = TimeMessage.last_time
        self.lag = lag

    @property
    def play_time(self):
        return self.creation_time + self.mido_message.time + self.lag

    def as_instant_mido_message(self):
        instant_message = self.mido_message.copy()
        instant_message.time = 0.0
        return instant_message


class NoteQueue(object):
    def __init__(self):
        self.queued_notes = []

    def append(self, message):
        self.queued_notes.append(message)

    @property
    def late_notes(self):
        return [note for note in self.queued_notes if note.play_time <= time.time()]

    def pop_late_notes(self):
        # TODO: make NoteQueue operations more efficient
        late_notes = self.late_notes
        for note in late_notes:
            self.queued_notes.remove(note)
        return late_notes


# noinspection PyTypeChecker
class TestCase(object):
    def test_convert_to_time(self):
        set_time(1.0)
        mido_message = mido.Message(type="note_on", time=0.1)
        # noinspection PyTypeChecker
        time_message = TimeMessage(mido_message)
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

        assert time_0.play_time == 0.0
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

    # noinspection PyTypeChecker
    def test_lag(self):
        set_time(0.0)

        mido_0 = mido.Message(type="note_on", time=0.0)

        assert TimeMessage(mido_0).play_time == 0.0
        assert TimeMessage(mido_0, lag=0.1).play_time == 0.1
        assert TimeMessage(mido_0, lag=1.0).play_time == 1.0

    def test_as_instant_mido_message(self):
        mido_message = mido.Message(type="note_on", time=0.1)
        # noinspection PyTypeChecker
        instant_message = TimeMessage(mido_message).as_instant_mido_message()
        assert instant_message is not mido_message
        assert instant_message.type == "note_on"
        assert instant_message.time == 0.0

    # noinspection PyTypeChecker
    def test_last_time(self):
        set_time(0.0)
        one = TimeMessage(
            mido.Message(
                type="note_on",
                time=0.0
            )
        )
        set_time(0.1)
        two = TimeMessage(
            mido.Message(
                type="note_on",
                time=0.0
            )
        )

        assert one.play_time == two.play_time


def main():
    from audio import audio
    from os import path
    import pygame

    clock = pygame.time.Clock()

    directory = path.dirname(path.realpath(__file__))
    note_queue = NoteQueue()

    track = audio.Track(
        "{}/media/audio/{}".format(
            directory,
            "bicycle-ride.mid"
        ),
        is_looping=True,
        message_read_listener=lambda midi_message: note_queue.append(
            TimeMessage(midi_message)),
        play_notes=False,
        play_any=False
    )

    track.start()

    while True:
        for note in note_queue.pop_late_notes():
            track.send_message(note.as_instant_mido_message())

        clock.tick(24)


if __name__ == "__main__":
    main()
