import effect
import player
import messaging
import signal
import dancemat


def note_on_listener(msg):
    messaging.write(messaging.MidiMessage(msg))


def create_track_and_combinator(track_path, configuration_path):
    track = player.Track(track_path, is_looping=True)
    combinator = effect.Combinator(configuration_path)
    for channel in track.channels:
        channel.note_on_listener = note_on_listener
    return track, combinator


class Mode(object):
    def __init__(self, track_path, configuration_path):
        signal.signal(signal.SIGINT, self.stop)

        self.configuration_path = configuration_path
        self.track_path = track_path
        self.track, self.combinator = create_track_and_combinator(self.track_path, self.configuration_path)

        self.last_on_buttons = []

    def change_to_track_with_name(self, track_name):
        self.track_path = "media/{}".format(track_name)
        self.track, self.combinator = create_track_and_combinator(self.track_path, self.configuration_path)

    def stop(self):
        self.track.stop()
        self.combinator.stop()

    def start(self):
        self.track.start()

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


class Normal(Mode):
    def __init__(self, track_path, configuration_path, track_names):
        super(Normal, self).__init__(track_path, configuration_path)

        self.track_number = 0
        self.track_names = track_names

    @property
    def selected_track_name(self):
        return self.track_names[self.track_number % len(self.track_names)]

    def did_receive_on_buttons(self, buttons):
        super(Normal, self).did_receive_on_buttons(buttons)
        if dancemat.Button.start in buttons:
            self.track_number += 1
            self.track.stop()
            self.change_to_track_with_name(self.selected_track_name)
            self.track.start()
        elif dancemat.Button.select in buttons:
            self.track_number -= 1
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
