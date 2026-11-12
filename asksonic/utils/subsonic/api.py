from os import getenv
from typing import Optional
from urllib.parse import quote_plus
from libsonic import Connection
from urllib.request import Request
from random import shuffle
from .track import Track


def _as_list(value) -> list:
    """Subsonic's API returns a bare dict instead of a one-item list when a
    collection (songs/albums/playlists/...) has exactly one result. Every
    caller below expects a list, so normalize here rather than crash on
    libraries/playlists/genres that happen to have exactly one match."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


class Subsonic(Connection):
    def __init__(
        self,
        baseUrl: str, username: str, password: str, port: int,
        serverPath: str, apiVersion: str, appName: str,
        extra_secret: Optional[str] = None
    ) -> None:
        super().__init__(
            baseUrl=baseUrl, username=username, password=password, port=port,
            serverPath=serverPath, appName=appName, apiVersion=apiVersion
        )
        self._extra_secret = extra_secret
        # Base API calls (search, random tracks, etc.) always use baseUrl/port
        # above, which should stay a fast local address. ASKS_PUBLIC_URL, if
        # set, is only substituted into stream/cover-art URLs handed to Alexa,
        # since those need to be fetched by Amazon's cloud, not this machine.
        self._public_url = getenv('ASKS_PUBLIC_URL', '').rstrip('/')

    def _doInfoReq(self, req: Request) -> dict:
        if self._extra_secret:
            req.add_header('asksonic-secret', self._extra_secret)
        return super()._doInfoReq(req)

    def request_url(self, request: Request) -> str:
        url = request.get_full_url()
        query = request.data.decode('UTF-8') if request.data else ''  # type: ignore # noqa
        if self._extra_secret:
            query += f'&asksonic-secret={quote_plus(self._extra_secret)}'
        full_url = f'{url}?{query}'
        if self._public_url:
            internal_base = f'{self.baseUrl}:{self.port}'
            full_url = full_url.replace(internal_base, self._public_url, 1)
        return full_url

    def search(self, query: str, search_options: dict = {}) -> dict:
        default_options = {
            'artistCount': 0, 'artistOffset': 0, 'albumCount': 0,
            'albumOffset': 0, 'songCount': 0, 'songOffset': 0,
            'musicFolderId': None
        }
        options = default_options | search_options
        return self.search3(query=query, **options)

    def _find_x(self, search_type: str, query: str) -> Optional[dict]:
        if search_type not in ['artist', 'album']:
            raise ValueError('search_type must be one of: artist, album')
        result = self.search(
            query=query,
            search_options={f'{search_type}Count': 10}
        )
        candidates = _as_list(result['searchResult3'].get(search_type))
        if not candidates:
            return None
        try:
            found = next(
                x for x in candidates
                if x['name'].lower() == query.lower()
            )
        except StopIteration:
            found = candidates[0]
        return found

    def find_artist(self, query: str) -> Optional[dict]:
        return self._find_x('artist', query)

    def find_album(
        self,
        query: str, artist_id: Optional[str]
    ) -> Optional[dict]:
        if artist_id:
            albums = self.getArtist(artist_id)
            albums = _as_list(albums['artist'].get('album'))
            try:
                return next(
                    x for x in albums
                    if x['name'].lower() == query.lower()
                )
            except StopIteration:
                return None
        return self._find_x('album', query)

    def find_playlist(self, query: str) -> Optional[dict]:
        playlists = self.list_playlists()
        if not playlists:
            return None
        try:
            return next(
                p for p in playlists if p['name'].lower() == query.lower()
            )
        except StopIteration:
            pass
        try:
            return next(
                p for p in playlists if query.lower() in p['name'].lower()
            )
        except StopIteration:
            return None

    def list_playlists(self) -> list[dict]:
        result = self.getPlaylists()
        return _as_list(result['playlists'].get('playlist'))

    def random_tracks(self, count: int = 50) -> list[Track]:
        tracks = self.getRandomSongs(count)
        tracks = _as_list(tracks['randomSongs'].get('song'))
        return [Track(**track) for track in tracks]

    def artist_albums(self, artist: str, count: int = 5) -> list[dict]:
        found_artist = self.find_artist(artist)
        if not found_artist:
            return []
        albums = self.getArtist(found_artist['id'])
        return _as_list(albums['artist'].get('album'))

    def artist_tracks(self, artist: str, count: int = 50) -> list[Track]:
        albums = self.artist_albums(artist)
        if not albums:
            return []
        shuffle(albums)
        tracks = []
        for album in albums:
            songs = self.getAlbum(album['id'])
            songs = _as_list(songs['album'].get('song'))
            shuffle(songs)
            tracks.extend([Track(**track) for track in songs])
            if len(tracks) >= count:
                tracks = tracks[:count]
                break
        shuffle(tracks)
        return tracks

    def album_tracks(self, album: str, artist: Optional[str]) -> list[Track]:
        if artist:
            found_artist = self.find_artist(artist)
            artist = found_artist['id'] if found_artist else ''
        found_album = self.find_album(album, artist)
        if not found_album:
            return []
        tracks = self.getAlbum(found_album['id'])
        tracks = _as_list(tracks['album'].get('song'))
        return [Track(**track) for track in tracks]

    def playlist_tracks(self, playlist_id: str) -> list[Track]:
        result = self.getPlaylist(playlist_id)
        songs = _as_list(result['playlist'].get('entry'))
        return [Track(**song) for song in songs]

    def search_tracks(self, query: str, count: int = 20) -> list[Track]:
        result = self.search(query, search_options={'songCount': count})
        songs = _as_list(result['searchResult3'].get('song'))
        return [Track(**song) for song in songs]

    def favorite_tracks(self, count: int = 50) -> list[Track]:
        result = self.getStarred2()
        songs = _as_list(result['starred2'].get('song'))
        shuffle(songs)
        return [Track(**song) for song in songs[:count]]

    def genre_tracks(self, genre: str, count: int = 50) -> list[Track]:
        result = self.getSongsByGenre(genre, count=count)
        songs = _as_list(result['songsByGenre'].get('song'))
        shuffle(songs)
        return [Track(**song) for song in songs]

    def radio_stations(self) -> list[dict]:
        result = self.getInternetRadioStations()
        return _as_list(
            result['internetRadioStations'].get('internetRadioStation')
        )

    def find_radio_station(self, query: str) -> Optional[dict]:
        stations = self.radio_stations()
        if not stations:
            return None
        try:
            return next(
                s for s in stations if s['name'].lower() == query.lower()
            )
        except StopIteration:
            pass
        try:
            return next(
                s for s in stations if query.lower() in s['name'].lower()
            )
        except StopIteration:
            pass
        # Fall back to stripping trailing "radio"/"station" and a leading
        # "the " so requests like "night drive radio station" still match
        # a station literally named "Night Drive Radio".
        stripped = query.lower()
        for suffix in ('station', 'radio'):
            if stripped.endswith(suffix):
                stripped = stripped[:-len(suffix)].strip()
        if stripped.startswith('the '):
            stripped = stripped[len('the '):].strip()
        if not stripped or stripped == query.lower():
            return None
        try:
            return next(
                s for s in stations if stripped in s['name'].lower()
            )
        except StopIteration:
            return None

    def radio_station(self, station_id: str) -> Optional[dict]:
        stations = self.radio_stations()
        try:
            return next(s for s in stations if s['id'] == station_id)
        except StopIteration:
            return None
