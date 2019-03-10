VELOCITY = (10, 0)


class MockNote(object):
    def __init__(self, note):
        self.note = note


class Alien(object):
    def __init__(self, note, position, velocity=VELOCITY):
        self.note = note
        self.position = position
        self.velocity = velocity


class SpaceFighterModel(object):
    def __init__(self, screen_shape, notes_per_side):
        self.screen_shape = screen_shape
        self.notes_per_side = notes_per_side
        self.aliens = list()

    def add_note(self, note):
        x_position = (float(note.note % self.notes_per_side) / self.notes_per_side) * self.screen_shape[0]
        self.aliens.append(Alien(note, position=(x_position, 0)))


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
