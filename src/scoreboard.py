from os import path

import pygame

import config
from audio import audio
from control import controller
from visual import font
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

wait_cycles = 10
cycle = 0

letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
           "V",
           "W", "X", "Y", "Z"]

directory = path.dirname(path.realpath(__file__))


class AbstractScore(object):
    def __init__(self, value):
        self.value = int(value)
        self.title = font.HighScoreNotice(str(self), (0, 0))

    @property
    def position(self):
        return self.title.position

    @position.setter
    def position(self, position):
        self.title.position = position

    @property
    def name(self):
        raise NotImplementedError()

    def __gt__(self, other):
        return self.value > other.value

    def __str__(self):
        return "{} {}".format(self.name, self.value)


class Score(AbstractScore):
    def __init__(self, name, value):
        self.__name = name
        super(Score, self).__init__(value)

    @property
    def name(self):
        return self.__name


class NewScore(AbstractScore):

    @property
    def name(self):
        return "".join([letters[character] for character in self.characters])

    def __init__(self, value):
        self.characters = [0, 0, 0, 0]
        super(NewScore, self).__init__(value)
        self.current_index = 0

    @property
    def current_index(self):
        return self.title.highlighted_character

    @current_index.setter
    def current_index(self, current_index):
        self.title.highlighted_character = current_index

    def move_right(self):
        self.current_index = (self.current_index + 1) % len(self.characters)

    def move_left(self):
        self.current_index = (self.current_index - 1) % len(self.characters)

    def move_up(self):
        self.characters[self.current_index] = (self.characters[self.current_index] + 1) % len(letters)
        self.title.text = str(self)

    def move_down(self):
        self.characters[self.current_index] = (self.characters[self.current_index] - 1) % len(letters)
        self.title.text = str(self)


class Scoreboard(object):
    def __init__(self, score_path):
        self.score_path = score_path
        self.position = (config.screen_shape[0] / 2, 2 * config.GAP)
        self.title = font.Notice("High Scores", self.position)
        try:
            with open(self.score_path) as f:
                self.scores = list(map(lambda line: Score(*line.split(",")), f.read().split("\n")))[
                              :config.NUMBER_OF_SCORES]
            self.set_positions()
        except IOError:
            self.scores = []

    def set_positions(self):
        for i, score in enumerate(self.scores):
            score.position = self.position_for_index(i)

    def position_for_index(self, score_index):
        return self.position[0], self.position[1] + (2 + score_index) * config.GAP

    def save(self):
        with open(self.score_path, "w") as f:
            f.write("\n".join(map(lambda score: "{},{}".format(score.name, score.value), self.scores)))

    def add_score(self, new_score):
        self.scores = list(sorted(self.scores + [new_score], reverse=True))
        self.set_positions()


class Player(object):
    def __init__(self, number, score, scoreboard):
        self.number = number
        self.scoreboard = scoreboard
        self.controller = controller.ArcadeController(self.button_listener, number)
        self.score = score
        self.is_active = True
        self.is_bored = False

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
                    self.scoreboard.save()
                    self.score.current_index = None
                    self.is_active = False
        elif button == "a":
            self.is_bored = True


def show_scoreboard(player_one_score=None, player_two_score=None):
    global cycle
    scoreboard = Scoreboard("scores.txt")

    track = audio.Track("{}/media/audio/{}".format(directory, config.HIGH_SCORE_TRACK), is_looping=True,
                        play_notes=False)

    def message_read_listener(msg):
        for channel_mapper in track.channel_mappers:
            channel_mapper.send_message(msg)

    track.message_read_listener = message_read_listener
    track.start()
    players = []

    def add_player(number, score):
        new_score = NewScore(score)
        scoreboard.add_score(new_score)
        players.append(Player(number, new_score, scoreboard))

    if player_one_score is not None:
        add_player(0, player_one_score)

    if player_two_score is not None:
        add_player(1, player_two_score)

    while True:
        clock.tick(24)

        cycle += 1

        controller.ArcadeController.read()

        visual.draw()

        if any(player.is_bored for player in players) and not any(player.is_active for player in players):
            break


if __name__ == "__main__":
    show_scoreboard(1234, 5678)
