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


# class Message(mido.Message):
#
#     def __init__(self, *args, **kwargs):
#         super(self, Message).__init__(*args, **kwargs)
#
#     @classmethod
#     def pitch_bend(cls, value=0, channel=0):
#         """modify the pitch of a channel.
#         Output.pitch_bend(value=0, channel=0)
#         Adjust the pitch of a channel.  The value is a signed integer
#         from -8192 to +8191.  For example, 0 means "no change", +4096 is
#         typically a semitone higher, and -8192 is 1 whole tone lower (though
#         the musical range corresponding to the pitch bend range can also be
#         changed in some synthesizers).
#         If no value is given, the pitch bend is returned to "no change".
#         """
#         if not (0 <= channel <= 15):
#             raise ValueError("Channel not between 0 and 15.")
#
#         if not (-8192 <= value <= 8191):
#             raise ValueError("Pitch bend value must be between "
#                              "-8192 and +8191, not %d." % value)
#
#         # "The 14 bit value of the pitch bend is defined so that a value of
#         # 0x2000 is the center corresponding to the normal pitch of the note
#         # (no pitch change)." so value=0 should send 0x2000
#         value += 0x2000  # Was value = value + 0x2000
#         lsb = value & 0x7f  # keep least 7 bits
#         msb = value >> 7
#         return mido.Message.from_bytes([0xe0 + channel, lsb, msb])


# Creates a port object corresponding to an instrument if it exists, else to a Simple inbuilt synth
def make_port(name):
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


# Class representing key-value pairs that can be queued as commands
class Command:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __repr__(self):
        return "<Command {} = {}>".format(self.name, self.value)

    def __str__(self):
        return self.__repr__()

    instrument_type = "instrument_type"
    instrument_version = "instrument_version"
    add_effect = "add_effect"
    remove_effect = "remove_effect"
    pitch_bend = "pitch_bend"
    volume = "volume"
    fade_out = "fade_out"
    stop = "stop"
    tempo_change = "tempo_change"


class Effect:
    def __init__(self, func):
        self.func = func

    def apply(self, msg_array):
        return self.func(msg_array)

    @staticmethod
    def repeat(msg_array):
        for msg in msg_array:
            new_msg = msg.copy()
            new_msg.time += 0.5
            msg_array.append(new_msg)
        return msg_array

    @staticmethod
    def fifth(msg_array):
        new_array = []
        for msg in msg_array:
            if msg.note + 7 > 127:
                continue
            new_msg = msg.copy()
            new_msg.note = key_tracker.scale.position_at_interval(msg.note, 5)
            new_msg.time = 0
            new_array.append(msg)
            new_array.append(new_msg)
        return new_array


# Class representing individual midi channel
class Channel(object):
    program_change = "program_change"
    note_off = "note_off"
    note_on = "note_on"

    def __init__(self, number, volume=1.0, fade_rate=1, note_on_listener=None):
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
        self.effects = []
        self.program = 1

    @property
    def instrument_type(self):
        print self.program
        return self.program / 8

    @instrument_type.setter
    def instrument_type(self, instrument_type):
        if 0 <= instrument_type < 128:
            self.program = 8 * instrument_type + self.instrument_version
            self.queue.put(Command(Command.instrument_type, instrument_type))
            self.port.send(mido.Message('program_change', program=self.program, time=0, channel=self.number))

    @property
    def instrument_version(self):
        return self.program % 8

    @instrument_version.setter
    def instrument_version(self, instrument_version):
        if 0 <= instrument_version < 128:
            self.program = 8 * self.instrument_type + instrument_version
            self.queue.put(Command(Command.instrument_version, instrument_version))
            self.port.send(mido.Message('program_change', program=self.program, time=0, channel=self.number))

    def process_waiting_commands(self):
        # Are there any commands waiting?
        while not self.queue.empty():
            command = self.queue.get()
            print command
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
            elif command.name == Command.add_effect:
                self.effects.append(command.value)
            elif command.name == Command.remove_effect and command.value in self.effects:
                self.effects.remove(command.value)
            elif command.name == Command.pitch_bend:
                self.port.send(mido.Message('pitchwheel', pitch=command.value, time=0, channel=self.number))
            # elif command.name == Command.instrument_version:
            #     print "self.instrument_type = {}".format(self.instrument_type)
            #     print "instrument_version = {}".format(command.value)
            #     program = 8 * self.instrument_type + command.value
            #     print "new_program = {}".format(program)
            #     self.port.send(mido.Message('program_change', program=program, time=0, channel=self.number))
            # elif command.name == Command.instrument_type:
            #     print "instrument_type = {}".format(command.value)
            #     print "self.instrument_version = {}".format(self.instrument_version)
            #     program = 8 * command.value + self.instrument_version
            #     print "new_program = {}".format(program)
            #     self.port.send(mido.Message('program_change', program=program, time=0, channel=self.number))

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
                msgs = self.apply_effects(msg.copy())
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

    def apply_effects(self, msg):
        msg_array = [msg]
        for effect in self.effects:
            msg_array = effect.apply(msg_array)
        return msg_array


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


repeat = Effect(Effect.repeat)
fifth = Effect(Effect.fifth)
