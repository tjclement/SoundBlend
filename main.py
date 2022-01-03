import sys
import midi
from sounds import Player, PlayMode, SoundProperties, get_output_devices
from PyQt5.QtWidgets import QApplication

from main_ui import MainUI

updating_ui = False


class Controller:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ui = MainUI()

        self.midi_inputs = None
        self.sound_outputs = None
        self.updating_ui = False
        self.active_note = 60

        self.player = None  # Type: Optional[Player]
        self.midi_device = None  # Type: Optional[MidiDevice]

        self.update_inputs_outputs()
        self.ui_set_devices()
        self.set_input_device()
        self.set_output_device()

        self.ui.on_settings_change(self.update_props)
        self.ui.on_grid_press(self.ui_button_handler)
        self.ui.choice_inputs.currentIndexChanged.connect(self.set_input_device)
        self.ui.choice_outputs.currentIndexChanged.connect(self.set_output_device)

    def update_inputs_outputs(self):
        self.midi_inputs, _ = midi.get_devices()
        self.sound_outputs = get_output_devices()

    def ui_set_devices(self):
        self.ui.choice_inputs.clear()
        self.ui.choice_inputs.addItems([device.name.decode("utf-8") for device in self.midi_inputs])
        self.ui.choice_outputs.clear()
        self.ui.choice_outputs.addItems([device["name"] for device in self.sound_outputs])

    def set_output_device(self):
        index = self.ui.choice_outputs.currentIndex()
        if index < 0 or index >= len(self.sound_outputs):
            return
        output = self.sound_outputs[index]
        if self.player is not None:
            self.player.stop()
        self.player = Player(output)

        if self.midi_device is not None:
            self.midi_device.add_callback(self.player.callback)

        # TODO: change this to load from and save to a profile file
        self.player.register_sounds([
            {"on_note": 0x3C, "mode": PlayMode.HOLD, "path": "/Users/tom/Downloads/soundboard/applause.mp3",
             "fade_in": 300, "fade_out": 300},
            {"on_note": 0x3D, "mode": PlayMode.TOGGLE, "path": "/Users/tom/Downloads/soundboard/i-feel-good.mp3"},
            {"on_note": 0x3E, "mode": PlayMode.HOLD, "path": "/Users/tom/Downloads/soundboard/cricket-sound.mp3"},
            {"on_note": 0x3F, "mode": PlayMode.MULTI, "path": "/Users/tom/Downloads/soundboard/doh.mp3", "gain": -9},
            {"on_note": 0x40, "mode": PlayMode.MULTI, "path": "/Users/tom/Downloads/soundboard/anime-wow.mp3"},
        ])

    def set_input_device(self):
        index = self.ui.choice_inputs.currentIndex()
        if index < 0 or index >= len(self.midi_inputs):
            return
        device = self.midi_inputs[index]
        self.midi_device = midi.MidiConnection(device.id)
        self.midi_device.add_callback(self.midi_button_handler)

        if self.player is not None:
            self.midi_device.add_callback(self.player.callback)

        self.ui.on_tick(self.midi_device.handle_events)

    def update_ui(self):
        if self.active_note not in self.player.registered_sounds:
            return
        props = self.player.registered_sounds[self.active_note]
        self.updating_ui = True
        self.ui.input_path.setText(props.path or "")
        self.ui.input_on_note.setText(str(props.on_note) or "60")
        self.ui.choice_play_mode.setCurrentText(props.mode.value or PlayMode.MULTI)
        self.ui.input_gain.setValue(props.gain or 0.0)
        self.ui.input_fade_in.setValue(props.fade_in or 100)
        self.ui.input_fade_out.setValue(props.fade_out or 100)
        self.ui.check_remove_silence.setChecked(props.remove_silence or True)
        self.ui.check_loop.setChecked(props.loop or False)
        self.ui.input_skip_start.setValue(props.skip_start or 0)
        self.ui.input_skip_end.setValue(props.skip_end or 0)
        self.updating_ui = False

    def update_props(self):
        if self.updating_ui or self.active_note not in self.player.registered_sounds:
            return

        props = self.player.registered_sounds[self.active_note]
        props.path = self.ui.input_path.text()
        props.on_note = int(self.ui.input_on_note.text(), 10)
        props.mode = PlayMode.from_string(self.ui.choice_play_mode.currentText())
        props.gain = float(self.ui.input_gain.value())
        props.fade_in = int(self.ui.input_fade_in.value())
        props.fade_out = int(self.ui.input_fade_out.value())
        props.remove_silence = self.ui.check_remove_silence.isChecked()
        props.loop = self.ui.check_loop.isChecked()
        props.skip_start = int(self.ui.input_skip_start.value())
        props.skip_end = int(self.ui.input_skip_end.value())

    def ui_button_handler(self, midi_note):
        self.active_note = midi_note

        if midi_note not in self.player.registered_sounds:
            self.player.registered_sounds[midi_note] = SoundProperties.from_dict({"on_note": midi_note})

        self.update_ui()

    def midi_button_handler(self, note, pressed):
        if pressed:
            self.ui_button_handler(note)

    def exec(self):
        self.app.exec_()


if __name__ == "__main__":
    # TODO: change this to update from the output device dropdown
    controller = Controller()
    sys.exit(controller.exec())
