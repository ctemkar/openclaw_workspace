from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


@dataclass
class Signal:
    symbol: str
    direction: Direction
    score: float       # 0.0 to 1.0, higher = stronger
    reason: str
    strategy_name: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class FeatureSet:
    symbol: str
    last_price: float
    returns: List[float]            # Recent percent returns
    volume: float
    avg_volume: float
    high: float
    low: float
    close_prices: List[float]       # Recent closes (oldest first)
    atr: Optional[float] = None
    timestamp: Optional[object] = None


class Strategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def generate_signals(self, features: Dict[str, FeatureSet]) -> List[Signal]: ...
