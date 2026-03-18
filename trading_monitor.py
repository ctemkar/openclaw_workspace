import requests
import json
import datetime
import re

LOG_FILE = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
CRITICAL_ALERTS_FILE = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

def fetch_trading_data():
    try:
        # Try to get JSON data from the dashboard
        response = requests.get("http://localhost:5001/summary")
        response.raise_for_status()
        
        # Parse the text data
        content = response.text
        return parse_trading_summary(content)
    except requests.exceptions.RequestException as e:
        log_message(f"Error fetching data: {e}")
        return None
    except Exception as e:
        log_message(f"Error processing data: {e}")
        return None

def parse_trading_summary(content):
    """Parse the text trading summary into structured data"""
    data = {
        "parameters": {},
        "trades": [],
        "market_analysis": {}
    }
    
    # Extract capital and parameters
    capital_match = re.search(r'Capital:\s*\$([\d,]+\.\d+)', content)
    if capital_match:
        data["parameters"]["capital"] = float(capital_match.group(1).replace(',', ''))
    
    stop_loss_match = re.search(r'Stop-loss:\s*([\d\.]+)%', content)
    if stop_loss_match:
        data["parameters"]["stop_loss"] = float(stop_loss_match.group(1))
    
    take_profit_match = re.search(r'Take-profit:\s*([\d\.]+)%', content)
    if take_profit_match:
        data["parameters"]["take_profit"] = float(take_profit_match.group(1))
    
    # Extract BTC price - look for BTC/USD section
    btc_section = re.search(r'🔍 Analyzing BTC/USD.*?(?=🔍 Analyzing|\Z)', content, re.DOTALL)
    if btc_section:
        btc_price_match = re.search(r'Price:\s*\$([\d,]+\.\d+)', btc_section.group(0))
        if btc_price_match:
            data["market_analysis"]["btc_price"] = float(btc_price_match.group(1).replace(',', ''))
    
    # Extract ETH price - look for ETH/USD section
    eth_section = re.search(r'🔍 Analyzing ETH/USD.*?(?=🔍 Analyzing|\Z)', content, re.DOTALL)
    if eth_section:
        eth_price_match = re.search(r'Price:\s*\$([\d,]+\.\d+)', eth_section.group(0))
        if eth_price_match:
            data["market_analysis"]["eth_price"] = float(eth_price_match.group(1).replace(',', ''))
    
    # Check for max trades reached
    max_trades_match = re.search(r"Today's trades:\s*(\d+)/\d+", content)
    if max_trades_match:
        data["parameters"]["trades_today"] = int(max_trades_match.group(1))
    
    # Check for alerts in the content
    if "MAX DAILY TRADES REACHED" in content:
        data["alerts"] = ["MAX_DAILY_TRADES_REACHED"]
    
    if "NO stop-loss or take-profit triggers" in content:
        data["alerts"] = data.get("alerts", []) + ["NO_CRITICAL_TRIGGERS"]
    
    return data

def log_message(message):
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def log_critical_alert(alert):
    timestamp = datetime.datetime.now().isoformat()
    with open(CRITICAL_ALERTS_FILE, "a") as f:
        f.write(f"CRITICAL ALERT [{timestamp}]: {alert}\n")

def analyze_data(data):
    if not data or "parameters" not in data:
        log_message("Incomplete data received.")
        return

    parameters = data.get("parameters", {})
    market_analysis = data.get("market_analysis", {})
    alerts = data.get("alerts", [])

    capital = parameters.get("capital")
    stop_loss_pct = parameters.get("stop_loss")  # percentage
    take_profit_pct = parameters.get("take_profit")  # percentage
    trades_today = parameters.get("trades_today")
    
    btc_price = market_analysis.get("btc_price")
    eth_price = market_analysis.get("eth_price")

    log_message(f"Status Update: Capital=${capital}, Stop Loss={stop_loss_pct}%, Take Profit={take_profit_pct}%, Trades Today={trades_today}")
    
    if btc_price:
        log_message(f"BTC Price: ${btc_price}")
    
    if eth_price:
        log_message(f"ETH Price: ${eth_price}")

    # Check for alerts
    for alert in alerts:
        if alert == "MAX_DAILY_TRADES_REACHED":
            log_message("ALERT: Maximum daily trades reached - trading paused")
        elif alert == "NO_CRITICAL_TRIGGERS":
            log_message("Status: No stop-loss or take-profit triggers detected")
    
    # Check if we have price data to analyze against stop-loss/take-profit
    # Note: This is simplified - in a real system we'd need entry prices for each trade
    if btc_price and stop_loss_pct:
        # Simplified check - we'd need actual entry prices for proper analysis
        log_message(f"BTC Analysis: Current price ${btc_price}, Stop-loss would trigger at ~${btc_price * (1 - stop_loss_pct/100):.2f}")
    
    if eth_price and stop_loss_pct:
        log_message(f"ETH Analysis: Current price ${eth_price}, Stop-loss would trigger at ~${eth_price * (1 - stop_loss_pct/100):.2f}")

if __name__ == "__main__":
    log_message("Starting trading dashboard monitor...")
    trading_data = fetch_trading_data()
    if trading_data:
        analyze_data(trading_data)
    log_message("Trading dashboard monitor finished.")