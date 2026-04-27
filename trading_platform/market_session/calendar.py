from __future__ import annotations
from datetime import date, timedelta
from typing import List


class TradingCalendar:
    """
    Minimal trading calendar that knows about weekends and user-supplied
    holiday lists.  Can be extended to fetch exchange calendars via API.
    """

    def __init__(self, holidays: List[str] | None = None) -> None:
        self._holidays = set(holidays or [])

    def is_trading_day(self, d: date) -> bool:
        if d.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        return d.isoformat() not in self._holidays

    def next_trading_day(self, from_date: date) -> date:
        d = from_date + timedelta(days=1)
        while not self.is_trading_day(d):
            d += timedelta(days=1)
        return d

    def previous_trading_day(self, from_date: date) -> date:
        d = from_date - timedelta(days=1)
        while not self.is_trading_day(d):
            d -= timedelta(days=1)
        return d

    def trading_days_between(self, start: date, end: date) -> List[date]:
        """Return a sorted list of trading days in [start, end]."""
        days: List[date] = []
        current = start
        while current <= end:
            if self.is_trading_day(current):
                days.append(current)
            current += timedelta(days=1)
        return days
