from __future__ import annotations
from config.models import RiskConfig
from broker.models import AccountSummary


class PositionSizer:
    """
    ATR-based position sizing.

    Risk per trade = equity × max_per_trade_risk_pct / 100
    Shares         = risk_per_trade / (ATR × atr_multiplier)
    Capped at max_per_symbol_pct of equity.
    """

    def calculate_size(
        self,
        symbol: str,
        account: AccountSummary,
        atr: float,
        price: float,
        config: RiskConfig,
    ) -> float:
        if price <= 0 or atr <= 0:
            return 0.0

        equity = account.equity
        risk_amount = equity * config.max_per_trade_risk_pct / 100.0
        stop_distance = atr * config.atr_multiplier

        raw_shares = risk_amount / stop_distance
        max_shares_by_value = (equity * config.max_per_symbol_pct / 100.0) / price

        shares = min(raw_shares, max_shares_by_value)
        # Round down to whole shares
        return max(0.0, float(int(shares)))
