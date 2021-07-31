from asksonic.utils.response import play_track_response
from flask import render_template
from flask_ask import question, audio
from asksonic import ask, logger, tracks_count
from asksonic.utils.subsonic import subsonic
from . import queue


@ask.intent('AMAZON.HelpIntent')
@ask.launch
def launch() -> question:
    log('Launch')
    return question(render_template('launch_text')) \
        .simple_card(
            title=render_template('launch_title'),
            content=render_template('launch_content')
        )


@ask.intent('AskSonicShuffleLibraryIntent')
def play_random_tracks() -> audio:
    log('Shuffle Library')
    tracks = subsonic.random_tracks(tracks_count)
    track = queue.reset(tracks)
    return play_track_response(track, render_template('playing_library'))


def log(msg: str) -> None:
    logger.debug(msg)
