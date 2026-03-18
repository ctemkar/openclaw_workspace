#!/usr/bin/env python3
"""
Trading Monitoring Script
Fetches data from trading dashboard, monitors risk parameters, and logs alerts.
"""

import requests
import json
import os
import time
from datetime import datetime
import logging
import sys
from pathlib import Path

# Configuration
BASE_DIR = Path("/Users/chetantemkar/.openclaw/workspace/app")
DASHBOARD_URL = "http://localhost:5001"
MONITORING_LOG = BASE_DIR / "trading_monitoring.log"
CRITICAL_ALERTS_LOG = BASE_DIR / "critical_alerts.log"
COMPLETED_TRADES_FILE = BASE_DIR / "completed_trades.json"
TRADING_LOG_FILE = BASE_DIR / "trading_bot_clean.log"

# Risk parameters (these could be fetched from config API)
RISK_PARAMS = {
    "capital": 100.0,  # Initial capital
    "stop_loss_pct": 0.03,  # 3% stop loss
    "take_profit_pct": 0.06,  # 6% take profit
    "critical_drawdown_pct": 0.10,  # 10% critical drawdown threshold
}

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(MONITORING_LOG, mode='a'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

class TradingMonitor:
    def __init__(self):
        self.logger = setup_logging()
        self.session = requests.Session()
        self.session.timeout = 10
        
    def fetch_dashboard_data(self):
        """Fetch data from trading dashboard API"""
        try:
            # Try to get the active port from .active_port file
            port_file = BASE_DIR / ".active_port"
            if port_file.exists():
                with open(port_file, 'r') as f:
                    port = f.read().strip()
                    url = f"http://localhost:{port}/api/status/all"
            else:
                url = f"{DASHBOARD_URL}/api/status/all"
            
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch dashboard data: {e}")
            return None
    
    def fetch_trading_config(self):
        """Fetch trading configuration from API"""
        try:
            port_file = BASE_DIR / ".active_port"
            if port_file.exists():
                with open(port_file, 'r') as f:
                    port = f.read().strip()
                    url = f"http://localhost:{port}/api/trading/configure"
            else:
                url = f"{DASHBOARD_URL}/api/trading/configure"
            
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Failed to fetch trading config: {e}")
            return None
    
    def load_completed_trades(self):
        """Load completed trades from JSON file"""
        try:
            if COMPLETED_TRADES_FILE.exists():
                with open(COMPLETED_TRADES_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load completed trades: {e}")
        return []
    
    def parse_trading_logs(self):
        """Parse recent trading logs for analysis"""
        logs = []
        try:
            if TRADING_LOG_FILE.exists():
                with open(TRADING_LOG_FILE, 'r') as f:
                    # Read last 100 lines
                    lines = f.readlines()[-100:]
                    for line in lines:
                        logs.append(line.strip())
        except Exception as e:
            self.logger.error(f"Failed to parse trading logs: {e}")
        return logs
    
    def analyze_trades(self, trades):
        """Analyze trades for performance and risk"""
        analysis = {
            "total_trades": len(trades),
            "buy_trades": 0,
            "sell_trades": 0,
            "models": {},
            "symbols": {},
            "recent_trades": [],
            "total_volume": 0,
            "avg_trade_size": 0,
        }
        
        if not trades:
            return analysis
        
        # Analyze last 10 trades
        recent_trades = trades[:10]
        analysis["recent_trades"] = recent_trades
        
        for trade in trades:
            # Count buy/sell
            if trade.get("side", "").lower() == "buy":
                analysis["buy_trades"] += 1
            elif trade.get("side", "").lower() == "sell":
                analysis["sell_trades"] += 1
            
            # Count by model
            model = trade.get("model", "unknown")
            analysis["models"][model] = analysis["models"].get(model, 0) + 1
            
            # Extract symbol from model name or infer
            if "BTC" in model.upper():
                symbol = "BTC/USD"
            elif "ETH" in model.upper():
                symbol = "ETH/USD"
            elif "SOL" in model.upper():
                symbol = "SOL/USD"
            else:
                symbol = "UNKNOWN"
            
            analysis["symbols"][symbol] = analysis["symbols"].get(symbol, 0) + 1
            
            # Calculate volume
            price = trade.get("price", 0)
            amount = trade.get("amount", 0)
            analysis["total_volume"] += price * amount
        
        if analysis["total_trades"] > 0:
            analysis["avg_trade_size"] = analysis["total_volume"] / analysis["total_trades"]
        
        return analysis
    
    def calculate_risk_metrics(self, trades, current_prices=None):
        """Calculate risk metrics based on trades"""
        risk_metrics = {
            "stop_loss_triggers": [],
            "take_profit_triggers": [],
            "drawdown_analysis": {},
            "position_summary": {},
            "pnl_analysis": {},
            "volatility_metrics": {},
        }
        
        if not trades:
            return risk_metrics
        
        # Default current prices (would ideally come from market data)
        if current_prices is None:
            current_prices = {
                "BTC/USD": 74500.0,
                "ETH/USD": 2340.0,
                "SOL/USD": 95.0,
            }
        
        # Group trades by symbol
        symbol_trades = {}
        for trade in trades:
            # Determine symbol
            model = trade.get("model", "").upper()
            if "BTC" in model:
                symbol = "BTC/USD"
            elif "ETH" in model:
                symbol = "ETH/USD"
            elif "SOL" in model:
                symbol = "SOL/USD"
            else:
                continue
            
            if symbol not in symbol_trades:
                symbol_trades[symbol] = []
            symbol_trades[symbol].append(trade)
        
        # Analyze each symbol
        for symbol, trades_list in symbol_trades.items():
            if not trades_list:
                continue
            
            # Calculate average entry price for buys
            buy_trades = [t for t in trades_list if t.get("side", "").lower() == "buy"]
            sell_trades = [t for t in trades_list if t.get("side", "").lower() == "sell"]
            
            if buy_trades:
                avg_buy_price = sum(t.get("price", 0) for t in buy_trades) / len(buy_trades)
                current_price = current_prices.get(symbol, avg_buy_price)
                
                # Calculate stop loss and take profit levels
                stop_loss_price = avg_buy_price * (1 - RISK_PARAMS["stop_loss_pct"])
                take_profit_price = avg_buy_price * (1 + RISK_PARAMS["take_profit_pct"])
                
                # Check for triggers
                if current_price <= stop_loss_price:
                    risk_metrics["stop_loss_triggers"].append({
                        "symbol": symbol,
                        "avg_entry": avg_buy_price,
                        "current": current_price,
                        "stop_loss": stop_loss_price,
                        "drawdown_pct": (current_price - avg_buy_price) / avg_buy_price * 100,
                    })
                
                if current_price >= take_profit_price:
                    risk_metrics["take_profit_triggers"].append({
                        "symbol": symbol,
                        "avg_entry": avg_buy_price,
                        "current": current_price,
                        "take_profit": take_profit_price,
                        "profit_pct": (current_price - avg_buy_price) / avg_buy_price * 100,
                    })
                
                # Calculate drawdown
                drawdown_pct = (current_price - avg_buy_price) / avg_buy_price * 100
                risk_metrics["drawdown_analysis"][symbol] = {
                    "avg_entry": avg_buy_price,
                    "current": current_price,
                    "drawdown_pct": drawdown_pct,
                    "is_critical": abs(drawdown_pct) >= RISK_PARAMS["critical_drawdown_pct"] * 100,
                }
                
                risk_metrics["position_summary"][symbol] = {
                    "avg_entry": avg_buy_price,
                    "current": current_price,
                    "buy_count": len(buy_trades),
                    "sell_count": len(sell_trades),
                    "net_position": "LONG" if len(buy_trades) > len(sell_trades) else "SHORT",
                    "unrealized_pnl": (current_price - avg_buy_price) * len(buy_trades),
                    "unrealized_pnl_pct": (current_price - avg_buy_price) / avg_buy_price * 100,
                }
        
        # Calculate P&L metrics
        risk_metrics["pnl_analysis"] = self.calculate_pnl_metrics(trades)
        
        # Calculate volatility metrics
        risk_metrics["volatility_metrics"] = self.calculate_volatility_metrics(trades)
        
        return risk_metrics
    
    def calculate_pnl_metrics(self, trades):
        """Calculate profit and loss metrics"""
        pnl_metrics = {
            "total_realized_pnl": 0,
            "total_unrealized_pnl": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "largest_win": 0,
            "largest_loss": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "win_rate": 0,
        }
        
        if not trades:
            return pnl_metrics
        
        # For simplicity, we'll calculate based on completed trades
        # In a real system, you'd track entry/exit prices
        
        return pnl_metrics
    
    def calculate_volatility_metrics(self, trades):
        """Calculate volatility and risk metrics"""
        volatility_metrics = {
            "trade_frequency": 0,
            "avg_trade_interval": 0,
            "position_concentration": {},
            "risk_score": 0,
        }
        
        if not trades or len(trades) < 2:
            return volatility_metrics
        
        # Calculate trade frequency
        try:
            times = []
            for trade in trades:
                if "time" in trade:
                    # Parse time string to timestamp
                    # This is simplified - would need proper datetime parsing
                    times.append(0)  # Placeholder
            
            if len(times) > 1:
                volatility_metrics["trade_frequency"] = len(trades) / (max(times) - min(times)) if max(times) > min(times) else 0
        except:
            pass
        
        return volatility_metrics
    
    def log_monitoring_data(self, dashboard_data, trade_analysis, risk_metrics):
        """Log monitoring data to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"""
=== Trading Monitoring Log ===
Timestamp: {timestamp} (Asia/Bangkok)

1. DASHBOARD STATUS:
   - Status: {dashboard_data.get('status', 'UNKNOWN') if dashboard_data else 'NO DATA'}
   - Last Update: {dashboard_data.get('timestamp', 'N/A') if dashboard_data else 'N/A'}
   - Total Trades: {trade_analysis['total_trades']}

2. TRADE ANALYSIS:
   - Total Trades: {trade_analysis['total_trades']}
   - Buy Trades: {trade_analysis['buy_trades']}
   - Sell Trades: {trade_analysis['sell_trades']}
   - Buy/Sell Ratio: {trade_analysis['buy_trades']/trade_analysis['sell_trades']:.2f}:1 if trade_analysis['sell_trades'] > 0 else 'N/A'
   - Total Volume: ${trade_analysis['total_volume']:.2f}
   - Avg Trade Size: ${trade_analysis['avg_trade_size']:.2f}
   
   Models Used:
"""
        
        for model, count in trade_analysis['models'].items():
            log_entry += f"     - {model}: {count} trades\n"
        
        log_entry += f"""
   Symbols Traded:
"""
        for symbol, count in trade_analysis['symbols'].items():
            log_entry += f"     - {symbol}: {count} trades\n"
        
        log_entry += f"""
3. RISK METRICS:
   - Stop-Loss Triggers: {len(risk_metrics['stop_loss_triggers'])}
   - Take-Profit Triggers: {len(risk_metrics['take_profit_triggers'])}
   - Critical Drawdowns: {sum(1 for d in risk_metrics['drawdown_analysis'].values() if d.get('is_critical', False))}
   
   Position Summary:
"""
        for symbol, summary in risk_metrics['position_summary'].items():
            pnl = summary.get('unrealized_pnl', 0)
            pnl_pct = summary.get('unrealized_pnl_pct', 0)
            pnl_sign = "+" if pnl >= 0 else ""
            log_entry += f"     - {symbol}: {summary.get('net_position', 'N/A')}, Entry: ${summary.get('avg_entry', 0):.2f}, Current: ${summary.get('current', 0):.2f}, P&L: {pnl_sign}${pnl:.2f} ({pnl_sign}{pnl_pct:.2f}%)\n"
        
        log_entry += f"""
4. RECENT TRADES (last 5):
"""
        for i, trade in enumerate(trade_analysis['recent_trades'][:5], 1):
            log_entry += f"   {i}. {trade.get('time', 'N/A')} - {trade.get('model', 'N/A')} - {trade.get('side', 'N/A').upper()} at ${trade.get('price', 0):.2f}\n"
        
        log_entry += f"""
5. SYSTEM HEALTH:
   - Dashboard: {'ONLINE' if dashboard_data else 'OFFLINE'}
   - Trades File: {'PRESENT' if COMPLETED_TRADES_FILE.exists() else 'MISSING'}
   - Log File: {'PRESENT' if TRADING_LOG_FILE.exists() else 'MISSING'}
   
=== End of Monitoring Entry ===
"""
        
        # Write to monitoring log
        with open(MONITORING_LOG, 'a') as f:
            f.write(log_entry)
        
        self.logger.info(f"Monitoring data logged at {timestamp}")
        
        # Check for critical alerts
        self.check_critical_alerts(risk_metrics, timestamp)
    
    def check_critical_alerts(self, risk_metrics, timestamp):
        """Check for critical alerts and log them if found"""
        critical_alerts = []
        
        # Check stop-loss triggers
        for trigger in risk_metrics['stop_loss_triggers']:
            alert = {
                "type": "STOP_LOSS_TRIGGERED",
                "symbol": trigger['symbol'],
                "message": f"Stop loss triggered for {trigger['symbol']}! Entry: ${trigger['avg_entry']:.2f}, Current: ${trigger['current']:.2f}, Drawdown: {trigger['drawdown_pct']:.2f}%",
                "severity": "HIGH",
                "data": trigger,
            }
            critical_alerts.append(alert)
        
        # Check take-profit triggers
        for trigger in risk_metrics['take_profit_triggers']:
            alert = {
                "type": "TAKE_PROFIT_TRIGGERED",
                "symbol": trigger['symbol'],
                "message": f"Take profit triggered for {trigger['symbol']}! Entry: ${trigger['avg_entry']:.2f}, Current: ${trigger['current']:.2f}, Profit: {trigger['profit_pct']:.2f}%",
                "severity": "MEDIUM",
                "data": trigger,
            }
            critical_alerts.append(alert)
        
        # Check critical drawdowns
        for symbol, drawdown in risk_metrics['drawdown_analysis'].items():
            if drawdown.get('is_critical', False):
                alert = {
                    "type": "CRITICAL_DRAWDOWN",
                    "symbol": symbol,
                    "message": f"Critical drawdown detected for {symbol}! Drawdown: {drawdown['drawdown_pct']:.2f}% (Threshold: {RISK_PARAMS['critical_drawdown_pct']*100}%)",
                    "severity": "CRITICAL",
                    "data": drawdown,
                }
                critical_alerts.append(alert)
        
        # Log critical alerts if any
        if critical_alerts:
            alert_entry = f"\n=== Critical Alerts Log ===\nTimestamp: {timestamp} (Asia/Bangkok)\n\n"
            alert_entry += f"Alert Status: {len(critical_alerts)} CRITICAL ALERT(S) DETECTED\n\n"
            
            for i, alert in enumerate(critical_alerts, 1):
                alert_entry += f"{i}. [{alert['severity']}] {alert['type']}\n"
                alert_entry += f"   Symbol: {alert['symbol']}\n"
                alert_entry += f"   Message: {alert['message']}\n"
                alert_entry += f"   Details: Entry=${alert['data'].get('avg_entry', 'N/A'):.2f}, Current=${alert['data'].get('current', 'N/A'):.2f}\n\n"
            
            alert_entry += "Recommended Actions:\n"
            for alert in critical_alerts:
                if alert['type'] == "STOP_LOSS_TRIGGERED":
                    alert_entry += f"  - Consider closing {alert['symbol']} position to limit losses\n"
                elif alert['type'] == "TAKE_PROFIT_TRIGGERED":
                    alert_entry += f"  - Consider taking profits on {alert['symbol']} position\n"
                elif alert['type'] == "CRITICAL_DRAWDOWN":
                    alert_entry += f"  - Review {alert['symbol']} strategy immediately\n"
            
            alert_entry += "\n=== End of Alert Entry ===\n"
            
            # Write to critical alerts log
            with open(CRITICAL_ALERTS_LOG, 'a') as f:
                f.write(alert_entry)
            
            self.logger.warning(f"{len(critical_alerts)} critical alert(s) detected and logged")
        else:
            # Log no alerts status
            no_alert_entry = f"""
=== Critical Alerts Log ===
Timestamp: {timestamp} (Asia/Bangkok)

Alert Status: NO NEW CRITICAL ALERTS

Recent Checks:
1. Stop-Loss Triggers: {len(risk_metrics['stop_loss_triggers'])} detected
2. Take-Profit Triggers: {len(risk_metrics['take_profit_triggers'])} detected
3. Critical Drawdown: {sum(1 for d in risk_metrics['drawdown_analysis'].values() if d.get('is_critical', False))} detected

Monitoring Status: All systems normal
Next Check: Scheduled monitoring will continue

=== End of Alert Entry ===
"""
            with open(CRITICAL_ALERTS_LOG, 'a') as f:
                f.write(no_alert_entry)
            
            self.logger.info("No critical alerts detected")
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        self.logger.info("Starting trading monitoring cycle...")
        
        # Fetch data
        dashboard_data = self.fetch_dashboard_data()
        trading_config = self.fetch_trading_config()
        
        # Load and analyze trades
        trades = self.load_completed_trades()
        trade_analysis = self.analyze_trades(trades)
        
        # Calculate risk metrics
        risk_metrics = self.calculate_risk_metrics(trades)
        
        # Log monitoring data
        self.log_monitoring_data(dashboard_data, trade_analysis, risk_metrics)
        
        # Parse and log recent trading activity
        logs = self.parse_trading_logs()
        if logs:
            self.logger.info(f"Parsed {len(logs)} recent log entries")
        
        self.logger.info("Monitoring cycle completed")
        
        return {
            "dashboard_data": dashboard_data,
            "trade_analysis": trade_analysis,
            "risk_metrics": risk_metrics,
            "log_count": len(logs),
        }
    
    def continuous_monitoring(self, interval_seconds=300):
        """Run continuous monitoring at specified interval"""
        self.logger.info(f"Starting continuous monitoring (interval: {interval_seconds}s)")
        
        try:
            while True:
                start_time = time.time()
                
                # Run monitoring cycle
                results = self.run_monitoring_cycle()
                
                # Calculate time to sleep
                elapsed = time.time() - start_time
                sleep_time = max(1, interval_seconds - elapsed)
                
                self.logger.info(f"Next monitoring cycle in {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
            raise

def main():
    """Main entry point"""
    monitor = TradingMonitor()
    
    # Check if we should run continuously or once
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor.continuous_monitoring()
    else:
        # Run single monitoring cycle
        results = monitor.run_monitoring_cycle()
        print(f"Monitoring completed. Check {MONITORING_LOG} for details.")

if __name__ == "__main__":
    main()