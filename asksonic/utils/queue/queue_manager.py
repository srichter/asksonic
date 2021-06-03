# This file is derived from the Flask Ask project and
# is licensed under the Apache License 2.0.
# https://github.com/johnwheeler/flask-ask

import collections
from copy import copy
from typing import Optional


class QueueManager(object):
    """Manages queue data in a separate context from current_stream.
    The flask-ask Local current_stream refers only to the current data from
    Alexa requests and Skill Responses. Alexa Skills Kit does not provide
    enqueued or stream-history data and does not provide a session attribute
    when delivering AudioPlayer Requests. This class is used to maintain
    accurate control of multiple streams, so that the user may send Intents
    to move throughout a queue.
    """

    def __init__(self, tracks: list[Optional[dict]] = []) -> None:
        self.reset(tracks)

    @property
    def status(self) -> dict:
        status = {
            'Current Position': self.current_position,
            'Current Track': self.current,
            'Next Track': self.up_next,
            'Previous': self.previous,
            'History': list(self.history)
        }
        return status

    @property
    def up_next(self) -> Optional[dict]:
        """Returns the track at the front of the queue"""
        qcopy = copy(self._queued)
        try:
            return qcopy.popleft()
        except IndexError:
            return None

    @property
    def current(self) -> Optional[dict]:
        return self._current

    @current.setter
    def current(self, track: dict) -> None:
        self._save_to_history()
        self._current = track

    @property
    def history(self) -> collections.deque:
        return self._history

    @property
    def previous(self) -> Optional[dict]:
        history = copy(self.history)
        try:
            return history.pop()
        except IndexError:
            return None

    def add(self, track: dict) -> None:
        self._tracks.append(track)
        self._queued.append(track)

    def extend(self, tracks: list[dict]) -> None:
        self._tracks.extend(tracks)
        self._queued.extend(tracks)

    def _save_to_history(self) -> None:
        if self._current:
            self._history.append(self._current)

    def end_current(self) -> None:
        self._save_to_history()
        self._current = None

    def step(self) -> Optional[dict]:
        self.end_current()
        self._current = self._queued.popleft()
        return self._current

    def step_back(self) -> Optional[dict]:
        self._queued.appendleft(self._current)
        self._current = self._history.pop()
        return self._current

    def reset(self, tracks: list[Optional[dict]]) -> None:
        self._tracks = tracks
        self._queued = collections.deque(tracks)
        self._history = collections.deque()
        self._current = None

    def start(self) -> Optional[dict]:
        self.__init__(self._tracks)
        return self.step()

    @property
    def current_position(self) -> int:
        return len(self._history) + 1
