import mido
from Queue import Queue
from threading import Thread
import logging
from datetime import datetime
import os
import music

path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))

# noinspection PyUnresolvedReferences
input_names = mido.get_output_names()

REFACE = 'reface DX'
MPX = 'MPX16'
SIMPLE_SYNTH = 'SimpleSynth virtual input'

CHANNEL_PARTITION = 8

simple_port = None

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


keys_port = make_port(REFACE)
drum_port = make_port(MPX)


class Command:
    """Contains a key value pair that can be passed into a queue to invoke a change in state of a channel"""

    def __init__(self, name, value=None):
        """

        :param name: The name of the command (e.g. command.add_effect)
        :param value: The value of the command (optional)
        """
        self.name = name
        self.value = value

    def __repr__(self):
        return "<Command {} = {}>".format(self.name, self.value)

    def __str__(self):
        return self.__repr__()

    add_effect = "add_effect"
    remove_effect = "remove_effect"
    pitch_bend = "pitch_bend"
    volume = "volume"
    fade_out = "fade_out"
    stop = "stop"
    tempo_change = "tempo_change"


class Intervals:
    """Class used to apply set of intervals to a note, using the most likely key"""
    def __init__(self, intervals):
        """

        :param intervals: A series of intervals. For example, [2, 4] would turn a note into a triad
        """
        self.intervals = intervals

    def __call__(self, msg):
        """

        :param msg: A midi note_on message
        :return: An array of midi messages
        """
        new_array = [msg]

        for interval in self.intervals:
            new_msg = msg.copy()
            note = key_tracker.scale.position_at_interval(msg.note, interval)
            if 0 <= note <= 127:
                new_msg.note = note
                new_msg.time = 0
                new_array.append(new_msg)

        return new_array


class Channel(object):
    """Represents an individual midi channel through which messages are passed"""
    note_off = "note_off"
    note_on = "note_on"

    def __init__(self, number, volume=1.0, fade_rate=1, note_on_listener=None):
        """

        :param number: The number of this channel (0-15)
        :param volume: The initial volume of this channel (0.0 - 1.0)
        :param fade_rate: The rate at which this channel should fade
        :param note_on_listener: A listener that is called every time a note_on is played by this channel
        """
        self.note_on_listener = note_on_listener
        self.message_send_listener = None
        self.number = number
        # Decides which port output should be used depending on the channel number
        self.port = keys_port if number < CHANNEL_PARTITION else drum_port
        self.volume = volume
        self.fade_rate = fade_rate
        self.queue = Queue()
        self.fade_start = None
        self.playing_notes = []
        self.__intervals = None
        self.__intervals_queue = Queue()
        self.__program = 0

    @property
    def intervals(self):
        """The set of intervals currently applied to notes played on this channel"""
        while not self.__intervals_queue.empty():
            self.__intervals = self.__intervals_queue.get()
        return self.__intervals

    @intervals.setter
    def intervals(self, intervals):
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

    def process_waiting_commands(self):
        # Are there any commands waiting?
        while not self.queue.empty():
            command = self.queue.get()
            # Volume changing command. Overrides current fades
            if command.name == Command.volume:
                self.volume = command.value
                self.fade_start = None
            # Fade out command. Fade out occurs constantly until silent or overridden by volume change
            elif command.name == Command.fade_out:
                # Fade out command has no effect if fadeout already underway
                if self.fade_start is None:
                    # When did the fadeout start?
                    self.fade_start = datetime.now()

    # Send a midi message to this channel
    def send_message(self, msg):

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

            if hasattr(msg, 'velocity') and self.intervals is not None:
                msgs = self.intervals(msg)
            else:
                msgs = [msg]

            for msg in msgs:
                if callable(self.message_send_listener):
                    self.message_send_listener(msg)
                # Actually send the midi message
                self.port.send(msg)
                if hasattr(msg, "note"):
                    # Update the key tracker
                    key_tracker.add_note(msg.note)
            if hasattr(msg, 'type'):
                # Check if it was a note message
                if msg.type == Channel.note_on:
                    # Keep track of notes that are currently playing
                    self.playing_notes.append(msg.note)
                    self.playing_notes.sort()
                    if self.note_on_listener is not None:
                        self.note_on_listener(msg)
                elif msg.type == Channel.note_off:
                    self.playing_notes.remove(msg.note)
                elif msg.type == Channel.program_change:
                    self.program = msg.program
        except AttributeError as e:
            logging.exception(e)
        except ValueError as e:
            logging.exception(e)

    def add_effect(self, effect):
        self.queue.put(Command(Command.add_effect, effect))

    def remove_effect(self, effect):
        self.queue.put(Command(Command.remove_effect, effect))

    # Stop all currently playing notes
    def stop_playing_notes(self):
        for note in self.playing_notes:
            self.stop_note(note)

    # Stop a specific note
    def stop_note(self, note):
        # noinspection PyTypeChecker
        self.send_message(mido.Message(type=Channel.note_off, velocity=0, note=note))

    # Set the volume of this channel (float from 0 - 1)
    def set_volume(self, volume):
        self.queue.put(Command(Command.volume, volume))

    # Start fading out this channel
    def fade_out(self):
        self.queue.put(Command(Command.fade_out))


# Represents a midi song loaded from a file
class Song:
    def __init__(self, filename="media/channels_test.mid", is_looping=False):
        self.filename = filename
        self.queue = Queue()
        self.is_stopping = False
        self.is_looping = is_looping
        self.mid = mido.MidiFile("{}/{}".format(dir_path, self.filename))
        self.original_tempo = self.mid.ticks_per_beat
        self.channels = map(Channel, range(0, 16))

    def channels_with_instrument_type(self, instrument_type):
        return filter(lambda c: c.instrument_type == instrument_type, self.channels)

    # Play the midi file (should be called on new thread)
    def play_midi_file(self):
        self.is_stopping = False
        play = self.mid.play(meta_messages=True)

        while True:

            for channel in self.channels:
                channel.process_waiting_commands()

            # Take midi messages from a generator
            msg = play.next()

            if msg is None:
                if self.is_looping:
                    play = self.mid.play(meta_messages=True)
                    continue
                break

            # Break if should stop
            if self.is_stopping:
                break
            # Check if any commands in queue
            if not self.queue.empty():
                command = self.queue.get()
                if isinstance(command, Command):
                    if command.name == Command.stop:
                        self.is_stopping = True
                    if command.name == Command.tempo_change:
                        self.mid.ticks_per_beat = command.value * self.original_tempo

            try:
                if isinstance(msg, mido.MetaMessage):
                    continue
                # Send a message to its assigned channel
                self.channels[msg.channel].send_message(msg)
            except AttributeError as e:
                logging.exception(e)
            except IndexError as e:
                logging.exception(e)

    # Start this song on a new thread
    def start(self):
        t = Thread(target=self.play_midi_file)
        t.start()

    # Stop this song
    # noinspection PyUnusedLocal
    def stop(self, *args):
        self.send_command(Command.stop)

    # Queue up a command
    def send_command(self, name, value=None):
        self.queue.put(Command(name, value))

    # Set which channels should be playing
    def set_included_channels(self, pressed_positions):
        for channel in self.channels:
            if channel.number in pressed_positions:
                channel.set_volume(1.0)
            else:
                channel.fade_out()

    # Play all channels
    def include_all_channels(self):
        for channel in self.channels:
            channel.set_volume(1.0)
