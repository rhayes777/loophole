import time, math

## Class called SongClock which issues a pulse for each beat

class SongClock:

    def __init__(self, bpm, tick, state):
        self.bpm = bpm
        self.step = self.bpm / 60
        self.tick = tick
        self.state = 0

    def update(self):

        if(self.tick<15):
            self.tick = self.tick + 1

        else :
            self.tick = 0


        time.sleep(self.step)

        print(self.tick)


