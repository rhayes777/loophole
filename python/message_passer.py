import os
from time import sleep

dirname = os.path.dirname(os.path.realpath(__file__))

FILENAME = ".message_io"

FULL_PATH = "{}/{}".format(dirname, FILENAME)


class Writer:
    def __init__(self):
        self.counter = 0
        with open(FULL_PATH, 'w') as f:
            f.write("")
        self.f = open(FULL_PATH, 'a')

    def write(self, msg):
        self.f.write("{}:{}\n".format(self.counter, msg))
        self.f.flush()
        self.counter += 1


class Reader:
    def __init__(self):
        self.counter = 0

    def read(self):
        while True:
            with open(FULL_PATH) as f:
                for line in f:
                    arr = line.split(":")
                    if int(arr[0]) == self.counter:
                        self.counter += 1
                        yield arr[1].split("\n")[0]

            sleep(0.1)
