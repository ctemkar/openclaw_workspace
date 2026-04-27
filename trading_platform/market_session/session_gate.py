from __future__ import annotations
from datetime import datetime
from typing import Callable, Optional

from .session_engine import SessionEngine, SessionState


class SessionGate:
    """
    A gate that wraps a callable and only executes it when the market
    session permits entries.  Useful for wrapping strategy signal routing.
    """

    def __init__(self, engine: SessionEngine) -> None:
        self._engine = engine

    def allow_entry(self, now: Optional[datetime] = None) -> bool:
        return self._engine.can_enter(now)

    def allow_exit(self, now: Optional[datetime] = None) -> bool:
        """Exits are always allowed during market hours and during flatten window."""
        state = self._engine.get_state(now)
        return state not in (SessionState.CLOSED, SessionState.HOLIDAY)

    def gate(
        self,
        fn: Callable,
        now: Optional[datetime] = None,
        *args,
        **kwargs,
    ):
        """
        Execute *fn* only if the session gate is open for entries.
        Returns the function's result or None if gated out.
        """
        if self.allow_entry(now):
            return fn(*args, **kwargs)
        return None
