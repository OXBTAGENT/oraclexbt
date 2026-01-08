#!/usr/bin/env python3
"""AI-powered tweet generator using trained agent"""

import os
from datetime import datetime
from agent.agent import PredictionMarketAgent
from agent.twitter_tools import TwitterTools
import tweepy

# Initialize Twitter client
print("🔧 Fetching recent tweets to avoid duplication...")
twitter = TwitterTools()

recent_tweets = []
try:
    # Get user's own recent tweets
    client = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN")
    )
    
    # Get authenticated user's ID
    me = client.get_me()
    user_id = me.data.id
    
    # Fetch recent tweets from timeline
    response = client.get_users_tweets(user_id, max_results=10, tweet_fields=['created_at'])
    
    if response.data:
        recent_tweets = [tweet.text for tweet in response.data]
        print(f"✓ Found {len(recent_tweets)} recent tweets\n")
except Exception as e:
    print(f"⚠️  Could not fetch recent tweets: {e}\n")

# Initialize agent
print("🤖 Initializing AI agent...")
agent = PredictionMarketAgent()

# Build context with recent tweets
tweet_context = ""
if recent_tweets:
    tweet_context = "\n\nRECENT TWEETS YOU ALREADY POSTED (DO NOT REPEAT THESE TOPICS OR PHRASES):\n"
    for i, t in enumerate(recent_tweets[:5], 1):
        tweet_context += f"{i}. {t}\n"

# Generate tweet using AI with retry logic
print("💭 Generating unique tweet content...")

max_attempts = 3
tweet = None

for attempt in range(max_attempts):
    prompt = f"""Generate a single tweet about prediction markets. Use your expertise and knowledge. 
Focus on one specific insight - could be about market patterns, platform features, trading strategies, 
or current market dynamics. Be specific with numbers and data where relevant. 

CRITICAL LENGTH REQUIREMENT: Your tweet MUST be 270 characters or less. Complete your thought within this limit.
Write a complete sentence - do not let it trail off. Make it concise and impactful.

Do NOT use any emojis. Do NOT use external tools. Just write the tweet based on your knowledge.

CRITICAL: Review your recent tweets below and ensure you generate COMPLETELY DIFFERENT content.
DO NOT repeat the same topics, themes, or concepts. Choose a totally different angle.{tweet_context}

Generate a NEW tweet on a DIFFERENT topic now:"""

    response = agent.chat(prompt)
    candidate = response.strip()
    
    if len(candidate) <= 280:
        tweet = candidate
        break
    else:
        print(f"⚠️  Attempt {attempt + 1}: Tweet too long ({len(candidate)} chars), regenerating...")

if tweet is None:
    # Last resort: truncate cleanly at sentence boundary
    tweet = response.strip()
    if len(tweet) > 280:
        # Try to cut at last period, exclamation, or question mark before 277 chars
        for char in ['. ', '! ', '? ']:
            last_punct = tweet[:277].rfind(char)
            if last_punct > 200:  # Only if we have substantial content
                tweet = tweet[:last_punct + 1]
                break
        else:
            tweet = tweet[:277] + "..."

print(f"\n📝 Generated Tweet: {tweet}")
print(f"📏 Length: {len(tweet)} characters\n")

# Initialize Twitter tools
print("🔧 Initializing Twitter client...")
twitter = TwitterTools()

if not twitter.is_available:
    print("❌ Twitter not configured")
    exit(1)

print("✓ Twitter ready\n")

# Post tweet
print("📤 Posting tweet...")
try:
    result = twitter.post_tweet(tweet)
    
    if result.get("success"):
        print(f"\n✅ SUCCESS! Tweet posted!")
        if "url" in result:
            print(f"🔗 {result['url']}")
        print(f"\n{result}")
    else:
        print(f"\n❌ Failed: {result.get('error')}")
        print(f"Full result: {result}")
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()
