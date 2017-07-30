import pygame
import logging

# Set up pygame
pygame.init()
pygame.display.init()
pygame.display.set_mode((300, 300))
clock = pygame.time.Clock()


# noinspection PyClassHasNoInit
# List of button names
class Button:
    left = 'left'
    down = 'down'
    up = 'up'
    right = 'right'
    triangle = 'triangle'
    square = 'square'
    x = 'x'
    circle = 'circle'
    select = 'select'
    start = 'start'

    all = ['left', 'down', 'up', 'right', 'triangle', 'square', 'x', 'circle', 'select', 'start']


# Object representing dancemat

class DanceMat:
    def __init__(self, number=0):
        try:
            self.joystick = pygame.joystick.Joystick(number)
            self.joystick.init()
        except pygame.error:
            logging.warn("Dancemat not found")
        self.button_listener = None

    # Read data and alert listeners
    def read(self):
        for _ in pygame.event.get():
            if self.button_listener is not None:
                button_dict = {Button.all[n]: self.joystick.get_button(n) == 1 for n in
                               range(0, self.joystick.get_numbuttons())} if self.joystick is not None else {
                    button: False for button in Button.all}
                key = pygame.key.get_pressed()
                qwerty_input = {'x': key[pygame.K_q],
                                'up': key[pygame.K_w],
                                'circle': key[pygame.K_e],
                                'right': key[pygame.K_d],
                                'square': key[pygame.K_c],
                                'down': key[pygame.K_x],
                                'triangle': key[pygame.K_z],
                                'left': key[pygame.K_a]}
                for k in qwerty_input.keys():
                    if qwerty_input[k]:
                        button_dict[k] = True
                self.button_listener(button_dict)

    # Sets a listener that is alerted to any button press or depress
    def set_button_listener(self, button_listener):
        self.button_listener = button_listener
