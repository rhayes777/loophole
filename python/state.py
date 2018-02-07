import effect
import player
import messaging
import signal
import dancemat
import logging

logging.basicConfig()

logger = logging.getLogger(__name__)


def note_on_listener(msg):
    messaging.write(messaging.MidiMessage(msg))


def create_track_and_combinator(track_path, configuration_path):
    track = player.Track(track_path, is_looping=True)
    combinator = effect.Combinator(configuration_path, track)
    for channel in track.channels:
        channel.note_on_listener = note_on_listener
    return track, combinator


class State(object):
    def __init__(self, configuration_path):
        signal.signal(signal.SIGINT, self.stop)

        self.configuration_path = configuration_path
        self.track_path = None
        self.track = None
        self.combinator = None
        self.no_button_presses = 0

        self.last_on_buttons = []

    def change_to_track_with_name(self, track_name):
        self.track_path = "media/{}".format(track_name)
        self.track, self.combinator = create_track_and_combinator(self.track_path, self.configuration_path)

    def stop(self):
        if self.track is not None:
            self.track.stop()
        if self.combinator is not None:
            self.combinator.stop()

    def start(self):
        if self.track is not None:
            self.track.start()
        else:
            logger.warn("Tried to start track that is None")

    def did_receive_status_dict(self, status_dict):
        on_buttons = [button for (button, is_on) in status_dict.iteritems() if is_on]
        new_on_buttons = filter(lambda b: b not in self.last_on_buttons, on_buttons)
        self.last_on_buttons = on_buttons

        self.did_receive_on_buttons(on_buttons)
        self.did_receive_new_on_buttons(new_on_buttons)

    def did_receive_on_buttons(self, buttons):
        self.combinator.apply_for_buttons(buttons)

    # noinspection PyMethodMayBeStatic
    def did_receive_new_on_buttons(self, buttons):
        for button in buttons:
            messaging.write(messaging.ButtonMessage(button))
            self.no_button_presses += 1


class Normal(State):
    def __init__(self, configuration_path, track_names):
        super(Normal, self).__init__(configuration_path)

        self.track_number = 0
        self.track_names = track_names

    @property
    def selected_track_name(self):
        return self.track_names[self.track_number % len(self.track_names)]

    def did_receive_on_buttons(self, buttons):
        super(Normal, self).did_receive_on_buttons(buttons)
        if dancemat.Button.start in buttons:
            self.track_number += 1
            if self.track is not None:
                self.track.stop()
            self.change_to_track_with_name(self.selected_track_name)
            self.track.start()
        elif dancemat.Button.select in buttons:
            self.track_number -= 1
            if self.track is not None:
                self.track.stop()
            self.change_to_track_with_name(self.selected_track_name)
            self.track.start()
        else:
            super(Normal, self).did_receive_on_buttons(buttons)

    def did_receive_new_on_buttons(self, buttons):
        super(Normal, self).did_receive_new_on_buttons(buttons)
        if len(buttons) > 0:
            player.set_program(15, program=116)
            player.note_on(15, velocity=127)


class Accelerate(Normal):
    def __init__(self, configuration_path, track_names, rate=0.1):
        super(Accelerate, self).__init__(configuration_path, track_names)
        self.rate = rate

    def did_receive_new_on_buttons(self, buttons):
        super(Accelerate, self).did_receive_new_on_buttons(buttons)
        self.track.tempo_shift = 1 + self.rate * self.no_button_presses
