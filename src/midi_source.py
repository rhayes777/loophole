from time import sleep
from threading import Thread
from Queue import Queue
import iterators


class TrackThread(Thread):
    def __init__(self, track, queue):
        super(TrackThread, self).__init__()
        self.track = track
        self.queue = queue

    def run(self):
        for item in self.track:
            self.queue.put(item)


class HeartbeatThread(Thread):
    def __init__(self, queue, interval=0.05):
        super(HeartbeatThread, self).__init__()
        self.queue = queue
        self.interval = interval

    def run(self):
        while True:
            ls = self.queue.queue
            if len(ls) > 0 and ls[-1] is stop:
                break
            self.queue.put(iterators.heartbeat)
            sleep(self.interval)


class Stop(object):
    __stop = None

    def __new__(cls, *args, **kwargs):
        if Stop.__stop is None:
            Stop.__stop = object.__new__(Stop)
        return Stop.__stop


stop = Stop()


class MidiSource(object):
    def __init__(self, track, interval=0.05):
        self.queue = Queue()
        self.heartbeat_thread = HeartbeatThread(self.queue, interval)
        self.track_thread = TrackThread(track, self.queue)

    def __iter__(self):
        self.track_thread.start()
        self.heartbeat_thread.start()
        return self

    def next(self):
        if not self.queue.empty():
            message = self.queue.get()
            if message is stop:
                raise StopIteration()
            return self.queue.get()
        sleep(0.01)
        return self.next()


class TestCase(object):
    def test_heartbeats(self):
        def track():
            sleep(0.3)
            yield Stop()

        midi_source = MidiSource(track(), interval=0.05)
        assert 5 == len([n for n in midi_source])
