from typing import Optional, Union
from flask.templating import render_template
from asksonic import ask, logger
from flask_ask import audio, context, request, statement
from . import queue
from .radio import play_radio_response
from asksonic.utils.response import empty_response, enqueue_track_response, \
    play_track_response


@ask.on_playback_started()
def playback_started() -> tuple:
    log('Playback Started')
    # queue.current is already None in radio mode, but skip explicitly so
    # this doesn't depend on that invariant.
    if queue.current and not queue.radio:
        queue.current.scrobble(submission=False, timestamp=queue.start_time)
    return empty_response


@ask.on_playback_stopped()
def playback_stopped(offset: int = 0) -> tuple:
    log('Playback Stopped')
    # flask-ask's audio().resume() rebuilds the Play directive from
    # current_stream, which lives in a cache with a 300-second timeout. To
    # resume reliably after longer pauses, AskSonic tracks the offset itself.
    if queue.current or queue.radio:
        queue.offset = int(offset or 0)
        log(f'Stored offset {queue.offset}')
    return empty_response


@ask.on_playback_failed()
def playback_failed() -> tuple:
    log('Playback Failed')
    return empty_response


@ask.on_playback_nearly_finished()
def playback_nearly_finished() -> Union[audio, tuple]:
    log('Playback Nearly Finished')
    if queue.radio:
        # Radio is a single live stream - never enqueue anything after it.
        return empty_response
    if queue.repeat and queue.current:
        log('Repeat On - Re-enqueuing Current Track')
        return enqueue_track_response(queue.current)
    if queue.up_next:
        log('Enqueuing Next Track')
        return enqueue_track_response(queue.up_next)
    log('Reached End of Queue')
    return empty_response


@ask.on_playback_finished()
def playback_finished() -> tuple:
    log('Playback Finished')
    if queue.radio:
        # Live streams don't "finish" - nothing to scrobble or advance.
        return empty_response
    if queue.current:
        queue.current.scrobble(submission=True, timestamp=queue.start_time)
    if not queue.repeat:
        queue.next()
    return empty_response


@ask.intent('AMAZON.PauseIntent')
def pause() -> audio:
    log('Playback Pausing')
    offset = _context_offset()
    if offset is not None:
        queue.offset = offset
    return audio().stop()


@ask.intent('AMAZON.ResumeIntent')
def resume() -> Union[audio, statement]:
    log('Playback Resuming')
    if queue.radio:
        # Live streams can't be seeked - always resume live, at offset 0.
        return play_radio_response(queue.radio)
    if queue.current:
        return play_track_response(queue.current, offset=queue.offset)
    return statement(render_template('nothing_playing'))


@ask.intent('AMAZON.StopIntent')
def stop() -> audio:
    log('Playback Stopping')
    # Unlike Cancel, Stop no longer clears the queue - it captures the
    # current offset below so a later AMAZON.ResumeIntent can pick back up
    # where playback left off instead of saying nothing is playing.
    offset = _context_offset()
    if offset is not None:
        queue.offset = offset
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
    if queue.radio:
        return play_radio_response(queue.radio)
    if queue.current:
        return play_track_response(queue.current, offset=queue.offset)
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


@ask.intent('AMAZON.ShuffleOnIntent')
def shuffle_on() -> statement:
    log('Shuffle On')
    queue.shuffle()
    return statement(render_template('shuffle_on'))


@ask.intent('AMAZON.ShuffleOffIntent')
def shuffle_off() -> statement:
    log('Shuffle Off')
    return statement(render_template('shuffle_off'))


@ask.intent('AMAZON.LoopOnIntent')
def repeat_on() -> statement:
    log('Repeat On')
    queue.repeat = True
    return statement(render_template('repeat_on'))


@ask.intent('AMAZON.LoopOffIntent')
def repeat_off() -> statement:
    log('Repeat Off')
    queue.repeat = False
    return statement(render_template('repeat_off'))


@ask.default_intent
@ask.intent('AMAZON.FallbackIntent')
@ask.intent('AMAZON.RepeatIntent')
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


@ask.intent('AskSonicUnstarIntent')
def unstar_track() -> statement:
    log('Unstar Current Track')
    track = queue.current
    if not track:
        return statement(render_template('nothing_playing'))
    track.unstar()
    return statement(render_template('okay'))


@ask.intent('AskSonicUnstarPreviousIntent')
def unstar_previous_track() -> statement:
    log('Unstar Previous Track')
    track = queue.last
    if not track:
        return statement(render_template('no_previous_track'))
    track.unstar()
    return statement(render_template('okay'))


def _context_offset() -> Optional[int]:
    """The offsetInMilliseconds from the request's context.AudioPlayer, if
    present. Guarded so a request with no AudioPlayer context (e.g. a plain
    IntentRequest before any audio has played) doesn't raise."""
    try:
        value = context.AudioPlayer.offsetInMilliseconds
    except AttributeError:
        return None
    if value is None:
        return None
    return int(value)


def log(msg: str) -> None:
    logger.debug(msg)
    logger.debug(queue.status)
