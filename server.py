from asksonic import app
from os import getenv

if __name__ == '__main__':
    host = getenv('ASKS_HOST', '0.0.0.0')
    port = int(getenv('ASKS_PORT', 4545))

    app.run(host=host, port=port)
