import time
from threading import Thread

# Class called SongClock which issues a pulse for each beat

import threading


class SongClock:
    def __init__(self, bpm):
        self.bpm = bpm
        self.step = self.bpm / 60
        self.functions = []
        self.thread = Thread(target=self.run, args=())

    def run(self):
        while 1:
            time.sleep(self.step)
            print "running functions"
            for function in self.functions:
                function()

    def start(self):
        threading.Timer(self.step, self.run).start()

    def add_function(self, function):
        self.functions.append(function)
