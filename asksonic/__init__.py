from os import getenv
import logging
from flask import Flask
from flask_ask import Ask


if getenv('ASKS_DEBUG', 'False') == 'True':
    logging.getLogger('flask_ask').setLevel(logging.DEBUG)

route_prefix = getenv('ASKS_ROUTEPREFIX', '/alexa')
songs_count = getenv('ASKS_SONGS_COUNT', 50)

app = Flask(__name__)
ask = Ask(app, route_prefix, path='templates/en.yaml')


from . import intents
