#!/usr/bin/env python

import mido
import sys

f = mido.MidiFile(sys.argv[1])
f.print_tracks()
