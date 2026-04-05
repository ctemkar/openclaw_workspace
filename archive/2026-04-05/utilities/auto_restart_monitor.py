#!/usr/bin/env python3
"""
AUTO-RESTART MONITOR FOR TRADING BOTS
Monitors all trading bots and auto-restarts them if they stop
Runs as a background service
"""

import os
import sys
import time
import subprocess
import logging
from datetime import datetime
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_restart_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot configurations with auto-restart enabled
BOTS = [
    {
        'name': 'Forex Arbitration Bot',
        'file': 'forex_bot_with_schwab.py',
        'command': 'python3 forex_bot_with_schwab.py',
        'log_file': 'forex_auto_restart.log',
        'check_interval': 60,  # Check every 60 seconds
        'max_restarts': 5,     # Max 5 restarts per hour
        'enabled': True
    },
    {
        'name': 'Auto Arbitrage Bot',
        'file': 'auto_arbitrage_bot.py',
        'command': 'python3 auto_arbitrage_bot.py',
        'log_file': 'arbitrage_auto_restart.log',
        'check_interval': 60,
        'max_restarts': 5,
        'enabled': True
    },
    {
        'name': 'Practical Profit Bot',
        'file': 'practical_profit_bot.py',
        'command': 'python3 practical_profit_bot.py',
        'log_file': 'profit_auto_restart.log',
        'check_interval': 60,
        'max_restarts': 5,
        'enabled': True
    },
    {
        'name': 'Multi-LLM Trading Bot',
        'file': 'multi_llm_trading_bot_fixed_order.py',
        'command': 'python3 multi_llm_trading_bot_fixed_order.py',
        'log_file': 'llm_auto_restart.log',
        'check_interval': 60,
        'max_restarts': 5,
        'enabled': True
    }
]

# Track restart history
restart_history = {}

def is_bot_running(bot_file):
    """Check if a bot is running"""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return bot_file in result.stdout
    except Exception as e:
        logger.error(f"Error checking if {bot_file} is running: {e}")
        return False

def start_bot(bot_config):
    """Start a bot"""
    bot_name = bot_config['name']
    bot_file = bot_config['file']
    
    # Initialize restart history for this bot
    if bot_file not in restart_history:
        restart_history[bot_file] = {
            'count': 0,
            'last_restart': None,
            'last_hour_restarts': 0,
            'last_hour_reset': time.time()
        }
    
    # Check if we've exceeded max restarts in the last hour
    current_time = time.time()
    if current_time - restart_history[bot_file]['last_hour_reset'] > 3600:  # 1 hour
        restart_history[bot_file]['last_hour_restarts'] = 0
        restart_history[bot_file]['last_hour_reset'] = current_time
    
    if restart_history[bot_file]['last_hour_restarts'] >= bot_config['max_restarts']:
        logger.warning(f"⚠️  Max restarts ({bot_config['max_restarts']}) exceeded for {bot_name} in last hour. Skipping restart.")
        return False
    
    try:
        logger.info(f"🔄 Starting {bot_name}...")
        
        # Start the bot
        process = subprocess.Popen(
            bot_config['command'].split(),
            stdout=open(bot_config['log_file'], 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )
        
        # Update restart history
        restart_history[bot_file]['count'] += 1
        restart_history[bot_file]['last_hour_restarts'] += 1
        restart_history[bot_file]['last_restart'] = datetime.now().isoformat()
        
        # Wait to check if it started
        time.sleep(3)
        
        if is_bot_running(bot_file):
            logger.info(f"✅ {bot_name} started successfully!")
            return True
        else:
            logger.error(f"❌ {bot_name} failed to start")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error starting {bot_name}: {e}")
        return False

def monitor_bot(bot_config):
    """Monitor and auto-restart a single bot"""
    bot_name = bot_config['name']
    bot_file = bot_config['file']
    
    logger.info(f"👀 Starting monitor for {bot_name} (checking every {bot_config['check_interval']}s)")
    
    while True:
        try:
            if not is_bot_running(bot_file):
                logger.warning(f"🚨 {bot_name} is NOT RUNNING! Attempting auto-restart...")
                
                if start_bot(bot_config):
                    logger.info(f"✅ {bot_name} auto-restarted successfully")
                else:
                    logger.error(f"❌ Failed to auto-restart {bot_name}")
            else:
                # Bot is running, log status occasionally
                if int(time.time()) % 300 == 0:  # Log every 5 minutes
                    logger.info(f"✓ {bot_name} is running normally")
            
        except Exception as e:
            logger.error(f"❌ Error monitoring {bot_name}: {e}")
        
        # Wait before next check
        time.sleep(bot_config['check_interval'])

def start_all_monitors():
    """Start monitor threads for all bots"""
    threads = []
    
    for bot in BOTS:
        if bot['enabled']:
            thread = threading.Thread(
                target=monitor_bot,
                args=(bot,),
                daemon=True,
                name=f"Monitor-{bot['name'].replace(' ', '-')}"
            )
            thread.start()
            threads.append(thread)
            logger.info(f"🚀 Started monitor thread for {bot['name']}")
    
    return threads

def print_status():
    """Print current status of all bots"""
    print("\n" + "="*60)
    print("🤖 AUTO-RESTART MONITOR STATUS")
    print("="*60)
    
    for bot in BOTS:
        status = "✅ RUNNING" if is_bot_running(bot['file']) else "❌ NOT RUNNING"
        restarts = restart_history.get(bot['file'], {}).get('count', 0)
        
        print(f"\n📊 {bot['name']}:")
        print(f"   Status: {status}")
        print(f"   File: {bot['file']}")
        print(f"   Total restarts: {restarts}")
        
        if bot['file'] in restart_history:
            last_restart = restart_history[bot['file']].get('last_restart', 'Never')
            print(f"   Last restart: {last_restart}")
    
    print("\n" + "="*60)
    print("📈 Monitor running in background")
    print("📝 Logs: auto_restart_monitor.log")
    print("🛑 Press Ctrl+C to stop")
    print("="*60 + "\n")

def main():
    """Main function"""
    logger.info("="*60)
    logger.info("🚀 STARTING AUTO-RESTART MONITOR FOR TRADING BOTS")
    logger.info("="*60)
    
    # Initial status check
    print_status()
    
    # Start all monitor threads
    threads = start_all_monitors()
    
    # Keep main thread alive
    try:
        while True:
            # Print status every 5 minutes
            time.sleep(300)
            print_status()
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Auto-restart monitor stopped by user")
        print("\n🛑 Auto-restart monitor stopped")
        
    except Exception as e:
        logger.error(f"❌ Monitor crashed: {e}")
        print(f"❌ Monitor crashed: {e}")

if __name__ == "__main__":
    main()