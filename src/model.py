import math
from random import uniform

from config import DECAY_RATE, SPEED

ANGULAR_RANGE = math.pi / 4


class Object(object):
    def __init__(self, position=(0., 0.), velocity=(0., 0.), acceleration=(0., 0.), angle=0., rotation_speed=0.5):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.angle = angle
        self.rotation_speed = rotation_speed

    def step_forward(self):
        self.velocity = tuple(sum(pair) for pair in zip(self.velocity, self.acceleration))
        self.position = tuple(sum(pair) for pair in zip(self.position, self.velocity))
        self.angle = (self.angle + self.rotation_speed) % (2 * math.pi)

    def __str__(self):
        return "position:{}\n" \
               "velocity:{}\n" \
               "acceleration:{}".format(self.position, self.velocity, self.acceleration)


class NoteObject(Object):
    def __init__(self, colour, position=(0., 0.), velocity=(0., 0.), acceleration=(0., 0.), note=None):
        super(NoteObject, self).__init__(position, velocity, acceleration)
        self.note = note
        self.colour = colour


class Scorer(object):
    def __init__(self, decay_rate=DECAY_RATE):
        self.score = 0
        self.decay_rate = decay_rate

    def add_points(self, points):
        self.score += points

    def decay(self):
        self.score -= self.decay_rate
        self.score = max(self.score, 0)


class NoteGenerator(object):
    def __init__(self, position, direction, angular_range=ANGULAR_RANGE, speed=SPEED):
        self.position = position
        self.speed = speed
        self.min_direction = direction - angular_range
        self.max_direction = direction + angular_range

    def make_note(self, note, colour):
        direction = uniform(self.min_direction, self.max_direction)
        velocity = (self.speed * math.sin(direction), self.speed * math.cos(direction))
        return NoteObject(colour, self.position, velocity, note=note)
