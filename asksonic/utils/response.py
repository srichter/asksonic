from asksonic.utils.subsonic.track import Track
from flask_ask import audio


empty_response = (
    '{"response": {"shouldEndSession": true}, "version": "1.0"}',
    200,
)


def track_response(track: Track, speech: str = '') -> audio:
    return audio(speech) \
        .play(track.download_url) \
        .metadata(**track.metadata)
