#!/usr/bin/env python

import sys

import mido
import combiner

if len(sys.argv) < 2:
    print("Usage: midi_info.py example.mid")
    exit(1)

name = sys.argv[1]

f = mido.MidiFile(name)

no_tracks = len(f.tracks)

messages = [message for track in f.tracks for message in track]

instruments = {combiner.instrument_map[message.program + 1] for message in messages if message.type == "program_change"}
channels = {message.channel + 1 for message in messages if hasattr(message, "channel")}

print("{} has {} tracks on channels: {}".format(name, no_tracks, " ".join(map(str, channels))))
print("It instruments:\n{}".format("\n".join(instruments)))
