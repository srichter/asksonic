from typing import Optional, Union
from flask_ask.models import statement
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


@ask.intent('AskSonicPlayArtistIntent')
def play_artist(artist: str) -> Union[audio, statement]:
    log(f'Play Artist: {artist}')
    tracks = subsonic.artist_tracks(artist, tracks_count)
    if tracks:
        track = queue.reset(tracks)
        return play_track_response(
            track,
            render_template('playing_artist', artist=track.artist)
        )
    return statement(render_template('artist_not_found', artist=artist))


@ask.intent('AskSonicPlayAlbumIntent')
def play_album(album: str, artist: Optional[str]) -> Union[audio, statement]:
    log(f'Play Album: {artist} - {album}')
    tracks = subsonic.album_tracks(album, artist)
    if tracks:
        track = queue.reset(tracks)
        return play_track_response(
            track,
            render_template(
                'playing_album',
                album=track.album, artist=track.artist
            )
        )
    return statement(
        render_template('album_not_found', album=album, artist=artist)
    )


def log(msg: str) -> None:
    logger.debug(msg)
