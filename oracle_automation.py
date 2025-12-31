"""
OracleXBT Complete Automation System
Combines hourly tweeting with real-time reply monitoring
Runs both operations concurrently with proper orchestration
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import schedule
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent import PredictionMarketAgent
from agent.tweet_scheduler import HourlyTweetScheduler, TweetContentType
from oracle_realtime_monitor import RealtimeTweetMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - OracleXBT - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oraclexbt.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OracleXBTAutomationSystem:
    """
    Complete automation system that manages:
    1. Hourly tweet generation and posting
    2. Real-time monitoring and reply generation for ALL monitored accounts
    
    Runs both operations concurrently with intelligent scheduling.
    """
    
    def __init__(self, hourly_interval: int = 3600, monitoring_interval: int = 300):
        """
        Initialize the complete automation system.
        
        Args:
            hourly_interval: Seconds between hourly tweets (default 3600 = 1 hour)
            monitoring_interval: Seconds between monitoring cycles (default 300 = 5 min)
        """
        logger.info("🚀 Initializing OracleXBT Automation System...")
        
        self.agent = PredictionMarketAgent()
        
        # Initialize scheduler for hourly tweets
        self.tweet_scheduler = HourlyTweetScheduler(
            self.agent,
            config={
                'randomize_order': True,
                'include_threads': False,
                'max_retries': 3
            }
        )
        
        # Initialize monitor for real-time replies
        self.tweet_monitor = RealtimeTweetMonitor(check_interval=monitoring_interval)
        
        # Configuration
        self.hourly_interval = hourly_interval
        self.monitoring_interval = monitoring_interval
        
        # State tracking
        self.running = False
        self.threads = {}
        self.system_stats = {
            'start_time': None,
            'uptime_seconds': 0,
            'total_tweets_posted': 0,
            'total_replies_posted': 0,
            'hourly_tweet_threads': 0,
            'last_hourly_tweet': None,
            'last_monitoring_cycle': None
        }
        
        logger.info("✅ OracleXBT Automation System initialized")
        logger.info(f"   - Hourly tweet interval: {hourly_interval}s ({hourly_interval/3600:.1f}h)")
        logger.info(f"   - Monitoring check interval: {monitoring_interval}s")
        logger.info(f"   - Monitoring {len(self.tweet_monitor.monitored_accounts)} accounts")
    
    def _hourly_tweet_worker(self):
        """Worker thread that posts tweets on schedule"""
        logger.info("🕐 Hourly tweet worker started")
        
        try:
            while self.running:
                try:
                    logger.info("📝 Generating hourly tweet...")
                    
                    success = self.tweet_scheduler.post_hourly_tweet()
                    
                    if success:
                        self.system_stats['total_tweets_posted'] += 1
                        self.system_stats['last_hourly_tweet'] = datetime.now().isoformat()
                        logger.info(f"✅ Tweet posted! (Total: {self.system_stats['total_tweets_posted']})")
                    else:
                        logger.warning("❌ Failed to post hourly tweet")
                    
                    # Sleep until next hour
                    logger.info(f"⏳ Next tweet in {self.hourly_interval/60:.0f} minutes...")
                    time.sleep(self.hourly_interval)
                    
                except Exception as e:
                    logger.error(f"Error in hourly tweet worker: {e}")
                    time.sleep(5)  # Brief pause before retry
                    
        except KeyboardInterrupt:
            logger.info("⏹ Hourly tweet worker stopped")
        finally:
            logger.info("🕐 Hourly tweet worker ended")
    
    def _monitoring_worker(self):
        """Worker thread that monitors and replies to tweets"""
        logger.info("👁️ Real-time monitoring worker started")
        
        try:
            while self.running:
                try:
                    logger.info("📊 Running monitoring cycle...")
                    
                    cycle_result = self.tweet_monitor.run_monitoring_cycle()
                    
                    replies_posted = cycle_result.get('replies_posted', 0)
                    self.system_stats['total_replies_posted'] += replies_posted
                    self.system_stats['last_monitoring_cycle'] = datetime.now().isoformat()
                    
                    if replies_posted > 0:
                        logger.info(f"✅ {replies_posted} replies posted (Total: {self.system_stats['total_replies_posted']})")
                    
                    # Wait before next cycle
                    logger.info(f"⏳ Next monitoring cycle in {self.monitoring_interval}s...")
                    time.sleep(self.monitoring_interval)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring worker: {e}")
                    time.sleep(5)  # Brief pause before retry
                    
        except KeyboardInterrupt:
            logger.info("⏹ Monitoring worker stopped")
        finally:
            logger.info("👁️ Monitoring worker ended")
    
    def start(self):
        """Start the automation system with both workers running"""
        if self.running:
            logger.warning("System is already running")
            return
        
        logger.info("\n" + "=" * 70)
        logger.info("🎯 STARTING ORACLEXBT AUTOMATION SYSTEM")
        logger.info("=" * 70)
        
        self.running = True
        self.system_stats['start_time'] = datetime.now().isoformat()
        
        # Start hourly tweet worker
        hourly_thread = threading.Thread(
            target=self._hourly_tweet_worker,
            name="HourlyTweetWorker",
            daemon=False
        )
        hourly_thread.start()
        self.threads['hourly'] = hourly_thread
        logger.info("✓ Hourly tweet worker thread started")
        
        # Start monitoring worker
        monitoring_thread = threading.Thread(
            target=self._monitoring_worker,
            name="MonitoringWorker",
            daemon=False
        )
        monitoring_thread.start()
        self.threads['monitoring'] = monitoring_thread
        logger.info("✓ Real-time monitoring worker thread started")
        
        logger.info("=" * 70)
        logger.info("🚀 ORACLEXBT IS NOW RUNNING")
        logger.info("=" * 70)
        logger.info("\n🔄 Agent is now:")
        logger.info("   - Posting engaging tweets every hour")
        logger.info("   - Monitoring ALL tweets from 25+ prediction market accounts")
        logger.info("   - Replying to every relevant tweet with valuable insights")
        logger.info("\nPress Ctrl+C to stop gracefully\n")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n⏹ Shutdown signal received...")
            self.stop()
    
    def stop(self):
        """Gracefully stop the automation system"""
        if not self.running:
            logger.warning("System is not running")
            return
        
        logger.info("\n" + "=" * 70)
        logger.info("⏹ STOPPING ORACLEXBT AUTOMATION SYSTEM")
        logger.info("=" * 70)
        
        self.running = False
        
        # Wait for threads to finish
        timeout = 10
        for name, thread in self.threads.items():
            logger.info(f"Waiting for {name} thread to stop...")
            thread.join(timeout=timeout)
            if thread.is_alive():
                logger.warning(f"⚠️ {name} thread did not stop cleanly")
            else:
                logger.info(f"✓ {name} thread stopped")
        
        self.print_statistics()
        
        logger.info("=" * 70)
        logger.info("✅ ORACLEXBT AUTOMATION SYSTEM STOPPED")
        logger.info("=" * 70 + "\n")
    
    def print_statistics(self):
        """Print system statistics"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 ORACLEXBT STATISTICS")
        logger.info("=" * 70)
        
        if self.system_stats['start_time']:
            start = datetime.fromisoformat(self.system_stats['start_time'])
            uptime = datetime.now() - start
            logger.info(f"Uptime: {uptime}")
        
        logger.info(f"Total tweets posted: {self.system_stats['total_tweets_posted']}")
        logger.info(f"Total replies posted: {self.system_stats['total_replies_posted']}")
        
        if self.system_stats['last_hourly_tweet']:
            logger.info(f"Last hourly tweet: {self.system_stats['last_hourly_tweet']}")
        
        if self.system_stats['last_monitoring_cycle']:
            logger.info(f"Last monitoring cycle: {self.system_stats['last_monitoring_cycle']}")
        
        # Tweet scheduler stats
        scheduler_stats = self.tweet_scheduler.get_stats()
        logger.info(f"\nTweet Scheduler Stats:")
        logger.info(f"  - Generated tweets: {scheduler_stats['tweets_posted']}")
        logger.info(f"  - Failed attempts: {scheduler_stats['failed_attempts']}")
        if scheduler_stats['tweets_posted'] + scheduler_stats['failed_attempts'] > 0:
            logger.info(f"  - Success rate: {scheduler_stats['success_rate']:.1%}")
        
        # Monitor stats
        logger.info(f"\nMonitoring Stats:")
        logger.info(f"  - Accounts monitored: {self.tweet_monitor.stats['accounts_monitored']}")
        logger.info(f"  - Total replied tweets tracked: {len(self.tweet_monitor.replied_tweets)}")
        
        logger.info("=" * 70 + "\n")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'running': self.running,
            'start_time': self.system_stats['start_time'],
            'tweets_posted': self.system_stats['total_tweets_posted'],
            'replies_posted': self.system_stats['total_replies_posted'],
            'accounts_monitored': len(self.tweet_monitor.monitored_accounts),
            'threads_running': len([t for t in self.threads.values() if t.is_alive()])
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OracleXBT Automation System')
    parser.add_argument(
        '--hourly-interval',
        type=int,
        default=3600,
        help='Seconds between hourly tweets (default 3600)'
    )
    parser.add_argument(
        '--monitoring-interval',
        type=int,
        default=300,
        help='Seconds between monitoring cycles (default 300)'
    )
    parser.add_argument(
        '--stats-only',
        action='store_true',
        help='Print statistics and exit'
    )
    
    args = parser.parse_args()
    
    system = OracleXBTAutomationSystem(
        hourly_interval=args.hourly_interval,
        monitoring_interval=args.monitoring_interval
    )
    
    if args.stats_only:
        system.print_statistics()
    else:
        try:
            system.start()
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            system.stop()
            raise


if __name__ == "__main__":
    main()
