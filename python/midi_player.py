import mido
from Queue import Queue
import music
from threading import Thread
import logging

instrument = music.MidiInstrument()


# noinspection PyClassHasNoInit
class Command:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    pitch_bend = "pitch_bend"
    set_included_channels = "set_included_channels"


class Track:
    def __init__(self, track_name):
        self.track_name = track_name
        self.queue = Queue()

    def play_midi_file(self):
        # noinspection PyUnresolvedReferences
        port = mido.open_output()

        included_channels = []

        mid = mido.MidiFile("media/{}".format(self.track_name))
        for msg in mid.play():
            if not self.queue.empty():
                command = self.queue.get()
                if isinstance(command, Command):
                    if command.name == Command.pitch_bend:
                        instrument.pitch_bend(command.value)
                    elif command.name == Command.set_included_channels:
                        included_channels = command.value
            try:
                if msg.channel in included_channels:
                    port.send(msg)
            except AttributeError as e:
                logging.exception(e)

    def start(self):
        t = Thread(target=self.play_midi_file)
        t.start()

    def send_command(self, name, value):
        self.queue.put(Command(name, value))

    def set_included_channels(self, channels):
        self.send_command(Command.set_included_channels, channels)
