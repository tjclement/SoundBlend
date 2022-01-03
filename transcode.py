import pydub
from pydub import AudioSegment, silence


def extract_samples(sound_info):
    extension = sound_info.path.split(".")[-1]
    song = AudioSegment.from_file(sound_info.path, extension)

    start, end = sound_info.skip_start, -sound_info.skip_end if sound_info.skip_end else None
    if sound_info.remove_silence:
        if not start:
            start = silence.detect_leading_silence(song, chunk_size=1,
                                                   silence_threshold=-40) or None
        if not end:
            end = -silence.detect_leading_silence(song.reverse(), chunk_size=1,
                                                  silence_threshold=-40) or None

    clipped_song = song[start:end] + sound_info.gain
    return clipped_song.raw_data
