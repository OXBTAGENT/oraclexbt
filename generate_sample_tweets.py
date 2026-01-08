#!/usr/bin/env python3
"""Generate sample tweets to review agent's communication style"""

from agent import PredictionMarketAgent
import time

print("=" * 70)
print("🔮 OracleXBT Sample Tweet Generation")
print("=" * 70)
print("\nGenerating 10 tweets in the agent's trained style...")
print("(Professional, data-driven, NO emojis)\n")

# Initialize agent with trained knowledge
agent = PredictionMarketAgent()

# Different tweet prompts to showcase variety
prompts = [
    "Write a tweet about current prediction market trends. Keep it under 280 characters, no emojis.",
    "Compose a tweet about Bitcoin prediction markets. Professional tone, data-focused, under 280 chars, no emojis.",
    "Create a tweet about election betting markets. Market analyst style, under 280 characters, no emojis.",
    "Write a tweet comparing Polymarket and Kalshi platforms. Professional, under 280 chars, no emojis.",
    "Compose a tweet about arbitrage opportunities in prediction markets. Data-driven, under 280 chars, no emojis.",
    "Create a tweet about weekend trading patterns in prediction markets. Analytical tone, under 280 chars, no emojis.",
    "Write a tweet about volatility in political prediction markets. Professional, under 280 chars, no emojis.",
    "Compose a tweet sharing a prediction market insight. Market analyst voice, under 280 chars, no emojis.",
    "Create a tweet about cross-platform price spreads. Data-focused, under 280 chars, no emojis.",
    "Write a tweet about market liquidity observations. Professional tone, under 280 chars, no emojis."
]

tweets = []
for i, prompt in enumerate(prompts, 1):
    print(f"\n[{i}/10] Generating tweet {i}...")
    try:
        response = agent.chat(prompt)
        # Extract just the tweet text (remove any explanations)
        tweet = response.strip().strip('"').strip("'")
        
        # If response is too long, take first sentence or truncate
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        
        tweets.append(tweet)
        print(f"✓ Generated ({len(tweet)} chars)")
        
    except Exception as e:
        tweets.append(f"[Error generating tweet: {e}]")
        print(f"✗ Error: {e}")
    
    # Small delay to avoid rate limits
    time.sleep(2)

print("\n" + "=" * 70)
print("📊 GENERATED TWEETS - REVIEW")
print("=" * 70)

for i, tweet in enumerate(tweets, 1):
    print(f"\n--- Tweet {i} ({len(tweet)} characters) ---")
    print(tweet)
    print()

print("=" * 70)
print(f"✅ Generated {len(tweets)} tweets successfully")
print("Review complete - these showcase the agent's communication style")
print("=" * 70)
