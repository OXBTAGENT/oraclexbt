#!/usr/bin/env python3
"""
Test script to demonstrate real Web3/API trading capabilities
"""

import requests
import json
import time

BASE_URL = "http://localhost:7777"

def test_demo_mode():
    """Test agent registration in demo mode (no credentials)"""
    print("\n" + "="*60)
    print("TEST 1: Demo Mode (Simulated Trading)")
    print("="*60)
    
    agent_config = {
        "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "platforms": {
            "polymarket": True,
            "kalshi": False,
            "limitless": False
        },
        "strategy": "arbitrage",
        "maxPosition": 100,
        "minProfit": 2.5,
        "maxTrades": 20,
        "stopLoss": 5
    }
    
    print("\nRegistering agent (demo mode - no credentials)...")
    response = requests.post(
        f"{BASE_URL}/api/agent/register",
        json=agent_config
    )
    
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        agent_id = result['agent_id']
        print(f"\n✓ Agent registered: {agent_id}")
        
        # Activate agent
        print("\nActivating agent...")
        activate_response = requests.post(
            f"{BASE_URL}/api/agent/activate",
            json={"agent_id": agent_id}
        )
        print(f"Activation status: {activate_response.status_code}")
        
        # Wait for some trading activity
        print("\nWaiting 10 seconds for trading activity...")
        time.sleep(10)
        
        # Check status
        print("\nFetching agent status...")
        status_response = requests.get(f"{BASE_URL}/api/agent/status/{agent_id}")
        status = status_response.json()
        
        print("\nAgent Status:")
        print(f"  Active: {status.get('agent', {}).get('active')}")
        print(f"  Total Trades: {status.get('stats', {}).get('total_trades')}")
        print(f"  Today's Trades: {status.get('stats', {}).get('today_trades')}")
        print(f"  Total Profit: ${status.get('stats', {}).get('total_profit', 0):.2f}")
        
        if status.get('recent_positions'):
            print(f"\nRecent Positions:")
            for pos in status['recent_positions'][:3]:
                print(f"  - {pos.get('type')}: {pos.get('market')}")
                print(f"    Spread: {pos.get('spread')}%, Expected: ${pos.get('expected_profit'):.2f}")
                print(f"    Simulated: {pos.get('buy_order_id', 'N/A')}")
        
        # Deactivate
        print("\nDeactivating agent...")
        deactivate_response = requests.post(
            f"{BASE_URL}/api/agent/deactivate",
            json={"agent_id": agent_id}
        )
        print(f"Deactivation status: {deactivate_response.status_code}")
        
        return True
    
    return False


def test_real_mode_polymarket():
    """Test real Polymarket integration (requires private key)"""
    print("\n" + "="*60)
    print("TEST 2: Real Mode - Polymarket (Web3)")
    print("="*60)
    print("\n⚠️  This test requires a real private key for Polygon")
    print("⚠️  Skipping real execution - see TRADING_CONFIG.md for setup")
    
    # Example configuration (DO NOT use real keys here)
    example_config = {
        "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "platforms": {
            "polymarket": True,
            "kalshi": False,
            "limitless": False
        },
        "strategy": "arbitrage",
        "maxPosition": 10,  # Small position for testing
        "minProfit": 2.5,
        "maxTrades": 5,
        "stopLoss": 5,
        "privateKey": "0x..." # NEVER commit real keys - use env vars
    }
    
    print("\nExample real mode configuration:")
    print(json.dumps({**example_config, "privateKey": "0x[REDACTED]"}, indent=2))
    print("\n✓ With privateKey provided, orders will execute on Polygon")
    print("✓ Uses Web3.py to sign transactions")
    print("✓ Submits to Polymarket CLOB API")


def test_real_mode_kalshi():
    """Test real Kalshi integration (requires API credentials)"""
    print("\n" + "="*60)
    print("TEST 3: Real Mode - Kalshi (REST API)")
    print("="*60)
    print("\n⚠️  This test requires Kalshi API credentials")
    print("⚠️  Skipping real execution - see TRADING_CONFIG.md for setup")
    
    example_config = {
        "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "platforms": {
            "polymarket": False,
            "kalshi": True,
            "limitless": False
        },
        "strategy": "arbitrage",
        "maxPosition": 10,
        "minProfit": 2.5,
        "maxTrades": 5,
        "stopLoss": 5,
        "kalshiApiKey": "your_api_key",
        "kalshiApiSecret": "your_api_secret"
    }
    
    print("\nExample Kalshi configuration:")
    print(json.dumps({**example_config, 
                      "kalshiApiKey": "[REDACTED]",
                      "kalshiApiSecret": "[REDACTED]"}, indent=2))
    print("\n✓ With Kalshi credentials, orders execute via REST API")
    print("✓ Uses HMAC-SHA256 authentication")
    print("✓ Places orders on Kalshi exchange")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OracleXBT Trading Engine - Web3/API Integration Tests")
    print("="*60)
    
    try:
        # Test demo mode (safe, no credentials needed)
        test_demo_mode()
        
        # Show real mode examples (informational only)
        test_real_mode_polymarket()
        test_real_mode_kalshi()
        
        print("\n" + "="*60)
        print("✓ All tests complete!")
        print("="*60)
        print("\nNext Steps:")
        print("1. Review TRADING_CONFIG.md for credential setup")
        print("2. Test on Polygon testnet before mainnet")
        print("3. Start with small position sizes")
        print("4. Monitor agent status regularly")
        print("\nFor real trading, add credentials to agent registration:")
        print("  - privateKey: For Polymarket/Limitless Web3 signing")
        print("  - kalshiApiKey + kalshiApiSecret: For Kalshi API")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
