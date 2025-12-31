#!/usr/bin/env python3
"""
Example: Twitter/X Integration with the Prediction Market Agent.

This example shows how to use the agent to:
1. Search for prediction market discussions on X
2. Post market insights
3. Engage with the community
"""

import os
from agent import PredictionMarketAgent, AgentConfig


def check_credentials():
    """Check if required credentials are set."""
    llm_ok = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    twitter_ok = all([
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET"),
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    ])
    
    if not llm_ok:
        print("❌ Missing LLM API key (ANTHROPIC_API_KEY or OPENAI_API_KEY)")
        return False
    
    if not twitter_ok:
        print("⚠️  Twitter credentials not fully configured.")
        print("   Set these environment variables for full functionality:")
        print("   - TWITTER_API_KEY")
        print("   - TWITTER_API_SECRET")
        print("   - TWITTER_ACCESS_TOKEN")
        print("   - TWITTER_ACCESS_TOKEN_SECRET")
        print("\n   Agent will work but Twitter posting will be simulated.\n")
    
    return True


def main():
    if not check_credentials():
        return
    
    with PredictionMarketAgent() as agent:
        print("🔮 Prediction Market Agent with Twitter Integration")
        print("=" * 55)
        
        # Check Twitter status
        if agent.twitter_enabled:
            print("✅ Twitter integration: ACTIVE")
        else:
            print("⚠️  Twitter integration: NOT CONFIGURED (compose-only mode)")
        print()
        
        # Example 1: Search Twitter for prediction market discussions
        print("📱 Example 1: Searching X for prediction market discussions")
        print("-" * 55)
        
        response = agent.chat(
            "Search Twitter for recent discussions about Polymarket. "
            "What are people talking about?"
        )
        print(response)
        print()
        
        # Example 2: Compose a tweet about an interesting market
        print("📝 Example 2: Composing a market insight tweet")
        print("-" * 55)
        
        response = agent.chat(
            "Find the most interesting political market right now and "
            "compose a tweet about it. Don't post it yet, just show me the draft."
        )
        print(response)
        print()
        
        # Example 3: Create an arbitrage alert
        print("🚨 Example 3: Composing an arbitrage alert")
        print("-" * 55)
        
        response = agent.chat(
            "Look for any arbitrage opportunities and compose a tweet "
            "alerting followers about the best one you find."
        )
        print(response)
        print()
        
        # Example 4: Check what Polymarket is posting
        print("🏢 Example 4: Checking platform activity")
        print("-" * 55)
        
        response = agent.chat(
            "What has @Polymarket been tweeting about recently? "
            "Summarize their last few posts."
        )
        print(response)
        print()
        
        # Example 5: Full workflow - analyze and post
        print("🚀 Example 5: Full workflow")
        print("-" * 55)
        
        response = agent.chat(
            "Do a quick market scan, find something interesting, "
            "and create a thread (2-3 tweets) analyzing it. "
            "Show me the thread but don't post it."
        )
        print(response)


if __name__ == "__main__":
    main()
