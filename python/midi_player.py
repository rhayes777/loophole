import mido
from Queue import Queue
import music
from threading import Thread
import logging
import signal
from datetime import datetime

REFACE = 'reface DX'
MPX = 'MPX16'
SIMPLE_SYNTH = 'SimpleSynth virtual input'

CHANNEL_PARTITION = 8

simple_port = None

# noinspection PyBroadException
try:
    instrument = music.MidiInstrument()
except Exception:
    logging.warn("Midi instrument could not be opened")


# Creates a port object corresponding to an instrument if it exists, else to a Simple inbuilt synth
def make_port(name):
    global simple_port
    try:
        # noinspection PyUnresolvedReferences
        return mido.open_output(name)
    except IOError:
        logging.warn("{} not found.".format(name))
        if simple_port is None:
            # noinspection PyUnresolvedReferences
            simple_port = mido.open_output(SIMPLE_SYNTH)
        return simple_port


keys_port = make_port(REFACE)
drum_port = make_port(MPX)


# Class representing key-value pairs that can be queued as commands
class Command:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    pitch_bend = "pitch_bend"
    volume = "volume"
    fade_out = "fade_out"


# Class representing individual midi channel
class Channel:
    note_off = "note_off"
    note_on = "note_on"

    def __init__(self, number, volume=1.0, fade_rate=0.1, note_on_listener=None):
        self.note_on_listener = note_on_listener
        self.number = number
        self.port = keys_port if number < CHANNEL_PARTITION else drum_port
        self.volume = volume
        self.fade_rate = fade_rate
        self.queue = Queue()
        self.fade_start = None
        self.playing_notes = []

    # Send a midi message to this channel
    def send_message(self, msg):
        try:
            # Are there any commands waiting?
            if not self.queue.empty():
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
            # True if a fade out is in progress
            if self.fade_start is not None:
                # How long has the fade been occurring?
                seconds = (datetime.now() - self.fade_start).total_seconds()
                self.volume *= (1 - self.fade_rate * seconds)
                if self.volume < 0:
                    self.volume = 0
                    self.fade_start = None
            msg.velocity = int(self.volume * msg.velocity)
            # Actually send the midi message
            self.port.send(msg)
            # Check if it was a note message
            if msg.type == Channel.note_on:
                # Keep track of notes that are currently playing
                self.playing_notes.append(msg.note)
                self.playing_notes.sort()
                if self.note_on_listener is not None:
                    self.note_on_listener(msg)
            elif msg.type == Channel.note_off:
                self.playing_notes.remove(msg.note)
        except AttributeError:
            pass

    # Stop all currently playing notes
    def stop_playing_notes(self):
        for note in self.playing_notes:
            self.stop_note(note)

    # Stop a specific note
    def stop_note(self, note):
        # noinspection PyTypeChecker
        self.send_message(mido.Message(type=Channel.note_off, velocity=0, note=note))

    # Play a specific note
    def play_note(self, note, velocity=100):
        # noinspection PyTypeChecker
        self.send_message(mido.Message(type=Channel.note_on, velocity=velocity, note=note))

    # Returns a currently playing note for a position or the last playing note if the position too high. Throws index
    # error if there are no playing notes
    def playing_note_with_position(self, position):
        if position > len(self.playing_notes):
            position = len(self.playing_notes) - 1
        return self.playing_notes[position]

    # Set the volume of this channel (float from 0 - 1)
    def set_volume(self, volume):
        self.queue.put(Command(Command.volume, volume))

    # Start fading out this channel
    def fade_out(self):
        self.queue.put(Command(Command.fade_out))


# A bass channel that plays a note from a chord shifted down two octaves on a drum beat
class BassChannel(Channel, object):
    def __init__(self, number, chord_channel, drum_channel, volume=1.0, octave_shift=2):
        super(BassChannel, self).__init__(number, volume)
        self.chord_channel = chord_channel
        self.drum_channel = drum_channel
        self.drum_channel.note_on_listener = self.on_drum_played
        self.pressed_positions = []
        self.octave_shift = octave_shift
        self.pressed_positions_queue = Queue()

    # Called when a drum beat is played
    def on_drum_played(self, msg):
        # Stop all playing notes
        self.stop_playing_notes()
        # Updated pressed positions if waiting in queue
        if not self.pressed_positions_queue.empty():
            self.pressed_positions = self.pressed_positions_queue.get()
        for position in self.pressed_positions:
            try:
                # Grab a note from the chord channel for each pressed position
                note = self.chord_channel.playing_note_with_position(position)

                msg.channel = self.number
                msg.note = note - 12 * self.octave_shift

                self.send_message(msg)
            except IndexError as e:
                logging.exception(e)

    # Set the positions of pressed notes
    def set_pressed_positions(self, pressed_positions):
        self.pressed_positions_queue.put(pressed_positions)


# Represents a midi song loaded from a file
class Song:
    def __init__(self, filename="channels_test.mid", is_looping=False):
        self.filename = filename
        self.queue = Queue()
        self.is_stopping = False
        self.is_looping = is_looping
        self.mid = mido.MidiFile("media/{}".format(self.filename))
        signal.signal(signal.SIGINT, self.stop)
        channel_numbers = range(0, 16)
        self.channels = map(Channel, sorted(list(channel_numbers)))

    # Play the midi file (should be called on new thread)
    def play_midi_file(self):
        self.is_stopping = False

        # Take midi messages from a generator
        for msg in self.mid.play():
            # Break if should stop
            if self.is_stopping:
                break
            # Check if any commands in queue
            if not self.queue.empty():
                command = self.queue.get()
                if isinstance(command, Command):
                    if command.name == Command.pitch_bend:
                        instrument.pitch_bend(command.value)
            try:
                # Send a message to its assigned channel
                self.channels[msg.channel].send_message(msg)
            except AttributeError as e:
                logging.exception(e)
            except IndexError as e:
                logging.exception(e)
        # Loop again if set to do so
        if self.is_looping and not self.is_stopping:
            self.play_midi_file()

    # Start this song on a new thread
    def start(self):
        t = Thread(target=self.play_midi_file)
        t.start()

    # Stop this song
    def stop(self):
        self.is_stopping = True

    # Queue up a command
    def send_command(self, name, value):
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
