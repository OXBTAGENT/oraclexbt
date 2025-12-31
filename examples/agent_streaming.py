#!/usr/bin/env python3
"""
Example: Streaming responses from the Prediction Market Agent.

Demonstrates how to use streaming for real-time output,
useful for long analysis tasks.
"""

import os
from agent import PredictionMarketAgent


def main():
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable")
        return
    
    with PredictionMarketAgent() as agent:
        print("🔮 Streaming market analysis...\n")
        print("-" * 50)
        
        # Stream a complex analysis
        query = """
        Give me a comprehensive market briefing:
        1. What are the 3 most active markets right now?
        2. Any significant price movements in the last 24 hours?
        3. What categories are seeing the most trading activity?
        """
        
        for chunk in agent.chat_stream(query):
            print(chunk, end="", flush=True)
        
        print("\n" + "-" * 50)
        print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
