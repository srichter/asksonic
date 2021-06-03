from os import getenv
from libsonic import Connection
from urllib.request import Request


subsonic = Connection(
    getenv('ASKS_SUBSONIC_URL'),
    getenv('ASKS_SUBSONIC_USER'),
    getenv('ASKS_SUBSONIC_PASS'),
    getenv('ASKS_SUBSONIC_PORT', 443),
)


def getSubsonicRequestUrl(request: Request) -> str:
    return '{}?{}'.format(request.get_full_url(), request.data.decode('UTF-8'))


def getStreamUrl(id: str) -> str:
    request = subsonic._getRequest('download.view', {'id': id})
    return getSubsonicRequestUrl(request)


def getCoverArtUrl(id: str, size: int = 0) -> str:
    request = subsonic._getRequest(
        'getCoverArt.view',
        {'id': id, 'size': size}
    )
    return getSubsonicRequestUrl(request)
