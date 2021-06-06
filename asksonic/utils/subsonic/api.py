from typing import Optional
from urllib.parse import quote_plus
from libsonic import Connection
from urllib.request import Request
from .track import Track


class Subsonic(Connection):
    def __init__(
        self,
        baseUrl: str, username: str, password: str, port: int,
        extra_secret: Optional[str] = None
    ) -> None:
        super().__init__(baseUrl, username, password, port)
        self._extra_secret = extra_secret

    def _getRequest(self, viewName: str, query: dict = {}) -> Request:
        req = super()._getRequest(viewName=viewName, query=query)
        if self._extra_secret:
            req.add_header('asksonic-secret', self._extra_secret)
        return req

    def request_url(self, request: Request) -> str:
        url = request.get_full_url()
        query = request.data.decode('UTF-8')
        if self._extra_secret:
            query += f'&asksonic-secret={quote_plus(self._extra_secret)}'
        return f'{url}?{query}'

    def random_tracks(self, count: int) -> list[Track]:
        tracks = self.getRandomSongs(count)
        tracks = tracks['randomSongs']['song']
        tracks = [Track(**track) for track in tracks]
        return tracks
