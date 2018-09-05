class Note(object):
    def __init__(self, position=(0, 0), velocity=(0, 0)):
        self.position = position
        self.velocity = velocity

    def move(self):
        self.position = tuple(position + velocity for position, velocity in zip(self.position, self.velocity))


class TestNote(object):
    def test_no_movement(self):
        note = Note(position=(0, 0), velocity=(0, 0))
        note.move()

        assert note.position == (0, 0)

    def test_up_movement(self):
        note = Note(position=(0, 0), velocity=(1, 0))
        note.move()

        assert note.position == (1, 0)

    def test_right_movement(self):
        note = Note(position=(0, 0), velocity=(0, 1))
        note.move()

        assert note.position == (0, 1)

    def test_left_movement(self):
        note = Note(position=(0, 0), velocity=(0, -1))
        note.move()

        assert note.position == (0, -1)
