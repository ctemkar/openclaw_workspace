import requests
import datetime
import re

def monitor_trading_dashboard(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        content = response.text

        # --- Extraction ---
        trading_logs = extract_trading_logs(content)
        status_updates = extract_status_updates(content)
        risk_parameters = extract_risk_parameters(content)

        # --- Alert Detection ---
        critical_alerts = detect_critical_alerts(content)

        # --- Logging ---
        log_trading_data(trading_logs, status_updates, risk_parameters)
        log_critical_alerts(critical_alerts)

        # --- Summary Generation ---
        summary = generate_summary(trading_logs, status_updates, risk_parameters, critical_alerts)
        return summary

    except requests.exceptions.RequestException as e:
        return f"Error fetching or processing URL: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def extract_trading_logs(content):
    # Placeholder for actual log extraction logic
    # Example: Find lines starting with "LOG:"
    logs = re.findall(r"LOG:.*", content)
    return logs if logs else ["No trading logs found."]

def extract_status_updates(content):
    # Placeholder for actual status update extraction logic
    # Example: Find lines starting with "STATUS:"
    updates = re.findall(r"STATUS:.*", content)
    return updates if updates else ["No status updates found."]

def extract_risk_parameters(content):
    # Placeholder for actual risk parameter extraction logic
    # Example: Find lines like "Risk: X%"
    params = re.findall(r"Risk:.*?%", content)
    return params if params else ["No risk parameters found."]

def detect_critical_alerts(content):
    alerts = []
    # Example: Detect "STOP-LOSS TRIGGERED" or "TAKE-PROFIT TRIGGERED"
    if "STOP-LOSS TRIGGERED" in content:
        alerts.append("STOP-LOSS TRIGGERED")
    if "TAKE-PROFIT TRIGGERED" in content:
        alerts.append("TAKE-PROFIT TRIGGERED")
    # Example: Detect critical drawdown, e.g., "Drawdown: >10%"
    drawdown_match = re.search(r"Drawdown:.*?(\d+(\.\d+)?%)", content)
    if drawdown_match and float(drawdown_match.group(1).replace('%', '')) > 10:
        alerts.append(f"Critical Drawdown Detected: {drawdown_match.group(1)}")

    return alerts if alerts else ["No critical alerts detected."]

def log_trading_data(logs, updates, params):
    timestamp = datetime.datetime.now().isoformat()
    with open("./trading_monitoring.log", "a") as f:
        f.write(f"--- {timestamp} ---\n")
        f.write("Trading Logs:\n")
        for log in logs:
            f.write(f"- {log}\n")
        f.write("\nStatus Updates:\n")
        for update in updates:
            f.write(f"- {update}\n")
        f.write("\nRisk Parameters:\n")
        for param in params:
            f.write(f"- {param}\n")
        f.write("-" * 20 + "\\n")

def log_critical_alerts(alerts):
    timestamp = datetime.datetime.now().isoformat()
    with open("./critical_alerts.log", "a") as f:
        f.write(f"--- {timestamp} ---\n")
        for alert in alerts:
            f.write(f"- {alert}\n")
        f.write("-" * 20 + "\\n")

def generate_summary(logs, updates, params, alerts):
    summary = f"Trading Dashboard Summary ({datetime.datetime.now().isoformat()}):\n\n"
    summary += "--- Trading Logs ---\n"
    summary += "\\n".join(logs) + "\\n\\n"
    summary += "--- Status Updates ---\n"
    summary += "\\n".join(updates) + "\\n\\n"
    summary += "--- Risk Parameters ---\n"
    summary += "\\n".join(params) + "\\n\\n"
    summary += "--- Critical Alerts ---\n"
    summary += "\\n".join(alerts) + "\\n"
    return summary

if __name__ == "__main__":
    dashboard_url = "http://localhost:5001/"
    # This part will be run in a loop by the exec command
    # For now, we run it once to test the script structure
    # summary_text = monitor_trading_dashboard(dashboard_url)
    # print(summary_text)

    # For continuous monitoring, the script needs to be executed repeatedly.
    # This is handled by the exec command spawning a loop.
    pass
