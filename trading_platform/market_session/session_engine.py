from __future__ import annotations
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Optional
import pytz

from config.models import ExchangeConfig


class SessionState(str, Enum):
    PRE_MARKET = "PRE_MARKET"
    OPEN = "OPEN"
    LUNCH = "LUNCH"
    POST_MARKET = "POST_MARKET"
    CLOSED = "CLOSED"
    HOLIDAY = "HOLIDAY"
    FLATTEN = "FLATTEN"   # Near-close window – exit only


def _parse_hhmm(hhmm: str) -> time:
    parts = hhmm.split(":")
    return time(int(parts[0]), int(parts[1]))


class SessionEngine:
    """
    Determines the current market session state and whether new entries
    or flattening are appropriate based on the exchange configuration.
    """

    def __init__(self, config: ExchangeConfig) -> None:
        self._cfg = config
        self._tz = pytz.timezone(config.timezone)

        self._open = _parse_hhmm(config.open_time)
        self._close = _parse_hhmm(config.close_time)
        self._pre_open = _parse_hhmm(config.pre_open_time)
        self._entry_cutoff = _parse_hhmm(config.entry_cutoff_time)
        self._flatten_delta = timedelta(minutes=config.flatten_before_close_mins)

        self._lunch_start: Optional[time] = (
            _parse_hhmm(config.lunch_start) if config.lunch_start else None
        )
        self._lunch_end: Optional[time] = (
            _parse_hhmm(config.lunch_end) if config.lunch_end else None
        )

        # Pre-compute flatten cutoff time
        dummy_date = datetime(2000, 1, 1)
        close_dt = datetime.combine(dummy_date, self._close)
        flatten_dt = close_dt - self._flatten_delta
        self._flatten_start: time = flatten_dt.time()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_state(self, now: Optional[datetime] = None) -> SessionState:
        """Return the current session state for the given UTC datetime."""
        local = self._to_local(now)
        t = local.time()
        date_str = local.strftime("%Y-%m-%d")

        if date_str in self._cfg.holidays:
            return SessionState.HOLIDAY

        if not (self._pre_open <= t < self._close):
            return SessionState.CLOSED

        if t < self._open:
            return SessionState.PRE_MARKET

        if self._lunch_start and self._lunch_end:
            if self._lunch_start <= t < self._lunch_end:
                return SessionState.LUNCH

        if t >= self._flatten_start:
            return SessionState.FLATTEN

        return SessionState.OPEN

    def can_enter(self, now: Optional[datetime] = None) -> bool:
        """True if new long/short entries are permitted."""
        state = self.get_state(now)
        local = self._to_local(now)
        t = local.time()
        return state == SessionState.OPEN and t < self._entry_cutoff

    def should_flatten(self, now: Optional[datetime] = None) -> bool:
        """True if positions should be closed (near close or holiday)."""
        state = self.get_state(now)
        return state in (SessionState.FLATTEN, SessionState.HOLIDAY, SessionState.CLOSED)

    def is_trading_day(self, now: Optional[datetime] = None) -> bool:
        """True if today is not a holiday or weekend."""
        local = self._to_local(now)
        if local.strftime("%Y-%m-%d") in self._cfg.holidays:
            return False
        return local.weekday() < 5  # Mon-Fri

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _to_local(self, now: Optional[datetime]) -> datetime:
        if now is None:
            now = datetime.utcnow().replace(tzinfo=pytz.utc)
        if now.tzinfo is None:
            now = pytz.utc.localize(now)
        return now.astimezone(self._tz)
