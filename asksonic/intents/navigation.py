from flask import render_template
from flask_ask import question, audio
from asksonic import ask, songs_count
from asksonic.utils.subsonic import subsonic, getStreamUrl, getCoverArtUrl
from . import queue


@ask.launch
def launch() -> question:
    return question(render_template('launch_text')) \
        .simple_card(
            title=render_template('launch_title'),
            content=render_template('launch_content')
        )


@ask.intent('AskSonicShuffleLibraryIntent')
def play_random_tracks():
    tracks = subsonic.getRandomSongs(songs_count)
    queue.reset(tracks['randomSongs']['song'])
    track = queue.start()
    return audio(render_template('playing_library_text')) \
        .play(getStreamUrl(track['id'])) \
        .metadata(
            title=track['title'],
            subtitle='{} - {}'.format(track['artist'], track['album']),
            image=getCoverArtUrl(track['id'])
        )
