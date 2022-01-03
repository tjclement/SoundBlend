import time
import pygame.midi as midi
from dataclasses import dataclass

from typing import Tuple, List


@dataclass
class MidiDevice:
    id: int
    interface: str
    name: str
    input: bool
    output: bool
    opened: bool


class MidiConnection:
    def __init__(self, device_id):
        midi.init()  # Can be called multiple times
        self.input = midi.Input(device_id)
        self.callbacks = []

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        self.callbacks.remove(callback)

    def handle_events(self) -> None:
        if self.input.poll():
            for event in self.input.read(10):
                [status, note, _, __], ___ = event
                is_pressed = status == 0x90
                for callback in self.callbacks:
                    callback(note, is_pressed)


def get_devices() -> Tuple[List[MidiDevice], List[MidiDevice]]:
    midi.init()  # Can be called multiple times
    inputs, outputs = [], []

    for i in range(midi.get_count()):
        interface, name, input, output, opened = midi.get_device_info(i)
        device = MidiDevice(i, interface, name, input, output, opened)
        if not input and not output:
            raise SystemError(f"Midi device is neither input or output: {interface}:{name}")
        target = inputs if input else outputs
        target.append(device)

    return inputs, outputs


if __name__ == "__main__":
    inputs, outputs = MidiConnection.get_devices()
    device = inputs[0]
    connection = MidiConnection(device.id)

    while True:
        connection.handle_events()
        time.sleep(0.01)
    pass
