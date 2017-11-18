import json
import player
import logging
import os

logging.basicConfig()

logger = logging.getLogger(__name__)

path = os.path.realpath(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))


class Combinator(object):
    def __init__(self, filename, track):
        self.current_combo = None
        with open("{}/{}".format(dir_path, filename)) as f:
            self.combos = map(lambda d: Combo(track, d), json.loads(f.read()))
            self.button_map = {sum(map(hash, combo.buttons)): combo for combo in self.combos}

    def apply_for_buttons(self, buttons):
        if self.current_combo is not None:
            self.current_combo.remove()
        try:
            self.current_combo = self.button_map[sum(map(hash, buttons))]
            self.current_combo.apply()
        except KeyError:
            logger.info("{} not found in combinator".format(buttons))


class Combo(object):
    def __init__(self, track, combo_dict):
        self.buttons = set(combo_dict["buttons"])
        self.effects = map(lambda d: Effect.from_dict(track, d), combo_dict["effects"])

    def apply(self):
        for effect in self.effects:
            effect.apply()

    def remove(self):
        for effect in self.effects:
            effect.remove()

    def __repr__(self):
        return str(map(Effect.__repr__, self.effects))

    def __str__(self):
        return self.__repr__()


class Effect(object):
    def __init__(self, effect_dict):
        self.name = effect_dict["name"]
        self.value = effect_dict["value"]

    @classmethod
    def from_dict(cls, track, effect_dict):
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
    def __init__(self, track, effect_dict):
        super(ChannelEffect, self).__init__(effect_dict)
        self.channels = []
        if "channels" in effect_dict:
            self.channels.extend([channel for channel in track.channels if channel.number in effect_dict["channels"]])
        if "instrument_types" in effect_dict:
            for instrument_type in effect_dict["instrument_types"]:
                # TODO: standardise instrument type counting (0-15 or 1-16)
                self.channels.extend(track.channels_with_instrument_type(instrument_type))
        if len(self.channels) == 0:
            raise AssertionError(
                "At least one channel or one present instrument type must be set for {}".format(self.name))


class PitchBend(ChannelEffect):
    def apply(self):
        for channel in self.channels:
            channel.pitch_bend(self.value)

    def remove(self):
        for channel in self.channels:
            channel.pitch_bend(0)  # TODO: Is this unbent?


class VolumeChange(ChannelEffect):
    def apply(self):
        for channel in self.channels:
            channel.volume = self.value

    def remove(self):
        for channel in self.channels:
            channel.volume = player.DEFAULT_VOLUME


class Intervals(ChannelEffect):
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
    def __init__(self, track, effect_dict):
        super(TrackEffect, self).__init__(effect_dict)
        self.track = track


class TempoShift(TrackEffect):
    def apply(self):
        self.track.tempo_shift = self.value

    def remove(self):
        self.track.tempo_shift = player.DEFAULT_TEMPO_SHIFT
