import logging

import pygame


# List of button names
class Button(object):
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


class AbstractController(object):
    def __init__(self, number=0):
        try:
            self.number = number
            self.joystick = pygame.joystick.Joystick(number)
            self.joystick.init()
        except pygame.error:
            logging.warning("Controller {} not found".format(number))


class ArcadeController(AbstractController):
    controllers = {}

    def __init__(self, button_listener, number=0):
        super(ArcadeController, self).__init__(number=number)
        self.button_listener = button_listener
        ArcadeController.controllers[number] = self

    @classmethod
    def read(cls):
        for event in pygame.event.get():
            print(event)
            if hasattr(event, "joy"):
                ArcadeController.controllers[event.joy].on_event(event)

    def on_event(self, event):
        if event.type == 7:
            value = int(event.value)
            if value == 0:
                self.button_listener("centre")
            else:
                if event.axis == 1:
                    if value == -1:
                        self.button_listener("up")
                    else:
                        self.button_listener("down")
                else:
                    if value == -1:
                        self.button_listener("left")
                    else:
                        self.button_listener("right")
        elif event.type == 10:
            if event.button == 0:
                self.button_listener("a")
            elif event.button == 1:
                self.button_listener("b")
        elif event.type == 11:
            # Button up
            pass


# Object representing a midi controller input (e.g. a dancemat)
class Controller(AbstractController):
    def __init__(self, number=0):
        super(Controller, self).__init__(number)
        self.button_listener = None

    # Read data and alert listeners
    def read(self):
        for _ in pygame.event.get():
            if self.button_listener is not None:
                try:
                    print self.joystick.get_numbuttons()
                    button_dict = {Button.all[n]: self.joystick.get_button(n) == 1 for n in
                                   range(0, self.joystick.get_numbuttons())}
                except AttributeError:
                    button_dict = {button: False for button in Button.all}
                key = pygame.key.get_pressed()
                print key
                qwerty_input = {'x': key[pygame.K_q],
                                'up': key[pygame.K_w],
                                'circle': key[pygame.K_e],
                                'right': key[pygame.K_d],
                                'square': key[pygame.K_c],
                                'down': key[pygame.K_x],
                                'triangle': key[pygame.K_z],
                                'left': key[pygame.K_a],
                                'start': key[pygame.K_1],
                                'select': key[pygame.K_3]}
                for k in qwerty_input.keys():
                    if qwerty_input[k]:
                        button_dict[k] = True
                self.button_listener(button_dict)

    # Sets a listener that is alerted to any button press or depress
    def set_button_listener(self, button_listener):
        self.button_listener = button_listener
