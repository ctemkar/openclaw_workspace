#!/usr/bin/env python3
"""
TRADING BOT SUPERVISOR
Monitors and restarts trading bots automatically
Prevents crashes from stopping trading
"""

import os
import sys
import time
import subprocess
import logging
import signal
import psutil
from datetime import datetime
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("supervisor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingBotSupervisor:
    """Supervisor that monitors and restarts trading bots"""
    
    def __init__(self):
        print("\n" + "="*80)
        print("🤖 TRADING BOT SUPERVISOR")
        print("="*80)
        print("Purpose: Monitor, restart, and maintain trading bots 24/7")
        print("="*80)
        
        # Bots to supervise
        self.bots = {
            "make_money_now": {
                "script": "scripts/make_money_now.py",
                "working_dir": os.path.dirname(os.path.abspath(__file__)),
                "process": None,
                "pid": None,
                "start_time": None,
                "restart_count": 0,
                "max_restarts_per_hour": 5,
                "last_restart": None,
                "status": "STOPPED",
                "required": True,
                "health_check_interval": 60,  # seconds
                "last_health_check": None
            },
            "practical_monitor": {
                "script": "practical_monitor_bot.py",
                "working_dir": os.path.dirname(os.path.abspath(__file__)),
                "process": None,
                "pid": None,
                "start_time": None,
                "restart_count": 0,
                "max_restarts_per_hour": 3,
                "last_restart": None,
                "status": "STOPPED",
                "required": True,
                "health_check_interval": 120,
                "last_health_check": None
            },
            "next_gen_trader": {
                "script": "next_gen_trading_bot.py",
                "working_dir": os.path.dirname(os.path.abspath(__file__)),
                "process": None,
                "pid": None,
                "start_time": None,
                "restart_count": 0,
                "max_restarts_per_hour": 2,
                "last_restart": None,
                "status": "STOPPED",
                "required": False,  # Optional for now
                "health_check_interval": 300,
                "last_health_check": None
            }
        }
        
        # Supervisor settings
        self.check_interval = 30  # seconds between checks
        self.max_crash_logs = 100
        self.crash_log = []
        self.running = True
        
        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logger.info(f"🤖 Supervisor initialized with {len(self.bots)} bots to monitor")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        self.stop_all_bots()
    
    def start_bot(self, bot_name: str) -> bool:
        """Start a trading bot"""
        bot = self.bots[bot_name]
        
        # Check if already running
        if bot["process"] is not None and bot["process"].poll() is None:
            logger.info(f"✅ {bot_name} is already running (PID: {bot['pid']})")
            return True
        
        # Check restart limits
        if self._exceeded_restart_limit(bot_name):
            logger.error(f"🚨 {bot_name} exceeded restart limit ({bot['max_restarts_per_hour']}/hour)")
            return False
        
        try:
            logger.info(f"🚀 Starting {bot_name}...")
            
            # Change to working directory
            original_cwd = os.getcwd()
            os.chdir(bot["working_dir"])
            
            # Start the process
            process = subprocess.Popen(
                [sys.executable, bot["script"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Return to original directory
            os.chdir(original_cwd)
            
            # Update bot info
            bot["process"] = process
            bot["pid"] = process.pid
            bot["start_time"] = datetime.now()
            bot["restart_count"] += 1
            bot["last_restart"] = datetime.now()
            bot["status"] = "RUNNING"
            
            # Start output monitoring threads
            self._start_output_monitoring(bot_name, process)
            
            logger.info(f"✅ {bot_name} started successfully (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {bot_name}: {e}")
            bot["status"] = "FAILED"
            self._log_crash(bot_name, f"Start failed: {e}")
            return False
    
    def stop_bot(self, bot_name: str, force: bool = False) -> bool:
        """Stop a trading bot gracefully"""
        bot = self.bots[bot_name]
        
        if bot["process"] is None:
            logger.info(f"ℹ️ {bot_name} is not running")
            return True
        
        try:
            pid = bot["pid"]
            logger.info(f"🛑 Stopping {bot_name} (PID: {pid})...")
            
            if force:
                bot["process"].kill()
            else:
                bot["process"].terminate()
            
            # Wait for process to end
            try:
                bot["process"].wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ {bot_name} didn't stop gracefully, forcing...")
                bot["process"].kill()
                bot["process"].wait()
            
            bot["process"] = None
            bot["pid"] = None
            bot["status"] = "STOPPED"
            
            logger.info(f"✅ {bot_name} stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop {bot_name}: {e}")
            return False
    
    def stop_all_bots(self):
        """Stop all bots gracefully"""
        logger.info("🛑 Stopping all bots...")
        for bot_name in self.bots:
            self.stop_bot(bot_name)
        logger.info("✅ All bots stopped")
    
    def check_bot_health(self, bot_name: str) -> bool:
        """Check if a bot is healthy"""
        bot = self.bots[bot_name]
        
        if bot["process"] is None:
            logger.warning(f"⚠️ {bot_name} process is None")
            return False
        
        # Check if process is still running
        if bot["process"].poll() is not None:
            exit_code = bot["process"].poll()
            logger.error(f"❌ {bot_name} crashed with exit code {exit_code}")
            
            # Get stderr output if available
            try:
                stderr = bot["process"].stderr.read()
                if stderr:
                    logger.error(f"🚨 {bot_name} stderr: {stderr[:500]}")
                    self._log_crash(bot_name, f"Exit code {exit_code}: {stderr[:500]}")
            except:
                pass
            
            bot["status"] = "CRASHED"
            return False
        
        # Check process CPU/memory (optional)
        try:
            pid = bot["pid"]
            if pid:
                proc = psutil.Process(pid)
                cpu_percent = proc.cpu_percent(interval=0.1)
                memory_mb = proc.memory_info().rss / 1024 / 1024
                
                # Log if resource usage is high
                if cpu_percent > 80 or memory_mb > 500:
                    logger.warning(f"⚠️ {bot_name} high resource usage: CPU {cpu_percent}%, Memory {memory_mb:.1f}MB")
                
                bot["last_health_check"] = datetime.now()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return True
    
    def restart_bot(self, bot_name: str) -> bool:
        """Restart a bot"""
        logger.info(f"🔄 Restarting {bot_name}...")
        
        # Stop if running
        if self.bots[bot_name]["process"] is not None:
            self.stop_bot(bot_name)
        
        # Start fresh
        return self.start_bot(bot_name)
    
    def _exceeded_restart_limit(self, bot_name: str) -> bool:
        """Check if bot has exceeded restart limits"""
        bot = self.bots[bot_name]
        
        if bot["last_restart"] is None:
            return False
        
        # Count restarts in last hour
        hour_ago = datetime.now().timestamp() - 3600
        recent_restarts = 0
        
        for crash in self.crash_log:
            if crash["bot"] == bot_name and crash["time"].timestamp() > hour_ago:
                recent_restarts += 1
        
        return recent_restarts >= bot["max_restarts_per_hour"]
    
    def _log_crash(self, bot_name: str, reason: str):
        """Log a crash for analysis"""
        crash_entry = {
            "bot": bot_name,
            "time": datetime.now(),
            "reason": reason,
            "restart_count": self.bots[bot_name]["restart_count"]
        }
        
        self.crash_log.append(crash_entry)
        
        # Keep only recent crashes
        if len(self.crash_log) > self.max_crash_logs:
            self.crash_log = self.crash_log[-self.max_crash_logs:]
        
        logger.error(f"📝 Crash logged for {bot_name}: {reason}")
    
    def _start_output_monitoring(self, bot_name: str, process):
        """Start monitoring bot output (stub for now)"""
        # In a real implementation, this would start threads to read
        # stdout/stderr and log them appropriately
        pass
    
    def print_status(self):
        """Print current status of all bots"""
        print("\n" + "="*80)
        print("📊 TRADING BOT STATUS")
        print("="*80)
        
        for bot_name, bot in self.bots.items():
            status = bot["status"]
            pid = bot["pid"] or "N/A"
            uptime = "N/A"
            
            if bot["start_time"]:
                uptime_seconds = (datetime.now() - bot["start_time"]).total_seconds()
                uptime = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
            
            restart_count = bot["restart_count"]
            
            # Status emoji
            if status == "RUNNING":
                status_emoji = "✅"
            elif status == "CRASHED":
                status_emoji = "❌"
            elif status == "STOPPED":
                status_emoji = "⏸️"
            else:
                status_emoji = "❓"
            
            print(f"{status_emoji} {bot_name:20} | PID: {pid:6} | Status: {status:10} | Uptime: {uptime:8} | Restarts: {restart_count}")
        
        print("="*80)
        
        # Show recent crashes
        if self.crash_log:
            print("\n🚨 RECENT CRASHES (last 5):")
            for crash in self.crash_log[-5:]:
                time_str = crash["time"].strftime("%H:%M:%S")
                print(f"   • {time_str} - {crash['bot']}: {crash['reason'][:100]}...")
    
    def run(self):
        """Main supervisor loop"""
        logger.info("🤖 Supervisor starting...")
        
        # Start all required bots
        for bot_name, bot in self.bots.items():
            if bot["required"]:
                self.start_bot(bot_name)
        
        # Main monitoring loop
        cycle = 0
        while self.running:
            cycle += 1
            
            if cycle % 10 == 0:  # Print status every 10 cycles
                self.print_status()
            
            # Check each bot
            for bot_name in self.bots:
                bot = self.bots[bot_name]
                
                # Skip if not required or not supposed to be running
                if not bot["required"] and bot["status"] == "STOPPED":
                    continue
                
                # Check health
                is_healthy = self.check_bot_health(bot_name)
                
                # Restart if crashed and required
                if not is_healthy and bot["required"]:
                    logger.warning(f"⚠️ {bot_name} is not healthy, restarting...")
                    self.restart_bot(bot_name)
            
            # Sleep until next check
            time.sleep(self.check_interval)
        
        # Clean shutdown
        self.stop_all_bots()
        logger.info("👋 Supervisor shutdown complete")

def main():
    """Main function"""
    print("\n" + "="*80)
    print("🚀 TRADING BOT SUPERVISOR - STARTING")
    print("="*80)
    print("This supervisor will:")
    print("  1. Monitor all trading bots 24/7")
    print("  2. Restart crashed bots automatically")
    print("  3. Log all crashes for analysis")
    print("  4. Prevent trading interruptions")
    print("="*80)
    print("\n📋 Bots being supervised:")
    print("   • make_money_now.py - Main trading bot (REQUIRED)")
    print("   • practical_monitor_bot.py - Market monitor (REQUIRED)")
    print("   • next_gen_trading_bot.py - Next-gen system (OPTIONAL)")
    print("\n⚙️  Settings:")
    print("   • Health check: Every 30 seconds")
    print("   • Max restarts: 5/hour per bot")
    print("   • Auto-restart: Enabled for required bots")
    print("="*80)
    print("\nPress Ctrl+C to stop the supervisor\n")
    
    supervisor = TradingBotSupervisor()
    supervisor.run()

if __name__ == "__main__":
    main()