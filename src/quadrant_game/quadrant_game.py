import copy
import math
from Queue import Queue
from os import path
from random import randint

import pygame

import config
import model
import model_quadrant_game
import visual.color
from audio import audio as pl
from audio.audio import play_note
from control import controller
from visual import visual

note_queue = Queue()


def message_read_listener(msg):
    if msg.type == "note_on":
        note_queue.put(msg)


directory = path.dirname(path.realpath(__file__))

play = True

pygame.init()
# midi.init()
pygame.display.init()
clock = pygame.time.Clock()

track = pl.Track("{}/media/audio/{}".format(directory, config.TRACK_NAME), is_looping=True,
                 message_read_listener=message_read_listener, play_notes=False)

player = model_quadrant_game.MassiveObject()

model_instance = model_quadrant_game.Model(player, visual.SCREEN_SHAPE)

model_instance.player.position = (visual.SCREEN_SHAPE[0] / 2, visual.SCREEN_SHAPE[1] / 2)

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


def button_listener(button):
    if button == "centre":
        return
    model_instance.boost(boost_dict[button])


controller = controller.ArcadeController(pygame, button_listener)


def rand_tuple():
    return float(randint(0, visual.SCREEN_SHAPE[0])), float(randint(0, visual.SCREEN_SHAPE[1]))


def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    if old_value > old_range_max:
        old_value = old_range_max
    if old_value < old_range_min:
        old_value = old_range_min
    return (old_value - old_range_min) * (new_range_max - new_range_min) / (
            old_range_max - old_range_min) + new_range_min


state_limits = list(map(int, config.parser.get("general", "state_limits").split(",")))
debug = "t" in config.parser.get("general", "debug").lower()


class Side(object):
    def __init__(self, name, position, direction, colour):
        self.name = name
        self.generator = model_quadrant_game.NoteGenerator(position, direction)
        self.position = position
        self.direction = direction
        self.output_channel = int(config.parser.get(self.name, "output_channel"))
        self.colour = colour
        self.glow = visual.EnergyGlow(position, colour)
        self.scorer = model.Scorer()
        self.channels = list(map(int, config.parser.get(self.name, "channels").split(",")))

    @property
    def state(self):
        index = 0
        while True:
            try:
                if self.scorer.score < state_limits[index]:
                    return index
                index += 1
            except IndexError:
                return index

    def update(self):
        visual.make_score_notice(self.scorer.score, self.position, 5, self.colour)
        self.glow.set_alpha(min(255, self.scorer.score))
        if debug:
            visual.make_score_notice(10 * self.state, self.position, 5, visual.color.Color.WHITE)

    def add_note(self, side_note):
        if side_note.channel == self.channels[self.state]:
            model_instance.notes.add(self.generator.make_note(side_note, self.colour))
            side_note.channel = self.output_channel
            track.channels[self.output_channel].send_message(side_note)


# class DrumSide(Side):
#     def add_note(self, side_note):
#         if side_note.channel % 4 == self.state:
#             model_instance.notes.add(self.generator.make_note(side_note, self.colour))
#             track.channels[10].send_message(side_note)


sides = [
    Side("bass", (config.INDENT, visual.config.screen_shape[1] / 2), math.pi / 2, visual.color_dict[0]),
    Side("drums", (visual.config.screen_shape[0] - config.INDENT, visual.config.screen_shape[1] / 2), 1.5 * math.pi,
         visual.color_dict[1]),
    Side("guitar", (visual.config.screen_shape[0] / 2, visual.config.screen_shape[1] - config.INDENT), math.pi,
         visual.color_dict[2]),
    Side("keys", (visual.config.screen_shape[0] / 2, config.INDENT), 2 * math.pi, visual.color_dict[3]),
]

for side in sides:
    model_instance.generators.append(side.generator)
    model_instance.scorers.append(side.scorer)

rotation_frame = 0

track.start()

# Keep reading forever
while play:
    rotation_frame += 1
    controller.read()
    clock.tick(24)
    model_instance.step_forward()
    visual.player_cursor_instance.draw(player.position)
    for note in model_instance.notes:
        visual.Note(visual.sprite_sheet.image_for_angle(note.angle), note.position, note.colour, 255)

    while not note_queue.empty():
        note = note_queue.get()
        for side in sides:
            if note.channel in side.channels:
                side.add_note(note)

    # Collision for Score.Notice creation
    for note in model_instance.dead_notes:
        for side in sides:
            if note.note.channel in side.channels:
                side.scorer.add_points(config.POINTS_PER_NOTE)

        visual.make_score_notice(config.POINTS_PER_NOTE, note.position, 30, note.colour)
        visual.make_circle_explosion(visual.color.Color.GREY, 5, note.position)

        midi_note = copy.copy(note.note)
        midi_note.channel = 9
        midi_note.time = 0
        play_note(midi_note)

    for side in sides:
        side.update()

    visual.draw()
    visual.sprite_group_notes.empty()
