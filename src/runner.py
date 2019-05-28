import logging

import pygame

import config
import scoreboard
from control import controller
from space_fighter_game import space_fighter_game
from visual import font
from visual import visual

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()


def print_sprites():
    print "len(sprite_group_player) == {}".format(len(visual.sprite_group_player.sprites()))
    print "len(sprite_group_notes) == {}".format(len(visual.sprite_group_notes.sprites()))
    print "len(sprite_group_energy_glows) == {}".format(len(visual.sprite_group_energy_glows.sprites()))
    print "len(notices_list) == {}".format(len(font.notices_list))


def run_game(game):
    game.start()

    while game.should_continue:
        clock.tick(config.clockspeed_runner)
        try:
            game.step_forward()
        except Exception as e:
            logging.exception(e)
        visual.draw()
        visual.sprite_group_notes.empty()

    game.stop()


def main():
    run_count = 0
    try:
        while True:
            track_name = config.TRACK_NAMES[run_count % len(config.TRACK_NAMES)]
            game = space_fighter_game.SpaceFighterGame(track_name)
            run_game(game)
            font.notices_list = []
            scoreboard.show_scoreboard(*game.scores)
            font.notices_list = []
            run_count += 1

    except controller.QuitException:
        pygame.display.quit()
        pygame.quit()


if __name__ == "__main__":
    main()
