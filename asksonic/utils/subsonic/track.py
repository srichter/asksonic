from asksonic.utils import subsonic


class Track():
    def __init__(
        self,
        id: str,
        title: str,
        artist: str,
        artistId: str,
        album: str,
        albumId: str,
        **kwargs
    ) -> None:
        self._id = id
        self._title = title
        self._artist = artist
        self._artist_id = artistId
        self._album = album
        self._album_id = albumId

        self._subsonic = subsonic.subsonic

    def __repr__(self) -> str:
        return (
            f'Track(id="{self.id}", title="{self.title}", '
            f'artist="{self.artist}", artistId="{self.artist_id}", '
            f'album="{self.album}", albumId="{self.album_id}")'
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Track):
            return False
        return self.id == o.id

    def __str__(self) -> str:
        return f'{self.artist} - {self.title}'

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def artist(self) -> str:
        return self._artist

    @property
    def artist_id(self) -> str:
        return self._artist_id

    @property
    def album(self) -> str:
        return self._album

    @property
    def album_id(self) -> str:
        return self._album_id

    @property
    def subtitle(self) -> str:
        return f'{self.artist} - {self.album}'

    @property
    def stream_url(self) -> str:
        request = self._subsonic._getRequest('stream.view', {'id': self.id})
        return self._subsonic.request_url(request)

    @property
    def cover_art_url(self) -> str:
        request = self._subsonic._getRequest(
            'getCoverArt.view',
            {'id': self.id}
        )
        return self._subsonic.request_url(request)

    @property
    def metadata(self) -> dict[str, str]:
        return {
            'title': self.title,
            'subtitle': self.subtitle,
            'image': self.cover_art_url,
        }

    def scrobble(self, submission: bool = False) -> None:
        submit = 'true' if submission else 'false'
        self._subsonic.scrobble(self.id, submission=submit)

    def star(self) -> None:
        self._subsonic.star(self.id)
