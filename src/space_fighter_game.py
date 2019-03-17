import pygame

import config
import model_space_fighter
from control import input
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

player = model_space_fighter.User()


def button_listener(button):
    if button == "centre":
        player.velocity = (0, 0)
    elif button == "left":
        player.velocity = (-config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
    elif button == "right":
        player.velocity = (config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
    elif button == "a":
        player.fire()


controller = input.ArcadeController(pygame, button_listener)

play = True

if __name__ == "__main__":
    while play:
        controller.read()
        clock.tick(24)
        player.step_forward()
        visual.player_cursor_instance.draw(player.position)

        for shot in player.shots:
            visual.Note(visual.sprite_sheet.image_for_angle(shot.angle), shot.position)

        visual.draw()
        visual.sprite_group_notes.empty()
