class Note(object):
    def __init__(self, position=(0, 0), velocity=(0, 0)):
        self.position = position
        self.velocity = velocity

    def move(self):
        pass


class TestNote(object):
    def test_no_movement(self):
        note = Note(position=(0, 0), velocity=(1, 0))

        assert note.position == (0, 0)
        note.move()

        assert note.position == (0, 0)
