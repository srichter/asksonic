from asksonic import app
from os import getenv

if __name__ == '__main__':
    host = getenv('ASKS_HOST', '0.0.0.0')
    port = int(getenv('ASKS_PORT', getenv('PORT', 443)))
    debug = getenv('ASKS_DEBUG', 'False') == 'True'

    app.run(host=host, port=port, debug=debug)
