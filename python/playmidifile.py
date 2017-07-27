import mido

# noinspection PyUnresolvedReferences
port = mido.open_output()

mid = mido.MidiFile('big-blue.mid')
for msg in mid.play():
    port.send(msg)
