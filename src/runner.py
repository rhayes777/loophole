import pygame

import scoreboard
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
        clock.tick(24)

        game.step_forward()

        # print_sprites()

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
