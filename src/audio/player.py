import mido
from Queue import Queue
from threading import Thread
import logging
from datetime import datetime
import os
import music

mido.set_backend('mido.backends.pygame')

path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))

# noinspection PyUnresolvedReferences
input_names = mido.get_output_names()

REFACE = 'reface DX'
MPX = 'MPX16'
SIMPLE_SYNTH = 'SimpleSynth virtual input'

CHANNEL_PARTITION = 8

VOLUME_MAX = 1.0
VOLUME_MIN = 0.0
VOLUME_DEFAULT = 1.0

TEMPO_SHIFT_MAX = 10
TEMPO_SHIFT_DEFAULT = 1
TEMPO_SHIFT_MIN = 0.1

PITCHWHEEL_MIN = -8191
PITCHWHEEL_DEFAULT = 0
PITCHWHEEL_MAX = 8191

simple_port = None

# TODO: Consider passing the key tracker only into select tracks
key_tracker = music.KeyTracker()


# noinspection PyClassHasNoInit
class InstrumentType:
    """Different types of midi instrument. The program number of each instrument ranges from n * 8 to (n + 1) * 8"""
    piano = 0
    chromatic_percussion = 1
    organ = 2
    guitar = 3
    bass = 4
    strings = 5
    ensemble = 6
    brass = 7
    reed = 8
    pipe = 9
    synth_lead = 10
    synth_pad = 11
    synth_effects = 12
    ethnic = 13
    percussive = 14
    sound_effects = 15

    instrument_type_dict = {"piano": piano,
                            "chromatic_percussion": chromatic_percussion,
                            "organ": organ,
                            "guitar": guitar,
                            "bass": bass,
                            "strings": strings,
                            "ensemble": ensemble,
                            "brass": brass,
                            "reed": reed,
                            "pipe": pipe,
                            "synth_lead": synth_lead,
                            "synth_pad": synth_pad,
                            "synth_effects": synth_effects,
                            "ethnic": ethnic,
                            "percussive": percussive,
                            "sound_effects": sound_effects}

    @staticmethod
    def with_name(name):
        return InstrumentType.instrument_type_dict[name]


# noinspection PyClassHasNoInit
class InstrumentGroup:
    """Different groups of midi instrument."""
    melodic = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    percussive = [1, 14, 15]
    all = range(15)

    instrument_group_dict = {"melodic": melodic, "percussive": percussive, "all": all}

    @staticmethod
    def with_name(name):
        return InstrumentGroup.instrument_group_dict[name]


def make_port(name):
    """
    Create a port with the given name, defaulting to the SimpleSynth port otherwise
    :param name: The name of the port
    :return: A port through which midi messages can be sent
    """
    for input_name in input_names:
        if name in input_name:
            name = input_name
    global simple_port
    try:
        # noinspection PyUnresolvedReferences
        return mido.open_output(name)
    except IOError:
        logging.warn("{} not found.".format(name))
        if simple_port is None:
            # noinspection PyUnresolvedReferences
            simple_port = mido.open_output()
        return simple_port


def note_on(channel=0, note=50, velocity=50):
    keys_port.send(mido.Message('note_on', channel=channel, note=note, velocity=velocity))


def set_program(channel=0, program=0):
    keys_port.send(mido.Message('program_change', program=program, time=0, channel=channel))


keys_port = make_port(REFACE)
drum_port = make_port(MPX)


class Intervals:
    """Class used to apply set of intervals to a note, using the most likely key"""

    def __init__(self, intervals):
        """

        :param intervals: A series of intervals. For example, [2, 4] would turn a note into a triad
        """
        self.intervals = intervals
        self.playing_notes = set()

    def __call__(self, msg):
        """

        :param msg: A midi note_on message
        :return: An array of midi messages
        """
        new_array = []

        for interval in self.intervals:
            new_msg = msg.copy()
            note = key_tracker.scale.position_at_interval(msg.note, interval)
            if 0 <= note <= 127:
                new_msg.note = note
                new_msg.time = 0
                new_array.append(new_msg)

                if new_msg.type == 'note_on':
                    self.playing_notes.add(new_msg.note)
                elif new_msg.type == 'note_off' and new_msg.note in self.playing_notes:
                    self.playing_notes.remove(new_msg.note)

        return new_array

    @property
    def note_offs(self):
        return map(lambda note: mido.Message('note_off', note=note, velocity=0), self.playing_notes)


class Channel(object):
    """Represents an individual midi channel through which messages are passed"""
    note_off = "note_off"
    note_on = "note_on"

    def __init__(self, number, volume=VOLUME_DEFAULT, fade_rate=1, note_on_listener=None):
        """

        :param number: The number of this channel (0-15)
        :param volume: The initial volume of this channel (0.0 - 1.0)
        :param fade_rate: The rate at which this channel should fade
        :param note_on_listener: A listener that is called every time a note_on is played by this channel
        """
        self.note_on_listener = note_on_listener
        self.listening_queue = None
        self.number = number
        # Decides which port output should be used depending on the channel number
        self.port = keys_port if number < CHANNEL_PARTITION else drum_port
        self.__volume = volume
        self.__volume_queue = Queue()
        self.fade_rate = fade_rate
        self.__fade_start = None
        self.__fade_start_queue = Queue()
        self.playing_notes = set()
        self.__intervals = None
        self.__intervals_queue = Queue()
        self.__program = 0
        self.__modulation = 0
        self.__pan = 63
        self.key_tracker = None

    @property
    def volume(self):
        while not self.__volume_queue.empty():
            self.__volume = self.__volume_queue.get()
        return self.__volume

    @volume.setter
    def volume(self, volume):
        self.fade_start = None
        self.__volume_queue.put(volume)

    @property
    def modulation(self):
        return self.__modulation

    @modulation.setter
    def modulation(self, modulation):
        self.__modulation = modulation
        self.port.send(mido.Message('control_change', channel=self.number, control=1, value=self.__modulation))

    @property
    def pan(self):
        return self.__pan

    @pan.setter
    def pan(self, pan):
        self.__pan = pan
        self.port.send(mido.Message('control_change', channel=self.number, control=10, value=self.__modulation))

    @property
    def fade_start(self):
        while not self.__fade_start_queue.empty():
            if self.__fade_start is None:
                self.__fade_start = datetime.now()
        return self.__fade_start

    @fade_start.setter
    def fade_start(self, fade_start):
        self.__fade_start = fade_start

    def fade(self):
        self.__fade_start_queue.put("start")

    @property
    def intervals(self):
        """The set of intervals currently applied to notes played on this channel"""
        while not self.__intervals_queue.empty():
            if self.__intervals is not None:
                for note_off in self.__intervals.note_offs:
                    note_off.channel = self.number
                    self.port.send(note_off)
            self.__intervals = self.__intervals_queue.get()
        return self.__intervals

    @intervals.setter
    def intervals(self, intervals):
        if isinstance(intervals, list):
            intervals = Intervals(intervals)
        self.__intervals_queue.put(intervals)

    @property
    def program(self):
        """The program (i.e. instrument) of this channel"""
        return self.__program

    @program.setter
    def program(self, program):
        self.__program = program
        self.port.send(mido.Message('program_change', program=self.__program, time=0, channel=self.number))

    @property
    def instrument_type(self):
        """The type of instrument (see InstrumentType above)"""
        return self.program / 8

    @instrument_type.setter
    def instrument_type(self, instrument_type):
        if isinstance(instrument_type, str) or isinstance(instrument_type, unicode):
            instrument_type = InstrumentType.with_name(instrument_type)
        if 0 <= instrument_type < 16:
            self.program = 8 * instrument_type + self.instrument_version

    @property
    def instrument_version(self):
        """The version of the instrument. Each instrument has 8 versions."""
        return self.program % 8

    @instrument_version.setter
    def instrument_version(self, instrument_version):
        if 0 <= instrument_version < 8:
            self.program = 8 * self.instrument_type + instrument_version

    def pitch_bend(self, value):
        """
        Send a pitch bend to this channel
        :param value: The value of the pitch bend
        """
        self.port.send(mido.Message('pitchwheel', pitch=value, time=0, channel=self.number))

    def send_message(self, msg):
        """
        Apply effects and dispatch a midi message
        :param msg: a midi message
        """

        try:
            # True if a fade out is in progress
            if self.fade_start is not None:
                # How long has the fade been occurring?
                seconds = (datetime.now() - self.fade_start).total_seconds()
                self.volume *= (1 - self.fade_rate * seconds)
                if self.volume < 0:
                    self.volume = 0
                    self.fade_start = None

            if hasattr(msg, 'velocity'):
                msg.velocity = int(self.volume * msg.velocity)

            if self.key_tracker and hasattr(msg, "note"):
                # Update the key tracker
                self.key_tracker.add_note(msg.note)

            if hasattr(msg, 'velocity') and self.intervals is not None:
                msgs = self.intervals(msg)
            else:
                msgs = [msg]

            for msg in msgs:
                if self.listening_queue is not None and msg.type == "note_on":
                    self.listening_queue.put(msg)
                if self.is_percussive:
                    msg.channel = 10
                # Actually send the midi message
                self.port.send(msg)
            if hasattr(msg, 'type'):
                # Check if it was a note message
                if msg.type == Channel.note_on:
                    # Keep track of notes that are currently playing
                    self.playing_notes.add(msg.note)
                    if self.note_on_listener is not None:
                        self.note_on_listener(msg)
                elif msg.type == Channel.note_off and msg.note in self.playing_notes:
                    self.playing_notes.remove(msg.note)
        except AttributeError as e:
            logging.exception(e)
        except ValueError as e:
            logging.exception(e)

    def stop_playing_notes(self):
        """Stop all currently playing notes"""
        for note in self.playing_notes.copy():
            self.stop_note(note)

    def stop_note(self, note):
        """
        Stop a specific note
        :param note: The midi position of the note
        """
        # noinspection PyTypeChecker
        self.send_message(mido.Message(type=Channel.note_off, velocity=0, note=note))

    def stop_all_notes(self):
        for i in range(128):
            self.port.send(mido.Message(type="note_off", velocity=0, channel=self.number, note=i))

    @property
    def is_percussive(self):
        return self.instrument_type == InstrumentType.percussive


class Track(Thread):
    """Represents a midi song loaded from a file"""

    def __init__(self, file_path="../media/channels_test.mid", is_looping=False):
        super(Track, self).__init__()
        self.filename = file_path
        self.is_stopping = False
        self.is_looping = is_looping
        self.mid = mido.MidiFile(file_path)
        self.original_tempo = self.mid.ticks_per_beat
        self.channels = map(Channel, range(0, 16))
        for track in self.mid.tracks:
            msg = track[0]
            if msg.type == "program_change":
                self.channels[msg.channel].instrument_type = msg.program
        for channel in self.channels_with_instrument_group("melodic"):
            channel.key_tracker = key_tracker
        self.__tempo_shift = TEMPO_SHIFT_DEFAULT
        self.__tempo_shift_queue = Queue()

    @property
    def tempo_shift(self):
        return self.__tempo_shift

    @tempo_shift.setter
    def tempo_shift(self, tempo_shift):
        self.mid.ticks_per_beat = tempo_shift * self.original_tempo
        self.__tempo_shift = tempo_shift

    def channels_with_instrument_type(self, instrument_type):
        """
        Returns all channels associated with instruments of a particular type
        :param instrument_type: The string name or integer number of the instrument type (see InstrumentType)
        :return: A list of channels
        """
        if isinstance(instrument_type, str):
            instrument_type = InstrumentType.with_name(instrument_type)
        return filter(lambda c: c.instrument_type == instrument_type, self.channels)

    def channels_with_instrument_group(self, instrument_group):
        """
            Returns all channels associated with instruments of a particular group
            :param instrument_group: The string name or integer number of the instrument group (see InstrumentGroup)
            :return: A list of channels
            """
        channels = []
        for instrument_type in InstrumentGroup.with_name(instrument_group):
            channels.extend(self.channels_with_instrument_type(instrument_type))
        return channels

    def run(self):
        """Play the midi file (call start() to run on new thread)"""
        self.is_stopping = False
        play = self.mid.play(meta_messages=True)

        while True:

            # Take midi messages from a generator
            for msg in play:

                if self.is_stopping:
                    break

                try:
                    if isinstance(msg, mido.MetaMessage):
                        continue
                    # Send a message to its assigned channel
                    self.channels[msg.channel].send_message(msg)
                except AttributeError as e:
                    logging.exception(e)
                except IndexError as e:
                    logging.exception(e)

            if self.is_looping and not self.is_stopping:
                play = self.mid.play(meta_messages=True)
                continue
            break
        for channel in self.channels:
            channel.stop_all_notes()

    # noinspection PyUnusedLocal
    def stop(self, *args):
        """Stops the song by breaking the loop"""
        self.is_stopping = True
