import pygame

# Set up pygame
pygame.init()
pygame.display.init()
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
        self.joystick = pygame.joystick.Joystick(number)
        self.joystick.init()
        self.listener_dict = {}
        self.button_listener = None

    # Read data and alert listeners
    def read(self):
        for event in pygame.event.get():
            for n in range(0, self.joystick.get_numbuttons()):
                is_on = self.joystick.get_button(n) == 1
                button = Button.all[n]
                if button in self.listener_dict:
                    self.listener_dict[n](is_on)
                if self.button_listener is not None:
                    self.button_listener(button, is_on)

    # Adds a listener to listen for a specific button being pressed or depressed
    def add_listener_to_button(self, button, listener):
        self.listener_dict[button] = listener

    # Sets a listener that is alerted to any button press or depress
    def set_button_listener(self, button_listener):
        self.button_listener = button_listener
