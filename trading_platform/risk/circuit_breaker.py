from __future__ import annotations
import threading
from datetime import datetime, timezone, timedelta
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "CLOSED"       # Normal operation
    OPEN = "OPEN"           # Blocking all orders
    HALF_OPEN = "HALF_OPEN" # Probing – allow limited flow


class CircuitBreaker:
    """
    Three-state circuit breaker protecting the platform from cascading failures.

    Trips to OPEN on:
      - N consecutive execution failures  (default 5)
      - Data feed unhealthy for threshold seconds
      - Daily P&L exceeds the configured loss limit

    Transitions to HALF_OPEN after cooldown_seconds, then back to CLOSED
    on the next successful event.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        data_unhealthy_threshold_seconds: float = 60.0,
        cooldown_seconds: float = 300.0,
    ) -> None:
        self._lock = threading.RLock()
        self._failure_threshold = failure_threshold
        self._data_unhealthy_threshold = timedelta(seconds=data_unhealthy_threshold_seconds)
        self._cooldown = timedelta(seconds=cooldown_seconds)

        self._state: CircuitState = CircuitState.CLOSED
        self._reason: str = ""
        self._consecutive_failures: int = 0
        self._opened_at: datetime | None = None
        self._data_unhealthy_since: datetime | None = None

    # ------------------------------------------------------------------
    # Event recorders
    # ------------------------------------------------------------------

    def record_execution_result(self, success: bool) -> None:
        with self._lock:
            if success:
                self._consecutive_failures = 0
                if self._state == CircuitState.HALF_OPEN:
                    self._reset()
            else:
                self._consecutive_failures += 1
                if self._consecutive_failures >= self._failure_threshold:
                    self._trip(
                        f"Tripped after {self._consecutive_failures} "
                        "consecutive execution failures"
                    )

    def record_data_event(self, is_healthy: bool) -> None:
        with self._lock:
            now = datetime.now(timezone.utc)
            if is_healthy:
                self._data_unhealthy_since = None
                if self._state == CircuitState.HALF_OPEN:
                    self._reset()
            else:
                if self._data_unhealthy_since is None:
                    self._data_unhealthy_since = now
                elif now - self._data_unhealthy_since >= self._data_unhealthy_threshold:
                    self._trip("Tripped due to sustained data feed unhealthy state")

    def record_pnl(
        self, daily_pnl: float, equity: float, max_loss_pct: float
    ) -> None:
        with self._lock:
            max_loss = equity * max_loss_pct / 100.0
            if daily_pnl < -max_loss:
                self._trip(
                    f"Tripped: daily P&L {daily_pnl:.2f} exceeded "
                    f"loss limit -{max_loss:.2f}"
                )

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def is_open(self) -> bool:
        """Return True if the circuit is OPEN (blocking)."""
        with self._lock:
            self.try_reset()
            return self._state == CircuitState.OPEN

    def try_reset(self) -> None:
        """Move from OPEN to HALF_OPEN once the cooldown period expires."""
        with self._lock:
            if self._state == CircuitState.OPEN and self._opened_at is not None:
                elapsed = datetime.now(timezone.utc) - self._opened_at
                if elapsed >= self._cooldown:
                    self._state = CircuitState.HALF_OPEN
                    self._reason = "Half-open: probing after cooldown"

    def get_state(self) -> CircuitState:
        with self._lock:
            self.try_reset()
            return self._state

    def get_reason(self) -> str:
        with self._lock:
            return self._reason

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _trip(self, reason: str) -> None:
        if self._state != CircuitState.OPEN:
            self._state = CircuitState.OPEN
            self._reason = reason
            self._opened_at = datetime.now(timezone.utc)

    def _reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._reason = ""
        self._consecutive_failures = 0
        self._opened_at = None
        self._data_unhealthy_since = None
