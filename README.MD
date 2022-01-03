# Play sound samples on MIDI key press

This tool was designed to play sounds to BlackHole when a button is pressed on a CampZone 2020 badge running the MIDI Controller app. Work in progress.

What works:
* Detecting key presses and releases from a MIDI device (responds to MIDI notes 60-76).
* Loading, transforming (removing silence, gain, fading), and playing samples to a given output device.
* Rendering and changing the configured sample and its properties on key press or button press in UI.

What doesn't work:
* Saving settings to and loading from a profile file.
* Loading a sample path via the load button next to its input field.
* Switching MIDI input and sound output device from the UI dropdowns.

## Sample settings
`on_note`: which MIDI note to trigger on (0x3C-0x4B or 60-75).

`mode`:
* PlayMode.MULTI to have samples play from beginning to end when you press a button. Pressing it again plays another instance of the sound concurrently.
* PlayMode.STARTSTOP starts a sample on the first press, and stops it on a second press.
* PlayMode.HOLD starts a sample when you press a key, and stops it when you release the key.

`path`: absolute path to the sample file (.wav, .mp3, and anything else that ffmpeg understands).

`gain`: Gain in dB (postive or negative) to apply to the sample. 0dB by default.

`fade_in`: Time in ms to fade in when starting the sample. 100ms by default.

`fade_out`: Time in ms to fade out when stopping the sample. 100ms by default.

`remove_silence`: Whether to automatically skip leading and trailing silence when playing the sample. On by default.

`loop`: Whether to play the sample again indefinitely when it ends. Only use with `mode` STARTSTOP or HOLD.

`skip_start`: Time in ms to skip in the beginning of the sample. Only use when not using `remove_silence`.

`skip_end`: Time in ms to skip in the end of the sample. Only use when not using `remove_silence`.
 
## Setup
Currently only tested on Mac OS, but the used libraries should also support Linux and Windows.

### Mac OS
First, install the prerequisites:
```bash
brew install ffmpeg
pip3 install -r requirements.txt
```

Next, change the hardcoded sound output device in main.py (`device = sound_outputs[4]`). You can see which device you should set it to by running `from sounds import get_output_devices; get_output_devices()` inside a python shell.

Also in main.py, hardcode your samples in the list passed to `player.register_sounds()`. The CampZone2020 MIDI Controller app has note number 0x3C (decimal 60) in the top left, and 0x4B (75) in the bottom right.

Finally, run with `python3 main.py`.
