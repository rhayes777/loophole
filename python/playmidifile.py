import mido


def play_midi_file(name='big-blue.mid'):
    # noinspection PyUnresolvedReferences
    port = mido.open_output()

    mid = mido.MidiFile(name)
    for msg in mid.play():
        port.send(msg)
