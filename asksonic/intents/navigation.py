from typing import Optional, Union
from flask_ask.models import statement
from asksonic.utils.response import play_track_response
from flask.templating import render_template
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


@ask.intent('AskSonicListArtistAlbumsIntent')
def list_artist_albums(artist: str) -> Union[audio, statement]:
    log(f'List Artist Albums: {artist}')
    albums = subsonic.artist_albums(artist)
    if albums:
        album_titles = ', '.join([a['name'] for a in albums])
        return statement(
            render_template(
                'artist_albums',
                artist=artist, album_titles=album_titles
            )
        )
    return statement(
        render_template('artist_not_found', artist=artist)
    )


@ask.intent('AskSonicPlayPlaylistIntent')
def play_playlist(playlist: str) -> Union[audio, statement]:
    log(f'Play Playlist: {playlist}')
    found = subsonic.find_playlist(playlist)
    tracks = subsonic.playlist_tracks(found['id']) if found else []
    if tracks:
        track = queue.reset(tracks)
        return play_track_response(
            track,
            render_template('playing_playlist', playlist=found['name'])
        )
    return statement(
        render_template('playlist_not_found', playlist=playlist)
    )


@ask.intent('AskSonicListPlaylistsIntent')
def list_playlists() -> statement:
    log('List Playlists')
    playlists = subsonic.list_playlists()
    if playlists:
        names = ', '.join(p['name'] for p in playlists)
        return statement(render_template('playlists_list', playlists=names))
    return statement(render_template('no_playlists'))


@ask.intent('AskSonicPlaySongIntent')
def play_song(song: str) -> Union[audio, statement]:
    log(f'Play Song: {song}')
    tracks = subsonic.search_tracks(song)
    if tracks:
        track = queue.reset(tracks)
        return play_track_response(
            track,
            render_template(
                'playing_song', title=track.title, artist=track.artist
            )
        )
    return statement(render_template('song_not_found', song=song))


@ask.intent('AskSonicPlayFavoritesIntent')
def play_favorites() -> Union[audio, statement]:
    log('Play Favorites')
    tracks = subsonic.favorite_tracks(tracks_count)
    if tracks:
        track = queue.reset(tracks)
        return play_track_response(track, render_template('playing_favorites'))
    return statement(render_template('no_favorites'))


@ask.intent('AskSonicPlayGenreIntent')
def play_genre(genre: str) -> Union[audio, statement]:
    log(f'Play Genre: {genre}')
    tracks = subsonic.genre_tracks(genre, tracks_count)
    if tracks:
        track = queue.reset(tracks)
        return play_track_response(
            track, render_template('playing_genre', genre=genre)
        )
    return statement(render_template('genre_not_found', genre=genre))


def log(msg: str) -> None:
    logger.debug(msg)
