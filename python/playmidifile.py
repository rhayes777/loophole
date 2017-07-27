import mido
from Queue import Queue
import music
from threading import Thread

instrument = music.MidiInstrument()
queue = Queue()


# noinspection PyClassHasNoInit
class Command:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    pitch_bend = "pitch_bend"
    include_channel = "include_channel"
    disclude_channel = "disclude_channel"


def play_midi_file(name='big-blue.mid'):
    # noinspection PyUnresolvedReferences
    port = mido.open_output()

    discluded_channels = set()

    mid = mido.MidiFile(name)
    for msg in mid.play():
        if not queue.empty():
            command = queue.get()
            if command.name == Command.pitch_bend:
                instrument.pitch_bend(command.value)
            elif command.name == Command.disclude_channel:
                discluded_channels.add(command.value)
            elif command.name == Command.include_channel:
                discluded_channels.remove(command.value)
        if msg.channel not in discluded_channels:
            port.send(msg)


def play_midi_file_on_new_thread(name='big-blue.mid'):
    t = Thread(target=play_midi_file, args=(name,))
    t.start()


def send_command(name, value):
    queue.put(Command(name, value))
