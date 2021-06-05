from os import getenv
from libsonic import Connection
from urllib.request import Request
from asksonic.utils.subsonic.track import Track


class Subsonic(Connection):
    def __init__(
        self,
        baseUrl: str, username: str, password: str, port: int,
        extra_secret: str
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
            query += f'&asksonic-secret={self._extra_secret}'
        return f'{url}?{query}'

    def random_tracks(self, count: int) -> list[Track]:
        tracks = self.getRandomSongs(count)
        tracks = tracks['randomSongs']['song']
        tracks = [Track(**track) for track in tracks]
        return tracks


subsonic_url = getenv('ASKS_SUBSONIC_URL', '')
subsonic_user = getenv('ASKS_SUBSONIC_USER', '')
subsonic_pass = getenv('ASKS_SUBSONIC_PASS', '')
extra_secret = getenv('ASKS_EXTRA_SECRET', '')

if any(x == '' for x in [subsonic_url, subsonic_user, subsonic_pass]):
    raise RuntimeError('Subsonic login information is missing from .env')


subsonic = Subsonic(
    subsonic_url,
    subsonic_user,
    subsonic_pass,
    int(getenv('ASKS_SUBSONIC_PORT', 443)),
    extra_secret
)
