import pygame

import scoreboard
from space_fighter_game import space_fighter_game
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()


def run_game(game):
    game.start()

    while game.should_continue:
        clock.tick(24)

        game.step_forward()

        visual.draw()
        visual.sprite_group_notes.empty()

    game.stop()


def main():
    while True:
        game = space_fighter_game.SpaceFighterGame()
        run_game(game)
        scoreboard.show_scoreboard(*game.scores)


if __name__ == "__main__":
    main()
