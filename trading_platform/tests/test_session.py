import pytest
from datetime import datetime
import pytz
from market_session.session_engine import SessionEngine, SessionState
from config.models import ExchangeConfig


def _make_nyse_config(holidays=None):
    return ExchangeConfig(
        name="NYSE",
        timezone="America/New_York",
        open_time="09:30",
        close_time="16:00",
        pre_open_time="09:00",
        entry_cutoff_time="15:45",
        flatten_before_close_mins=15,
        holidays=holidays or [],
    )


def _make_eu_config():
    return ExchangeConfig(
        name="Euronext",
        timezone="Europe/Paris",
        open_time="09:00",
        close_time="17:30",
        pre_open_time="08:00",
        lunch_start="12:30",
        lunch_end="13:00",
        entry_cutoff_time="17:15",
        flatten_before_close_mins=15,
    )


def _et(hour, minute, year=2024, month=6, day=3):
    """Return a UTC-aware datetime corresponding to the given Eastern Time."""
    et = pytz.timezone("America/New_York")
    local = et.localize(datetime(year, month, day, hour, minute, 0))
    return local.astimezone(pytz.utc)


def _cet(hour, minute, year=2024, month=6, day=3):
    """Return a UTC-aware datetime corresponding to the given CET time."""
    cet = pytz.timezone("Europe/Paris")
    local = cet.localize(datetime(year, month, day, hour, minute, 0))
    return local.astimezone(pytz.utc)


# ---------------------------------------------------------------------------
# Test 1: entry blocked outside regular hours
# ---------------------------------------------------------------------------

def test_entry_blocked_outside_hours():
    engine = SessionEngine(_make_nyse_config())
    after_close = _et(17, 0)   # 5 PM ET — after market close
    assert engine.can_enter(after_close) is False


# ---------------------------------------------------------------------------
# Test 2: entry allowed during normal session hours
# ---------------------------------------------------------------------------

def test_entry_allowed_in_session():
    engine = SessionEngine(_make_nyse_config())
    mid_day = _et(10, 0)   # 10 AM ET — well within open hours
    assert engine.can_enter(mid_day) is True


# ---------------------------------------------------------------------------
# Test 3: flatten triggered near the close
# ---------------------------------------------------------------------------

def test_flatten_triggered_near_close():
    engine = SessionEngine(_make_nyse_config())
    # 15:48 ET is within the 15-minute flatten window (15:45–16:00)
    near_close = _et(15, 48)
    assert engine.should_flatten(near_close) is True
    state = engine.get_state(near_close)
    assert state == SessionState.FLATTEN


# ---------------------------------------------------------------------------
# Test 4: holiday blocking
# ---------------------------------------------------------------------------

def test_holiday_blocking():
    holiday_date = "2024-07-04"
    engine = SessionEngine(_make_nyse_config(holidays=[holiday_date]))
    et = pytz.timezone("America/New_York")
    holiday_mid_day = et.localize(datetime(2024, 7, 4, 11, 0, 0)).astimezone(pytz.utc)
    assert engine.can_enter(holiday_mid_day) is False
    assert engine.get_state(holiday_mid_day) == SessionState.HOLIDAY


# ---------------------------------------------------------------------------
# Test 5: lunch break blocking for EU exchange
# ---------------------------------------------------------------------------

def test_lunch_break_blocking():
    engine = SessionEngine(_make_eu_config())
    lunch_time = _cet(12, 45)   # 12:45 CET — inside lunch window
    state = engine.get_state(lunch_time)
    assert state == SessionState.LUNCH
    assert engine.can_enter(lunch_time) is False
