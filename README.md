# AskSonic
AskSonic is an Alexa skill to play music from Subsonic API compatible music servers. It's powered by Flask-Ask and the Flask Python web framework.

## Features
- Shuffle music from your library
    - _Ask sub sonic to play my library_
- Current track information
    - _Ask sub sonic what song this is_
    - _Ask sub sonic what album this song is from_
- Star tracks
    - _Tell sub sonic to star this song_
    - _Tell sub sonic to star the last song_

Standard playback controls (_Alexa: Pause, Resume, Previous, Next, etc._) can be used without using the skill's name.
AskSonic will scrobble tracks with the server after they finish playing.

### Planned Features
- Play specific artists, albums, songs, playlists
- Add specific songs to the play queue via interactive search

## Setup
AskSonic can easily run in a free [Heroku dyno](#running-on-heroku), or run [alongside your Subsonic server](#running-locally). Once it's running, you'll need to [Create the Alexa skill](#creating-the-alexa-skill)

### Configuring the Subsonic server
It's recommended to use a non-admin user as we will be storing the login credentials in AskSonic's configuration. Consider how your Subsonic server handles play counts, starred tracks, playlists, etc. to decide if you want to create a new user account or use your existing one. You may want to configure transcoding for this user/player as Alexa has [limited file-type support](https://developer.amazon.com/en-US/docs/alexa/custom-skills/audioplayer-interface-reference.html#audio-stream-requirements).

### Running on Heroku
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/srichter/asksonic)
1. Create a Heroku account and login
2. Click the button above
3. Choose a name for your app. You may want to add random characters to the name to obfuscate your app's URL
4. Fill in the configuration variables. See [Configuration](#configuration) for further details
5. Click `Deploy app`. Once deployment completes, click `View` and copy the URL

### Running locally
If you instead prefer to host the AskSonic server yourself, you can follow these steps:
1. Clone the repository and install requirements: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill it in. See [Configuration](#configuration) for further details
3. Install `foreman` (Either the [Gem](https://github.com/ddollar/foreman) or the [Node version](https://github.com/strongloop/node-foreman))
4. You can start the server with `foreman start`. If you would like to run the server in debug mode, you can use the `Procfile.dev` instead
5. Your AskSonic server will need to be publicly accessible over https with a valid certificate. The best option is to use a reverse proxy such as [Caddy](https://github.com/caddyserver/caddy) with a certificate from Let's Encrypt

### Creating the Alexa Skill
1. [Visit the Alexa Console](https://developer.amazon.com/alexa/console/ask) and select `Create Skill`. Use the same Amazon account that is logged in to your Alexa-powered device
2. Enter a name for your skill (this doesn't affect how you invoke the skill from Alexa). Select `Custom` for the model and `Provision your Own` for the backend. Select `Start from Scratch` for the skill template
3. Once the skill is created, from the skill menu, select `Interaction Model -> JSON Editor` and paste in the contents of [interactionModel.json](/../../raw/main/interactionModel.json). Then select `Save Model`
4. Select `Invocation` from the menu. Here you can adjust how you invoke the skill from within Alexa
5. Select `Endpoint` from the menu. Change to `HTTPS` and enter the URL to your AskSonic instance under `Default Region`. If you customized `ASKS_ROUTE_PREFIX`, add that to the end of the URL, otherwise add `/alexa`. Select the SSL certificate type. If you used Heroku this will be `My development endpoint is a sub-domain [...]`
6. Select `Interfaces` from menu. Enable the Audio Player interface
7. Select `Save Model` and `Build Model`

**Important: Do not publish the skill as that would allow anyone to access your Subsonic server and potentially retrieve the login credentials**

## Configuration
| Variable | Description | Required |
|-|-|:-:|
| ``ASKS_SUBSONIC_URL`` | The base URL of your Subsonic-compatible music server. (Must be https) | ✅ |
| ``ASKS_SUBSONIC_USER`` | Your Subsonic server username | ✅ |
| ``ASKS_SUBSONIC_PASS`` | Your Subsonic server password | ✅ |
| ``ASKS_SUBSONIC_PORT`` | The port your Subsonic server listens on (if not the default for https) | Default: 443 |
| ``ASKS_HOST`` | The host AskSonic's server will listen on | Default: 0.0.0.0 |
| ``ASKS_PORT`` | The port AskSonic's server will listen on | Default: 4545 or `$PORT` |
| ``ASKS_ROUTE_PREFIX`` | The endpoint that Alexa will use to communicate with AskSonic. You can obscure your AskSonic instance by customizing this | Default: /alexa |
| ``ASKS_TRACKS_COUNT`` | The number of tracks enqueued at a time | Default: 50 |
| ``ASKS_EXTRA_SECRET`` | An extra secret that will be appended to all requests as either a header or to the query string. Useful for authenticating requests if your Subsonic server is behind a WAF such as Cloudflare | ❌ |

## Acknowledgements
AskSonic was inspired by the following projects:
 - [Geemusic](https://github.com/stevenleeg/geemusic)
 - [Sublexa](https://github.com/andocromn/sublexa)
 - [Flask-Ask](https://github.com/johnwheeler/flask-ask)

AskSonic recommends the following Subsonic-compatible music server:
 - [Navidrome](https://github.com/navidrome/navidrome)

## License
AskSonic is licensed under the [MIT License](./LICENSE).
