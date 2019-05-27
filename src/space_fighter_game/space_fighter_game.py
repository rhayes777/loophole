from Queue import Queue
from os import path

import config
import model_space_fighter
import visual.color
from audio import audio as pl
from control import controller
from visual import color
from visual import font
from visual import visual

directory = path.dirname(path.realpath(__file__))

COLORS = [color.Color.FLIRT, color.Color.KEEN, color.Color.LIGHTNING, color.Color.SHAKA]


class SpaceFighterGame(object):
    def __init__(self, track_name):
        self.note_queue = Queue()
        self.model = model_space_fighter.SpaceFighterModel()
        self.players = [Player(n, self.model.new_player()) for n in range(2)]

        self.track = pl.Track("{}/../media/audio/{}".format(directory, track_name), is_looping=True,
                              message_read_listener=self.message_read_listener, play_notes=False)

    def message_read_listener(self, msg):
        if msg.type == "note_on" and msg.channel in self.track.current_channels:
            self.note_queue.put(msg)
        for channel_mapper in self.track.channel_mappers:
            channel_mapper.send_message(msg)

    def start(self):
        self.track.start()

    def stop(self):
        self.track.stop()

    def step_forward(self):
        self.model.step_forward()

        while not self.note_queue.empty():
            self.model.add_note(self.note_queue.get())

        controller.ArcadeController.read()
        for player in self.players:
            player.step()

        for alien in self.model.aliens:
            visual.Note(visual.note_sprite_sheet.image_for_angle(alien.angle), alien.position,
                        colour=COLORS[self.track.output_channels.index(alien.note.channel)])

        for mapper in self.track.channel_mappers:
            mapper.mode = self.mode
            self.track.tempo_shift = [1, 1.1, 1.5, 2][self.mode]
            for channel in self.track.channels:
                channel.pitch_bend = [1, 1.1, 1.3, 1.5]

    @property
    def mode(self):
        return min(3, self.max_score / 100)

    @property
    def max_score(self):
        try:
            return max(player.model_player.score for player in self.started_players)
        except ValueError:
            return 0

    @property
    def started_players(self):
        return [player for player in self.players if player.is_started]

    @property
    def should_continue(self):
        if len(self.started_players) == 0:
            return True
        return not all(player.is_dead for player in self.started_players)

    @property
    def scores(self):
        return (player.model_player.score for player in self.started_players)


class Player(object):
    def __init__(self, number, model_player):
        self.number = number
        self.controller = controller.ArcadeController(self.button_listener, number)
        self.model_player = model_player
        self.cursor = None
        self.start_position = config.PLAYER_ONE_START if number == 0 else config.PLAYER_TWO_START
        self.model_player.position = self.start_position
        self.color = color.Color.KEEN if number == 0 else color.Color.FLIRT
        self.score_notice = font.Notice(
            "Player {} start".format(
                self.number + 1
            ),
            self.start_position,
            self.color
        )
        self.lives_notice = font.Notice(
            "",
            self.lives_position,
            color.Color.RED
        )

    @property
    def is_started(self):
        return self.model_player.is_started

    @is_started.setter
    def is_started(self, is_started):
        self.model_player.is_started = is_started

    @property
    def lives_position(self):
        return self.start_position[0] + config.LIVES_OFFSET, self.start_position[1]

    @property
    def is_dead(self):
        return self.model_player.lives <= 0

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.number)

    def button_listener(self, button):
        if self.is_started:
            if button == "centre":
                self.model_player.velocity = (0, 0)
            elif button == "left":
                self.model_player.velocity = (-config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
            elif button == "right":
                self.model_player.velocity = (config.SPACE_FIGHTER_PLAYER_VELOCITY, 0)
            elif button == "a":
                self.model_player.fire()
        elif button != "centre":
            self.is_started = True
            self.cursor = visual.PlayerCursor()
            self.button_listener(button)

    def step(self):
        if self.is_dead:
            self.score_notice.text = "DEAD"
            self.score_notice.color = color.Color.RED
            self.lives_notice.should_blit = False
            self.cursor.remove()
        elif self.is_started:
            self.cursor.draw(self.model_player.position)
            for shot in self.model_player.shots:
                visual.Note(
                    visual.bullet_sprite_sheet.image_for_angle(shot.angle),
                    (
                        shot.position[0] - visual.bullet_sprite_sheet.shape[0] / 2,
                        shot.position[1] - visual.bullet_sprite_sheet.shape[1] / 2
                    ),
                    colour=self.color
                )
            self.score_notice.text = str(self.model_player.score)
            self.lives_notice.text = str(self.model_player.lives)
