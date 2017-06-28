import logging
import pyaudio
import sys
import wave
from threading import Thread
import numpy
import struct
from Queue import Queue
import os

# http://playground.arduino.cc/Interfacing/Python

TRACK3_drums = "TRACK3_drums.wav"
TRACK3_bass = "TRACK3_bass.wav"
TRACK3_guitar_keys = "TRACK3_guitar_keys.wav"
TRACK3_noises = "TRACK3_noises.wav"

WHITE_sitar = "WHITE_sitar.wav"
WHITE_guitar = "WHITE_sitar.wav"
WHITE_percnsub = "WHITE_percnsub.wav"
WHITE_atmos = "WHITE_atmos.wav"

KLAXON_MIXDOWN_KLAXON1 = "KLAXON_MIXDOWN_KLAXON1.wav"
KLAXON_MIXDOWN_KLAXON2 = "KLAXON_MIXDOWN_KLAXON2.wav"
KLAXON_MIXDOWN_KLAXON3 = "KLAXON_MIXDOWN_KLAXON3.wav"
KLAXON_MIXDOWN_KLAXON4 = "KLAXON_MIXDOWN_KLAXON4.wav"

KOTO_bass = "KOTO_bass.wav"
KOTO_lead = "KOTO_lead.wav"
KOTO_inst = "KOTO_inst.wav"
KOTO_drums = "KOTO_drums.wav"

LONG_AMBIENT_PART1 = "LONG_AMBIENT_PART1.wav"
LONG_AMBIENT_PART2 = "LONG_AMBIENT_PART2.wav"
LONG_AMBIENT_PART3 = "LONG_AMBIENT_PART3.wav"

track3 = [
    TRACK3_drums,
    TRACK3_bass,
    TRACK3_guitar_keys,
    TRACK3_noises,
    LONG_AMBIENT_PART1
]

koto = [
    KOTO_bass,
    KOTO_lead,
    KOTO_inst,
    KOTO_drums,
    LONG_AMBIENT_PART2
]

white = [
    WHITE_atmos,
    WHITE_guitar,
    WHITE_percnsub,
    WHITE_sitar,
    LONG_AMBIENT_PART3
]

klaxon = [
    KLAXON_MIXDOWN_KLAXON1,
    KLAXON_MIXDOWN_KLAXON2,
    KLAXON_MIXDOWN_KLAXON3,
    KLAXON_MIXDOWN_KLAXON4
]

track_dict = {"morning": white,
              "afternoon": track3,
              "evening": koto,
              "night": track3,
              "koto": koto,
              "white": white,
              "klaxon": klaxon}

# Instantiate PyAudio.
p = pyaudio.PyAudio()
should_play = True
is_sample_tapering = True

queues = []

number_of_ready_loops = 0

CHUNK_SIZE = 512
FADE_OUT_RATE = 0.04

dir = os.path.dirname(__file__)


def play_track(track_name, number_of_channels):
    audio_samples = track_dict[track_name]

    for n in range(0, number_of_channels):
        logging.info("Playing {}".format(audio_samples[n]))
        loop_wav_on_new_thread(audio_samples[n], number_of_channels)


# logging.basicConfig(level=logging.DEBUG)

class Loop:
    def __init__(self, wav_filename, no_of_loops_required, chunk_size=CHUNK_SIZE, volume=1, number_of_times_to_loop=-1,
                 fade_out_rate=FADE_OUT_RATE):
        self.number_of_times_to_loop = number_of_times_to_loop
        self.wav_filename = wav_filename
        self.chunk_size = chunk_size
        self.volume = volume
        self.fade_out_rate = fade_out_rate
        self.no_of_loops_required = no_of_loops_required
        self.queue = Queue()

    def start(self):

        global should_play
        global number_of_ready_loops

        should_play = True

        try:
            self.log('Trying to play file ' + self.wav_filename)
            wf = wave.open(os.path.join(dir, '../samples/{}'.format(self.wav_filename)), 'rb')
        except IOError as ioe:
            sys.stderr.write('IOError on file ' + self.wav_filename + '\n' + \
                             str(ioe) + '. Skipping.\n')
            return
        except EOFError as eofe:
            sys.stderr.write('EOFError on file ' + self.wav_filename + '\n' + \
                             str(eofe) + '. Skipping.\n')
            return

        self.log("framerate = {}".format(wf.getframerate()))
        self.log("sampwidth = {}".format(wf.getsampwidth()))
        self.log("nchannels = {}".format(wf.getnchannels()))

        self.log("opening stream")

        # Open stream.
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        self.log("getting data")

        data = wf.readframes(self.chunk_size)
        self.log("data got")

        loop_number = 0

        number_of_ready_loops += 1
        while number_of_ready_loops < self.no_of_loops_required:
            pass

        while should_play:
            if not self.queue.empty():
                new_volume = self.queue.get()
                if new_volume >= self.volume:
                    self.volume = new_volume
                else:
                    self.volume -= self.fade_out_rate
                    if self.volume < 0:
                        self.volume = 0

            arr = self.volume * numpy.fromstring(data, numpy.int16)
            data = struct.pack('h' * len(arr), *arr)

            stream.write(data)

            data = wf.readframes(self.chunk_size)

            if data == '':  # If file is over then rewind.
                if self.number_of_times_to_loop > 0:
                    loop_number += 1
                    if loop_number == self.number_of_times_to_loop:
                        should_play = False
                wf.rewind()
                data = wf.readframes(self.chunk_size)

        self.log("sample finished")

        # Stop stream.
        self.log("stopping stream")
        stream.stop_stream()
        self.log("closing stream")
        stream.close()

    def log(self, message):
        logging.debug("{}: {}".format(self.wav_filename, message))


def loop_wav_on_new_thread(name, no_of_queues_required=0, no_of_times_to_loop=-1, fade_out_rate=FADE_OUT_RATE):
    t = Thread(target=loop_wav, args=(name, no_of_queues_required, no_of_times_to_loop, fade_out_rate,))
    t.start()


def loop_wav(name, no_of_queues_required, no_of_times_to_loop, fade_out_rate):
    loop = Loop(name, no_of_queues_required, number_of_times_to_loop=no_of_times_to_loop, fade_out_rate=fade_out_rate)
    if no_of_queues_required:
        logging.debug("appending queue to queues")
        queues.append(loop.queue)
        logging.debug("new size = {}".format(len(queues)))
    logging.debug("starting loop...")
    loop.start()