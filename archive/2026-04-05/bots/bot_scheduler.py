#!/usr/bin/env python3
"""
Bot Scheduler - Intelligently pauses/resumes bots based on market conditions
Saves resources during low-opportunity periods
"""

import time
import subprocess
import psutil
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotScheduler:
    def __init__(self):
        """Initialize scheduler"""
        self.bot_configs = {
            'market_maker_analyzer': {
                'process_name': 'market_maker_analyzer.py',
                'active_hours': [9, 10, 11, 12, 13, 14, 15, 16, 17],  # 9AM-5PM
                'min_spread_threshold': 0.1,  # Need at least 0.1% spreads
                'last_opportunity': None
            },
            'portfolio_rebalancer': {
                'process_name': 'portfolio_rebalancer.py',
                'check_interval_hours': 6,  # Check every 6 hours
                'last_check': None
            }
        }
        
    def check_bot_status(self, bot_name):
        """Check if a bot is running"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and bot_name in ' '.join(proc.info['cmdline']):
                    return True, proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False, None
    
    def should_bot_run(self, bot_name):
        """Determine if a bot should be running based on conditions"""
        config = self.bot_configs.get(bot_name)
        if not config:
            return True  # Default to running
        
        current_hour = datetime.now().hour
        
        if bot_name == 'market_maker_analyzer':
            # Check active hours
            if current_hour not in config['active_hours']:
                logger.info(f"⏸️  {bot_name}: Outside active hours ({current_hour}:00)")
                return False
            
            # Check recent opportunities (would need market data)
            # For now, just use time-based scheduling
            return True
            
        elif bot_name == 'portfolio_rebalancer':
            # Check interval
            if config['last_check']:
                hours_since_last = (datetime.now() - config['last_check']).seconds / 3600
                if hours_since_last < config['check_interval_hours']:
                    logger.info(f"⏸️  {bot_name}: Checked recently ({hours_since_last:.1f}h ago)")
                    return False
            
            config['last_check'] = datetime.now()
            return True
        
        return True  # Default to running
    
    def manage_bots(self):
        """Main management loop"""
        logger.info("🤖 BOT SCHEDULER STARTED")
        logger.info("Intelligently managing bot resources")
        
        while True:
            current_time = datetime.now().strftime("%H:%M")
            logger.info(f"
🔄 SCHEDULER CYCLE - {current_time}")
            
            for bot_name, config in self.bot_configs.items():
                is_running, pid = self.check_bot_status(config['process_name'])
                should_run = self.should_bot_run(bot_name)
                
                if is_running and not should_run:
                    # Bot is running but shouldn't be - pause it
                    logger.info(f"⏸️  Pausing {bot_name} (PID: {pid})")
                    try:
                        subprocess.run(['pkill', '-f', config['process_name']])
                        logger.info(f"✅ {bot_name} paused")
                    except Exception as e:
                        logger.error(f"❌ Failed to pause {bot_name}: {e}")
                        
                elif not is_running and should_run:
                    # Bot should be running but isn't - start it
                    logger.info(f"▶️  Starting {bot_name}")
                    try:
                        subprocess.Popen(['python3', f'{bot_name}.py'], 
                                       stdout=open(f'{bot_name}.log', 'a'),
                                       stderr=subprocess.STDOUT)
                        logger.info(f"✅ {bot_name} started")
                    except Exception as e:
                        logger.error(f"❌ Failed to start {bot_name}: {e}")
                else:
                    # Status matches desired state
                    status = "running" if is_running else "paused"
                    logger.info(f"✓ {bot_name}: {status} (correct)")
            
            # Wait before next check
            logger.info(f"💤 Next check in 5 minutes...")
            time.sleep(300)  # 5 minutes

def main():
    """Main function"""
    scheduler = BotScheduler()
    
    try:
        scheduler.manage_bots()
    except KeyboardInterrupt:
        logger.info("👋 Bot scheduler stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
