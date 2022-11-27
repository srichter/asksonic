from typing import Optional
from urllib.parse import quote_plus
from libsonic import Connection
from urllib.request import Request
from random import shuffle
from .track import Track


class Subsonic(Connection):
    def __init__(
        self,
        baseUrl: str, username: str, password: str, port: int,
        serverPath: str, apiVersion: str, appName: str, legacyAuth: bool,
        extra_secret: Optional[str] = None
    ) -> None:
        super().__init__(
              baseUrl=baseUrl
            , username=username
            , password=password
            , port=port
            , serverPath=serverPath
            , appName=appName
            , apiVersion=apiVersion
            , legacyAuth=legacyAuth
        )
        self._extra_secret = extra_secret

    def _doInfoReq(self, req: Request) -> dict:
        if self._extra_secret:
            req.add_header('asksonic-secret', self._extra_secret)
        return super()._doInfoReq(req)

    def request_url(self, request: Request) -> str:
        url = request.get_full_url()
        query = request.data.decode('UTF-8') if request.data else ''  # type: ignore # noqa
        if self._extra_secret:
            query += f'&asksonic-secret={quote_plus(self._extra_secret)}'
        return f'{url}?{query}'

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
        if search_type not in result['searchResult3']:
            return None
        try:
            found = next(
                x for x in result['searchResult3'][search_type]
                if x['name'].lower() == query.lower()
            )
        except StopIteration:
            found = result['searchResult3'][search_type][0]
        return found

    def find_artist(self, query: str) -> Optional[dict]:
        return self._find_x('artist', query)

    def find_album(
        self,
        query: str, artist_id: Optional[str]
    ) -> Optional[dict]:
        if artist_id:
            albums = self.getArtist(artist_id)
            albums = albums['artist']['album']
            try:
                return next(
                    x for x in albums
                    if x['name'].lower() == query.lower()
                )
            except StopIteration:
                return None
        return self._find_x('album', query)

    def random_tracks(self, count: int = 50) -> list[Track]:
        tracks = self.getRandomSongs(count)
        tracks = tracks['randomSongs']['song']
        tracks = [Track(**track) for track in tracks]
        return tracks

    def artist_albums(self, artist: str, count: int = 5) -> list[dict]:
        found_artist = self.find_artist(artist)
        if not found_artist:
            return []
        albums = self.getArtist(found_artist['id'])
        return albums['artist']['album']

    def artist_tracks(self, artist: str, count: int = 50) -> list[Track]:
        albums = self.artist_albums(artist)
        if not albums:
            return []
        shuffle(albums)
        tracks = []
        for album in albums:
            songs = self.getAlbum(album['id'])
            songs = songs['album']['song']
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
        tracks = tracks['album']['song']
        tracks = [Track(**track) for track in tracks]
        return tracks

    def playlist_tracks(self, playlist: str, shuffle_playlist: bool) -> list[Track]:
        playlists = self.getPlaylists()
        playlists = playlists['playlists']['playlist']
        playlists = [pls for pls in playlists]
        found_playlist = None
        for pls in playlists:
            if playlist == pls['name']:
                found_playlist = pls
                break
        if not found_playlist:
            return []
        tracks = self.getPlaylist(found_playlist['id'])
        tracks = tracks['playlist']['entry']
        if shuffle_playlist:
            shuffle(tracks)
        tracks = [Track(**track) for track in tracks]
        return tracks
