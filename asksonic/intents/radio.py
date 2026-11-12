import hashlib
import hmac
from os import getenv
from typing import Optional, Union
from urllib.parse import quote, urlparse

import requests
from flask import Response, abort, request as flask_request, stream_with_context
from flask.templating import render_template
from flask_ask import audio, statement
from asksonic import app, ask, logger, route_prefix
from asksonic.utils.subsonic import extra_secret, subsonic, subsonic_pass
from . import queue


def radio_token(station_id: str) -> str:
    """HMAC-SHA256 of the station id, so the proxy URL handed to Alexa can't
    be used to fetch arbitrary stations without a valid token."""
    key = extra_secret or subsonic_pass
    digest = hmac.new(
        key.encode('utf-8'), station_id.encode('utf-8'), hashlib.sha256
    ).hexdigest()
    return digest[:32]


def radio_stream_url(station: dict) -> str:
    # Alexa's AudioPlayer requires streams on HTTPS port 443 with a trusted
    # certificate. Navidrome's internet radio stations may live on other
    # ports/schemes (e.g. an Icecast stream on :7920), which Alexa can't
    # fetch directly, so route it through this app's own public HTTPS
    # endpoint (Caddy terminates 443 and forwards to Flask) and proxy the
    # bytes through in the /radio/<id> route below.
    public_url = getenv('ASKS_PUBLIC_URL', '')
    if public_url:
        parsed = urlparse(public_url)
        base = f'{parsed.scheme}://{parsed.netloc}'
    else:
        base = flask_request.host_url.rstrip('/')
    token = radio_token(station['id'])
    return f'{base}{route_prefix}/radio/{quote(station["id"], safe="")}?t={token}'


def play_radio_response(station: dict, speech: str = '') -> audio:
    return audio(speech) \
        .play(radio_stream_url(station)) \
        .metadata(
            title=station['name'],
            subtitle=render_template('radio_subtitle')
    )


@ask.intent('AskSonicPlayRadioIntent')
def play_radio(station: Optional[str]) -> Union[audio, statement]:
    log(f'Play Radio: {station}')
    found = subsonic.find_radio_station(station) if station else None
    if not found and not station:
        stations = subsonic.radio_stations()
        if len(stations) == 1:
            found = stations[0]
    if found:
        queue.clear()
        queue.radio = found
        return play_radio_response(
            found, render_template('playing_radio', station=found['name'])
        )
    if not subsonic.radio_stations():
        return statement(render_template('no_radio_stations'))
    return statement(render_template('radio_not_found', station=station or ''))


@app.route(f'{route_prefix}/radio/<station_id>', methods=['GET'])
def radio_stream(station_id: str):
    token = flask_request.args.get('t', '')
    if not hmac.compare_digest(token, radio_token(station_id)):
        abort(403)
    station = subsonic.radio_station(station_id)
    if not station:
        abort(404)
    try:
        upstream = requests.get(
            station['streamUrl'], stream=True, timeout=(10, 30),
            headers={'User-Agent': 'AskSonic'}
        )
    except requests.RequestException as e:
        logger.error(f'Radio proxy connection error for {station_id}: {e}')
        abort(502)
    if not (200 <= upstream.status_code < 300):
        logger.error(
            f'Radio proxy got status {upstream.status_code} for {station_id}'
        )
        upstream.close()
        abort(502)

    def generate():
        try:
            for chunk in upstream.iter_content(chunk_size=8192):
                yield chunk
        finally:
            upstream.close()

    content_type = upstream.headers.get('Content-Type') or 'audio/mpeg'
    response = Response(
        stream_with_context(generate()),
        status=200,
        content_type=content_type,
        direct_passthrough=True,
    )
    response.headers['Cache-Control'] = 'no-cache'
    return response


def log(msg: str) -> None:
    logger.debug(msg)
