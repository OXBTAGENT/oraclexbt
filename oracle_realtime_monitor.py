"""
OracleXBT Real-Time Tweet Reply System
Monitors ALL tweets from prediction market accounts and replies to every single one with valuable insights
"""

import time
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
import json
import os
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent import PredictionMarketAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - OracleXBT Monitor - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealtimeTweetMonitor:
    """
    Real-time monitor that tracks and replies to EVERY tweet from monitored accounts.
    Continuously monitors for new tweets and generates intelligent, contextual replies.
    """
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize the real-time tweet monitor.
        
        Args:
            check_interval: Seconds between checking for new tweets (default 60)
        """
        self.agent = PredictionMarketAgent()
        self.monitored_accounts = self._get_prediction_market_accounts()
        self.check_interval = check_interval
        
        # Tweet tracking
        self.reply_history_file = "oracle_reply_history.json"
        self.replied_tweets: Set[str] = self._load_replied_tweets()
        
        # Stats tracking
        self.stats = {
            'total_tweets_seen': 0,
            'total_replies_posted': 0,
            'failed_replies': 0,
            'last_check': None,
            'accounts_monitored': len(self.monitored_accounts),
            'check_interval': check_interval
        }
        
        # Per-account tracking
        self.account_stats = defaultdict(lambda: {'tweets_seen': 0, 'replies_posted': 0})
        
    def _get_prediction_market_accounts(self) -> List[Dict[str, str]]:
        """Get comprehensive list of ALL prediction market accounts to monitor"""
        return [
            # ===== OFFICIAL PLATFORM ACCOUNTS =====
            {
                "username": "Polymarket",
                "priority": "critical",
                "type": "platform",
                "description": "Official Polymarket account"
            },
            {
                "username": "Kalshi",
                "priority": "critical",
                "type": "platform",
                "description": "Official Kalshi account"
            },
            {
                "username": "ManifoldMarkets",
                "priority": "high",
                "type": "platform",
                "description": "Manifold Markets platform"
            },
            {
                "username": "PredictIt",
                "priority": "high",
                "type": "platform",
                "description": "PredictIt platform"
            },
            {
                "username": "GoodJudgmentInc",
                "priority": "medium",
                "type": "platform",
                "description": "Good Judgment Project"
            },
            
            # ===== KEY PLATFORM EXECUTIVES & FOUNDERS =====
            {
                "username": "shayne_coplan",
                "priority": "critical",
                "type": "executive",
                "description": "Polymarket CEO"
            },
            {
                "username": "CalebBrown412",
                "priority": "high",
                "type": "executive",
                "description": "Kalshi CEO"
            },
            {
                "username": "AustinGingerKirk",
                "priority": "high",
                "type": "executive",
                "description": "Manifold Markets founder"
            },
            
            # ===== MAJOR PREDICTION MARKET TRADERS & ANALYSTS =====
            {
                "username": "nabeelqureshi",
                "priority": "critical",
                "type": "trader",
                "description": "Prediction market analyst and trader"
            },
            {
                "username": "RyanBerckmans",
                "priority": "high",
                "type": "trader",
                "description": "Active prediction market trader"
            },
            {
                "username": "maxbmckinnon",
                "priority": "high",
                "type": "trader",
                "description": "Prediction market trader and analyst"
            },
            {
                "username": "ElectionBettingOdds",
                "priority": "high",
                "type": "data",
                "description": "Prediction market odds aggregator"
            },
            {
                "username": "theSamParr",
                "priority": "medium",
                "type": "trader",
                "description": "Prediction market participant"
            },
            {
                "username": "CryptoCred",
                "priority": "medium",
                "type": "analyst",
                "description": "Crypto market analyst"
            },
            {
                "username": "APompliano",
                "priority": "medium",
                "type": "analyst",
                "description": "Market analyst and commentator"
            },
            
            # ===== POLITICAL & ECONOMIC ANALYSTS =====
            {
                "username": "NateSilver538",
                "priority": "high",
                "type": "analyst",
                "description": "Statistical analyst, highly relevant for prediction markets"
            },
            {
                "username": "gelliottmorris",
                "priority": "high",
                "type": "analyst",
                "description": "Elections analyst"
            },
            {
                "username": "Politics_Polls",
                "priority": "medium",
                "type": "data",
                "description": "Political polling data aggregator"
            },
            
            # ===== CRYPTO & FINANCE ANALYSTS =====
            {
                "username": "loomdart",
                "priority": "high",
                "type": "analyst",
                "description": "Crypto market analyst"
            },
            {
                "username": "CryptoHayes",
                "priority": "medium",
                "type": "trader",
                "description": "Crypto market commentator"
            },
            {
                "username": "DaanCrypto",
                "priority": "medium",
                "type": "analyst",
                "description": "Crypto analyst"
            },
            
            # ===== FORECASTING & RESEARCH ORGANIZATIONS =====
            {
                "username": "metaculus",
                "priority": "high",
                "type": "platform",
                "description": "Metaculus forecasting platform"
            },
            {
                "username": "FuturismInst",
                "priority": "medium",
                "type": "research",
                "description": "Futurism research institute"
            },
        ]
    
    def _load_replied_tweets(self) -> Set[str]:
        """Load previously replied tweet IDs to avoid duplicate replies"""
        try:
            if os.path.exists(self.reply_history_file):
                with open(self.reply_history_file, 'r') as f:
                    data = json.load(f)
                    replied = set(data.get('replied_tweets', []))
                    logger.info(f"Loaded {len(replied)} previously replied tweets")
                    return replied
        except Exception as e:
            logger.warning(f"Could not load reply history: {e}")
        return set()
    
    def _save_replied_tweet(self, tweet_id: str, account: str, reply_text: str):
        """Save replied tweet to history to prevent duplicate replies"""
        try:
            data = {"replied_tweets": list(self.replied_tweets)}
            if os.path.exists(self.reply_history_file):
                with open(self.reply_history_file, 'r') as f:
                    existing = json.load(f)
                    data = existing
            
            self.replied_tweets.add(tweet_id)
            data['replied_tweets'] = list(self.replied_tweets)
            
            # Also save reply details for auditing
            if 'reply_details' not in data:
                data['reply_details'] = []
            
            data['reply_details'].append({
                'tweet_id': tweet_id,
                'account': account,
                'reply_text': reply_text,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 5000 replies in history
            data['reply_details'] = data['reply_details'][-5000:]
            
            with open(self.reply_history_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Could not save reply history: {e}")
    
    def _should_reply_to_tweet(self, tweet_data: Dict[str, Any]) -> bool:
        """Determine if we should reply to this tweet"""
        tweet_text = tweet_data.get('text', '').lower()
        tweet_id = tweet_data.get('id')
        
        # Skip if already replied
        if tweet_id in self.replied_tweets:
            return False
        
        # Skip if tweet is too old (>12 hours)
        created_at = tweet_data.get('created_at')
        if created_at:
            try:
                tweet_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if datetime.now().timestamp() - tweet_time.timestamp() > 12 * 3600:
                    return False
            except:
                pass
        
        # Keywords indicating prediction market relevance
        prediction_keywords = [
            'prediction', 'market', 'polymarket', 'kalshi', 'manifold',
            'odds', 'forecast', 'probability', 'betting', 'trade',
            'arbitrage', 'spread', 'liquidity', 'volume', 'price'
        ]
        
        # Topics OracleXBT can add value to
        valuable_topics = [
            'election', 'politics', 'economy', 'crypto', 'bitcoin',
            'sports', 'earnings', 'fed', 'inflation', 'recession',
            'ai', 'tech', 'stock', 'debate', 'poll', 'rate',
            'gdp', 'unemployment', 'war', 'climate', 'data'
        ]
        
        # Check if tweet matches any criteria - more liberal for replies
        has_prediction_keywords = any(kw in tweet_text for kw in prediction_keywords)
        has_valuable_topics = any(topic in tweet_text for topic in valuable_topics)
        
        # Reply to most tweets from monitored accounts for engagement
        return has_prediction_keywords or has_valuable_topics or len(tweet_text) > 20
    
    def _generate_intelligent_reply(self, tweet_text: str, author: str, account_type: str) -> Optional[str]:
        """Generate an intelligent, contextual reply to a tweet"""
        try:
            prompt = f"""
            You are OracleXBT, an expert in prediction markets who provides valuable market insights.
            
            A tweet was posted by @{author} (account type: {account_type}):
            "{tweet_text}"
            
            Generate a VALUABLE reply that adds genuine insight, data, or analysis.
            
            Your reply should:
            1. Add specific value - data, analysis, cross-platform insights, market context
            2. Be conversational and engaging, not promotional
            3. Include numbers/percentages/odds when possible
            4. Stay under 280 characters
            5. Sound like a knowledgeable market professional
            6. Only respond if you can add real value
            
            Return ONLY the reply text (no quotes, no explanations). If no good reply, respond with "SKIP".
            """
            
            response = self.agent.chat(prompt)
            
            if "SKIP" in response.upper():
                return None
            
            reply_text = response.strip().strip('"\'')
            
            # Ensure tweet length
            if len(reply_text) > 280:
                reply_text = reply_text[:277] + "..."
            
            return reply_text
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return None
    
    def monitor_account_tweets(self, account: Dict[str, str], max_tweets: int = 10) -> int:
        """
        Monitor a specific account and reply to ALL new tweets.
        
        Args:
            account: Account info dict with username, type, etc
            max_tweets: Max tweets to check in one monitoring cycle
            
        Returns:
            Number of replies posted
        """
        username = account['username']
        replies_posted = 0
        
        try:
            logger.info(f"Monitoring @{username}...")
            
            # Get recent tweets from this account
            search_prompt = f"""
            Get the latest {max_tweets} tweets from @{username}.
            Return them with tweet ID, text, and creation time.
            
            Use the search_tweets tool or get_user_tweets if available.
            """
            
            tweets_response = self.agent.chat(search_prompt)
            
            # Parse tweets and generate replies
            # For now, process with a simpler approach using the agent to handle the full cycle
            
            reply_prompt = f"""
            For the most recent tweets from @{username}, analyze them and:
            
            1. Check which ones are about prediction markets, politics, economics, crypto, or data/analysis
            2. For EACH relevant tweet, generate a valuable reply with specific market insights
            3. Reply to ALL suitable tweets (be liberal - if you can add any insight, reply)
            4. Use the reply_to_tweet tool to post each reply
            
            Focus on recent tweets (last 6 hours). Make each reply count.
            Report how many replies you posted.
            """
            
            response = self.agent.chat(reply_prompt)
            
            # Try to extract number of replies from response
            if "posted" in response.lower() or "replied" in response.lower():
                # Count mentions of actions taken
                import re
                numbers = re.findall(r'\d+', response)
                if numbers:
                    replies_posted = int(numbers[0])
            
            self.account_stats[username]['tweets_seen'] += max_tweets
            self.account_stats[username]['replies_posted'] += replies_posted
            
            if replies_posted > 0:
                logger.info(f"✓ Posted {replies_posted} replies to @{username}")
                self.stats['total_replies_posted'] += replies_posted
            else:
                logger.info(f"No new tweet replies for @{username}")
            
            return replies_posted
            
        except Exception as e:
            logger.error(f"Error monitoring @{username}: {e}")
            self.stats['failed_replies'] += 1
            return 0
    
    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """
        Run one complete monitoring cycle across ALL monitored accounts.
        
        Returns:
            Stats dict with results
        """
        logger.info("=" * 60)
        logger.info("🔄 Starting real-time monitoring cycle...")
        logger.info("=" * 60)
        
        cycle_start = datetime.now()
        total_replies = 0
        
        # Prioritize accounts: critical > high > medium > low
        priority_order = ['critical', 'high', 'medium', 'low']
        sorted_accounts = []
        
        for priority in priority_order:
            sorted_accounts.extend([
                acc for acc in self.monitored_accounts
                if acc.get('priority', 'low') == priority
            ])
        
        # Monitor each account
        for account in sorted_accounts:
            try:
                replies = self.monitor_account_tweets(account, max_tweets=15)
                total_replies += replies
                
                # Small delay between accounts to avoid rate limits
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {account['username']}: {e}")
        
        # Update stats
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        self.stats['total_tweets_seen'] += 1
        self.stats['total_replies_posted'] += total_replies
        self.stats['last_check'] = datetime.now().isoformat()
        
        logger.info("=" * 60)
        logger.info(f"✅ Monitoring cycle complete!")
        logger.info(f"   Total replies posted: {total_replies}")
        logger.info(f"   Accounts monitored: {len(sorted_accounts)}")
        logger.info(f"   Cycle duration: {cycle_duration:.1f}s")
        logger.info("=" * 60)
        
        return {
            'replies_posted': total_replies,
            'cycle_duration': cycle_duration,
            'accounts_checked': len(sorted_accounts),
            'timestamp': datetime.now().isoformat()
        }
    
    def start_continuous_monitoring(self, run_forever: bool = True):
        """
        Start continuous monitoring that runs every check_interval seconds.
        
        Args:
            run_forever: If True, runs indefinitely. If False, runs once.
        """
        logger.info(f"🚀 Starting real-time tweet monitoring (check every {self.check_interval}s)")
        logger.info(f"📊 Monitoring {len(self.monitored_accounts)} accounts")
        
        cycle_count = 0
        try:
            while True:
                cycle_count += 1
                logger.info(f"\n📍 Cycle #{cycle_count}")
                
                self.run_monitoring_cycle()
                
                if not run_forever:
                    break
                
                logger.info(f"⏳ Waiting {self.check_interval}s until next check...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⏹ Monitoring stopped by user")
            self.print_stats()
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            raise
    
    def print_stats(self):
        """Print monitoring statistics"""
        logger.info("\n" + "=" * 60)
        logger.info("📈 MONITORING STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total tweets seen: {self.stats['total_tweets_seen']}")
        logger.info(f"Total replies posted: {self.stats['total_replies_posted']}")
        logger.info(f"Failed replies: {self.stats['failed_replies']}")
        logger.info(f"Accounts monitored: {self.stats['accounts_monitored']}")
        
        if self.account_stats:
            logger.info("\nTop accounts by replies:")
            sorted_accounts = sorted(
                self.account_stats.items(),
                key=lambda x: x[1]['replies_posted'],
                reverse=True
            )[:5]
            for account, stats in sorted_accounts:
                logger.info(
                    f"  @{account}: {stats['replies_posted']} replies "
                    f"({stats['tweets_seen']} tweets seen)"
                )
        logger.info("=" * 60 + "\n")


def start_monitoring():
    """Start the real-time monitoring system"""
    monitor = RealtimeTweetMonitor(check_interval=60)  # Check every 60 seconds
    monitor.start_continuous_monitoring(run_forever=True)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        monitor = RealtimeTweetMonitor()
        monitor.run_monitoring_cycle()
    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        monitor = RealtimeTweetMonitor()
        monitor.print_stats()
    else:
        print("""
OracleXBT Real-Time Tweet Monitor
Usage:
  python3 oracle_realtime_monitor.py      - Start continuous monitoring
  python3 oracle_realtime_monitor.py once - Run one monitoring cycle
  python3 oracle_realtime_monitor.py stats- Show statistics
        """)
        start_monitoring()
