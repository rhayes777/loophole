import mido
from Queue import Queue
import music
from threading import Thread
import logging

instrument = music.MidiInstrument()
queue = Queue()


# noinspection PyClassHasNoInit
class Command:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    pitch_bend = "pitch_bend"
    set_included_channels = "set_included_channels"


def play_midi_file(name='big-blue.mid'):
    # noinspection PyUnresolvedReferences
    port = mido.open_output()

    included_channels = []

    mid = mido.MidiFile("media/{}".format(name))
    for msg in mid.play():
        if not queue.empty():
            command = queue.get()
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


def play_midi_file_on_new_thread(name='big-blue.mid'):
    t = Thread(target=play_midi_file, args=(name,))
    t.start()


def send_command(name, value):
    queue.put(Command(name, value))


def set_included_channels(channels):
    send_command(Command.set_included_channels, channels)
