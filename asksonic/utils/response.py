from asksonic.utils.subsonic.track import Track
from flask_ask import audio


empty_response = (
    '{"response": {"shouldEndSession": true}, "version": "1.0"}',
    200,
)


def play_track_response(track: Track, speech: str = '') -> audio:
    return audio(speech) \
        .play(track.stream_url) \
        .metadata(**track.metadata)


def enqueue_track_response(track: Track, speech: str = '') -> audio:
    return audio(speech) \
        .enqueue(track.stream_url) \
        .metadata(**track.metadata)
