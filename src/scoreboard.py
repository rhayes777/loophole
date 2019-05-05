import pygame

import config
from control import controller
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

wait_cycles = 10
cycle = 0

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

    def save(self):
        with open(self.score_path, "w") as f:
            f.write("\n".join(map(lambda score: "{},{}".format(score.name, score.value), self.scores)))

    def show(self):
        position = (config.screen_shape[0] / 2, 2 * config.GAP)
        visual.make_score_notice("High Scores", position, None, visual.Color.WHITE)
        position = (position[0], position[1] + 2 * config.GAP)
        for score in self.scores:
            visual.make_score_notice(str(score), position, 5, visual.Color.WHITE)
            position = (position[0], position[1] + config.GAP)

    def add_score(self, new_score):
        self.scores = list(sorted(self.scores + [new_score], reverse=True))


scoreboard = Scoreboard("scores.txt")
players = []


class Player(object):
    def __init__(self, number, score):
        self.number = number
        self.controller = controller.ArcadeController(self.button_listener, number)
        self.score = score
        self.is_active = True

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.number)

    def button_listener(self, button):
        if self.is_active:
            if button == "up":
                self.score.move_up()
            elif button == "down":
                self.score.move_down()
            elif button == "left":
                self.score.move_left()
            elif button == "right":
                self.score.move_right()
            elif button == "a":
                if cycle > wait_cycles:
                    scoreboard.save()
                    self.is_active = False



def show_scoreboard(player_one_score=None, player_two_score=None):
    global players
    global cycle
    players = []

    def add_player(number, score):
        new_score = NewScore(score)
        scoreboard.add_score(new_score)
        players.append(Player(number, new_score))

    if player_one_score is not None:
        add_player(0, player_one_score)

    if player_two_score is not None:
        add_player(1, player_two_score)

    while True:
        scoreboard.show()
        clock.tick(24)

        cycle += 1

        controller.ArcadeController.read()

        visual.draw()


if __name__ == "__main__":
    show_scoreboard(1234, 5678)
