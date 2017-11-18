import json
import player
import logging
import os

logging.basicConfig()

logger = logging.getLogger(__name__)

path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))


class Combinator(object):
    """Interprets a JSON dancemat effects configuration and applies effects corresponding to button combinations"""

    def __init__(self, filename, track):
        """

        :param filename: The json configuration file (see configurations/effects_1.json)
        :param track: The midi track
        """
        self.current_combo = None
        with open("{}/{}".format(dir_path, filename)) as f:
            self.combos = map(lambda d: Combo(track, d), json.loads(f.read()))
            self.button_map = {sum(map(hash, combo.buttons)): combo for combo in self.combos}

    def apply_for_buttons(self, buttons):
        """
        Removes the currently applied effects and applies a new set corresponding to the buttons pressed. If no set in
        the configuration matches the buttons passed no effects will be applied.
        :param buttons: A list of buttons
        """
        if self.current_combo is not None:
            self.current_combo.remove()
        try:
            self.current_combo = self.button_map[sum(map(hash, buttons))]
            self.current_combo.apply()
        except KeyError:
            logger.info("{} not found in combinator".format(buttons))


class Combo(object):
    """Maps a set of buttons to a set of effects"""

    def __init__(self, track, combo_dict):
        """

        :param track: The midi track
        :param combo_dict: A dictionary describing
        """
        self.buttons = set(combo_dict["buttons"])
        self.effects = map(lambda d: Effect.from_dict(track, d), combo_dict["effects"])

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

    def __repr__(self):
        return str(map(Effect.__repr__, self.effects))

    def __str__(self):
        return self.__repr__()


class Effect(object):
    """An individual effect that can be applied to change the music"""

    def __init__(self, effect_dict):
        """

        :param effect_dict: A dictionary describing this effect.
        """
        self.name = effect_dict["name"]
        self.value = effect_dict["value"]

    @classmethod
    def from_dict(cls, track, effect_dict):
        """
        Factory method to create an effect class for a dictionary
        :param track: A midi track
        :param effect_dict: A dictionary describing an effect.
        """
        name = effect_dict["name"]
        if name == "pitch_bend":
            return PitchBend(track, effect_dict)
        elif name == "volume_change":
            return VolumeChange(track, effect_dict)
        elif name == "intervals":
            return Intervals(track, effect_dict)
        elif name == "instrument_type":
            return InstrumentType(track, effect_dict)
        elif name == "instrument_version":
            return InstrumentVersion(track, effect_dict)
        elif name == "tempo_shift":
            return TempoShift(track, effect_dict)

        raise AssertionError("No effect named {}".format(name))

    def apply(self):
        raise AssertionError("{}.apply not overridden".format(self.name))

    def remove(self):
        raise AssertionError("{}.default not overridden".format(self.name))

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
        self.channels = []
        if "channels" in effect_dict:
            self.channels.extend([channel for channel in track.channels if channel.number in effect_dict["channels"]])
        if "instrument_types" in effect_dict:
            for instrument_type in effect_dict["instrument_types"]:
                self.channels.extend(track.channels_with_instrument_type(instrument_type))
        if "instrument_group" in effect_dict:
            self.channels.extend(track.channels_with_instrument_group(effect_dict["instrument_group"]))
        if "channels" not in effect_dict \
                and "instrument_types" not in effect_dict \
                and "instrument_group" not in effect_dict:
            self.channels = track.channels_with_instrument_group("all")
        if len(self.channels) == 0:
            raise AssertionError(
                "At least one channel or one present instrument type must be set for {}".format(self.name))


class PitchBend(ChannelEffect):
    """Bends the pitch of one or more channels"""

    def apply(self):
        for channel in self.channels:
            channel.pitch_bend(self.value)

    def remove(self):
        for channel in self.channels:
            channel.pitch_bend(0)  # TODO: Is this unbent?


class VolumeChange(ChannelEffect):
    """Changes the volume of one or more channels"""

    def apply(self):
        for channel in self.channels:
            channel.volume = self.value

    def remove(self):
        for channel in self.channels:
            channel.volume = player.DEFAULT_VOLUME


class Intervals(ChannelEffect):
    """Converts notes played through a channel into one or more relative intervals in the key"""

    def __init__(self, track, effect_dict):
        super(Intervals, self).__init__(track, effect_dict)
        self.value = player.Intervals(self.value)

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
        self.track.tempo_shift = player.DEFAULT_TEMPO_SHIFT
