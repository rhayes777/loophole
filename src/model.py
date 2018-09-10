import math
import pytest
from random import uniform

# MASS = 1000.
MASS = 0.
DISTANT_MASS = 0.
COLLISION_RADIUS = 30.
VELOCITY = 0.1
SPEED = 2

almost_zero = pytest.approx(0, abs=0.0001)


class NoteGenerator(object):
    def __init__(self, style, position, min_direction, max_direction, speed=SPEED):
        self.position = position
        self.style = style
        self.speed = speed
        self.min_direction = min_direction
        self.max_direction = max_direction

    def make_note(self):
        direction = uniform(self.min_direction, self.max_direction)
        velocity = (self.speed * math.sin(direction), self.speed * math.cos(direction))
        return NoteObject(self.style, self.position, velocity)


class Object(object):
    def __init__(self, position=(0., 0.), velocity=(0., 0.), acceleration=(0., 0.)):
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration

    def step_forward(self):
        self.velocity = tuple(sum(pair) for pair in zip(self.velocity, self.acceleration))
        self.position = tuple(sum(pair) for pair in zip(self.position, self.velocity))

    def __str__(self):
        return "position:{}\n" \
               "velocity:{}\n" \
               "acceleration:{}".format(self.position, self.velocity, self.acceleration)


class NoteObject(Object):
    def __init__(self, style, position=(0., 0.), velocity=(0., 0.), acceleration=(0., 0.)):
        super(NoteObject, self).__init__(position, velocity, acceleration)
        self.style = style


class MassiveObject(Object):
    def __init__(self, position=(0., 0.), mass=MASS, collision_radius=COLLISION_RADIUS):
        super(MassiveObject, self).__init__(position)
        self.mass = mass
        self.collision_radius = collision_radius

    def distance_from(self, position):
        return tuple(other - this for other, this in zip(self.position, position))

    def angle_from(self, position):
        distance = self.distance_from(position)
        return math.atan2(distance[1], distance[0])

    def absolute_distance_from(self, position):
        distance = self.distance_from(position)
        return (distance[0] ** 2 + distance[1] ** 2) ** 0.5

    def force_from_position(self, position):
        absolute_distance = self.absolute_distance_from(position)
        try:
            return self.mass / (absolute_distance ** 2) + DISTANT_MASS
        except ZeroDivisionError:
            return 0

    def acceleration_from(self, position):
        force = self.force_from_position(position)
        angle = self.angle_from(position)
        return force * math.cos(angle), force * math.sin(angle)

    def is_collision(self, position):
        return self.absolute_distance_from(position) <= self.collision_radius

    def __str__(self):
        return "mass:{}\n" \
               "collision_radius:{}\n" \
               "{}".format(self.mass, self.collision_radius, super(MassiveObject, self).__str__())


class Model(object):
    def __init__(self, player):
        self.player = player
        self.generators = {}
        self.notes = set()

    def add_note(self, style):
        self.notes.add(self.generators[style].make_note())

    def step_forward(self):
        for note in list(self.notes):
            note.step_forward()
            note.acceleration = self.player.acceleration_from(note.position)
            if self.player.is_collision(note.position):
                self.notes.remove(note)

        self.player.step_forward()

    def __str__(self):
        return "Player:\n{}\nNotes:\n{}".format(str(self.player, ), "\n".join(map(str, self.notes)))


@pytest.fixture(name="model")
def make_model():
    return Model(MassiveObject())


@pytest.fixture(name="note_across")
def make_note_across():
    return Object(velocity=(1, 0))


@pytest.fixture(name="note_up")
def make_note_up():
    return Object(velocity=(0, 1))


class TestModel(object):
    def test_init(self, model):
        model.player.collision_radius = None
        assert isinstance(model.player, MassiveObject)
        assert model.notes == set()

    def test_step_forward(self, model, note_across, note_up):
        model.player.collision_radius = None
        model.notes.update([note_across, note_up])

        model.step_forward()

        assert note_across.position == (1, 0)
        assert note_up.position == (0, 1)

        assert note_across.acceleration == (-1, almost_zero)
        assert note_up.acceleration == (almost_zero, -1)

        assert model.player.position == (0, 0)

    def test_moving_player(self, model):
        model.player.velocity = (1, 0)

        model.step_forward()

        assert model.player.position == (1, 0)

    def test_collision(self):
        player = MassiveObject()
        note = Object()

        assert player.is_collision(note.position)

        note = Object(position=(1.1, 0))

        assert not player.is_collision(note.position)

    def test_elimination(self, model, note_up):
        model.notes.add(note_up)
        model.step_forward()

        assert model.notes == set()

    def test_falling_objects(self, model):
        model.player.collision_radius = None
        model.notes.update(
            [Object(position=(1, 0)),
             Object(position=(0, 1)),
             Object(position=(-1, 0)),
             Object(position=(0, -1))])

        for _ in range(100):
            model.step_forward()
            for note in list(model.notes):
                assert model.player.absolute_distance_from(note.position) <= 1


class TestMassiveObject(object):
    def test_distance(self):
        massive_object = MassiveObject(position=(0., 0.), mass=1.)
        assert massive_object.distance_from((1, 1)) == (-1, -1)
        assert massive_object.distance_from((0, 1)) == (0, -1)
        assert massive_object.distance_from((1, 0)) == (-1, 0)
        assert massive_object.distance_from((-1, -1)) == (1, 1)

    def test_absolute_distance_from(self):
        massive_object = MassiveObject(position=(0., 0.))

        assert massive_object.absolute_distance_from((0., 1.)) == 1
        assert massive_object.absolute_distance_from((0., -1.)) == 1
        assert massive_object.absolute_distance_from((1., 0.)) == 1
        assert massive_object.absolute_distance_from((-1., 0.)) == 1
        assert massive_object.absolute_distance_from((1., 1.)) == 2 ** 0.5

    def test_force_from_position(self):
        massive_object = MassiveObject(position=(0., 0.))

        assert massive_object.force_from_position((0., 1.)) == 1
        assert massive_object.force_from_position((1., 0.)) == 1
        assert massive_object.force_from_position((2., 0.)) == 0.25

    def test_angle_from(self):
        massive_object = MassiveObject(position=(0., 0.))
        assert massive_object.angle_from((1., 0.)) == math.pi
        assert massive_object.angle_from((0., 1.)) == -math.pi / 2
        assert massive_object.angle_from((-1., 0.)) == 0

    def test_acceleration(self):
        massive_object = MassiveObject(position=(0., 0.), mass=1.)
        assert massive_object.acceleration_from((0, 1)) == (almost_zero, -1)
        assert massive_object.acceleration_from((1, 0)) == (-1, almost_zero)

    def test_bigger_acceleration(self):
        massive_object = MassiveObject(position=(0., 0.), mass=2.)
        assert massive_object.acceleration_from((1, 0)) == (-2, almost_zero)
        assert massive_object.acceleration_from((-1, 0)) == (2, almost_zero)

    def test_bigger_distance(self):
        massive_object = MassiveObject(position=(0., 0.), mass=4.)
        assert massive_object.acceleration_from((2, 0)) == (-1, almost_zero)
        assert massive_object.acceleration_from((-2, 0)) == (1, almost_zero)


class TestNote(object):
    def test_no_movement(self):
        note = Object(position=(0., 0.), velocity=(0., 0.))
        note.step_forward()

        assert note.position == (0., 0.)

    def test_up_movement(self):
        note = Object(position=(0., 0.), velocity=(1., 0.))
        note.step_forward()

        assert note.position == (1., 0.)

    def test_right_movement(self):
        note = Object(position=(0., 0.), velocity=(0., 1.))
        note.step_forward()

        assert note.position == (0., 1.)

    def test_left_movement(self):
        note = Object(position=(0., 0.), velocity=(0., -1.))
        note.step_forward()

        assert note.position == (0., -1.)

    def test_double_movement(self):
        note = Object(position=(0., 0.), velocity=(1., 1.))
        note.step_forward()
        note.step_forward()

        assert note.position == (2, 2)

    def test_acceleration(self):
        note = Object(position=(0., 0.), velocity=(0., 0.), acceleration=(1., 0.))

        note.step_forward()

        assert note.velocity == (1., 0.)
        assert note.position == (1., 0.)

        note.step_forward()

        assert note.velocity == (2, 0.)
        assert note.position == (3, 0.)
