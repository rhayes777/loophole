import mido
from Queue import Queue
import music
from threading import Thread

instrument = music.MidiInstrument()
queue = Queue()


def play_midi_file(name='big-blue.mid'):
    # noinspection PyUnresolvedReferences
    port = mido.open_output()

    mid = mido.MidiFile(name)
    for msg in mid.play():
        if not queue.empty():
            instrument.pitch_bend(queue.get())
        port.send(msg)


def play_midi_file_on_new_thread(name='big-blue.mid'):
    t = Thread(target=play_midi_file, args=(name,))
    t.start()
