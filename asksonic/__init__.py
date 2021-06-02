from os import getenv
import logging
from flask import Flask
from flask_ask import Ask
from libsonic import Connection

if getenv('ASKS_DEBUG', 'False') == 'True':
    logging.getLogger('flask_ask').setLevel(logging.DEBUG)

route_prefix = getenv('ASKS_ROUTEPREFIX', '/alexa')

app = Flask(__name__)
ask = Ask(app, route_prefix, path='templates/en.yaml')

subsonic = Connection(
    getenv('ASKS_SUBSONIC_URL'),
    getenv('ASKS_SUBSONIC_USER'),
    getenv('ASKS_SUBSONIC_PASS'),
    getenv('ASKS_SUBSONIC_PORT', 443),
)


def getStreamUrl(id: str) -> str:
    request = subsonic._getRequest('download.view', {'id': id})
    return '{}?{}'.format(request.get_full_url(), request.data.decode('UTF-8'))


from . import intents
