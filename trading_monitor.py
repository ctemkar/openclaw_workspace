import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

trading_log_file = "./trading_monitoring.log"
critical_alerts_file = "./critical_alerts.log"
url = "http://localhost:5001/"

def fetch_trading_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None

def analyze_data(data):
    if not data:
        return "No data received.", False

    trading_logs = []
    status_updates = []
    risk_parameters = {}
    critical_alerts = []
    has_critical_alert = False

    # Basic parsing - replace with more robust parsing as needed
    for line in data.splitlines():
        if "TRADING_LOG" in line:
            trading_logs.append(line)
        elif "STATUS_UPDATE" in line:
            status_updates.append(line)
        elif "RISK_PARAM" in line:
            try:
                key, value = line.split("=", 1)
                risk_parameters[key.strip()] = value.strip()
            except ValueError:
                logging.warning(f"Could not parse RISK_PARAM line: {line}")
        elif "STOP_LOSS_TRIGGERED" in line or "TAKE_PROFIT_TRIGGERED" in line or "CRITICAL_DRAWDOWN" in line:
            critical_alerts.append(line)
            has_critical_alert = True

    # Generate summary
    summary = "Trading Monitoring Summary:\n\n"
    summary += "--- Trading Logs ---\n" + "\n".join(trading_logs) + "\n\n"
    summary += "--- Status Updates ---\n" + "\n".join(status_updates) + "\n\n"
    summary += "--- Risk Parameters ---\n"
    for key, value in risk_parameters.items():
        summary += f"{key}: {value}\n"
    summary += "\n"

    if has_critical_alert:
        summary += "--- CRITICAL ALERTS DETECTED ---\n" + "\n".join(critical_alerts) + "\n"
        for alert in critical_alerts:
            logging.warning(f"CRITICAL ALERT: {alert}")
            with open(critical_alerts_file, "a") as f:
                f.write(alert + "\n")

    # Log all data
    with open(trading_log_file, "a") as f:
        f.write(data + "\n")

    return summary, has_critical_alert

# Main execution
if __name__ == "__main__":
    raw_data = fetch_trading_data(url)
    analysis_summary, detected_alerts = analyze_data(raw_data)

    # The summary will be returned to the system to be delivered.
    # For this script, we just log it. In a real cron job, the output of the script would be captured.
    logging.info(analysis_summary)
    if detected_alerts:
        logging.info("Critical alerts were detected and logged.")
    else:
        logging.info("No critical alerts detected.")
