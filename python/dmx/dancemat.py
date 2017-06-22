import pygame

pygame.init()


# noinspection PyClassHasNoInit
class Button:
    left = 'left'
    down = 'down'
    up = 'up'
    right = 'right'
    triangle = 'triangle'
    square = 'square'
    x = 'x'
    circle = 'circle'


button_list = ['left', 'down', 'up', 'right', 'triangle', 'square', 'x', 'circle']


class DanceMat:
    def __init__(self, number=0):
        self.joystick = pygame.joystick.Joystick(number)
        self.joystick.init()
        self.listener_dict = {}
        self.button_listener = None

    def read(self):
        for event in pygame.event.get():
            for n in range(0, self.joystick.get_numbuttons()):
                if self.joystick.get_button(n):
                    button = button_list[n]
                    if button in self.listener_dict:
                        self.listener_dict[n]()
                    if self.button_listener is not None:
                        self.button_listener(button)

    def add_listener_to_button(self, button, listener):
        self.listener_dict[button] = listener

    def set_button_listener(self, button_listener):
        self.button_listener = button_listener
