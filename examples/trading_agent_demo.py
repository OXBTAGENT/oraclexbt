"""
Example: OracleXBT Trading Agent
Demonstrates autonomous prediction market trading with the agent
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from agent import PredictionMarketAgent
try:
    from agent.branding import print_logo
except ImportError:
    def print_logo():
        print("🌈 OracleXBT")

load_dotenv()

def main():
    """Run OracleXBT trading agent demo"""
    print_logo()
    print("\n🎮 OracleXBT Trading Agent - Autonomous Trading Demo\n")
    
    # Initialize agent with trading tools enabled
    agent = PredictionMarketAgent(enable_twitter=False)
    
    print("="*70)
    print("Agent initialized with trading capabilities")
    print("="*70)
    
    # Demo scenarios
    scenarios = [
        {
            "name": "Portfolio Check",
            "query": "What's my current portfolio status?",
        },
        {
            "name": "Risk Assessment",
            "query": "Check my risk limits and exposure levels",
        },
        {
            "name": "Market Analysis",
            "query": "Find the top 3 most active prediction markets right now and analyze them for trading opportunities",
        },
        {
            "name": "Arbitrage Scan",
            "query": "Search for arbitrage opportunities across Polymarket and Kalshi. If you find any with >5% spread, explain the opportunity but don't execute yet.",
        },
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"Scenario {i}: {scenario['name']}")
        print('='*70)
        print(f"Query: {scenario['query']}\n")
        
        try:
            response = agent.run(scenario['query'])
            print(f"\n📝 Response:\n{response}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
        
        if i < len(scenarios):
            time.sleep(2)  # Brief pause between scenarios
    
    # Interactive mode
    print("\n" + "="*70)
    print("🎯 Interactive Trading Mode")
    print("="*70)
    print("\nCommands you can try:")
    print("  • 'check portfolio' - View current positions and P&L")
    print("  • 'check risk' - See exposure and limits")
    print("  • 'search for bitcoin markets' - Find BTC prediction markets")
    print("  • 'find arbitrage on election markets' - Scan for opportunities")
    print("  • 'analyze [market_id]' - Deep dive on specific market")
    print("  • 'quit' - Exit")
    print()
    
    while True:
        try:
            user_input = input("💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            print("\n🤔 Agent thinking...\n")
            response = agent.run(user_input)
            print(f"🤖 Agent: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")

def demo_simulated_trade():
    """Demo simulated trading (safe for testing)"""
    print("\n" + "="*70)
    print("🧪 SIMULATED TRADING DEMO (No Real Funds)")
    print("="*70)
    
    from trading_terminal import TradingTerminal
    from decimal import Decimal
    
    terminal = TradingTerminal()
    
    # Simulate finding an opportunity
    print("\n1️⃣ Scanning for opportunities...")
    print("   Found: Trump Election Market")
    print("   Polymarket: 52¢ | Kalshi: 57¢")
    print("   Spread: 5% profit potential")
    
    # Simulate arbitrage trade
    print("\n2️⃣ Executing simulated arbitrage...")
    opportunity = {
        "market_a": {
            "platform": "polymarket",
            "price": 0.52,
            "market_id": "0x1234567890abcdef"
        },
        "market_b": {
            "platform": "kalshi",
            "price": 0.57,
            "market_id": "PRES-2024-TRUMP"
        },
        "spread": 5.0,
        "size": 500
    }
    
    result = terminal.execute_arbitrage(opportunity)
    
    if result:
        print("\n✅ Simulated trade executed!")
        print(f"   Position size: $500")
        print(f"   Expected profit: ${500 * 0.05:.2f}")
    
    # Show portfolio
    print("\n3️⃣ Portfolio after trade:")
    summary = terminal.get_portfolio_summary()
    print(f"   Balance: ${summary['balance']:,.2f}")
    print(f"   Positions: {summary['num_positions']}")
    print(f"   Total Value: ${summary['total_value']:,.2f}")
    
    print("\n💡 Note: This was a simulation. To enable real trading:")
    print("   1. Add wallet addresses to .env")
    print("   2. Fund your wallet with USDC")
    print("   3. Test on testnet first")
    print("   4. Start with small amounts")

if __name__ == "__main__":
    import sys
    
    if "--simulate-trade" in sys.argv:
        demo_simulated_trade()
    else:
        main()
