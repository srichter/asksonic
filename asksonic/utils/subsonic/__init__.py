from os import getenv
from .api import Subsonic

subsonic_url = getenv('ASKS_SUBSONIC_URL', '')
subsonic_user = getenv('ASKS_SUBSONIC_USER', '')
subsonic_pass = getenv('ASKS_SUBSONIC_PASS', '')
subsonic_port = int(getenv('ASKS_SUBSONIC_PORT', 443))
extra_secret = getenv('ASKS_EXTRA_SECRET')

if any(x == '' for x in [subsonic_url, subsonic_user, subsonic_pass]):
    raise RuntimeError('Subsonic login information is missing from env')


subsonic = Subsonic(
    subsonic_url,
    subsonic_user,
    subsonic_pass,
    subsonic_port,
    extra_secret
)
