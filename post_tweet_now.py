#!/usr/bin/env python3
"""Quick script to post a tweet immediately"""

import sys
from agent import PredictionMarketAgent

def main():
    # Get tweet text from command line or use default
    if len(sys.argv) > 1:
        tweet_text = " ".join(sys.argv[1:])
    else:
        tweet_text = "🔮 Prediction markets are heating up! Check out the latest trends in political betting and crypto forecasts. The wisdom of the crowds is speaking. #PredictionMarkets #PolyMarket"
    
    print(f"📝 Tweet to post: {tweet_text}")
    print(f"📏 Length: {len(tweet_text)} characters")
    
    if len(tweet_text) > 280:
        print("❌ Tweet too long! Must be under 280 characters.")
        return
    
    # Initialize agent
    print("\n🚀 Initializing agent...")
    agent = PredictionMarketAgent()
    
    # Check Twitter is available
    if not agent.twitter_tools or not agent.twitter_tools.twitter_client.is_ready:
        print("❌ Twitter client not available!")
        return
    
    # Post the tweet
    print("\n📤 Posting tweet...")
    result = agent.twitter_tools.post_tweet(tweet_text)
    
    if result.get("success"):
        print(f"✅ Tweet posted successfully!")
        if "url" in result:
            print(f"🔗 URL: {result['url']}")
    else:
        print(f"❌ Failed to post tweet: {result.get('error')}")

if __name__ == "__main__":
    main()
