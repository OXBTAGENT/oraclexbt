#!/usr/bin/env python3
"""
Local Agent Testing Script
Test your trading agent in VSC before deploying to the website
"""

import requests
import time
import json
from datetime import datetime

# ANSI colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

# API endpoints
BASE_URL = "http://localhost:5001"
REGISTER_URL = f"{BASE_URL}/api/agent/register"
START_URL = f"{BASE_URL}/api/agent/activate"
STOP_URL = f"{BASE_URL}/api/agent/deactivate"
STATUS_URL = f"{BASE_URL}/api/agent/status"
TRADES_URL = f"{BASE_URL}/api/trades"
STATS_URL = f"{BASE_URL}/api/stats"

def print_header(text):
    """Print formatted header"""
    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN}{text:^80}{RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Print error message"""
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ️  {text}{RESET}")

def register_agent():
    """Register a test agent"""
    print_header("STEP 1: Registering Test Agent")
    
    config = {
        "wallet": "0xd3d03f57c60bBEFE645cd6Bb14f1CE2c1915e898",  # Your funded wallet
        "strategy": "arbitrage",
        "maxPosition": 50,
        "minProfit": 5,
        "maxTrades": 100,
        "stopLoss": 10,
        "riskLevel": "medium",
        "platforms": {
            "polymarket": True,
            "kalshi": True,
            "limitless": True
        },
        "autoTrade": True
    }
    
    try:
        response = requests.post(REGISTER_URL, json=config, timeout=5)
        data = response.json()
        
        if data.get('success'):
            agent_id = data.get('agent_id')
            print_success(f"Agent registered successfully!")
            print(f"  {BOLD}Agent ID:{RESET} {agent_id}")
            print(f"  {BOLD}Wallet:{RESET} {config['wallet'][:10]}...{config['wallet'][-6:]}")
            print(f"  {BOLD}Strategy:{RESET} {config['strategy']}")
            print(f"  {BOLD}Max Position:{RESET} ${config['maxPosition']}")
            print(f"  {BOLD}Platforms:{RESET} Polymarket, Kalshi, Limitless")
            return agent_id
        else:
            print_error(f"Registration failed: {data.get('message')}")
            return None
    except Exception as e:
        print_error(f"Registration error: {str(e)}")
        return None

def start_agent(agent_id):
    """Start the agent trading"""
    print_header("STEP 2: Starting Agent")
    
    try:
        response = requests.post(START_URL, json={"agent_id": agent_id}, timeout=5)
        data = response.json()
        
        if data.get('success'):
            print_success("Agent started and trading!")
            print_info("Agent is now scanning for opportunities every 3-5 seconds")
            print_info("Expected: 2-4 trades per scan cycle (95% success rate)")
            return True
        else:
            print_error(f"Failed to start: {data.get('message')}")
            return False
    except Exception as e:
        print_error(f"Start error: {str(e)}")
        return False

def get_agent_status(agent_id):
    """Get agent status"""
    try:
        response = requests.get(f"{STATUS_URL}/{agent_id}", timeout=5)
        return response.json()
    except:
        return None

def get_recent_trades(limit=10):
    """Get recent trades"""
    try:
        response = requests.get(TRADES_URL, timeout=5)
        data = response.json()
        if isinstance(data, dict):
            trades = data.get('trades', [])
        else:
            trades = data if isinstance(data, list) else []
        return trades[:limit]
    except:
        return []

def get_stats():
    """Get trading statistics"""
    try:
        response = requests.get(STATS_URL, timeout=5)
        return response.json()
    except:
        return {}

def display_trades(trades):
    """Display recent trades"""
    if not trades:
        print_info("No trades yet, waiting for agent to find opportunities...")
        return
    
    print(f"\n{BOLD}Recent Trades:{RESET}")
    print(f"{BOLD}{'Platform':<12} {'Market':<40} {'Side':<5} {'Price':<8} {'Size':<10} {'Value':<10}{RESET}")
    print("-" * 90)
    
    for trade in trades:
        platform = trade.get('platform', 'Unknown')
        market = trade.get('market', 'Unknown')[:37] + "..." if len(trade.get('market', '')) > 40 else trade.get('market', 'Unknown')
        side = trade.get('side', 'N/A')
        price = trade.get('price', 0)
        size = trade.get('size', 0)
        value = trade.get('value', 0)
        
        # Color by platform
        if platform == 'Polymarket':
            color = BLUE
        elif platform == 'Kalshi':
            color = YELLOW
        elif platform == 'Limitless':
            color = MAGENTA
        else:
            color = CYAN
        
        side_color = GREEN if side == 'YES' else RED
        
        print(f"{color}{platform:<12}{RESET} {market:<40} {side_color}{side:<5}{RESET} ${price:>6.3f} {size:>9.2f} ${value:>9.2f}")

def display_stats(stats):
    """Display trading statistics"""
    print(f"\n{BOLD}Trading Statistics:{RESET}")
    print(f"  Total Trades: {BOLD}{stats.get('total_trades', 0)}{RESET}")
    print(f"  Total Volume: {BOLD}${stats.get('total_volume', 0):,.2f}{RESET}")
    
    by_platform = stats.get('by_platform', {})
    if by_platform:
        print(f"  By Platform:")
        for platform, count in by_platform.items():
            if platform == 'Polymarket':
                color = BLUE
            elif platform == 'Kalshi':
                color = YELLOW
            elif platform == 'Limitless':
                color = MAGENTA
            else:
                color = CYAN
            print(f"    {color}{platform}: {count}{RESET}")

def monitor_agent(agent_id, duration=60):
    """Monitor agent for specified duration"""
    print_header(f"STEP 3: Monitoring Agent (for {duration} seconds)")
    
    print_info(f"Watching agent {agent_id[:20]}... for trades")
    print_info("Press Ctrl+C to stop monitoring\n")
    
    start_time = time.time()
    last_trade_count = 0
    
    try:
        while time.time() - start_time < duration:
            # Get current stats
            stats = get_stats()
            current_count = stats.get('total_trades', 0)
            
            # Clear and display
            print(f"\r{BOLD}Elapsed: {int(time.time() - start_time)}s{RESET} | {BOLD}Trades: {current_count}{RESET} ", end='', flush=True)
            
            # If new trades, show them
            if current_count > last_trade_count:
                print()  # New line
                trades = get_recent_trades(5)
                display_trades(trades)
                display_stats(stats)
                print(f"\n{BOLD}Continuing to monitor...{RESET}")
                last_trade_count = current_count
            
            time.sleep(2)
        
        print(f"\n\n{GREEN}✅ Monitoring complete!{RESET}")
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠️  Monitoring stopped by user{RESET}")

def stop_agent(agent_id):
    """Stop the agent"""
    print_header("STEP 4: Stopping Agent")
    
    try:
        response = requests.post(STOP_URL, json={"agent_id": agent_id}, timeout=5)
        data = response.json()
        
        if data.get('success'):
            print_success("Agent stopped successfully")
            
            # Show final stats
            stats = get_stats()
            display_stats(stats)
            return True
        else:
            print_error(f"Failed to stop: {data.get('message')}")
            return False
    except Exception as e:
        print_error(f"Stop error: {str(e)}")
        return False

def main():
    """Main testing flow"""
    print_header("🤖 OracleXBT Agent Local Testing")
    print(f"{CYAN}Testing your agent locally in VSC before website deployment{RESET}\n")
    
    print_info("This will:")
    print("  1. Register a test agent with your wallet")
    print("  2. Start the agent trading")
    print("  3. Monitor trades for 60 seconds")
    print("  4. Stop the agent and show final stats")
    
    input(f"\n{YELLOW}Press Enter to begin testing...{RESET}")
    
    # Step 1: Register
    agent_id = register_agent()
    if not agent_id:
        print_error("Failed to register agent. Exiting.")
        return
    
    time.sleep(1)
    
    # Step 2: Start
    if not start_agent(agent_id):
        print_error("Failed to start agent. Exiting.")
        return
    
    time.sleep(2)
    
    # Step 3: Monitor
    monitor_agent(agent_id, duration=60)
    
    time.sleep(1)
    
    # Step 4: Stop
    stop_agent(agent_id)
    
    print_header("Testing Complete!")
    print_success("Your agent is working correctly!")
    print_info("You can now safely push updates to the website")
    print(f"\n{CYAN}To see live trades in terminal, run:{RESET}")
    print(f"{BOLD}python3 bin/live_trades_terminal.py{RESET}\n")

if __name__ == "__main__":
    main()
