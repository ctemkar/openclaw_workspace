import requests
import json
import datetime
import os

def fetch_trading_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def parse_trading_logs(data):
    if not data:
        return [], {}, {}, [], False

    trading_logs = data.get('logs', [])
    status_updates = data.get('status', {})
    risk_parameters = data.get('risk_parameters', {})

    triggered_sl_tp = []
    critical_drawdown = False

    for log_entry in trading_logs:
        if "STOP_LOSS_TRIGGERED" in log_entry.get("message", ""):
            triggered_sl_tp.append(log_entry)
        if "TAKE_PROFIT_TRIGGERED" in log_entry.get("message", ""):
            triggered_sl_tp.append(log_entry)

    drawdown_indicator = risk_parameters.get('drawdown_indicator', 0)
    if drawdown_indicator > 0.8: # Example threshold
        critical_drawdown = True

    return trading_logs, status_updates, risk_parameters, triggered_sl_tp, critical_drawdown

def analyze_performance_and_risk(
    logs, status, risk_params, triggered_sl_tp, critical_drawdown
):
    print("Performing performance analysis...")
    # Placeholder for detailed performance analysis.
    pass

def log_data(
    file_path, logs, status, risk_params, triggered_sl_tp, critical_drawdown
):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "logs": logs,
        "status": status,
        "risk_parameters": risk_params,
        "triggered_sl_tp": triggered_sl_tp,
        "critical_drawdown": critical_drawdown,
    }
    with open(file_path, "a") as f:
        json.dump(log_entry, f)
        f.write("\n")

def log_alerts(file_path, alerts):
    if alerts:
        timestamp = datetime.datetime.now().isoformat()
        alert_entry = {
            "timestamp": timestamp,
            "alerts": alerts,
        }
        with open(file_path, "a") as f:
            json.dump(alert_entry, f)
            f.write("\n")

if __name__ == "__main__":
    dashboard_url = "http://localhost:5001/"
    log_file = "/Users/chetantemkar/.openclaw/workspace/app/trading_monitoring.log"
    alert_file = "/Users/chetantemkar/.openclaw/workspace/app/critical_alerts.log"

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    os.makedirs(os.path.dirname(alert_file), exist_ok=True)

    trading_data = fetch_trading_data(dashboard_url)

    if trading_data:
        logs, status, risk_params, triggered_sl_tp, critical_drawdown = parse_trading_logs(trading_data)

        analyze_performance_and_risk(logs, status, risk_params, triggered_sl_tp, critical_drawdown)
        log_data(log_file, logs, status, risk_params, triggered_sl_tp, critical_drawdown)

        alerts = []
        if triggered_sl_tp:
            alerts.append({"type": "STOP_LOSS_TAKE_PROFIT_TRIGGERED", "details": triggered_sl_tp})
        if critical_drawdown:
            alerts.append({"type": "CRITICAL_DRAWDOWN", "details": risk_params.get('drawdown_indicator')})

        if alerts:
            print("CRITICAL ALERTS DETECTED!")
            log_alerts(alert_file, alerts)
    else:
        print("Failed to retrieve trading data. No logs or alerts generated.")
