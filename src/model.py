import math


class Object(object):
    def __init__(self, position=(0., 0.)):
        self.position = position


class Note(Object):
    def __init__(self, position=(0., 0.), velocity=(0., 0.), acceleration=(0., 0.)):
        super(Note, self).__init__(position)
        self.velocity = velocity
        self.acceleration = acceleration

    def step_forward(self):
        self.velocity = tuple(sum(pair) for pair in zip(self.velocity, self.acceleration))
        self.position = tuple(sum(pair) for pair in zip(self.position, self.velocity))


class MassiveObject(Object):
    def __init__(self, position=(0., 0.), mass=1.):
        super(MassiveObject, self).__init__(position)
        self.mass = mass

    def distance_from(self, position):
        return tuple(other - this for other, this in zip(self.position, position))

    def angle_from(self, position):
        if position[0] == 0:
            return math.pi / 2

        distance = self.distance_from(position)
        return math.atan(distance[1] / distance[0])

    def absolute_distance_from(self, position):
        distance = self.distance_from(position)
        return (distance[0] ** 2 + distance[1] ** 2) ** (1 / 2)

    def acceleration_from(self, position):
        return tuple(self.mass / x ** 2 for x in self.distance_from(position))


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
        assert massive_object.absolute_distance_from((1., 1.)) == 2 ** (1 / 2)

    def test_angle_from(self):
        massive_object = MassiveObject(position=(0., 0.))
        assert massive_object.angle_from((1., 0.)) == 0
        assert massive_object.angle_from((0., 1.)) == math.pi / 2
        assert massive_object.angle_from((-1., 0.)) == math.pi

    # def test_acceleration(self):
    #     massive_object = MassiveObject(position=(0., 0.), mass=1.)
    #     assert massive_object.acceleration_from((1, 1)) == (-1, -1)
    #     assert massive_object.acceleration_from((0, 1)) == (0, -1)
    #     assert massive_object.acceleration_from((1, 0)) == (-1, 0)
    #     assert massive_object.acceleration_from((-1, -1)) == (1, 1)
    #
    # def test_bigger_acceleration(self):
    #     massive_object = MassiveObject(position=(0., 0.), mass=2.)
    #     assert massive_object.acceleration_from((1, 1)) == (-2, -2)
    #     assert massive_object.acceleration_from((-1, -1)) == (2, 2)
    #
    # def test_bigger_distance(self):
    #     massive_object = MassiveObject(position=(0., 0.), mass=4.)
    #     assert massive_object.acceleration_from((2, 2)) == (-1, -1)
    #     assert massive_object.acceleration_from((-2, -2)) == (1, 1)


class TestNote(object):
    def test_no_movement(self):
        note = Note(position=(0., 0.), velocity=(0., 0.))
        note.step_forward()

        assert note.position == (0., 0.)

    def test_up_movement(self):
        note = Note(position=(0., 0.), velocity=(1., 0.))
        note.step_forward()

        assert note.position == (1., 0.)

    def test_right_movement(self):
        note = Note(position=(0., 0.), velocity=(0., 1.))
        note.step_forward()

        assert note.position == (0., 1.)

    def test_left_movement(self):
        note = Note(position=(0., 0.), velocity=(0., -1.))
        note.step_forward()

        assert note.position == (0., -1.)

    def test_double_movement(self):
        note = Note(position=(0., 0.), velocity=(1., 1.))
        note.step_forward()
        note.step_forward()

        assert note.position == (2, 2)

    def test_acceleration(self):
        note = Note(position=(0., 0.), velocity=(0., 0.), acceleration=(1., 0.))

        note.step_forward()

        assert note.velocity == (1., 0.)
        assert note.position == (1., 0.)

        note.step_forward()

        assert note.velocity == (2, 0.)
        assert note.position == (3, 0.)
