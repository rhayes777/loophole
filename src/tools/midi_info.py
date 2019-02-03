#!/usr/bin/env python

import mido
import sys

if len(sys.argv) < 2:
    print("Usage: midi_info.py example.mid")
    exit(1)

name = sys.argv[1]

f = mido.MidiFile(name)

no_tracks = len(f.tracks)

messages = [message for track in f.tracks for message in track]
channels = {message.channel for message in messages if hasattr(message, "channel")}

print("{} has {} tracks on channels: {}".format(name, no_tracks, " ".join(map(str, channels))))
