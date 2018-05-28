import json
from audio import player
import logging
import os
from threading import Thread
from time import sleep
from Queue import Queue
import sys
import inspect
import re

INTERVAL = 0.1
EFFECT_LENGTH = 2

logging.basicConfig()

logger = logging.getLogger(__name__)

path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class Combinator(object):
    """Interprets a JSON dancemat effects configuration and applies effects corresponding to button combinations"""

    def __init__(self, filename=None, track=None):
        """

        :param filename: The json configuration file (see configurations/effects_1.json)
        :param track: The midi track

        If no arguments are passed this combinator can be used to generate a JSON template by adding combos
        """
        if filename is not None and track is not None:
            self.__current_combos = []
            with open(filename) as f:
                self.combos = map(lambda d: Combo(track, d), json.loads(f.read()))
                for combo in self.combos:
                    combo.start()
                self.button_map = {sum(map(hash, combo.buttons)): combo for combo in self.combos}
        else:
            self.combos = []

    def apply_for_buttons(self, buttons):
        """
        Sets the effects that best correspond to the set of buttons. If a specific combo is defined for the set of
        buttons that combo will be applied. Otherwise, effects for each individual buttons will be stacked.
        :param buttons: A list of buttons
        """
        buttons_hash = sum(map(hash, buttons))
        if buttons_hash in self.button_map:
            self.button_map[buttons_hash].play()

    def dict(self):
        return map(Combo.dict, self.combos)

    def stop(self):
        for combo in self.combos:
            combo.stop()


class Combo(object):
    """Maps a set of buttons to a set of effects"""

    def __init__(self, track=None, combo_dict=None):
        """

        :param track: The midi track
        :param combo_dict: A dictionary describing
        """
        if combo_dict is not None:
            self.buttons = set(combo_dict["buttons"])
            self.effects = map(lambda d: Effect.from_dict(track, d), combo_dict["effects"])
        else:
            self.buttons = []
            self.effects = []

    def apply(self):
        """
        Apply all of the effects listed in this combo
        """
        for effect in self.effects:
            effect.apply()

    def remove(self):
        """
        Remove all of the effects listed in this combo
        """
        for effect in self.effects:
            effect.remove()

    def start(self):
        for effect in self.effects:
            effect.start()

    def stop(self):
        for effect in self.effects:
            effect.stop()

    def play(self):
        for effect in self.effects:
            effect.play()

    def dict(self):
        return {"buttons": self.buttons, "effects": map(Effect.dict, self.effects)}

    def __repr__(self):
        return str(map(Effect.__repr__, self.effects))

    def __str__(self):
        return self.__repr__()


class Effect(Thread):
    """An individual effect that can be applied to change the music"""

    def __init__(self, effect_dict):
        """

        :param effect_dict: A dictionary describing this effect.
        """
        super(Effect, self).__init__()
        self.name = effect_dict["name"]
        self.value = effect_dict["value"]
        self.length = (effect_dict["length"] if "length" in effect_dict else EFFECT_LENGTH)
        self.is_started = False
        self.queue = Queue()

    @classmethod
    def from_dict(cls, track, effect_dict):
        """
        Factory method to create an effect class for a dictionary
        :param track: A midi track
        :param effect_dict: A dictionary describing an effect.
        """
        name = effect_dict["name"]
        print Effect.classes

        try:
            Effect.classes[name](track, effect_dict)
        except KeyError:
            raise AssertionError("No effect named {}".format(name))

    def apply(self):
        raise AssertionError("{}.apply not overridden".format(self.name))

    def remove(self):
        raise AssertionError("{}.default not overridden".format(self.name))

    def play(self):
        self.queue.put("play")

    def stop(self):
        self.queue.put("stop")

    def run(self):
        is_applied = False
        time = 0.
        while True:
            if not self.queue.empty():
                message = self.queue.get()
                if message == "play":
                    time = 0.
                    if not is_applied:
                        is_applied = True
                        self.apply()
                elif message == "stop":
                    break
            if time >= self.length and is_applied:
                is_applied = False
                self.remove()
            if time <= self.length:
                time += INTERVAL
            sleep(INTERVAL)

    def dict(self):
        return {"name": self.name, "value": self.value}

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Effect name={} value={}>".format(self.name, self.value)


class ChannelEffect(Effect):
    """An effect that modifies one or more channels"""

    def __init__(self, track, effect_dict):
        """

        :param track: A midi track
        :param effect_dict: An effect dictionary that includes one or more channels or instrument types
        (see player.InstrumentType)
        """
        super(ChannelEffect, self).__init__(effect_dict)
        self.instrument_types = None
        self.instrument_group = None
        self.__channels = None
        self.track = track
        if "channels" in effect_dict:
            self.__channels = effect_dict["channels"]
        if "instrument_types" in effect_dict:
            self.instrument_types = effect_dict["instrument_types"]
        if "instrument_group" in effect_dict:
            self.instrument_group = effect_dict["instrument_group"]
        if all(map(lambda p: p is None, [self.__channels, self.instrument_types, self.instrument_group])):
            self.channels = self.track.channels_with_instrument_group("all")
        else:
            self.channels = []
            if self.__channels is not None:
                self.channels.extend([channel for channel in self.track.channels if channel.number in self.__channels])
            if self.instrument_types is not None:
                for instrument_type in self.instrument_types:
                    self.channels.extend(self.track.channels_with_instrument_type(instrument_type))
            if self.instrument_group is not None:
                self.channels.extend(self.track.channels_with_instrument_group(self.instrument_group))

    @property
    def dict(self):
        d = super(ChannelEffect, self).dict()
        if self.__channels is not None:
            d["channels"] = self.__channels
        if self.instrument_types is not None:
            d["instrument_types"] = self.instrument_types
        if self.instrument_group is not None:
            d["instrument_group"] = self.instrument_group
        return d


class PitchBend(ChannelEffect):
    """Bends the pitch of one or more channels"""

    def apply(self):
        for channel in self.channels:
            channel.pitch_bend(self.value)

    def remove(self):
        for channel in self.channels:
            channel.pitch_bend(player.PITCHWHEEL_DEFAULT)


class VolumeChange(ChannelEffect):
    """Changes the volume of one or more channels"""

    def apply(self):
        for channel in self.channels:
            channel.volume = self.value

    def remove(self):
        for channel in self.channels:
            channel.volume = player.VOLUME_DEFAULT


class Intervals(ChannelEffect):
    """Converts notes played through a channel into one or more relative intervals in the key"""

    def apply(self):
        for channel in self.channels:
            channel.intervals = self.value

    def remove(self):
        for channel in self.channels:
            channel.intervals = None


class InstrumentType(ChannelEffect):
    """Changes the type of instrument of one or more channels. See player.InstrumentType"""

    def __init__(self, track, effect_dict):
        super(InstrumentType, self).__init__(track, effect_dict)
        self.defaults = [channel.instrument_type for channel in self.channels]

    def apply(self):
        for channel in self.channels:
            channel.instrument_type = self.value

    def remove(self):
        for n, channel in enumerate(self.channels):
            channel.instrument_type = self.defaults[n]


class InstrumentVersion(ChannelEffect):
    """Changes the version of the instrument for one or more channels. e.g. from one piano to a different piano"""

    def __init__(self, track, effect_dict):
        super(InstrumentVersion, self).__init__(track, effect_dict)
        self.defaults = [channel.instrument_version for channel in self.channels]

    def apply(self):
        for channel in self.channels:
            channel.instrument_version = self.value

    def remove(self):
        for n, channel in enumerate(self.channels):
            channel.instrument_version = self.defaults[n]


class TrackEffect(Effect):
    """An effect that is applied to the whole track"""

    def __init__(self, track, effect_dict):
        super(TrackEffect, self).__init__(effect_dict)
        self.track = track


class TempoShift(TrackEffect):
    """Shifts the tempo of the whole track by some factor. 0.5 is half tempo and 2 double tempo"""

    def apply(self):
        self.track.tempo_shift = self.value

    def remove(self):
        self.track.tempo_shift = player.TEMPO_SHIFT_DEFAULT


class Modulation(ChannelEffect):
    def apply(self):
        for channel in self.channels:
            channel.modulation = self.value

    def remove(self):
        for channel in self.channels:
            channel.modulation = 0


class Pan(ChannelEffect):
    def apply(self):
        for channel in self.channels:
            channel.pan = self.value

    def remove(self):
        for channel in self.channels:
            channel.pan = 63


class ChannelSwitch(ChannelEffect):
    def __init__(self, track, effect_dict):
        super(ChannelSwitch, self).__init__(track, effect_dict)
        self.position = 0

    def apply(self):
        self.position = (self.position + 1) % len(self.channels)
        for channel in self.channels:
            channel.volume = 0
        self.channels[self.position].volume = 1


Effect.classes = {convert(key): cls for key, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass)}


if __name__ == "__main__":
    """This code generates a template with every single buttons and double button combination"""

    combinator = Combinator()
    all_buttons = ['up', 'down', 'left', 'right', 'triangle', 'circle', 'square', 'x']

    for button1 in all_buttons:
        c = Combo()
        c.buttons = [button1]
        combinator.combos.append(c)
        for button2 in all_buttons:
            if button1 < button2:
                c = Combo()
                c.buttons = [button1, button2]
                combinator.combos.append(c)
    with open(sys.argv[1], 'w+') as f:
        f.write(json.dumps(combinator.dict()))


class TestEffect(object):
    def test_class_names(self):
        assert "channel_switch" in Effect.classes

    def test_convert(self):
        assert convert("ChannelSwitch") == "channel_switch"
