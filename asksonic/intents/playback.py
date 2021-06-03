from flask.templating import render_template
from asksonic import ask
from flask_ask import audio, logger


empty = '{"response": {}}'


@ask.on_playback_started()
def started():
    logger.debug('Playback Started')
    return empty


@ask.on_playback_stopped()
def stopped():
    logger.debug('Playback Stopped')
    return empty


@ask.intent('AMAZON.PauseIntent')
def pause():
    logger.debug('Playback Pausing')
    return audio(render_template('pausing')).stop()


@ask.intent('AMAZON.ResumeIntent')
def resume():
    logger.debug('Playback Resuming')
    return audio(render_template('resuming')).resume()


@ask.intent('AMAZON.StopIntent')
def stop():
    logger.debug('Playback Stopping')
    return audio(render_template('stopping')).stop()


@ask.on_playback_play_command()
def play_command():
    logger.debug('Play Command Issued')
    return audio().resume()


@ask.on_playback_pause_command()
def pause_command():
    logger.debug('Pause Command Issued')
    return audio().stop()
