import mido
from Queue import Queue
import music
from threading import Thread
import logging
import signal
from datetime import datetime

try:
    instrument = music.MidiInstrument()
    # noinspection PyUnresolvedReferences
    synth_port = mido.open_output()
except Exception:
    pass


class Command:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    pitch_bend = "pitch_bend"
    volume = "volume"
    fade_out = "fade_out"


class Channel:
    def __init__(self, number, port=synth_port, volume=1.0, fade_rate=0.2):
        self.number = number
        self.port = port
        self.volume = volume
        self.fade_rate = fade_rate
        self.queue = Queue()
        self.fade_start = None

    def send_message(self, msg):
        try:
            if not self.queue.empty():
                command = self.queue.get()
                if command.name == Command.volume:
                    self.volume = command.value
                elif command.name == Command.fade_out:
                    if self.fade_start is None:
                        self.fade_start = datetime.now()
            if self.fade_start is not None:
                seconds = (datetime.now() - self.fade_start).total_seconds()
                self.volume *= (1 - self.fade_rate * seconds)
                if self.volume < 0:
                    self.volume = 0
                    self.fade_start = None
            msg.velocity = int(self.volume * msg.velocity)
            self.port.send(msg)
        except AttributeError:
            pass

    def set_volume(self, volume):
        self.queue.put(Command(Command.volume, volume))

    def fade_out(self):
        self.queue.put(Command(Command.fade_out))


class Track:
    def __init__(self, track_name="bicycle-ride.mid", is_looping=False):
        self.track_name = track_name
        self.queue = Queue()
        self.is_stopping = False
        self.is_looping = is_looping
        self.mid = mido.MidiFile("media/{}".format(self.track_name))
        signal.signal(signal.SIGINT, self.stop)
        channel_numbers = set()
        for track in self.mid.tracks:
            for msg in track:
                try:
                    channel_numbers.add(msg.channel)
                except AttributeError:
                    pass
        self.channels = map(Channel, sorted(list(channel_numbers)))

    def play_midi_file(self):
        self.is_stopping = False

        for msg in self.mid.play():
            if self.is_stopping:
                break
            if not self.queue.empty():
                command = self.queue.get()
                if isinstance(command, Command):
                    if command.name == Command.pitch_bend:
                        instrument.pitch_bend(command.value)
            try:
                self.channels[msg.channel].send_message(msg)
            except AttributeError as e:
                logging.exception(e)
            except IndexError as e:
                logging.exception(e)
        if self.is_looping and not self.is_stopping:
            self.play_midi_file()

    def start(self):
        t = Thread(target=self.play_midi_file)
        t.start()

    def stop(self):
        self.is_stopping = True

    def send_command(self, name, value):
        self.queue.put(Command(name, value))
