from Queue import Queue
from os import path

import pygame

import config
import model_space_fighter
from audio import player as pl
from control import input
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

directory = path.dirname(path.realpath(__file__))

player = model_space_fighter.Player()
model = model_space_fighter.SpaceFighterModel()
model.add_player(player)


def button_listener(button):
    print(button)
    if button == "centre":
        player.velocity = (0, 0)
    elif button == "left":
        player.velocity = (-config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
    elif button == "right":
        player.velocity = (config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
    elif button == "a":
        player.fire()


note_queue = Queue()


def message_read_listener(msg):
    if msg.type == "note_on":
        note_queue.put(msg)


track = pl.Track("{}/media/audio/{}".format(directory, config.TRACK_NAME), is_looping=True,
                 message_read_listener=message_read_listener, play_notes=False)

controller = input.ArcadeController(pygame, button_listener)

play = True

track.start()

if __name__ == "__main__":
    while play:
        controller.read()
        clock.tick(24)
        model.step_forward()

        while not note_queue.empty():
            model.add_note(note_queue.get())

        for player in model.players:
            visual.player_cursor_instance.draw(player.position)
            for shot in player.shots:
                visual.Note(visual.sprite_sheet.image_for_angle(shot.angle), shot.position)

        for alien in model.aliens:
            model.add_note(alien.note)

        visual.draw()
        visual.sprite_group_notes.empty()
