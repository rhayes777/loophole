from Queue import Queue
from os import path

import pygame

import config
import model_space_fighter
import scoreboard
from audio import audio as pl
from control import controller
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

directory = path.dirname(path.realpath(__file__))


class SpaceFighterGame(object):
    def __init__(self):
        self.note_queue = Queue()
        self.model = model_space_fighter.SpaceFighterModel()
        self.players = [Player(n, self.model.new_player()) for n in range(2)]

        self.track = pl.Track("{}/../media/audio/{}".format(directory, config.TRACK_NAME), is_looping=True,
                              message_read_listener=self.message_read_listener, play_notes=True)

    def message_read_listener(self, msg):
        if msg.type == "note_on":
            self.note_queue.put(msg)

    def start(self):
        self.track.start()

    def stop(self):
        self.track.stop()

    def step_forward(self):
        self.model.step_forward()

        while not self.note_queue.empty():
            self.model.add_note(self.note_queue.get())

        controller.ArcadeController.read()
        for player in self.players:
            player.step()

        for alien in self.model.aliens:
            visual.Note(visual.sprite_sheet.image_for_angle(alien.angle), alien.position)

    @property
    def should_continue(self):
        return not any(player.model_player.score == 50 for player in self.players)

    @property
    def scores(self):
        return (player.model_player.score for player in self.players)


class Player(object):
    def __init__(self, number, model_player):
        self.is_started = False
        self.number = number
        self.controller = controller.ArcadeController(self.button_listener, number)
        self.model_player = model_player
        self.cursor = None
        self.start_position = config.PLAYER_ONE_START if number == 0 else config.PLAYER_TWO_START
        self.model_player.position = self.start_position
        self.color = visual.Color.WHITE

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.number)

    def button_listener(self, button):
        if self.is_started:
            if button == "centre":
                self.model_player.velocity = (0, 0)
            elif button == "left":
                self.model_player.velocity = (-config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
            elif button == "right":
                self.model_player.velocity = (config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
            elif button == "a":
                self.model_player.fire()
        elif button != "centre":
            self.is_started = True
            self.cursor = visual.PlayerCursor()
            self.button_listener(button)

    def step(self):
        if self.is_started:
            self.cursor.draw(self.model_player.position)
            for shot in self.model_player.shots:
                visual.Note(visual.sprite_sheet.image_for_angle(shot.angle), shot.position, colour=self.color)
            visual.make_score_notice(self.model_player.score, self.start_position, 5, self.color)
        else:
            visual.make_score_notice("Player {} start".format(self.number + 1), self.start_position, 5, self.color)


play = True

game = SpaceFighterGame()
game.start()

if __name__ == "__main__":
    while game.should_continue:
        clock.tick(24)

        game.step_forward()

        visual.draw()
        visual.sprite_group_notes.empty()

    game.stop()
    scoreboard.show_scoreboard(*game.scores)