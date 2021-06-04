from typing import Union
from flask.templating import render_template
from asksonic import ask, logger
from flask_ask import audio
from . import queue
from asksonic.utils.response import empty_response, track_response


@ask.on_playback_started()
def started() -> tuple:
    log('Playback Started')
    return empty_response


@ask.on_playback_stopped()
def stopped() -> tuple:
    log('Playback Stopped')
    return empty_response


@ask.intent('AMAZON.PauseIntent')
def pause() -> audio:
    log('Playback Pausing')
    return audio().stop()


@ask.intent('AMAZON.ResumeIntent')
def resume() -> Union[audio, tuple]:
    log('Playback Resuming')
    if queue.current:
        return audio().resume()
    return empty_response


@ask.intent('AMAZON.StopIntent')
def stop() -> audio:
    log('Playback Stopping')
    queue.clear()
    return audio(render_template('stopping')).stop()


@ask.intent('AMAZON.CancelIntent')
def cancel() -> audio:
    log('Playback Canceling')
    queue.clear()
    return audio().clear_queue(stop=True)


@ask.intent('AMAZON.NextIntent')
def next_track() -> audio:
    log('Next Track')
    track = queue.next()
    if track:
        return track_response(track)
    return audio(render_template('end_of_queue'))


@ask.intent('AMAZON.PreviousIntent')
def previous_track() -> audio:
    log('Previous Track')
    track = queue.previous()
    if track:
        return track_response(track)
    return audio(render_template('nothing_playing'))


@ask.on_playback_play_command()
def play_command() -> Union[audio, tuple]:
    log('Play Command Issued')
    if queue.current:
        return audio().resume()
    return empty_response


@ask.on_playback_pause_command()
def pause_command() -> audio:
    log('Pause Command Issued')
    return audio().stop()


@ask.on_playback_next_command()
def next_command() -> Union[audio, tuple]:
    log('Next Track Command Issued')
    track = queue.next()
    if track:
        return track_response(track)
    return audio().stop()


@ask.on_playback_previous_command()
def previous_command() -> Union[audio, tuple]:
    log('Previous Track Command Issued')
    track = queue.previous()
    if track:
        return track_response(track)
    return empty_response


def log(msg: str) -> None:
    logger.debug(msg)
    logger.debug(queue.status)
