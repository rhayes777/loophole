import config
import model

VELOCITY = (10, 0)


class MockNote(object):
    def __init__(self, note):
        self.note = note


class User(model.Object):
    def __init__(self, screen_shape=config.screen_shape):
        super(User, self).__init__((screen_shape[0] / 2, screen_shape[1] - config.INDENT), rotation_speed=0.0)
        self.screen_shape = screen_shape

    def step_forward(self):
        super(User, self).step_forward()
        if self.position[0] > self.screen_shape[0]:
            self.position[0] = self.screen_shape
        elif self.position[0] < 0:
            self.position[0] = 0


class SpaceFighterModel(object):
    def __init__(self, screen_shape, notes_per_side):
        self.screen_shape = screen_shape
        self.notes_per_side = notes_per_side
        self.aliens = list()

    def add_note(self, note):
        x_position = (float(note.note % self.notes_per_side) / self.notes_per_side) * self.screen_shape[0]
        self.aliens.append(model.NoteObject(note=note, velocity=(config.SPEED, 0), position=(x_position, 0)))


class TestCase(object):
    def test_add_notes(self):
        model = SpaceFighterModel(screen_shape=(100, 100), notes_per_side=10)

        model.add_note(MockNote(0))

        assert len(model.aliens) == 1
        assert model.aliens[0].position == (0, 0)

        model.add_note(MockNote(1))

        assert model.aliens[-1].position == (10, 0)

        model.add_note(MockNote(10))

        assert model.aliens[-1].position == (0, 0)
