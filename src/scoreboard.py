import pygame

import config
from control import input
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()


class Scoreboard(object):
    def __init__(self, score_path):
        self.score_path = score_path
        with open(self.score_path) as f:
            self.scores = list(map(lambda line: line.split(","), f.read().split("\n")))

    def show(self):
        position = (config.screen_shape[0] / 2, config.GAP)
        visual.make_score_notice("High Scores", position, None, visual.Color.WHITE)
        for score in self.scores:
            position = (position[0], position[1] + config.GAP)
            print score
            print position

            visual.make_score_notice("{} {}".join(score), position, None, visual.Color.WHITE)


if __name__ == "__main__":
    Scoreboard("scores.txt").show()
    while True:
        clock.tick(24)

        input.ArcadeController.read()

        visual.draw()
