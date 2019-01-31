import math
from Queue import Queue
from os import path
from random import randint

import pygame

import model
from audio import player
from audio.player import note_on
from control import input
from visual import visual

note_queue = Queue()


def note_on_listener(midi_note):
    note_queue.put(midi_note)


directory = path.dirname(path.realpath(__file__))

play = True

INDENT = 50

pygame.init()
pygame.display.init()
clock = pygame.time.Clock()

track = player.Track("{}/media/song_pc.mid".format(directory), is_looping=True)
for channel in track.channels:
    channel.note_on_listener = note_on_listener

controller = input.Controller(pygame)

player = model.MassiveObject()

model_instance = model.Model(player, visual.SCREEN_SHAPE)

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
    return float(randint(0, visual.SCREEN_SHAPE[0])), float(randint(0, visual.SCREEN_SHAPE[1]))


def get_new_range_value(old_range_min, old_range_max, old_value, new_range_min, new_range_max):
    if old_value > old_range_max:
        old_value = old_range_max
    if old_value < old_range_min:
        old_value = old_range_min
    return (old_value - old_range_min) * (new_range_max - new_range_min) / (
            old_range_max - old_range_min) + new_range_min


model_instance.generators[0] = model.NoteGenerator(0, (0, visual.SCREEN_SHAPE[1] / 2), math.pi / 2)
model_instance.generators[1] = model.NoteGenerator(1, (visual.SCREEN_SHAPE[0], visual.SCREEN_SHAPE[1] / 2),
                                                   1.5 * math.pi)
model_instance.generators[2] = model.NoteGenerator(2, (visual.SCREEN_SHAPE[0] / 2, visual.SCREEN_SHAPE[1]), math.pi)
model_instance.generators[3] = model.NoteGenerator(3, (visual.SCREEN_SHAPE[0] / 2, 0), 2 * math.pi)

model_instance.scorers = {i: model.Scorer() for i in range(4)}

glow_left = visual.EnergyGlow(model_instance.generators[0].position, model_instance.generators[0].style)
glow_right = visual.EnergyGlow(model_instance.generators[1].position, model_instance.generators[1].style)
glow_down = visual.EnergyGlow(model_instance.generators[2].position, model_instance.generators[2].style)
glow_up = visual.EnergyGlow(model_instance.generators[3].position, model_instance.generators[3].style)

rotation_frame = 0

track.start()

# Keep reading forever
while play:
    rotation_frame += 1
    controller.read()
    clock.tick(40)
    model_instance.step_forward()
    visual.player_cursor_instance.draw(player.position)
    for note in model_instance.notes:
        visual.Note(visual.sprite_sheet.image_for_angle(note.angle), note.position, note.style, 255)

    while not note_queue.empty():
        model_instance.add_note(note_queue.get())

    # Collision for Score.Notice creation
    for note in model_instance.dead_notes:
        visual.make_score_notice(note.points, note.position, 30, note.style)
        visual.make_circle_explosion(visual.Color.GREY, 5, note.position)
        note_set = [65, 66, 67, 68, 69, 70, 72, 55, 58, 59, 60, 61, 62, 63]
        note_on(channel=note.note.channel, note=note.note.note, velocity=note.note.velocity)

    visual.make_score_notice(model_instance.scorers[0].score, (INDENT, visual.SCREEN_SHAPE[1] / 2), 5, 0)
    visual.make_score_notice(model_instance.scorers[1].score,
                             (visual.SCREEN_SHAPE[0] - INDENT, visual.SCREEN_SHAPE[1] / 2), 5, 1)
    visual.make_score_notice(model_instance.scorers[2].score,
                             (visual.SCREEN_SHAPE[0] / 2, visual.SCREEN_SHAPE[1] - INDENT), 5, 2)
    visual.make_score_notice(model_instance.scorers[3].score, (visual.SCREEN_SHAPE[0] / 2, INDENT), 5, 3)

    track.tempo_shift = 1 + float(model_instance.average_score) / 1000

    visual.draw()
    visual.sprite_group_notes.empty()
