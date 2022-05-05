from os import getenv
from .api import Subsonic
from libsonic import API_VERSION

subsonic_url = getenv('ASKS_SUBSONIC_URL', '')
subsonic_user = getenv('ASKS_SUBSONIC_USER', '')
subsonic_pass = getenv('ASKS_SUBSONIC_PASS', '')
subsonic_serverpath = getenv('ASKS_SUBSONIC_SERVERPATH', '/rest')
subsonic_port = int(getenv('ASKS_SUBSONIC_PORT', 443))
subsonic_apiversion = getenv('ASKS_SUBSONIC_APIVERSION', API_VERSION)
subsonic_appname = getenv('ASKS_SUBSONIC_APPNAME', 'py-sonic')
subsonic_legacyauth = getenv('ASKS_SUBSONIC_LEGACYAUTH', False)
extra_secret = getenv('ASKS_EXTRA_SECRET')

if any(x == '' for x in [subsonic_url, subsonic_user, subsonic_pass]):
    raise RuntimeError('Subsonic login information is missing from env')


subsonic = Subsonic(
    subsonic_url,
    subsonic_user,
    subsonic_pass,
    subsonic_port,
    subsonic_serverpath,
    subsonic_apiversion,
    subsonic_appname,
    subsonic_legacyauth,
    extra_secret
)
