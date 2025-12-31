"""
OracleXBT Twitter Automation & Content Manager
Automated posting, monitoring, and engagement for prediction markets
"""

import os
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agent import PredictionMarketAgent
from oracle_account_monitor import AccountMonitor
from oracle_account_monitor import AccountMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - OracleXBT - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OracleXBTTwitterManager:
    """Automated Twitter management for OracleXBT"""
    
    def __init__(self):
        self.agent = PredictionMarketAgent()
        self.account_monitor = AccountMonitor()
        self.last_arbitrage_check = None
        self.daily_tweets_posted = 0
        self.max_daily_tweets = 24  # Hourly tweets
        self.daily_replies_posted = 0
        self.max_daily_replies = 20  # More replies for engagement
        self.last_content_type = None  # Track last tweet type for variety
        
    def post_morning_market_update(self):
        """Post morning market overview"""
        try:
            logger.info("Posting morning market update...")
            
            prompt = """
            Create a concise morning market update tweet. Write in a natural, analytical tone like a market professional. Include:
            - Top 2-3 most active prediction markets  
            - Any overnight price movements >10%
            - Volume highlights
            - Start with something like "Morning update:" or "Overnight action:"
            - Sound human and professional, not overly enthusiastic
            - Keep under 280 characters
            - Actually post it to Twitter
            """
            
            response = self.agent.chat(prompt)
            logger.info(f"Morning update posted: {response[:100]}...")
            self.daily_tweets_posted += 1
            
        except Exception as e:
            logger.error(f"Failed to post morning update: {e}")
    
    def check_and_post_arbitrage(self):
        """Check for arbitrage opportunities and post if found"""
        try:
            logger.info("Checking for arbitrage opportunities...")
            
            prompt = """
            Search for current arbitrage opportunities across all platforms.
            If you find any with >5% spread:
            1. Post a professional arbitrage alert tweet
            2. Include specific platforms and prices  
            3. Start with "Arbitrage opportunity:" or "Price discrepancy spotted:"
            4. Write in a clear, analytical tone - no excessive punctuation or emojis
            5. Actually post it
            
            If no good opportunities, just say "No significant arbitrage found"
            """
            
            response = self.agent.chat(prompt)
            
            if "arbitrage alert" in response.lower() or "posted" in response.lower():
                logger.info("Arbitrage opportunity posted!")
                self.daily_tweets_posted += 1
            else:
                logger.info("No arbitrage opportunities found")
                
        except Exception as e:
            logger.error(f"Failed to check arbitrage: {e}")
    
    def post_market_analysis(self):
        """Post detailed market analysis thread"""
        try:
            if self.daily_tweets_posted >= self.max_daily_tweets:
                logger.info("Daily tweet limit reached, skipping analysis")
                return
                
            logger.info("Posting market analysis thread...")
            
            prompt = """
            Create and post a market analysis thread about the most interesting trend today.
            Write in a professional, analytical tone like a financial analyst. Format:
            1/3 - Open with the key finding or trend
            2/3 - Present the data and reasoning behind it
            3/3 - Provide actionable insight or conclusion
            
            Keep the language natural and human - avoid excessive emojis or hype.
            Focus on something with real volume/movement.
            Actually post the thread.
            """
            
            response = self.agent.chat(prompt)
            logger.info(f"Analysis thread posted: {response[:100]}...")
            self.daily_tweets_posted += 3  # Thread counts as multiple tweets
            
        except Exception as e:
            logger.error(f"Failed to post analysis: {e}")
    
    def monitor_and_reply(self):
        """Monitor prediction market accounts and post intelligent replies"""
        try:
            if self.daily_replies_posted >= self.max_daily_replies:
                logger.info("Daily reply limit reached, skipping monitoring")
                return
                
            logger.info("Monitoring prediction market accounts for reply opportunities...")
            
            # Get high-priority accounts to check
            high_priority_accounts = [
                "Polymarket", "Kalshi", "shayne_coplan", "nabeelqureshi",
                "ManifoldMarkets", "RyanBerckmans", "maxbmckinnon"
            ]
            
            for username in high_priority_accounts:
                if self.daily_replies_posted >= self.max_daily_replies:
                    break
                    
                prompt = f"""
                Check the latest 3 tweets from @{username} and look for opportunities to add valuable insights.
                
                For each tweet that's about prediction markets, politics, economics, events we track, or general market discussion:
                1. Analyze if OracleXBT can add genuine value with data, analysis, or interesting perspective
                2. If yes, reply with specific insights, numbers, cross-platform comparisons, or relevant data
                3. Keep replies professional and analytical but engaging
                4. Be more liberal with replies - if you can add any valuable perspective, do it
                
                Focus on tweets from the last 8 hours. Look for opportunities to showcase market expertise.
                """
                
                try:
                    response = self.agent.chat(prompt)
                    
                    if "replied" in response.lower() or "posted" in response.lower():
                        self.daily_replies_posted += 1
                        logger.info(f"Posted intelligent reply to @{username}")
                        
                except Exception as e:
                    logger.error(f"Failed to check @{username}: {e}")
                    
                # Small delay between accounts
                time.sleep(1)
            
        except Exception as e:
            logger.error(f"Failed to monitor accounts: {e}")
    
    def post_educational_content(self):
        """Post educational prediction market content"""
        try:
            if self.daily_tweets_posted >= self.max_daily_tweets:
                return
                
            logger.info("Posting educational content...")
            
            topics = [
                "arbitrage basics for beginners",
                "understanding prediction market odds", 
                "platform comparison (fees, features)",
                "risk management in prediction markets",
                "reading volume and liquidity signals"
            ]
            
            import random
            topic = random.choice(topics)
            
            prompt = f"""
            Create an educational tweet about: {topic}
            
            Write in a clear, informative style like a knowledgeable trader sharing insights.
            Structure:
            - Start with the key insight or tip
            - Explain why it matters with a brief example
            - End with an actionable takeaway
            
            Keep it conversational and professional. Post it.
            """
            
            response = self.agent.chat(prompt)
            logger.info(f"Educational content posted: {response[:100]}...")
            self.daily_tweets_posted += 1
            
        except Exception as e:
            logger.error(f"Failed to post education: {e}")
    
    def engage_with_community(self):
        """Engage with prediction market community"""
        try:
            logger.info("Engaging with community...")
            
            prompt = """
            Search for recent prediction market tweets from @Polymarket, @Kalshi, or major traders.
            Find 2-3 interesting ones and:
            1. Reply with valuable, data-driven insights
            2. Add your analytical perspective with specific numbers or trends
            3. Keep replies conversational and professional - like a knowledgeable colleague
            4. Avoid emojis unless truly necessary
            
            Actually engage with the tweets.
            """
            
            response = self.agent.chat(prompt)
            logger.info(f"Community engagement: {response[:100]}...")
            
        except Exception as e:
            logger.error(f"Failed to engage: {e}")
    
    def evening_wrap_up(self):
        """Post evening market wrap-up"""
        try:
            if self.daily_tweets_posted >= self.max_daily_tweets:
                return
                
            logger.info("Posting evening wrap-up...")
            
            prompt = """
            Create an end-of-day market wrap-up tweet in a professional tone:
            - Biggest market moves of the day
            - Volume leaders
            - Any major news impact
            - Brief preview of tomorrow's key events
            
            Start with something like "End of day recap:" or "Today's market summary:"
            Keep it analytical and informative. Post it to Twitter.
            """
            
            response = self.agent.chat(prompt)
            logger.info(f"Evening wrap-up posted: {response[:100]}...")
            self.daily_tweets_posted += 1
            
        except Exception as e:
            logger.error(f"Failed to post wrap-up: {e}")
    
    def autonomous_hourly_post(self):
        """Autonomous hourly posting with varied content"""
        try:
            if self.daily_tweets_posted >= self.max_daily_tweets:
                logger.info("Daily tweet limit reached, skipping hourly post")
                return
            
            # Rotate through different content types for variety
            content_types = [
                'market_update',
                'arbitrage_check', 
                'analysis',
                'insight',
                'data_share'
            ]
            
            # Avoid repeating the same content type
            import random
            available_types = [t for t in content_types if t != self.last_content_type]
            content_type = random.choice(available_types)
            self.last_content_type = content_type
            
            logger.info(f"Autonomous hourly post: {content_type}")
            
            if content_type == 'market_update':
                prompt = """
                Post a quick market update tweet:
                - Highlight 1-2 interesting market movements or trends right now
                - Include specific odds or price changes
                - Keep it brief and data-focused
                - Post it to Twitter
                """
            elif content_type == 'arbitrage_check':
                self.check_and_post_arbitrage()
                return
            elif content_type == 'analysis':
                prompt = """
                Share a brief market analysis insight:
                - Pick an interesting pattern or trend you're seeing
                - Explain what the data shows
                - Keep it under 280 characters
                - Post it to Twitter
                """
            elif content_type == 'insight':
                prompt = """
                Share a quick prediction market insight or observation:
                - Something interesting about volume, liquidity, or market behavior
                - A notable correlation or divergence
                - Keep it analytical and professional
                - Post it to Twitter
                """
            else:  # data_share
                prompt = """
                Share interesting data from prediction markets:
                - Compare odds across platforms on a hot topic
                - Show volume trends or notable shifts
                - Present it clearly with numbers
                - Post it to Twitter
                """
            
            response = self.agent.chat(prompt)
            logger.info(f"Autonomous post completed: {content_type}")
            self.daily_tweets_posted += 1
            
        except Exception as e:
            logger.error(f"Failed autonomous hourly post: {e}")
    
    def reset_daily_counters(self):
        """Reset daily counters at midnight"""
        self.daily_tweets_posted = 0
        logger.info("Daily counters reset")
    
    def start_automation(self):
        """Start the automated posting schedule - autonomous hourly tweets"""
        logger.info("OracleXBT autonomous mode starting...")
        
        # Hourly autonomous posts (every hour on the hour)
        for hour in range(24):
            schedule.every().day.at(f"{hour:02d}:00").do(self.autonomous_hourly_post)
        
        # Monitoring & replies (every 2-3 hours throughout the day)
        schedule.every().day.at("08:30").do(self.monitor_and_reply)
        schedule.every().day.at("11:00").do(self.monitor_and_reply)
        schedule.every().day.at("13:30").do(self.monitor_and_reply)
        schedule.every().day.at("16:00").do(self.monitor_and_reply)
        schedule.every().day.at("18:30").do(self.monitor_and_reply)
        schedule.every().day.at("21:00").do(self.monitor_and_reply)
        schedule.every().day.at("23:00").do(self.monitor_and_reply)
        
        # Educational content (3x per week)
        schedule.every().monday.at("14:00").do(self.post_educational_content)
        schedule.every().wednesday.at("14:00").do(self.post_educational_content)
        schedule.every().friday.at("14:00").do(self.post_educational_content)
        
        # Deep analysis threads (2x per day)
        schedule.every().day.at("10:00").do(self.post_market_analysis)
        schedule.every().day.at("20:00").do(self.post_market_analysis)
        
        # Reset counters daily
        schedule.every().day.at("00:00").do(self.reset_daily_counters)
        
        
        print("""
🤖 AUTONOMOUS MODE ACTIVE
""")
        print("📊 Posting Strategy:")
        print("  • Hourly tweets (00:00 - 23:00) with varied content")
        print("  • Market updates, arbitrage checks, insights, data shares")
        print("  • 7 monitoring sessions for replies throughout the day")
        print("  • 2 deep analysis threads (10:00 & 20:00)")
        print("  • Educational content (Mon/Wed/Fri)")
        print()
        print("📈 Daily Volume: ~24 tweets + ~20 replies = ~44 posts/day")
        print()
        print("🔄 System running continuously. Press Ctrl+C to stop.")
        print()
        
        # Run scheduling loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def reset_daily_counters(self):
        """Reset daily posting counters"""
        self.daily_tweets_posted = 0
        self.daily_replies_posted = 0
        logger.info("Daily counters reset")

def manual_post_now():
    """Manual posting function for immediate use"""
    manager = OracleXBTTwitterManager()
    
    print("OracleXBT Manual Posting")
    print("1. Morning update")
    print("2. Check arbitrage") 
    print("3. Market analysis thread")
    print("4. Educational content")
    print("5. Evening wrap-up")
    print("6. Engage with community")
    print("7. Monitor & reply to accounts")
    
    choice = input("Select option (1-7): ")
    
    if choice == "1":
        manager.post_morning_market_update()
    elif choice == "2":
        manager.check_and_post_arbitrage()
    elif choice == "3":
        manager.post_market_analysis()
    elif choice == "4":
        manager.post_educational_content()
    elif choice == "5":
        manager.evening_wrap_up()
    elif choice == "6":
        manager.engage_with_community()
    elif choice == "7":
        manager.monitor_and_reply()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        manual_post_now()
    else:
        manager = OracleXBTTwitterManager()
        manager.start_automation()