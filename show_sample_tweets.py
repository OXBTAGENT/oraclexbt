#!/usr/bin/env python3
"""Generate sample tweets - direct prompts without tools"""

from agent import PredictionMarketAgent

print("=" * 70)
print("OracleXBT Sample Tweet Generation")
print("=" * 70)
print("\nGenerating 10 sample tweets in trained style...\n")

agent = PredictionMarketAgent()

# Prompts that don't require external data
prompts = [
    "Write one tweet about prediction market trading patterns. Professional analyst tone, under 280 chars, no emojis, no tools needed - just your knowledge.",
    "Compose one tweet explaining arbitrage in prediction markets. Expert voice, under 280 chars, no emojis.",
    "Write one tweet about Polymarket vs Kalshi differences. Market expert tone, under 280 chars, no emojis.",
    "Create one tweet about weekend trading volume patterns. Data analyst voice, under 280 chars, no emojis.",  
    "Write one tweet about election market volatility patterns. Professional tone, under 280 chars, no emojis.",
    "Compose one tweet about crypto prediction markets. Expert analysis, under 280 chars, no emojis.",
    "Write one tweet about liquidity in prediction markets. Professional voice, under 280 chars, no emojis.",
    "Create one tweet about market-making strategies. Expert tone, under 280 chars, no emojis.",
    "Write one tweet about price discovery in prediction markets. Analyst voice, under 280 chars, no emojis.",
    "Compose one tweet about risk management in prediction trading. Professional tone, under 280 chars, no emojis."
]

tweets = []
for i, prompt in enumerate(prompts, 1):
    print(f"[{i}/10] Generating...")
    try:
        response = agent.chat(prompt)
        tweet = response.strip().strip('"').strip("'")
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        tweets.append(tweet)
        print(f"✓ Done ({len(tweet)} chars)\n")
    except Exception as e:
        tweet = f"[Error: {str(e)[:50]}]"
        tweets.append(tweet)
        print(f"✗ Error\n")

print("=" * 70)
print("GENERATED SAMPLE TWEETS")
print("=" * 70)

for i, tweet in enumerate(tweets, 1):
    print(f"\nTweet {i} ({len(tweet)} chars):")
    print("-" * 70)
    print(tweet)

print("\n" + "=" * 70)
print(f"Generated {len(tweets)} tweets")
print("=" * 70)
