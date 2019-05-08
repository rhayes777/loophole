import math

import config


class Object(object):
    def __init__(self, position=(0., 0.), velocity=(0., 0.), acceleration=(0., 0.), angle=0., rotation_speed=0.5):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.angle = angle
        self.rotation_speed = rotation_speed

    def is_in_range(self, other_object):
        distance = ((self.position[0] - other_object.position[0]) ** 2 + (
                    self.position[1] - other_object.position[1]) ** 2) ** 0.5
        return distance < config.COLLISION_RADIUS

    @property
    def is_out_of_bounds(self):
        return self.position[0] > config.screen_shape[0] or self.position[0] < 0 or self.position[
            1] > config.screen_shape or self.position[1] < 0

    def step_forward(self):
        self.velocity = tuple(sum(pair) for pair in zip(self.velocity, self.acceleration))
        self.position = tuple(sum(pair) for pair in zip(self.position, self.velocity))
        self.angle = (self.angle + self.rotation_speed) % (2 * math.pi)

    def __str__(self):
        return "position:{}\n" \
               "velocity:{}\n" \
               "acceleration:{}".format(self.position, self.velocity, self.acceleration)


class NoteObject(Object):
    def __init__(self, position=(0., 0.), velocity=(0., 0.), acceleration=(0., 0.), note=None):
        super(NoteObject, self).__init__(position, velocity, acceleration)
        self.note = note


class Scorer(object):
    def __init__(self, decay_rate=config.DECAY_RATE):
        self.score = 0
        self.decay_rate = decay_rate

    def add_points(self, points):
        self.score += points

    def decay(self):
        self.score -= self.decay_rate
        self.score = max(self.score, 0)
