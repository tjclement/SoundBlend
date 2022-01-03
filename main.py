import sys
import midi
from sounds import Player, PlayMode, SoundProperties, get_output_devices
from PyQt5.QtWidgets import QApplication

from main_ui import MainUI

updating_ui = False


def update_props(props: SoundProperties, ui: MainUI):
    if updating_ui:
        return

    props.path = ui.input_path.text()
    props.on_note = int(ui.input_on_note.text(), 10)
    props.mode = PlayMode.from_string(ui.choice_play_mode.currentText())
    props.gain = float(ui.input_gain.value())
    props.fade_in = int(ui.input_fade_in.value())
    props.fade_out = int(ui.input_fade_out.value())
    props.remove_silence = ui.check_remove_silence.isChecked()
    props.loop = ui.check_loop.isChecked()
    props.skip_start = int(ui.input_skip_start.value())
    props.skip_end = int(ui.input_skip_end.value())


def update_ui(ui: MainUI, props: SoundProperties):
    global updating_ui
    updating_ui = True
    ui.input_path.setText(props.path or "")
    ui.input_on_note.setText(str(props.on_note) or "60")
    ui.choice_play_mode.setCurrentText(props.mode.value or PlayMode.MULTI)
    ui.input_gain.setValue(props.gain or 0.0)
    ui.input_fade_in.setValue(props.fade_in or 100)
    ui.input_fade_out.setValue(props.fade_out or 100)
    ui.check_remove_silence.setChecked(props.remove_silence or True)
    ui.check_loop.setChecked(props.loop or False)
    ui.input_skip_start.setValue(props.skip_start or 0)
    ui.input_skip_end.setValue(props.skip_end or 0)
    updating_ui = False


def ui_button_handler(midi_note):
    global shown_midi_note
    shown_midi_note = midi_note

    if midi_note not in player.registered_sounds:
        player.registered_sounds[midi_note] = SoundProperties.from_dict({"on_note": midi_note})

    update_ui(ui, player.registered_sounds[midi_note])


def midi_button_handler(note, pressed):
    if pressed:
        ui_button_handler(note)
    index = note - 60
    if 0 <= index <= 15:
        ui


def set_ui_devices(ui: MainUI, midi_inputs, sound_outputs):
    ui.choice_inputs.addItems([device.name.decode("utf-8") for device in midi_inputs])
    ui.choice_outputs.addItems([device["name"] for device in sound_outputs])


if __name__ == "__main__":
    sound_outputs = get_output_devices()
    device = sound_outputs[4]
    player = Player(device)
    shown_midi_note = 0

    player.register_sounds([
        {"on_note": 0x3C, "mode": PlayMode.HOLD, "path": "/Users/tom/Downloads/soundboard/applause.mp3", "fade_in": 300,
         "fade_out": 300},
        {"on_note": 0x3D, "mode": PlayMode.TOGGLE, "path": "/Users/tom/Downloads/soundboard/i-feel-good.mp3"},
        {"on_note": 0x3E, "mode": PlayMode.HOLD, "path": "/Users/tom/Downloads/soundboard/cricket-sound.mp3"},
        {"on_note": 0x3F, "mode": PlayMode.MULTI, "path": "/Users/tom/Downloads/soundboard/doh.mp3", "gain": -9},
        {"on_note": 0x40, "mode": PlayMode.MULTI, "path": "/Users/tom/Downloads/soundboard/anime-wow.mp3"},
    ])

    app = QApplication(sys.argv)
    ui = MainUI()
    ui.on_settings_change(lambda: update_props(player.registered_sounds[shown_midi_note], ui))
    ui.on_grid_press(ui_button_handler)

    midi_inputs, midi_outputs = midi.get_devices()
    if len(midi_inputs) > 0:
        midi_device = midi.MidiConnection(midi_inputs[0].id)
        midi_device.add_callback(player.callback)
        midi_device.add_callback(midi_button_handler)
        ui.on_tick(midi_device.handle_events)

    set_ui_devices(ui, midi_inputs, sound_outputs)

    sys.exit(app.exec_())
