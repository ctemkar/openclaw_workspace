#!/usr/bin/env python3
"""
SIMPLE BOT MONITOR
Checks if bots are running and restarts them if not
Runs every 5 minutes via cron
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_process_running(script_name):
    """Check if a process is running"""
    try:
        # Use pgrep to find process
        result = subprocess.run(
            ['pgrep', '-f', script_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error checking process {script_name}: {e}")
        return False

def start_bot(script_path):
    """Start a bot"""
    try:
        logger.info(f"🚀 Starting {script_path}...")
        
        # Determine working directory
        if script_path.startswith('scripts/'):
            # Run from parent directory
            working_dir = os.path.dirname(os.path.abspath(__file__))
            script_name = os.path.basename(script_path)
            cmd = ['python3', f'scripts/{script_name}']
        else:
            # Run from current directory
            working_dir = os.path.dirname(os.path.abspath(__file__))
            cmd = ['python3', script_path]
        
        # Start process
        process = subprocess.Popen(
            cmd,
            cwd=working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        logger.info(f"✅ Started {script_path} (PID: {process.pid})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start {script_path}: {e}")
        return False

def main():
    """Main monitoring function"""
    print("\n" + "="*60)
    print("🔍 BOT HEALTH CHECK - " + datetime.now().strftime("%H:%M:%S"))
    print("="*60)
    
    # Bots to monitor
    bots = [
        {
            "name": "make_money_now",
            "script": "scripts/make_money_now.py",
            "required": True,
            "description": "Main trading bot"
        },
        {
            "name": "practical_monitor",
            "script": "practical_monitor_bot.py", 
            "required": True,
            "description": "Market monitor"
        },
        {
            "name": "next_gen_trader",
            "script": "next_gen_trading_bot.py",
            "required": False,
            "description": "Next-gen system"
        }
    ]
    
    # Check each bot
    for bot in bots:
        is_running = check_process_running(bot["script"])
        status = "✅ RUNNING" if is_running else "❌ STOPPED"
        
        print(f"\n{bot['name']}: {status}")
        print(f"   Description: {bot['description']}")
        print(f"   Script: {bot['script']}")
        print(f"   Required: {'YES' if bot['required'] else 'NO'}")
        
        # Restart if not running and required
        if not is_running and bot["required"]:
            print(f"   🚨 ACTION: Restarting...")
            start_bot(bot["script"])
        elif not is_running:
            print(f"   ℹ️  INFO: Not required, leaving stopped")
    
    print("\n" + "="*60)
    print("📊 SUMMARY: All required bots checked and restarted if needed")
    print("="*60)
    
    # Log completion
    logger.info("Bot health check completed")

if __name__ == "__main__":
    main()