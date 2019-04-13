import pygame

import config
from control import controller
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
           "V",
           "W", "X", "Y", "Z"]


class AbstractScore(object):
    def __init__(self, value):
        self.value = int(value)

    @property
    def name(self):
        raise NotImplementedError()

    def __gt__(self, other):
        return self.value > other.value

    def __str__(self):
        return "{} {}".format(self.name, self.value)


class Score(AbstractScore):
    def __init__(self, name, value):
        super(Score, self).__init__(value)
        self.__name = name

    @property
    def name(self):
        return self.__name


class NewScore(AbstractScore):

    @property
    def name(self):
        return "".join([letters[character] for character in self.characters])

    def __init__(self, value):
        super(NewScore, self).__init__(value)
        self.characters = [0, 0, 0, 0, 0]
        self.current_index = 0

    def move_right(self):
        self.current_index = (self.current_index + 1) % len(self.characters)

    def move_left(self):
        self.current_index = (self.current_index - 1) % len(self.characters)

    def move_up(self):
        self.characters[self.current_index] = (self.characters[self.current_index] + 1) % len(letters)

    def move_down(self):
        self.characters[self.current_index] = (self.characters[self.current_index] - 1) % len(letters)


class Scoreboard(object):
    def __init__(self, score_path):
        self.score_path = score_path
        with open(self.score_path) as f:
            self.scores = list(map(lambda line: Score(*line.split(",")), f.read().split("\n")))

    def show(self):
        position = (config.screen_shape[0] / 2, 2 * config.GAP)
        visual.make_score_notice("High Scores", position, None, visual.Color.WHITE)
        position = (position[0], position[1] + 2 * config.GAP)
        for score in self.scores:
            visual.make_score_notice(str(score), position, 5, visual.Color.WHITE)
            position = (position[0], position[1] + config.GAP)

    def add_score(self, new_score):
        self.scores = list(sorted(self.scores + [new_score], reverse=True))


if __name__ == "__main__":
    scoreboard = Scoreboard("scores.txt")
    new_score = NewScore(1234)
    scoreboard.add_score(new_score)


    def button_listener(button):
        if button == "up":
            new_score.move_up()
        elif button == "down":
            new_score.move_down()
        elif button == "left":
            new_score.move_left()
        elif button == "right":
            new_score.move_right()
        elif button == "a":
            pass


    cont = controller.ArcadeController(button_listener)

    while True:
        scoreboard.show()
        clock.tick(24)

        controller.ArcadeController.read()

        visual.draw()
