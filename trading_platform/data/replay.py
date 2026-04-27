from __future__ import annotations
import csv
import json
from datetime import datetime, timezone
from typing import Dict, Iterator, List, Optional, Tuple

from .feed import Quote


class ReplayEngine:
    """
    Replays historical OHLCV data from a CSV or JSON file bar by bar.

    CSV format expected:
        timestamp,symbol,open,high,low,close,volume

    JSON format expected:
        A list of objects with the same field names.

    Usage::

        engine = ReplayEngine("data.csv")
        for timestamp, quotes in engine:
            feed.inject_quote(quotes["SPY"])
    """

    def __init__(self, data_file: str, speed_multiplier: float = 1.0) -> None:
        self._data_file = data_file
        self._speed_multiplier = speed_multiplier
        self._bars: List[Tuple[datetime, Dict[str, Quote]]] = []
        self._cursor: int = 0
        self._load()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if self._data_file.endswith(".json"):
            self._load_json()
        else:
            self._load_csv()
        self._bars.sort(key=lambda x: x[0])

    def _load_csv(self) -> None:
        grouped: Dict[datetime, Dict[str, Quote]] = {}
        with open(self._data_file, newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                ts = self._parse_timestamp(row["timestamp"])
                symbol = row["symbol"]
                quote = Quote(
                    symbol=symbol,
                    bid=float(row.get("open", row.get("close", 0))),
                    ask=float(row.get("high", row.get("close", 0))),
                    last=float(row["close"]),
                    volume=float(row.get("volume", 0)),
                    timestamp=ts,
                )
                if ts not in grouped:
                    grouped[ts] = {}
                grouped[ts][symbol] = quote
        self._bars = list(grouped.items())

    def _load_json(self) -> None:
        grouped: Dict[datetime, Dict[str, Quote]] = {}
        with open(self._data_file) as fh:
            records = json.load(fh)
        for row in records:
            ts = self._parse_timestamp(str(row["timestamp"]))
            symbol = str(row["symbol"])
            quote = Quote(
                symbol=symbol,
                bid=float(row.get("open", row.get("close", 0))),
                ask=float(row.get("high", row.get("close", 0))),
                last=float(row["close"]),
                volume=float(row.get("volume", 0)),
                timestamp=ts,
            )
            if ts not in grouped:
                grouped[ts] = {}
            grouped[ts][symbol] = quote
        self._bars = list(grouped.items())

    @staticmethod
    def _parse_timestamp(value: str) -> datetime:
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(value, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
        # Fallback: try fromisoformat
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def __iter__(self) -> Iterator[Tuple[datetime, Dict[str, Quote]]]:
        for bar in self._bars[self._cursor:]:
            self._cursor += 1
            yield bar

    def fast_forward(self, to: datetime) -> None:
        """Advance the cursor to the first bar at or after *to*."""
        if to.tzinfo is None:
            to = to.replace(tzinfo=timezone.utc)
        for i, (ts, _) in enumerate(self._bars):
            if ts >= to:
                self._cursor = i
                return
        self._cursor = len(self._bars)

    def reset(self) -> None:
        self._cursor = 0

    def get_speed_multiplier(self) -> float:
        return self._speed_multiplier

    def set_speed_multiplier(self, value: float) -> None:
        self._speed_multiplier = value

    def total_bars(self) -> int:
        return len(self._bars)

    def remaining_bars(self) -> int:
        return len(self._bars) - self._cursor
