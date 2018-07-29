from Queue import Queue


class Iterator(object):
    def __init__(self, source, operation=lambda message: [message]):
        if isinstance(source, list):
            self.source = iter(source).__iter__()
        else:
            self.source = source
        self.operation = operation
        self.queue = Queue()

    def __iter__(self):
        return self

    def next(self):
        if not self.queue.empty():
            return self.queue.get()
        for message in self.operation(self.source.next()):
            self.queue.put(message)
        return self.next()


class TestCase(object):
    def test_iter(self):
        iterator = Iterator([1, 2, 3])

        assert [1, 2, 3] == [n for n in iterator]

    def test_double_iter(self):
        iterator = Iterator(Iterator([1, 2, 3]))

        assert [1, 2, 3] == [n for n in iterator]

    def test_apply(self):
        iterator = Iterator([1, 2, 3], operation=lambda x: [2 * x])

        assert [2, 4, 6] == [n for n in iterator]
