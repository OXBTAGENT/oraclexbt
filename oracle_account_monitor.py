"""
OracleXBT Account Monitor - Intelligent Reply System
Monitors prediction market accounts and generates valuable replies
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import os
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

class AccountMonitor:
    """Monitor specific accounts and generate intelligent replies"""
    
    def __init__(self):
        self.agent = PredictionMarketAgent()
        self.monitored_accounts = self._get_prediction_market_accounts()
        self.reply_history_file = "oracle_reply_history.json"
        self.replied_tweets = self._load_replied_tweets()
        
    def _get_prediction_market_accounts(self) -> List[Dict[str, str]]:
        """Get list of prediction market accounts to monitor"""
        return [
            # Official Platform Accounts
            {
                "username": "Polymarket",
                "priority": "high",
                "type": "platform",
                "description": "Official Polymarket account"
            },
            {
                "username": "Kalshi", 
                "priority": "high",
                "type": "platform",
                "description": "Official Kalshi account"
            },
            {
                "username": "ManifoldMarkets",
                "priority": "medium",
                "type": "platform", 
                "description": "Manifold Markets platform"
            },
            
            # Key Industry Figures
            {
                "username": "shayne_coplan",
                "priority": "high",
                "type": "ceo",
                "description": "Polymarket CEO"
            },
            {
                "username": "nabeelqureshi",
                "priority": "high", 
                "type": "investor",
                "description": "Prediction market investor/analyst"
            },
            {
                "username": "RyanBerckmans",
                "priority": "medium",
                "type": "trader",
                "description": "Active prediction market trader"
            },
            {
                "username": "maxbmckinnon",
                "priority": "medium",
                "type": "trader", 
                "description": "Prediction market trader"
            },
            {
                "username": "ElectionBettingOdds",
                "priority": "medium",
                "type": "data",
                "description": "Prediction market odds aggregator"
            },
            
            # News/Analysis Accounts
            {
                "username": "PredictIt",
                "priority": "medium",
                "type": "platform",
                "description": "PredictIt platform"
            },
            {
                "username": "NateSilver538",
                "priority": "low",
                "type": "analyst", 
                "description": "Statistical analyst, relevant for prediction markets"
            },
            
            # Research/Academic
            {
                "username": "GoodJudgmentInc",
                "priority": "medium",
                "type": "research",
                "description": "Forecasting research organization"
            }
        ]
    
    def _load_replied_tweets(self) -> set:
        """Load previously replied tweet IDs to avoid duplicates"""
        try:
            if os.path.exists(self.reply_history_file):
                with open(self.reply_history_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('replied_tweets', []))
        except Exception as e:
            logger.warning(f"Could not load reply history: {e}")
        return set()
    
    def _save_replied_tweet(self, tweet_id: str, account: str, reply_text: str):
        """Save replied tweet to history"""
        try:
            data = {"replied_tweets": list(self.replied_tweets)}
            if os.path.exists(self.reply_history_file):
                with open(self.reply_history_file, 'r') as f:
                    existing = json.load(f)
                    data = existing
            
            self.replied_tweets.add(tweet_id)
            data['replied_tweets'] = list(self.replied_tweets)
            
            # Also save reply details
            if 'reply_details' not in data:
                data['reply_details'] = []
            
            data['reply_details'].append({
                'tweet_id': tweet_id,
                'account': account,
                'reply_text': reply_text,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 500 replies in history
            data['reply_details'] = data['reply_details'][-500:]
            
            with open(self.reply_history_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Could not save reply history: {e}")
    
    def should_reply_to_tweet(self, tweet_data: Dict[str, Any]) -> bool:
        """Determine if we should reply to this tweet"""
        tweet_text = tweet_data.get('text', '').lower()
        tweet_id = tweet_data.get('id')
        
        # Skip if already replied
        if tweet_id in self.replied_tweets:
            return False
            
        # Skip if tweet is too old (>6 hours)
        created_at = tweet_data.get('created_at')
        if created_at:
            tweet_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if datetime.now().timestamp() - tweet_time.timestamp() > 6 * 3600:
                return False
        
        # Keywords that indicate prediction market relevance
        prediction_keywords = [
            'prediction market', 'polymarket', 'kalshi', 'manifold',
            'betting odds', 'election odds', 'forecast', 'probability',
            'arbitrage', 'prediction', 'odds', 'bet', 'wager',
            'market prices', 'trading', 'volume', 'liquidity', 'price'
        ]
        
        # Topics OracleXBT can add value to (expanded)
        valuable_topics = [
            'election', 'politics', 'economy', 'crypto', 'bitcoin',
            'sports', 'earnings', 'fed', 'inflation', 'recession',
            'ai', 'tech', 'stock market', 'debate', 'poll', 'trump',
            'biden', 'rate', 'gdp', 'unemployment', 'housing',
            'gas prices', 'war', 'ukraine', 'china', 'climate'
        ]
        
        # General engagement topics (new - broader reach)
        general_topics = [
            'data', 'analysis', 'trend', 'numbers', 'statistics',
            'research', 'study', 'report', 'survey', 'chart'
        ]
        
        # Check if tweet contains relevant keywords
        has_pm_keywords = any(keyword in tweet_text for keyword in prediction_keywords)
        has_valuable_topics = any(topic in tweet_text for topic in valuable_topics)
        has_general_topics = any(topic in tweet_text for topic in general_topics)
        
        # More liberal reply criteria - reply if ANY of these match
        return has_pm_keywords or has_valuable_topics or has_general_topics
    
    def generate_intelligent_reply(self, tweet_data: Dict[str, Any], account_info: Dict[str, str]) -> Optional[str]:
        """Generate an intelligent, data-driven reply"""
        try:
            tweet_text = tweet_data.get('text', '')
            author = tweet_data.get('author_username', account_info['username'])
            account_type = account_info.get('type', 'unknown')
            
            prompt = f"""
            Analyze this tweet and generate a valuable reply as OracleXBT:
            
            Tweet: "{tweet_text}"
            Author: @{author} (type: {account_type})
            
            Guidelines for your reply:
            1. Add genuine VALUE with data, analysis, market insights, or interesting perspective
            2. Be conversational and engaging, like joining a discussion among professionals
            3. Include specific numbers, prices, probabilities, or trends when relevant
            4. Reference current market data, cross-platform comparisons, or historical patterns if applicable
            5. Keep under 280 characters
            6. Be more liberal with replies - if you can add ANY valuable perspective or insight, do it
            7. Sound like a knowledgeable market analyst who's excited to share insights
            
            Topics to engage on:
            - Prediction markets, politics, economics, crypto, AI, tech, sports
            - Data analysis, trends, statistics, research
            - Market movements, forecasting, probability discussions
            - Any topic where market analysis or data insights could be valuable
            
            Only skip if the tweet is completely unrelated to anything OracleXBT could comment on meaningfully.
            If unsure, err on the side of engaging.
            
            Generate the reply text only (no quotes, no explanations). If you decide to skip, respond with "SKIP".
            """
            
            response = self.agent.chat(prompt)
            
            # Check if agent decided to skip
            if "SKIP" in response.upper() or len(response.strip()) < 10:
                return None
                
            # Clean and validate response
            reply_text = response.strip()
            if len(reply_text) > 280:
                reply_text = reply_text[:277] + "..."
                
            return reply_text
            
        except Exception as e:
            logger.error(f"Failed to generate reply: {e}")
            return None
    
    def monitor_account(self, account_info: Dict[str, str], max_tweets: int = 5) -> int:
        """Monitor a specific account and reply to relevant tweets"""
        username = account_info['username']
        replies_posted = 0
        
        try:
            logger.info(f"Monitoring @{username}...")
            
            # Get recent tweets using agent's Twitter tools
            prompt = f"""
            Get the latest {max_tweets} tweets from @{username}.
            Return the tweet data so I can analyze them for potential replies.
            Use the get_platform_tweets or search tools to find their recent posts.
            """
            
            response = self.agent.chat(prompt)
            
            # For now, since we need to implement proper tweet retrieval,
            # let's use a simpler approach with the agent's existing tools
            
            return replies_posted
            
        except Exception as e:
            logger.error(f"Failed to monitor @{username}: {e}")
            return 0
    
    def monitor_all_accounts(self) -> Dict[str, int]:
        """Monitor all configured accounts"""
        logger.info("Starting account monitoring cycle...")
        results = {}
        
        # Process high priority accounts first
        high_priority = [acc for acc in self.monitored_accounts if acc.get('priority') == 'high']
        medium_priority = [acc for acc in self.monitored_accounts if acc.get('priority') == 'medium']
        
        for account in high_priority + medium_priority:
            try:
                replies = self.monitor_account(account)
                results[account['username']] = replies
                
                # Small delay between accounts to avoid rate limits
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error monitoring {account['username']}: {e}")
                results[account['username']] = 0
        
        total_replies = sum(results.values())
        logger.info(f"Monitoring cycle complete. Posted {total_replies} replies across {len(results)} accounts")
        
        return results
    
    def smart_reply_to_tweet(self, tweet_id: str, tweet_text: str, author: str) -> bool:
        """Generate and post an intelligent reply to a specific tweet"""
        try:
            # Create mock account info for the reply generation
            account_info = {'username': author, 'type': 'monitored'}
            tweet_data = {
                'id': tweet_id,
                'text': tweet_text,
                'author_username': author,
                'created_at': datetime.now().isoformat()
            }
            
            # Check if we should reply
            if not self.should_reply_to_tweet(tweet_data):
                logger.info(f"Skipping reply to @{author} - not relevant or already replied")
                return False
            
            # Generate reply
            reply_text = self.generate_intelligent_reply(tweet_data, account_info)
            if not reply_text:
                logger.info(f"No valuable reply generated for @{author}")
                return False
            
            # Post the reply
            reply_prompt = f"""
            Reply to this tweet with the following message:
            
            Tweet ID: {tweet_id}
            Reply text: {reply_text}
            
            Use the reply_to_tweet tool to post this reply.
            """
            
            response = self.agent.chat(reply_prompt)
            
            # Save to history
            self._save_replied_tweet(tweet_id, author, reply_text)
            logger.info(f"Posted reply to @{author}: {reply_text[:100]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to reply to tweet {tweet_id}: {e}")
            return False

def test_reply_system():
    """Test the reply system with a sample tweet"""
    monitor = AccountMonitor()
    
    # Test with a sample prediction market tweet
    test_tweet_id = "test_123"
    test_tweet_text = "Bitcoin prediction markets are showing 85% chance of $100k by end of year. Volume is massive on Polymarket."
    test_author = "CryptoTrader123"
    
    success = monitor.smart_reply_to_tweet(test_tweet_id, test_tweet_text, test_author)
    if success:
        print("✅ Reply system test successful!")
    else:
        print("❌ Reply system test failed")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_reply_system()
    elif len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor = AccountMonitor()
        monitor.monitor_all_accounts()
    else:
        print("""
OracleXBT Account Monitor
Usage:
  python3 oracle_account_monitor.py test     - Test reply generation
  python3 oracle_account_monitor.py monitor  - Run monitoring cycle
        """)