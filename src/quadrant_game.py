import model
import pygame
from control import input
from random import randint
import math
from visual import sprite

play = True

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

controller = input.Controller(pygame)

player = model.MassiveObject()

model_instance = model.Model(player, sprite.SCREEN_SHAPE)

model_instance.player.position = (sprite.SCREEN_SHAPE[0] / 2, sprite.SCREEN_SHAPE[1] / 2)

last_buttons = {'x': False,
                'up': False,
                'circle': False,
                'right': False,
                'square': False,
                'down': False,
                'triangle': False,
                'left': False,
                'start': False,
                'select': False}

velocity_dict = {'x': (-15, -15),
                 'up': (0, -15),
                 'circle': (15, -15),
                 'right': (15, 0),
                 'square': (15, 15),
                 'down': (0, 15),
                 'triangle': (-15, 15),
                 'left': (-15, 0),
                 'start': (0, 0),
                 'select': (0, 0)}

boost_dict = {'x': (-1, -1),
              'up': (0, -1),
              'circle': (1, -1),
              'right': (1, 0),
              'square': (1, 1),
              'down': (0, 1),
              'triangle': (-1, 1),
              'left': (-1, 0),
              'start': (0, 0),
              'select': (0, 0)}


def button_listener(button_dict):
    global last_buttons
    new_buttons = [button for button, is_on in button_dict.items() if is_on and not last_buttons[button]]
    last_buttons = button_dict

    if len(new_buttons) > 0:
        model_instance.boost(boost_dict[new_buttons[0]])


controller.button_listener = button_listener


def rand_tuple():
    return float(randint(0, sprite.SCREEN_SHAPE[0])), float(randint(0, sprite.SCREEN_SHAPE[1]))


# for _ in range(10):
#     model_instance.notes.add(model.Object(position=rand_tuple()))

model_instance.generators[0] = model.NoteGenerator(0, (0, sprite.SCREEN_SHAPE[1] / 2), 0, math.pi)
model_instance.generators[1] = model.NoteGenerator(1, (sprite.SCREEN_SHAPE[0], sprite.SCREEN_SHAPE[1] / 2), math.pi,
                                                   2 * math.pi)
model_instance.generators[2] = model.NoteGenerator(2, (sprite.SCREEN_SHAPE[0] / 2, sprite.SCREEN_SHAPE[1]), math.pi / 2,
                                                   (3 / 2) * math.pi)
model_instance.generators[3] = model.NoteGenerator(3, (sprite.SCREEN_SHAPE[0] / 2, 0), (3 / 2) * math.pi,
                                                   (5 / 2) * math.pi)

style = 0

# Keep reading forever
while play:
    style = (style + 1) % 4
    controller.read()
    clock.tick(40)
    model_instance.step_forward()
    sprite.Note(player.position, sprite.Style.Crotchet, randint(0, 255))
    for note in model_instance.notes:
        sprite.Note(note.position, note.style, 255)

    model_instance.add_note(style)

    sprite.draw()
    sprite.sprite_group_notes.empty()
