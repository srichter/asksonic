from os import getenv
import logging
from flask.app import Flask
from flask_ask import Ask


if getenv('FLASK_ENV') == 'development':
    logging.getLogger('flask_ask').setLevel(logging.DEBUG)
    logging.getLogger(__name__).setLevel(logging.DEBUG)


route_prefix = getenv('ASKS_ROUTE_PREFIX', '/alexa')
tracks_count = int(getenv('ASKS_TRACKS_COUNT', 50))

app = Flask(__name__)
template_path = f"templates/{getenv('ASK_LANGUAGE', 'en')}.yaml"
ask = Ask(app, route_prefix, path=template_path)

logger = app.logger


from . import intents
