from typing import Union
from flask.templating import render_template
from asksonic import ask, logger
from flask_ask import audio, request, statement
from . import queue
from asksonic.utils.response import empty_response, enqueue_track_response, \
    play_track_response


@ask.on_playback_started()
def playback_started() -> tuple:
    log('Playback Started')
    queue.current.scrobble(submission=False)
    return empty_response


@ask.on_playback_stopped()
def playback_stopped() -> tuple:
    log('Playback Stopped')
    return empty_response


@ask.on_playback_nearly_finished()
def playback_nearly_finished() -> Union[audio, tuple]:
    log('Playback Nearly Finished')
    if queue.up_next:
        log('Enqueuing Next Track')
        return enqueue_track_response(queue.up_next)
    log('Reached End of Queue')
    return empty_response


@ask.on_playback_finished()
def playback_finished() -> tuple:
    log('Playback Finished')
    queue.current.scrobble(submission=True)
    queue.next()
    return empty_response


@ask.intent('AMAZON.PauseIntent')
def pause() -> audio:
    log('Playback Pausing')
    return audio().stop()


@ask.intent('AMAZON.ResumeIntent')
def resume() -> Union[audio, statement]:
    log('Playback Resuming')
    if queue.current:
        return audio().resume()
    return statement(render_template('nothing_playing'))


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
def next_track() -> Union[audio, statement]:
    log('Next Track')
    track = queue.next()
    if track:
        return play_track_response(track)
    return statement(render_template('end_of_queue'))


@ask.intent('AMAZON.PreviousIntent')
def previous_track() -> Union[audio, statement]:
    log('Previous Track')
    track = queue.previous()
    if track:
        return play_track_response(track)
    return statement(render_template('nothing_playing'))


@ask.intent('AMAZON.StartOverIntent')
def restart_track() -> Union[audio, statement]:
    log('Restart Track')
    if queue.current:
        return play_track_response(queue.current)
    return statement(render_template('nothing_playing'))


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
def next_command() -> audio:
    log('Next Track Command Issued')
    track = queue.next()
    if track:
        return play_track_response(track)
    return audio().stop()


@ask.on_playback_previous_command()
def previous_command() -> Union[audio, tuple]:
    log('Previous Track Command Issued')
    track = queue.previous()
    if track:
        return play_track_response(track)
    return empty_response


@ask.default_intent
@ask.intent('AMAZON.FallbackIntent')
@ask.intent('AMAZON.LoopOffIntent')
@ask.intent('AMAZON.LoopOnIntent')
@ask.intent('AMAZON.RepeatIntent')
@ask.intent('AMAZON.ShuffleOffIntent')
@ask.intent('AMAZON.ShuffleOnIntent')
def unsupported_intent() -> statement:
    log(f'Unsupported Intent {request.intent.name}')  # type: ignore
    return statement(render_template('intent_not_supported'))


@ask.intent('AskSonicTrackInformationIntent')
def track_information() -> statement:
    log('Current Track Information')
    track = queue.current
    if not track:
        return statement(render_template('nothing_playing'))
    return statement(
        render_template('current_track')
        + render_template(
            'track_information',
            title=track.title,
            artist=track.artist
        )
    )


@ask.intent('AskSonicDetailedTrackInformationIntent')
def detailed_track_information() -> statement:
    log('Current Track Detailed Information')
    track = queue.current
    if not track:
        return statement(render_template('nothing_playing'))
    return statement(
        render_template('current_track')
        + render_template(
            'detailed_track_information',
            title=track.title,
            artist=track.artist,
            album=track.album,
        )
    )


@ask.intent('AskSonicStarIntent')
def star_track() -> statement:
    log('Star Current Track')
    track = queue.current
    if not track:
        return statement(render_template('nothing_playing'))
    track.star()
    return statement(render_template('okay'))


@ask.intent('AskSonicStarPreviousIntent')
def star_previous_track() -> statement:
    log('Star Previous Track')
    track = queue.last
    if not track:
        return statement(render_template('no_previous_track'))
    track.star()
    return statement(render_template('okay'))


def log(msg: str) -> None:
    logger.debug(msg)
    logger.debug(queue.status)
