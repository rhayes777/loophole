from mido import MidiFile, Message
import sys

original_track_names = sorted(sys.argv[2:])
new_track_name = sys.argv[1]

original_files = map(lambda tn: MidiFile(tn), original_track_names)

new_file = MidiFile()
new_file.ticks_per_beat = original_files[0].ticks_per_beat

for n, original_file in enumerate(original_files):
    track = original_file.tracks[0]
    for message in track:
        try:
            message.channel = n
        except AttributeError:
            pass

    new_file.tracks.append([Message('program_change', program=12, time=0)] + track)

new_file.save(new_track_name)
