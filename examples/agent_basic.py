#!/usr/bin/env python3
"""
Example: Basic usage of the Prediction Market Agent.

This example shows how to use the agent programmatically
for various prediction market research tasks.
"""

import os
from agent import PredictionMarketAgent, AgentConfig


def main():
    # Ensure API key is set
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable")
        return
    
    # Create agent with default config (uses Anthropic)
    with PredictionMarketAgent() as agent:
        
        # Example 1: Search for markets
        print("=" * 60)
        print("Example 1: Searching for political markets")
        print("=" * 60)
        
        response = agent.chat(
            "Find me the top 5 most active political prediction markets right now. "
            "Show me their current prices and trading volumes."
        )
        print(response)
        print()
        
        # Example 2: Deep dive into a specific topic
        print("=" * 60)
        print("Example 2: Deep dive into crypto markets")
        print("=" * 60)
        
        response = agent.chat(
            "What prediction markets exist for Bitcoin price? "
            "Analyze the one with the most volume."
        )
        print(response)
        print()
        
        # Example 3: Find arbitrage opportunities
        print("=" * 60)
        print("Example 3: Looking for arbitrage")
        print("=" * 60)
        
        response = agent.chat(
            "Are there any arbitrage opportunities right now? "
            "Look for the same events priced differently on Polymarket vs Kalshi."
        )
        print(response)
        print()
        
        # Example 4: Follow-up question (uses context)
        print("=" * 60)
        print("Example 4: Follow-up question (context-aware)")
        print("=" * 60)
        
        response = agent.chat(
            "Can you explain the risks of the first opportunity you found?"
        )
        print(response)


if __name__ == "__main__":
    main()
