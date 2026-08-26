"""In-memory session storage.

A prototype-appropriate store: a dict with an LRU cap, no database. Every
session holds the learner profile, the conversation, and the most recently
generated path. Swapping this for Redis or Postgres would touch only this file
— nothing else in the app reaches for persistence.
"""

from __future__ import annotations

import threading
import uuid
from collections import OrderedDict

from app.ml.conversation import Session
from app.ml.profiler import LearnerProfile

MAX_SESSIONS = 500


class SessionStore:
    def __init__(self, capacity: int = MAX_SESSIONS) -> None:
        self._sessions: OrderedDict[str, Session] = OrderedDict()
        self._capacity = capacity
        self._lock = threading.Lock()

    def create(self, name: str = "Learner") -> Session:
        session_id = uuid.uuid4().hex[:12]
        session = Session(id=session_id, profile=LearnerProfile(id=session_id, name=name))
        with self._lock:
            self._sessions[session_id] = session
            while len(self._sessions) > self._capacity:
                self._sessions.popitem(last=False)
        return session

    def get(self, session_id: str) -> Session | None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is not None:
                self._sessions.move_to_end(session_id)
            return session

    def __len__(self) -> int:
        return len(self._sessions)


STORE = SessionStore()
