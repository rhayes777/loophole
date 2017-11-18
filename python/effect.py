import json


class Combinator(object):
    def __init__(self, filename, track):
        with open(filename) as f:
            self.combos = map(lambda d: Combo(track, d), json.loads(f.read()))


class Combo(object):
    def __init__(self, track, combo_dict):
        self.buttons = set(combo_dict["buttons"])
        self.effects = map(lambda d: Effect.from_dict(track, d), combo_dict["effects"])


class Effect(object):
    def __init__(self, track, effect_dict):
        pass

    @classmethod
    def from_dict(cls, track, effect_dict):
        name = effect_dict("name")



# Pitch change
# Intervals
# Volume change
# Instrument type change
# Instrument version change
# Tempo change
