#!/usr/bin/env python3
"""
TRADING SYSTEM SUPERVISOR
Manages and monitors all trading components with auto-restart
"""

import os
import sys
import time
import json
import subprocess
import signal
import psutil
from datetime import datetime, timedelta
import threading
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'supervisor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================================================
# CONFIGURATION
# ================================================

COMPONENTS = [
    {
        'name': '26-crypto-trader',
        'command': ['python3', 'real_26_crypto_trader.py'],
        'cwd': BASE_DIR,
        'log_file': 'trader_supervised.log',
        'health_check': 'trader',
        'restart_delay': 30,
        'max_restarts_per_hour': 3,
        'required': True
    },
    {
        'name': 'llm-consensus-bot',
        'command': ['python3', 'llm_consensus_bot_resilient.py'],
        'cwd': BASE_DIR,
        'log_file': 'llm_supervised.log',
        'health_check': 'llm',
        'restart_delay': 60,
        'max_restarts_per_hour': 2,
        'required': False
    },
    {
        'name': 'dashboard-5007',
        'command': ['python3', 'simple_dashboard.py'],
        'cwd': BASE_DIR,
        'log_file': 'dashboard_supervised.log',
        'health_check': 'http:5007',
        'restart_delay': 15,
        'max_restarts_per_hour': 5,
        'required': False
    }
]

# Health check intervals (seconds)
HEALTH_CHECK_INTERVAL = 60
STATUS_UPDATE_INTERVAL = 300

# ================================================
# PROCESS MANAGEMENT
# ================================================

class ManagedProcess:
    """Manages a single process with monitoring and auto-restart"""
    
    def __init__(self, config):
        self.config = config
        self.name = config['name']
        self.process = None
        self.pid = None
        self.start_time = None
        self.restart_count = 0
        self.restart_timestamps = []
        self.last_health_check = None
        self.health_status = 'unknown'
        
    def start(self):
        """Start the process"""
        try:
            logger.info(f"🚀 Starting {self.name}...")
            
            # Open log file
            log_file = open(os.path.join(self.config['cwd'], self.config['log_file']), 'a')
            
            # Start process
            self.process = subprocess.Popen(
                self.config['command'],
                cwd=self.config['cwd'],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid
            )
            
            self.pid = self.process.pid
            self.start_time = datetime.now()
            
            # Record restart
            self.restart_count += 1
            self.restart_timestamps.append(self.start_time)
            
            # Clean old restart timestamps
            one_hour_ago = datetime.now() - timedelta(hours=1)
            self.restart_timestamps = [t for t in self.restart_timestamps if t > one_hour_ago]
            
            logger.info(f"✅ {self.name} started (PID: {self.pid})")
            self.health_status = 'starting'
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {self.name}: {e}")
            self.health_status = 'failed'
            return False
    
    def stop(self, force=False):
        """Stop the process gracefully"""
        if not self.process:
            return True
            
        try:
            logger.info(f"🛑 Stopping {self.name} (PID: {self.pid})...")
            
            if force:
                os.killpg(os.getpgid(self.pid), signal.SIGKILL)
            else:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ {self.name} didn't terminate gracefully, forcing...")
                    os.killpg(os.getpgid(self.pid), signal.SIGKILL)
            
            self.process = None
            self.pid = None
            logger.info(f"✅ {self.name} stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop {self.name}: {e}")
            return False
    
    def check_health(self):
        """Check if process is healthy"""
        self.last_health_check = datetime.now()
        
        # Check if process is running
        if not self.process or self.process.poll() is not None:
            self.health_status = 'dead'
            return False
        
        # Perform type-specific health checks
        health_ok = True
        check_type = self.config.get('health_check', '')
        
        if check_type == 'trader':
            health_ok = self._check_trader_health()
        elif check_type == 'llm':
            health_ok = self._check_llm_health()
        elif check_type.startswith('http:'):
            port = check_type.split(':')[1]
            health_ok = self._check_http_health(port)
        else:
            health_ok = True
        
        self.health_status = 'healthy' if health_ok else 'unhealthy'
        return health_ok
    
    def _check_trader_health(self):
        """Check if trader is making progress"""
        log_path = os.path.join(self.config['cwd'], self.config['log_file'])
        if not os.path.exists(log_path):
            return False
        
        mod_time = datetime.fromtimestamp(os.path.getmtime(log_path))
        if (datetime.now() - mod_time).total_seconds() > 300:
            logger.warning(f"⚠️ {self.name} log not updated in 5+ minutes")
            return False
        
        return True
    
    def _check_llm_health(self):
        """Check if LLM bot is working"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code != 200:
                logger.warning(f"⚠️ Ollama server not responding")
                return False
        except:
            logger.warning(f"⚠️ Cannot connect to Ollama server")
            return False
        
        log_path = os.path.join(self.config['cwd'], self.config['log_file'])
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                lines = f.readlines()[-20:]
                for line in lines:
                    if 'ERROR' in line or 'CRITICAL' in line:
                        if 'timeout' not in line.lower():
                            logger.warning(f"⚠️ {self.name} has errors in log")
                            return False
        
        return True
    
    def _check_http_health(self, port):
        """Check if HTTP service is responding"""
        try:
            import requests
            response = requests.get(f'http://localhost:{port}/', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def should_restart(self):
        """Check if process should be restarted"""
        if not self.config['required'] and self.restart_count >= 3:
            logger.warning(f"⚠️ {self.name} has restarted 3+ times, keeping stopped")
            return False
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_restarts = [t for t in self.restart_timestamps if t > one_hour_ago]
        
        if len(recent_restarts) >= self.config['max_restarts_per_hour']:
            logger.error(f"🚨 {self.name} exceeded max restarts per hour")
            return False
        
        return True
    
    def get_status(self):
        """Get process status for reporting"""
        return {
            'name': self.name,
            'pid': self.pid,
            'running': self.process is not None and self.process.poll() is None,
            'health': self.health_status,
            'restart_count': self.restart_count,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            'required': self.config['required']
        }

# ================================================
# SUPERVISOR
# ================================================

class TradingSystemSupervisor:
    """Main supervisor that manages all components"""
    
    def __init__(self):
        self.components = {}
        self.running = False
        self.status_file = os.path.join(BASE_DIR, 'system_status_supervised.json')
        
        for config in COMPONENTS:
            self.components[config['name']] = ManagedProcess(config)
    
    def start_all(self):
        """Start all components"""
        logger.info("="*70)
        logger.info("🚀 STARTING TRADING SYSTEM SUPERVISOR")
        logger.info("="*70)
        
        self.running = True
        
        # Start essential components first
        for name, process in self.components.items():
            if process.config['required']:
                process.start()
                time.sleep(5)
        
        # Start non-essential components
        for name, process in self.components.items():
            if not process.config['required']:
                process.start()
                time.sleep(3)
        
        # Start monitoring threads
        self._start_monitoring()
        
        logger.info("✅ All components started")
        logger.info("📊 Monitoring active...")
    
    def stop_all(self):
        """Stop all components gracefully"""
        logger.info("🛑 Stopping all components...")
        self.running = False
        
        for name, process in self.components.items():
            if not process.config['required']:
                process.stop()
        
        for name, process in self.components.items():
            if process.config['required']:
                process.stop()
        
        logger.info("✅ All components stopped")
    
    def _start_monitoring(self):
        """Start monitoring threads"""
        health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        health_thread.start()
        
        status_thread = threading.Thread(target=self._status_update_loop, daemon=True)
        status_thread.start()
    
    def _health_check_loop(self):
        """Continuously check component health"""
        while self.running:
            try:
                for name, process in self.components.items():
                    if not process.check_health():
                        logger.warning(f"⚠️ {name} is unhealthy ({process.health_status})")
                        
                        if process.should_restart():
                            logger.info(f"🔄 Restarting {name}...")
                            process.stop()
                            time.sleep(process.config['restart_delay'])
                            process.start()
                        else:
                            logger.warning(f"⚠️ Not restarting {name}")
                
                time.sleep(HEALTH_CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                time.sleep(30)
    
    def _status_update_loop(self):
        """Update status file periodically"""
        while self.running:
            try:
                self._update_status_file()
                time.sleep(STATUS_UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"❌ Status update error: {e}")
                time.sleep(60)
    
    def _update_status_file(self):
        """Update system status file"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'supervisor': 'running',
            'components': {},
            'summary': {
                'total': len(self.components),
                'healthy': 0,
                'unhealthy': 0,
                'dead': 0
            }
        }
        
        for name, process in self.components.items():
            comp_status = process.get_status()
            status['components'][name] = comp_status
            
            if comp_status['health'] == 'healthy':
                status['summary']['healthy'] += 1
            elif comp_status['health'] == 'unhealthy':
                status['summary']['unhealthy'] += 1
            else:
                status['summary']['dead'] += 1
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info(f"📊 Status: {status['summary']['healthy']}/{status['summary']['total']} healthy")
    
    def run_interactive(self):
        """Run supervisor with interactive control"""
        self.start_all()
        
        try:
            logger.info("\n" + "="*70)
            logger.info("🎮 SUPERVISOR CONTROLS:")
            logger.info("  [s] - Show status")
            logger.info("  [r <name>] - Restart component")
            logger.info("  [q] - Quit (stop all)")
            logger.info("="*70)
            
            while self.running:
                try:
                    cmd = input("\n> ").strip().lower()
                    
                    if cmd == 's':
                        self._show_status()
                    elif cmd.startswith('r '):
                        name = cmd[2:].strip()
                        if name in self.components:
                            self.components[name].stop()
                            time.sleep(5)
                            self.components[name].start()
                        else:
                            logger.error(f"❌ Unknown component: {name}")
                    elif cmd == 'q':
                        break
                    else:
                        logger.info("❓ Unknown command")
                        
                except (EOFError, KeyboardInterrupt):
                    break
                except Exception as e:
                    logger.error(f"❌ Command error: {e}")
        
        finally:
            self.stop_all()
    
    def _show_status(self):
        """Show current status"""
        print("\n" + "="*70)
        print("📊 SYSTEM STATUS")
        print("="*70)
        
        for name, process in self.components.items():
            status = process.get_status()
            symbol = "✅" if status['health'] == 'healthy' else "⚠️" if status['health'] == 'unhealthy' else "❌"
            req = "(REQUIRED)" if status['required'] else "(OPTIONAL)"
            print(f"{symbol} {name} {req}")
            print(f"   PID: {status['pid'] or 'N/A'}")
            print(f"   Health: {status['health']}")
            print(f"   Uptime: {status['uptime']:.0f}s")
            print(f"   Restarts: {status['restart_count']}")
            print()

# ================================================
# MAIN EXECUTION
# ================================================

if __name__ == "__main__":
    supervisor = TradingSystemSupervisor()
    
    print("="*70)
    print("🛡️ TRADING SYSTEM SUPERVISOR")
    print("="*70)
    print("Starting with components:")
    for config in COMPONENTS:
        req = "(REQUIRED)" if config['required'] else "(OPTIONAL)"
        print(f"  • {config['name']} {req}")
    print("="*70)
    
    try:
        supervisor.run_interactive()
    except KeyboardInterrupt:
        print("\n🛑 Supervisor stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()