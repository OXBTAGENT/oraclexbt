#!/usr/bin/env python3
"""
Example: Building a market monitoring bot.

This example shows how to build a simple bot that:
1. Monitors specific markets
2. Checks for price changes
3. Reports interesting movements
"""

import os
import time
from datetime import datetime
from agent import PredictionMarketAgent


def market_monitor():
    """Simple market monitoring bot."""
    
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable")
        return
    
    print("🤖 Market Monitor Bot Starting...")
    print("=" * 50)
    
    with PredictionMarketAgent() as agent:
        # Initial scan
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running initial market scan...")
        
        response = agent.chat("""
        Do a quick market scan and tell me:
        1. Top 3 markets by 24h volume
        2. Any markets with >10% price change in last 24h
        3. Any new arbitrage opportunities >2% spread
        
        Be concise - just the key facts.
        """)
        print(response)
        
        # Simulated monitoring loop (in practice, you'd run this continuously)
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for updates...")
        
        response = agent.chat("""
        Based on the markets you found, which one seems most likely to 
        see significant price movement soon? Why?
        """)
        print(response)
        
        print("\n" + "=" * 50)
        print("Monitor session complete. In a real bot, this would run continuously.")


if __name__ == "__main__":
    market_monitor()
