from threading import Thread

# Class called SongClock which issues a pulse for each beat

import threading


class SongClock:
    def __init__(self, bpm):
        self.count = 0.0
        self.bpm = bpm
        self.step = float(self.bpm) / 60
        self.action_dict = {}
        self.thread = Thread(target=self.run, args=())
        self.bar = 4 * self.step
        self.half_step = self.step / 2
        self.quarter_step = self.step / 4
        self.eighth_step = self.step / 8

    def run(self):
        threading.Timer(self.eighth_step, self.run).start()
        try:
            action = self.action_dict[str(self.count)]
            self.count += self.eighth_step
            action.start()
        except KeyError:
            self.count += self.eighth_step

    def start(self):
        self.count = 0.0
        self.run()

    def add_action(self, on_function, off_function=None, length=None):
        if length is None:
            length = self.step
        self.action_dict[str(self.count)] = Action(on_function, off_function=off_function, length=length)
        self.count += length


class Action:
    def __init__(self, on_function, off_function, length):
        self.on_function = on_function
        self.off_function = off_function
        self.length = length

    def start(self):
        if self.off_function is not None:
            threading.Timer(self.length, self.off_function).start()
        self.on_function()
