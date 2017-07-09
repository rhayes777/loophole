import time
from threading import Thread

# Class called SongClock which issues a pulse for each beat

import threading


class SongClock:
    def __init__(self, bpm):
        self.bpm = bpm
        self.step = self.bpm / 60
        self.eigth_step = self.step / 8
        self.functions = []
        self.thread = Thread(target=self.run, args=())

    def run(self):
        threading.Timer(self.eigth_step, self.run).start()
        for function in self.functions:
            function()

    def add_function(self, function):
        self.functions.append(function)
