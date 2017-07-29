import mido
from Queue import Queue
import music
from threading import Thread
import logging
import signal

instrument = music.MidiInstrument()


# noinspection PyClassHasNoInit
class Command:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    pitch_bend = "pitch_bend"
    set_included_channels = "set_included_channels"


class Track:
    def __init__(self, track_name="bicycle-ride.mid", is_looping=False, included_channels=()):
        self.track_name = track_name
        self.queue = Queue()
        self.is_stopping = False
        self.is_looping = is_looping
        self.included_channels = included_channels
        signal.signal(signal.SIGINT, self.stop)

    def play_midi_file(self):
        self.is_stopping = False
        # noinspection PyUnresolvedReferences
        port = mido.open_output()

        mid = mido.MidiFile("media/{}".format(self.track_name))
        for msg in mid.play():
            if self.is_stopping:
                break
            if not self.queue.empty():
                command = self.queue.get()
                if isinstance(command, Command):
                    if command.name == Command.pitch_bend:
                        instrument.pitch_bend(command.value)
                    elif command.name == Command.set_included_channels:
                        self.included_channels = command.value
            try:
                if msg.channel in self.included_channels:
                    port.send(msg)
            except AttributeError as e:
                logging.exception(e)
        if self.is_looping and not self.is_stopping:
            self.play_midi_file()

    def start(self):
        t = Thread(target=self.play_midi_file)
        t.start()

    def stop(self):
        self.is_stopping = True

    def send_command(self, name, value):
        self.queue.put(Command(name, value))

    def set_included_channels(self, channels):
        if isinstance(channels, int):
            channels = [channels]
        self.send_command(Command.set_included_channels, channels)
