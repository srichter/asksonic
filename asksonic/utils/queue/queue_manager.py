# This file is derived from the Flask Ask project and
# is licensed under the Apache License 2.0.
# https://github.com/johnwheeler/flask-ask

import collections
import random
import time
from typing import Optional, Union
from asksonic.utils.subsonic.track import Track


class QueueManager():
    """Manages queue data in a separate context from current_stream.
    The flask-ask Local current_stream refers only to the current data from
    Alexa requests and Skill Responses. Alexa Skills Kit does not provide
    enqueued or stream-history data and does not provide a session attribute
    when delivering AudioPlayer Requests. This class is used to maintain
    accurate control of multiple streams, so that the user may send Intents
    to move throughout a queue.
    """

    def __init__(self, tracks: Optional[list[Track]] = None) -> None:
        # Not reset by clear()/reset() - repeat is a player-wide setting that
        # should persist across switching to different content, same as on a
        # typical streaming service.
        self._repeat = False
        self.clear()
        if tracks:
            self.extend(tracks)

    @property
    def repeat(self) -> bool:
        """Whether the current track should repeat instead of advancing"""
        return self._repeat

    @repeat.setter
    def repeat(self, value: bool) -> None:
        self._repeat = value

    @property
    def status(self) -> dict[str, Union[str, list[str]]]:
        """Information about the queue"""
        status = {
            'Current Position': self.current_position,
            'Current Track': self.current,
            'Track Started': self.start_time,
            'Next Track': self.up_next,
            'Previous': self.last,
            'History': list(self.history),
            'Offset': self.offset,
            'Radio': self.radio,
        }
        return status

    @property
    def current_position(self) -> int:
        """Number of Tracks played (including current)"""
        return len(self.history) + 1

    @property
    def current(self) -> Optional[Track]:
        """The current Track"""
        return self._current

    @current.setter
    def current(self, track: Optional[Track]) -> None:
        if self.current:
            self.history.append(self.current)
        self._current = track
        self._start_time = int(time.time())
        self._offset = 0

    @property
    def start_time(self) -> int:
        return self._start_time

    @property
    def offset(self) -> int:
        """Playback position (ms) of the current Track/radio stream, as of
        the last PlaybackStopped/pause. Used to resume without relying on
        flask-ask's short-lived current_stream cache."""
        return self._offset

    @offset.setter
    def offset(self, value: int) -> None:
        self._offset = value

    @property
    def radio(self) -> Optional[dict]:
        """The currently playing Navidrome internet radio station, if any"""
        return self._radio

    @radio.setter
    def radio(self, station: Optional[dict]) -> None:
        self._radio = station

    @property
    def up_next(self) -> Optional[Track]:
        """The Track at the front of the queue"""
        try:
            return self._queue[0]
        except IndexError:
            return None

    @property
    def last(self) -> Optional[Track]:
        """The most recently played Track"""
        try:
            return self.history[-1]
        except IndexError:
            return None

    @property
    def history(self) -> collections.deque:
        """Previously played Tracks"""
        return self._history

    def next(self) -> Optional[Track]:
        """Move forward one Track"""
        if self.up_next:
            return self._step_forward()
        self.end_current()

    def previous(self) -> Optional[Track]:
        """Move backward one Track.
        If there is no history, return the same Track"""
        if self.history:
            return self._step_backward()
        return self.current

    def add(self, track: Track) -> None:
        """Add a Track to the end of the queue"""
        self._queue.append(track)

    def extend(self, tracks: list[Track]) -> None:
        """Add Tracks to the end of the queue"""
        self._queue.extend(tracks)

    def prepend(self, track: Track) -> None:
        """Add a Track to the beginning of the queue"""
        self._queue.appendleft(track)

    def shuffle(self) -> None:
        """Randomize the order of the remaining (not-yet-played) queue"""
        items = list(self._queue)
        random.shuffle(items)
        self._queue = collections.deque(items)

    def end_current(self) -> None:
        """Move the current Track to history"""
        self.current = None

    def reset(self, tracks: list[Track]) -> Track:
        """Replace the queue with Tracks and play the first one"""
        self.clear()
        self._queue = collections.deque(tracks)
        return self._step_forward()

    def clear(self) -> None:
        """Clear the queue and history"""
        self._queue = collections.deque()
        self._history = collections.deque()
        self._current = None
        self._start_time = 0
        self._offset = 0
        self._radio = None

    def _step_forward(self) -> Track:
        track = self._queue.popleft()
        self.current = track
        return track

    def _step_backward(self) -> Track:
        if self.current:
            self._queue.appendleft(self.current)
        track = self.history.pop()
        self._current = track
        self._offset = 0
        return track
