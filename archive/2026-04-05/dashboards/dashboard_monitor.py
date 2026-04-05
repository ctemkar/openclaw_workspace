#!/usr/bin/env python3
"""
DASHBOARD MONITOR - Automatically monitors and restarts dashboards
Runs as a background service to ensure dashboards stay up
"""

import subprocess
import time
import os
import sys
from datetime import datetime
import psutil
import signal

class DashboardMonitor:
    def __init__(self):
        self.dashboards = [
            {
                'name': 'Simple PnL Dashboard',
                'port': 5008,
                'command': ['python3', 'simple_pnl_dashboard.py'],
                'log_file': 'simple_pnl_dashboard.log',
                'pid_file': 'simple_pnl_dashboard.pid',
                'url': 'http://localhost:5008'
            },
            {
                'name': 'Simple Fixed Dashboard',
                'port': 5009,
                'command': ['python3', 'simple_fixed_dashboard.py'],
                'log_file': 'simple_fixed_dashboard.log',
                'pid_file': 'simple_fixed_dashboard.pid',
                'url': 'http://localhost:5009'
            }
        ]
        
        self.check_interval = 60  # Check every 60 seconds
        self.max_restart_attempts = 3
        self.restart_counts = {dashboard['name']: 0 for dashboard in self.dashboards}
        
    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
        
        # Also write to monitor log
        with open('dashboard_monitor.log', 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def is_port_listening(self, port):
        """Check if a port is listening"""
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], 
                                  capture_output=True, text=True)
            return 'LISTEN' in result.stdout
        except:
            return False
    
    def is_process_running(self, pid_file):
        """Check if process is running using PID file"""
        if not os.path.exists(pid_file):
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            return psutil.pid_exists(pid)
        except:
            return False
    
    def get_process_pid(self, name):
        """Get PID of a running process by name"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if name in ' '.join(proc.info['cmdline'] or []):
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def start_dashboard(self, dashboard):
        """Start a dashboard"""
        name = dashboard['name']
        port = dashboard['port']
        
        self.log(f"🚀 Starting {name} on port {port}...")
        
        try:
            # Start the process
            with open(dashboard['log_file'], 'a') as log_file:
                process = subprocess.Popen(
                    dashboard['command'],
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            
            # Save PID
            with open(dashboard['pid_file'], 'w') as f:
                f.write(str(process.pid))
            
            # Wait for startup
            time.sleep(3)
            
            # Verify it's running
            if self.is_port_listening(port):
                self.log(f"✅ {name} started successfully (PID: {process.pid})")
                self.restart_counts[name] = 0  # Reset restart count
                return True
            else:
                self.log(f"❌ {name} failed to start - port not listening")
                return False
                
        except Exception as e:
            self.log(f"❌ Failed to start {name}: {e}")
            return False
    
    def stop_dashboard(self, dashboard):
        """Stop a dashboard gracefully"""
        name = dashboard['name']
        
        # Try to get PID from file
        pid = None
        if os.path.exists(dashboard['pid_file']):
            try:
                with open(dashboard['pid_file'], 'r') as f:
                    pid = int(f.read().strip())
            except:
                pass
        
        # Also try to find by name
        if not pid:
            pid = self.get_process_pid(dashboard['command'][1])
        
        if pid:
            try:
                self.log(f"🛑 Stopping {name} (PID: {pid})...")
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                
                # Force kill if still running
                if psutil.pid_exists(pid):
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(1)
                
                self.log(f"✅ {name} stopped")
            except Exception as e:
                self.log(f"⚠️ Could not stop {name}: {e}")
        
        # Clean up PID file
        if os.path.exists(dashboard['pid_file']):
            os.remove(dashboard['pid_file'])
    
    def check_dashboard(self, dashboard):
        """Check if a dashboard is running and restart if needed"""
        name = dashboard['name']
        port = dashboard['port']
        
        # Check if port is listening
        if not self.is_port_listening(port):
            self.log(f"⚠️ {name} on port {port} is NOT listening")
            
            # Check if we should restart
            if self.restart_counts[name] < self.max_restart_attempts:
                self.log(f"🔄 Attempting to restart {name} (attempt {self.restart_counts[name] + 1})")
                
                # Stop if any orphaned process
                self.stop_dashboard(dashboard)
                
                # Start fresh
                if self.start_dashboard(dashboard):
                    self.restart_counts[name] += 1
                    return True
                else:
                    self.log(f"❌ Failed to restart {name}")
                    return False
            else:
                self.log(f"🚨 {name} failed {self.max_restart_attempts} times - giving up")
                return False
        else:
            # Dashboard is running
            pid = self.get_process_pid(dashboard['command'][1])
            if pid:
                # Update PID file
                with open(dashboard['pid_file'], 'w') as f:
                    f.write(str(pid))
            
            return True
    
    def run(self):
        """Main monitoring loop"""
        self.log("=" * 60)
        self.log("📊 DASHBOARD MONITOR STARTED")
        self.log("=" * 60)
        
        # Initial startup of all dashboards
        for dashboard in self.dashboards:
            if not self.is_port_listening(dashboard['port']):
                self.start_dashboard(dashboard)
        
        # Monitoring loop
        while True:
            try:
                self.log("-" * 40)
                self.log(f"🔍 Dashboard Health Check - {datetime.now().strftime('%H:%M:%S')}")
                
                all_healthy = True
                
                for dashboard in self.dashboards:
                    if not self.check_dashboard(dashboard):
                        all_healthy = False
                
                if all_healthy:
                    self.log("✅ All dashboards are healthy")
                
                # Show status summary
                self.log("\n📊 STATUS SUMMARY:")
                for dashboard in self.dashboards:
                    status = "✅ RUNNING" if self.is_port_listening(dashboard['port']) else "❌ DOWN"
                    self.log(f"  {dashboard['name']}: {status} - {dashboard['url']}")
                
                self.log(f"\n⏰ Next check in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                self.log("\n🛑 Monitor stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Monitor error: {e}")
                time.sleep(self.check_interval)

if __name__ == "__main__":
    monitor = DashboardMonitor()
    monitor.run()