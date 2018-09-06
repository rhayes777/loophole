import model
import pygame
from control import input
from random import randint

play = True

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

controller = input.Controller(pygame)

player = model.MassiveObject()

model_instance = model.Model(player)

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

velocity_dict = {'x': (0, 0),
                 'up': (1, 0),
                 'circle': (0, 0),
                 'right': (0, 1),
                 'square': (0, 0),
                 'down': (-1, 0),
                 'triangle': (0, 0),
                 'left': (-1, 0),
                 'start': (0, 0),
                 'select': (0, 0)}


def button_listener(button_dict):
    global last_buttons
    new_buttons = [button for button, is_on in button_dict.items() if is_on and last_buttons[button]]
    last_buttons = button_dict

    if len(new_buttons) > 0:
        model_instance.player.velocity = velocity_dict[new_buttons[0]]


def rand_tuple():
    return float(randint(0, 10)), float(randint(0, 10))


notes = set()
for _ in range(100):
    notes.add(model.Object(position=rand_tuple(), velocity=rand_tuple()))

# Keep reading forever
while play:
    controller.read()
    clock.tick(40)
    model_instance.step_forward()
    print(model_instance)
