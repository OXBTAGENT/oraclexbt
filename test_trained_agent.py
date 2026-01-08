#!/usr/bin/env python3
"""Test the trained agent personality and tweet generation"""

from datetime import datetime
from agent import PredictionMarketAgent
from agent.twitter_tools import TwitterTools

print("🔮 Testing OracleXBT with trained communication style...\n")

# Initialize agent with trained knowledge
agent = PredictionMarketAgent()

# Test prompts to see the trained personality
test_prompts = [
    "Write a quick market insight tweet about prediction markets (under 280 chars)",
    "What's your analysis style?",
]

for prompt in test_prompts:
    print(f"📝 Prompt: {prompt}")
    print(f"💬 Response:")
    
    try:
        response = agent.chat(prompt)
        print(f"{response}\n")
        print(f"Length: {len(response)} chars\n")
        print("="*70 + "\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")

# Now post a tweet with the trained style  
print("\n📤 Posting tweet with trained personality...\n")
twitter = TwitterTools()

if twitter.is_available:
    timestamp = datetime.now().strftime("%H:%M")
    
    # Simple market insight in trained style
    tweet = f"Market pulse check {timestamp}: Monitoring cross-platform price movements. Spread opportunities emerging as weekend liquidity normalizes. Data-driven insights coming all week. #PredictionMarkets"
    
    print(f"Tweet: {tweet}")
    print(f"Length: {len(tweet)} chars\n")
    
    try:
        result = twitter.post_tweet(tweet)
        if result.get('posted'):
            print(f"✅ Tweet posted!")
            print(f"🔗 {result.get('url')}")
        else:
            print(f"❌ Failed: {result}")
    except Exception as e:
        print(f"❌ Error posting: {e}")
else:
    print("❌ Twitter not available")
