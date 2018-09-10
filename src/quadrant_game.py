import model
import pygame
from control import input
from random import randint
from visual import sprite

play = True

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

controller = input.Controller(pygame)

player = model.MassiveObject()

model_instance = model.Model(player)

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


def button_listener(button_dict):
    print(button_dict)
    global last_buttons
    new_buttons = [button for button, is_on in button_dict.items() if is_on and not last_buttons[button]]
    last_buttons = button_dict

    if len(new_buttons) > 0:
        model_instance.player.velocity = velocity_dict[new_buttons[0]]


controller.button_listener = button_listener


def rand_tuple():
    return float(randint(0, 10)), float(randint(0, 10))


for _ in range(5):
    model_instance.notes.add(model.Object(position=rand_tuple(), velocity=rand_tuple()))

# Keep reading forever
while play:
    controller.read()
    clock.tick(40)
    model_instance.step_forward()
    note = sprite.Note((player.position[0], player.position[1]), sprite.Style.Crotchet, sprite.Color.RED, randint(0, 255))
    print(note.alpha)
    sprite.draw()
    sprite.sprite_group_notes.remove(note)

    print(model_instance)
