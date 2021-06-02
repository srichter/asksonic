from flask import render_template
from flask_ask import question, audio
from asksonic import ask, getStreamUrl, subsonic


@ask.launch
def launch() -> question:
    return question(render_template('launch_text')) \
        .simple_card(
            title=render_template('launch_title'),
            content=render_template('launch_content')
        )

