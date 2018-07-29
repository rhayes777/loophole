from Queue import Queue


class Iterator(object):
    def __init__(self, source):
        if isinstance(source, list):
            self.source = iter(source).__iter__()
        else:
            self.source = source
        self.queue = Queue()

    def __iter__(self):
        return self

    def next(self):
        if not self.queue.empty():
            return self.queue.get()
        self.queue.put(self.source.next())
        return self.next()


class OperationIterator(Iterator):
    def __init__(self, source, operation=lambda message: [message], operation_filter=lambda x: True):
        super(OperationIterator, self).__init__(source)
        self.operation = operation
        self.operation_filter = operation_filter

    def next(self):
        if not self.queue.empty():
            return self.queue.get()
        message = self.source.next()
        if not self.operation_filter(message):
            return message
        for message in self.operation(message):
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
        iterator = OperationIterator([1, 2, 3], operation=lambda x: [2 * x])

        assert [2, 4, 6] == [n for n in iterator]

    def test_effect_filter(self):
        iterator = OperationIterator([1, 2, 3], operation=lambda x: [2 * x], operation_filter=lambda x: x == 2)

        assert [1, 4, 3] == [n for n in iterator]
