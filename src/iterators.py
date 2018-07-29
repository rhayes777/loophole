from Queue import Queue
import pytest
from functools import wraps


class Heartbeat(object):
    __heartbeat = None

    def __new__(cls, *args, **kwargs):
        if Heartbeat.__heartbeat is None:
            Heartbeat.__heartbeat = object.__new__(Heartbeat)
        return Heartbeat.__heartbeat


heartbeat = Heartbeat()


def filter_heartbeats(source):
    def next_not_heartbeat():
        message = source.next()
        if message is heartbeat:
            return next_not_heartbeat()
        return message

    yield next_not_heartbeat()


class AbstractIterator(object):
    def __iter__(self):
        return self


def switch(func):
    @wraps(func)
    def wrapper(instance):
        if instance.is_on:
            return func(instance)
        return super(instance.__class__, instance).next()

    return wrapper


class Iterator(AbstractIterator):
    def __init__(self, source):
        super(Iterator, self).__init__()
        if isinstance(source, list):
            self.source = iter(source).__iter__()
        else:
            self.source = source
        self.__is_on = True
        self.__is_on_queue = Queue()

    @property
    def is_on(self):
        if not self.__is_on_queue.empty():
            self.__is_on = self.__is_on_queue.get()
        return self.__is_on

    @is_on.setter
    def is_on(self, new_value):
        self.__is_on_queue.put(new_value)

    def next(self):
        return self.source.next()


class OperationIterator(Iterator):
    def __init__(self, source, operation=lambda message: [message], operation_filter=lambda x: True):
        super(OperationIterator, self).__init__(source)
        self.operation = operation
        self.operation_filter = operation_filter
        self.queue = Queue()

    @switch
    def next(self):
        if not self.queue.empty():
            return self.queue.get()
        message = self.source.next()
        if not self.operation_filter(message):
            return message
        for message in self.operation(message):
            self.queue.put(message)
        return self.next()


class FilterIterator(Iterator):
    def __init__(self, source, filter_function=lambda x: True):
        super(FilterIterator, self).__init__(source)
        self.filter_function = filter_function

    @switch
    def next(self):
        message = self.source.next()
        if self.filter_function(message):
            return message
        return heartbeat


@pytest.fixture(name="iterator")
def make_iterator():
    return Iterator([1, 2, 3])


@pytest.fixture(name="filter_iterator")
def make_filter_iterator():
    return FilterIterator([1, 2, 3], filter_function=lambda x: x == 2)


class TestBasic(object):
    def test_iter(self, iterator):
        assert [1, 2, 3] == [n for n in iterator]

    def test_double_iter(self, iterator):
        iterator = Iterator(iterator)

        assert [1, 2, 3] == [n for n in iterator]

    def test_apply(self):
        iterator = OperationIterator([1, 2, 3], operation=lambda x: [2 * x])

        assert [2, 4, 6] == [n for n in iterator]

    def test_effect_filter(self):
        iterator = OperationIterator([1, 2, 3], operation=lambda x: [2 * x], operation_filter=lambda x: x == 2)

        assert [1, 4, 3] == [n for n in iterator]

    def test_message_filter(self, filter_iterator):
        assert [2] == [n for n in filter_heartbeats(filter_iterator)]


class Combiner(AbstractIterator):
    def __init__(self, *sources):
        super(Combiner, self).__init__()
        self.sources = map(Iterator, sources)
        self.next_source_number = -1

    def next(self):
        self.next_source_number = (self.next_source_number + 1) % len(self.sources)
        return self.sources[self.next_source_number].next()


class Splitter(Iterator):
    def __init__(self, source):
        super(Splitter, self).__init__(source)
        self.queue_dict = {}

    def new_iterator(self):
        splitter = Splitterator(self)
        self.queue_dict[splitter] = Queue()
        return splitter

    def next_for(self, splitterator):
        if self.queue_dict[splitterator].empty():
            message = self.next()
            for queue in self.queue_dict.values():
                queue.put(message)
        return self.queue_dict[splitterator].get()


class Splitterator(AbstractIterator):
    def __init__(self, splitter):
        super(Splitterator, self).__init__()
        self.splitter = splitter

    def next(self):
        return self.splitter.next_for(self)


@pytest.fixture(name="splitter")
def make_splitter():
    return Splitter([1, 2, 3])


class TestJunctions(object):
    def test_combiner(self):
        combiner = Combiner([1, 2, 3], [4, 5, 6])

        assert [1, 4, 2, 5, 3, 6] == [n for n in combiner]

    def test_splitter_simultaneous(self, splitter):
        list_one = []
        list_two = []

        iter1 = splitter.new_iterator()
        iter2 = splitter.new_iterator()

        for _ in range(3):
            list_one.append(iter1.next())
            list_two.append(iter2.next())

        assert list_one == [1, 2, 3]
        assert list_two == [1, 2, 3]

    def test_splitter_consecutive(self, splitter):
        iter1 = splitter.new_iterator()
        iter2 = splitter.new_iterator()

        assert [1, 2, 3] == [n for n in iter1]
        assert [1, 2, 3] == [n for n in iter2]


class TestHeartbeat(object):
    def test_filter(self, filter_iterator):
        assert [heartbeat, 2, heartbeat] == [n for n in filter_iterator]


class TestIsOn(object):
    def test_is_on(self, filter_iterator):
        filter_iterator.is_on = False
        assert [1, 2, 3] == [n for n in filter_iterator]
