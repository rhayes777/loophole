import pygame

import model_space_fighter
from control import input
from visual import visual
import config

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


controller = input.ArcadeController(pygame, button_listener)

play = True


if __name__ == "__main__":
    while play:
        controller.read()
        clock.tick(24)
        player.step_forward()
        visual.player_cursor_instance.draw(player.position)
        visual.draw()
