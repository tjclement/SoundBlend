import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

import midi
import sounddevice
import pygame.mixer as mixer

import transcode


class PlayMode(Enum):
    MULTI = "multi"  # Sound can be played multiple times concurrently, and will play until completion
    HOLD = "hold"  # Sound will play as long as its button is pressed, and stops when released
    TOGGLE = "toggle"  # Pressing once will start the sound, pressing again will stop it

    @staticmethod
    def from_string(string):
        if string == PlayMode.MULTI.value:
            return PlayMode.MULTI
        elif string == PlayMode.HOLD.value:
            return PlayMode.HOLD
        elif string == PlayMode.TOGGLE.value:
            return PlayMode.TOGGLE
        else:
            return None


@dataclass
class SoundProperties:
    on_note: int
    path: str
    mode: PlayMode
    gain: Optional[int]  # Gain in dB to apply to the sample volume (postive or negative)
    fade_in: Optional[int]  # Time in ms to fade in the sample when it starts playing
    fade_out: Optional[int]  # Time in ms to fade out the sample when it stops playing
    # Experimental: remove silence from beginning and end of sample.
    # Removes need for skip_start and skip_stop.
    remove_silence: Optional[bool]
    # Time in ms to skip over the beginning of the sample. Overrides remove_silence.
    skip_start: Optional[int]
    # Time in ms to skip at the end of the sample. Overrides remove_silence.
    skip_end: Optional[int]
    loop: Optional[bool]  # Keep repeating sample until cancelled
    sound: Optional[mixer.Sound]  # For internal use, not in the json data
    channel: Optional[mixer.Channel]  # For internal use, not in the json data

    def to_dict(self) -> dict:
        return {
            "on_note": self.on_note,
            "path": self.path,
            "mode": self.mode,
            "gain": self.gain,
            "fade_in": self.fade_in,
            "fade_out": self.fade_out,
            "remove_silence": self.remove_silence,
            "skip_start": self.skip_start,
            "skip_end": self.skip_end,
            "loop": self.loop,
        }

    @staticmethod
    def from_dict(data: dict):
        return SoundProperties(
            on_note=data.get("on_note", 0),
            path=data.get("path", ""),
            mode=data.get("mode", PlayMode.MULTI),
            gain=data.get("gain", 0),
            fade_in=data.get("fade_in", 0),
            fade_out=data.get("fade_out", 0),
            remove_silence=data.get("remove_silence", True),
            skip_start=data.get("skip_start", None),
            skip_end=data.get("skip_end", None),
            loop=data.get("loop", False),
            sound=None,
            channel=None
        )


class Player:
    def __init__(self, device: dict):
        if not mixer.get_init():
            mixer.init(frequency=int(device["default_samplerate"]), devicename=device["name"])
        # mixer.set_num_channels(4)
        self.registered_sounds = {}  # type: Dict[SoundProperties]

    def callback(self, note, is_pressed: bool) -> None:
        if note not in self.registered_sounds:
            return

        sound_info = self.registered_sounds[note]
        is_playing = sound_info.channel and sound_info.channel.get_busy()

        if (not is_pressed and sound_info.mode is PlayMode.HOLD) or \
                (is_pressed and sound_info.mode is PlayMode.TOGGLE and is_playing):
            sound_info.sound.fadeout(sound_info.fade_out)
            return

        if is_pressed and sound_info.sound:
            loops = -1 if sound_info.loop else 0
            sound_info.channel = sound_info.sound.play(fade_ms=sound_info.fade_in, loops=loops)

    def register_sounds(self, sounds: List[dict]) -> None:
        for sound_info in sounds:
            props = SoundProperties.from_dict(sound_info)
            data = transcode.extract_samples(props)
            sound = mixer.Sound(buffer=data)
            props.sound = sound
            self.registered_sounds[sound_info["on_note"]] = props

    def stop(self):
        self.registered_sounds = {}
        if mixer.get_init():
            mixer.quit()


def get_output_devices():
    return [device for device in sounddevice.query_devices() if device["max_output_channels"] >= 2]


if __name__ == "__main__":
    devices = get_output_devices()
    device = devices[2]
    player = Player(device)

    player.register_sounds([
        {"on_note": 0x3C, "mode": "hold", "path": "/Users/tom/Downloads/soundboard/applause.mp3", "fade_in": 300,
         "fade_out": 300},
        {"on_note": 0x3D, "mode": "toggle", "path": "/Users/tom/Downloads/soundboard/i-feel-good.mp3"},
        {"on_note": 0x3E, "mode": "hold", "path": "/Users/tom/Downloads/soundboard/cricket-sound.mp3"},
        {"on_note": 0x3F, "mode": "multi", "path": "/Users/tom/Downloads/soundboard/doh.mp3", "gain": -9},
        {"on_note": 0x40, "mode": "multi", "path": "/Users/tom/Downloads/soundboard/anime-wow.mp3"},
    ])

    midi_inputs, midi_outputs = midi.get_devices()
    midi_device = midi.MidiConnection(midi_inputs[0].id)
    midi_device.add_callback(player.callback)
    while True:
        midi_device.handle_events()
        time.sleep(0.01)
    pass
