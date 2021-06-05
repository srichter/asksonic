from os import getenv
from libsonic import Connection
from urllib.request import Request
from asksonic.utils.subsonic.track import Track


class Subsonic(Connection):
    def __init__(
        self,
        baseUrl: str, username: str, password: str, port: int,
        extra_param: tuple
    ) -> None:
        super().__init__(baseUrl, username, password, port)
        self._extra_param = extra_param

    def _getBaseQdict(self) -> dict[str, str]:
        qdict = super()._getBaseQdict()
        if self._extra_param:
            qdict.update([self._extra_param])
        return qdict

    def request_url(self, request: Request) -> str:
        url = request.get_full_url()
        query = request.data.decode('UTF-8')
        return f'{url}?{query}'

    def random_tracks(self, count: int) -> list[Track]:
        tracks = self.getRandomSongs(count)
        tracks = tracks['randomSongs']['song']
        tracks = [Track(**track) for track in tracks]
        return tracks


subsonic_url = getenv('ASKS_SUBSONIC_URL', '')
subsonic_user = getenv('ASKS_SUBSONIC_USER', '')
subsonic_pass = getenv('ASKS_SUBSONIC_PASS', '')

if any(x == '' for x in [subsonic_url, subsonic_user, subsonic_pass]):
    raise RuntimeError('Subsonic login information is missing from .env')

try:
    extra_param = tuple(getenv('ASKS_EXTRA_PARAM').split(',', 1))
    if len(extra_param) != 2:
        raise RuntimeError('The format of ASKS_EXTRA_PARAM is: "key,value"')
except AttributeError:
    extra_param = ()


subsonic = Subsonic(
    subsonic_url,
    subsonic_user,
    subsonic_pass,
    int(getenv('ASKS_SUBSONIC_PORT', 443)),
    extra_param
)
