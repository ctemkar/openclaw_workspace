#!/usr/bin/env python3
"""
AUTOMATED SYSTEM MONITOR
Proactively checks ALL trading systems and alerts if anything stops
"""

import subprocess
import time
import logging
from datetime import datetime
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_monitor.log'),
        logging.StreamHandler()
    ]
)

class SystemMonitor:
    def __init__(self):
        self.systems_to_check = [
            # Dashboards
            {
                'name': 'Arbitration Dashboard',
                'process': 'arbitration_trading_dashboard.py',
                'port': 5020,
                'url': 'http://localhost:5020',
                'critical': True
            },
            {
                'name': 'Simple Trading Dashboard',
                'process': 'simple_trading_dashboard.py',
                'port': 5010,
                'url': 'http://localhost:5010',
                'critical': False
            },
            
            # Arbitration Bots
            {
                'name': 'Forex Arbitration Bot ($220)',
                'process': 'forex_bot_with_schwab.py',
                'critical': True,
                'description': 'Schwab Account #13086459'
            },
            {
                'name': 'Auto Arbitrage Bot',
                'process': 'auto_arbitrage_bot.py',
                'critical': True
            },
            {
                'name': 'Practical Profit Bot',
                'process': 'practical_profit_bot.py',
                'critical': True
            },
            {
                'name': 'Market Maker Analyzer',
                'process': 'market_maker_analyzer.py',
                'critical': False
            },
            {
                'name': 'Multi-LLM Trading Bot',
                'process': 'multi_llm_trading_bot_fixed_order.py',
                'critical': True
            }
        ]
        
        self.check_interval = 60  # Check every 60 seconds
        self.alerts_sent = {}
        
        logging.info("🚀 AUTOMATED SYSTEM MONITOR INITIALIZED")
        logging.info(f"📊 Monitoring {len(self.systems_to_check)} systems")
        logging.info(f"⏰ Check interval: {self.check_interval} seconds")
        logging.info("🎯 I will proactively alert you if anything stops!")
    
    def is_process_running(self, process_name):
        """Check if a process is running"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            return process_name in result.stdout
        except:
            return False
    
    def is_port_responding(self, port):
        """Check if a port is responding"""
        try:
            result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
                                   f'http://localhost:{port}'], 
                                  capture_output=True, text=True, timeout=5)
            return result.stdout.strip() == '200'
        except:
            return False
    
    def check_system(self, system):
        """Check a single system"""
        name = system['name']
        process_name = system['process']
        
        # Check if process is running
        process_ok = self.is_process_running(process_name)
        
        # Check port if applicable
        port_ok = True
        if 'port' in system:
            port_ok = self.is_port_responding(system['port'])
        
        status = "✅ RUNNING" if (process_ok and port_ok) else "❌ STOPPED"
        
        # Log status
        log_msg = f"{name}: {status}"
        if 'port' in system and not port_ok:
            log_msg += f" (Port {system['port']} not responding)"
        
        if process_ok and port_ok:
            logging.info(log_msg)
        else:
            logging.error(log_msg)
            
            # Auto-restart if critical system stopped
            if system.get('critical', False):
                if name not in self.alerts_sent:
                    # First failure - try auto-restart
                    logging.warning(f"🔄 Attempting auto-restart for {name}")
                    restart_success = self.restart_system(system)
                    
                    # Send alert with restart status
                    self.send_alert(system, process_ok, port_ok, auto_restarted=True)
                    self.alerts_sent[name] = datetime.now()
                    
                    if restart_success:
                        logging.info(f"✅ Auto-restart successful for {name}")
                    else:
                        logging.error(f"❌ Auto-restart failed for {name}")
                else:
                    # Already alerted, check if it's been a while
                    last_alert = self.alerts_sent[name]
                    time_since_alert = (datetime.now() - last_alert).total_seconds()
                    
                    # Try restart again after 5 minutes
                    if time_since_alert > 300:  # 5 minutes
                        logging.warning(f"🔄 Re-attempting auto-restart for {name} (5 minutes since last attempt)")
                        restart_success = self.restart_system(system)
                        self.alerts_sent[name] = datetime.now()
                        
                        if restart_success:
                            logging.info(f"✅ Re-restart successful for {name}")
                        else:
                            logging.error(f"❌ Re-restart failed for {name}")
        
        return process_ok and port_ok
    
    def restart_system(self, system):
        """Automatically restart a dead system"""
        name = system['name']
        process_name = system['process']
        
        logging.info(f"🔄 Attempting to restart: {name}")
        
        try:
            # Kill any existing process (clean restart)
            subprocess.run(['pkill', '-f', process_name], 
                         capture_output=True, text=True)
            time.sleep(1)
            
            # Start the system
            if 'port' in system:
                # Dashboard - run in background
                subprocess.Popen(['python3', process_name],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                restart_type = "dashboard"
            else:
                # Bot - run in background
                subprocess.Popen(['python3', process_name],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                restart_type = "bot"
            
            # Wait a moment for startup
            time.sleep(3)
            
            # Verify restart worked
            if self.is_process_running(process_name):
                if 'port' in system:
                    port_ok = self.is_port_responding(system['port'])
                    if port_ok:
                        logging.info(f"✅ SUCCESS: {name} restarted and responding on port {system['port']}")
                        return True
                    else:
                        logging.error(f"❌ FAILED: {name} process started but port {system['port']} not responding")
                        return False
                else:
                    logging.info(f"✅ SUCCESS: {name} restarted")
                    return True
            else:
                logging.error(f"❌ FAILED: Could not restart {name}")
                return False
                
        except Exception as e:
            logging.error(f"❌ ERROR restarting {name}: {e}")
            return False
    
    def send_alert(self, system, process_ok, port_ok, auto_restarted=False):
        """Send alert about stopped system"""
        name = system['name']
        issue = []
        
        if not process_ok:
            issue.append(f"Process '{system['process']}' not running")
        if 'port' in system and not port_ok:
            issue.append(f"Port {system['port']} not responding")
        
        alert_msg = f"""
        🚨 **SYSTEM ALERT: {name} STOPPED!**
        
        **Issue:** {' & '.join(issue)}
        **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        if auto_restarted:
            alert_msg += f"\n\n**🔄 AUTO-RESTART ATTEMPTED**"
            if self.is_process_running(system['process']):
                alert_msg += f"\n✅ **RESTART SUCCESSFUL!**"
            else:
                alert_msg += f"\n❌ **RESTART FAILED - Manual intervention needed**"
        else:
            alert_msg += f"\n\n**Recommended Action:**"
            if 'port' in system:
                alert_msg += f"\n1. Restart dashboard: `python3 {system['process']}`"
                alert_msg += f"\n2. Check: {system['url']}"
            else:
                alert_msg += f"\n1. Restart bot: `python3 {system['process']}`"
        
        if system.get('description'):
            alert_msg += f"\n\n**Note:** {system['description']}"
        
        logging.error(f"🚨 ALERT: {name}")
        print("\n" + "="*60)
        print(alert_msg)
        print("="*60 + "\n")
    
    def run(self):
        """Main monitoring loop"""
        logging.info("🔄 Starting proactive monitoring...")
        
        check_count = 0
        
        while True:
            check_count += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            logging.info(f"\n=== MONITOR CHECK #{check_count} at {current_time} ===")
            
            # Check all systems
            all_ok = True
            for system in self.systems_to_check:
                if not self.check_system(system):
                    all_ok = False
            
            # Summary
            if all_ok:
                logging.info(f"✅ ALL SYSTEMS OK ({len(self.systems_to_check)} systems running)")
            else:
                logging.warning(f"⚠️  SOME SYSTEMS NEED ATTENTION")
            
            # Wait for next check
            next_check = time.time() + self.check_interval
            next_time = datetime.fromtimestamp(next_check).strftime('%H:%M:%S')
            
            logging.info(f"⏰ Next automatic check at: {next_time}")
            time.sleep(self.check_interval)

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run()