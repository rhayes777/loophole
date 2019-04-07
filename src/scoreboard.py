import pygame

import config
from control import input
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
           "W", "X", "Y", "Z"]


class Score(object):
    def __init__(self, name, value):
        self.__name = name
        self.value = value

    @property
    def name(self):
        return self.__name

    @classmethod
    def from_string(cls, string):
        name, value = string.split(",")
        return Score(name, int(value))


class Scoreboard(object):
    def __init__(self, score_path):
        self.score_path = score_path
        with open(self.score_path) as f:
            self.scores = list(map(lambda line: line.split(","), f.read().split("\n")))

    def show(self):
        position = (config.screen_shape[0] / 2, 2 * config.GAP)
        visual.make_score_notice("High Scores", position, None, visual.Color.WHITE)
        position = (position[0], position[1] + 2 * config.GAP)
        for score in self.scores:
            visual.make_score_notice(" ".join(score), position, 5, visual.Color.WHITE)
            position = (position[0], position[1] + config.GAP)


if __name__ == "__main__":
    scoreboard = Scoreboard("scores.txt")

    while True:
        scoreboard.show()
        clock.tick(24)

        input.ArcadeController.read()

        visual.draw()
