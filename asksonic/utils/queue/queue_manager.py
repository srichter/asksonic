# This file is derived from the Flask Ask project and
# is licensed under the Apache License 2.0.
# https://github.com/johnwheeler/flask-ask

import collections
from copy import copy
from typing import Optional
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

    def __init__(self, tracks: list[Track] = None) -> None:
        self.clear()
        if tracks:
            self.extend(tracks)

    @property
    def status(self) -> dict:
        """Information about the queue"""
        status = {
            'Current Position': self.current_position,
            'Current Track': self.current,
            'Next Track': self.up_next,
            'Previous': self.last,
            'History': list(self.history)
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

    def _step_forward(self) -> Track:
        track = self._queue.popleft()
        self.current = track
        return track

    def _step_backward(self) -> Track:
        if self.current:
            self._queue.appendleft(self.current)
        track = self.history.pop()
        self._current = track
        return track
