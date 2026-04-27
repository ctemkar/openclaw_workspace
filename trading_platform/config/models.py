from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, field_validator


class ExchangeConfig(BaseModel):
    name: str
    timezone: str
    open_time: str          # HH:MM
    close_time: str         # HH:MM
    pre_open_time: str      # HH:MM
    lunch_start: Optional[str] = None
    lunch_end: Optional[str] = None
    entry_cutoff_time: str  # HH:MM
    flatten_before_close_mins: int = 15
    holidays: List[str] = []
    allow_overnight: bool = False

    @field_validator("open_time", "close_time", "pre_open_time", "entry_cutoff_time", mode="before")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        parts = str(v).split(":")
        if len(parts) != 2:
            raise ValueError(f"Time must be HH:MM, got: {v}")
        h, m = parts
        if not (0 <= int(h) <= 23 and 0 <= int(m) <= 59):
            raise ValueError(f"Invalid time value: {v}")
        return str(v)


class BrokerConfig(BaseModel):
    adapter: str = "paper"          # paper | alpaca
    base_url: Optional[str] = None
    api_key_env: str = "ALPACA_API_KEY"
    api_secret_env: str = "ALPACA_API_SECRET"
    paper_initial_capital: float = 100_000.0


class RiskConfig(BaseModel):
    max_daily_loss_pct: float
    max_per_trade_risk_pct: float
    max_per_symbol_pct: float
    max_portfolio_concentration_pct: float
    max_concurrent_positions: int
    kill_switch: bool = False
    atr_period: int = 14
    atr_multiplier: float = 2.0


class StrategyConfig(BaseModel):
    enabled_strategies: List[str]
    symbol_universe: List[str]
    min_volume: float = 1_000_000.0
    min_price: float = 5.0


class ExecutionConfig(BaseModel):
    max_retries: int = 3
    retry_backoff_seconds: float = 1.0
    time_in_force: str = "DAY"


class DataConfig(BaseModel):
    primary_feed: str = "polygon"
    fallback_feed: Optional[str] = None
    freshness_threshold_seconds: int = 30
    heartbeat_interval_seconds: int = 10


class DashboardConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080


class PlatformConfig(BaseModel):
    exchange: ExchangeConfig
    broker: BrokerConfig
    risk: RiskConfig
    strategy: StrategyConfig
    execution: ExecutionConfig
    data: DataConfig
    dashboard: DashboardConfig
    mode: str = "paper"
