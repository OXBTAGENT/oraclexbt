#!/usr/bin/env python3
"""
Live Trades Terminal Display
Shows real-time trades streaming from OracleXBT trading engine
"""

import requests
import time
import os
from datetime import datetime

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

# Platform colors
PLATFORM_COLORS = {
    'Polymarket': BLUE,
    'Kalshi': YELLOW,
    'Limitless': MAGENTA
}

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')

def format_trade(trade):
    """Format a single trade for display"""
    platform = trade.get('platform', 'Unknown')
    platform_color = PLATFORM_COLORS.get(platform, CYAN)
    
    # Color based on side
    side_color = GREEN if trade.get('side', '').upper() == 'YES' else RED
    
    # Format values - ensure everything is converted to string properly
    time_str = str(trade.get('time', ''))[:8]
    order_id = str(trade.get('order_id', 'N/A'))[:12]
    market = str(trade.get('market', 'Unknown'))[:35]
    side = str(trade.get('side', 'N/A'))
    price = float(trade.get('price', 0))
    size = float(trade.get('size', 0))
    value = float(trade.get('value', 0))
    exec_time = float(trade.get('exec_time', 0))
    spread = float(trade.get('spread', 0))
    
    return f"{DIM}{time_str}{RESET} │ {order_id} │ {platform_color}{platform:10s}{RESET} │ {market:35s} │ {side_color}{side:4s}{RESET} │ ${price:6.3f} │ {size:8.2f} │ ${value:8.2f} │ {exec_time:5.0f}ms │ {spread:5.2f}%"

def display_header():
    """Display table header"""
    print(f"\n{BOLD}{CYAN}{'='*180}{RESET}")
    print(f"{BOLD}{CYAN}  🤖 OracleXBT - LIVE PREDICTION MARKET TRADES (Real-time){RESET}")
    print(f"{BOLD}{CYAN}{'='*180}{RESET}\n")
    print(f"{BOLD}Time     │ Order ID     │ Platform   │ Market                              │ Side │ Price   │ Size     │ Value    │ Exec   │ Spread{RESET}")
    print(f"{DIM}{'─'*180}{RESET}")

def fetch_trades():
    """Fetch latest trades from API"""
    try:
        response = requests.get('http://localhost:5001/api/trades', timeout=2)
        if response.status_code == 200:
            data = response.json()
            # Handle both list and dict responses
            if isinstance(data, dict):
                return data.get('trades', [])
            return data if isinstance(data, list) else []
        return []
    except:
        return []

def fetch_stats():
    """Fetch trading statistics"""
    try:
        response = requests.get('http://localhost:5001/api/stats', timeout=2)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}

def display_stats(stats):
    """Display trading statistics"""
    total_trades = stats.get('total_trades', 0)
    total_volume = stats.get('total_volume', 0)
    by_platform = stats.get('by_platform', {})
    
    print(f"\n{BOLD}{GREEN}📊 Trading Statistics:{RESET}")
    print(f"  Total Trades: {BOLD}{total_trades}{RESET} │ Total Volume: {BOLD}${total_volume:,.2f}{RESET}")
    
    if by_platform:
        print(f"  By Platform: ", end='')
        for platform, count in by_platform.items():
            color = PLATFORM_COLORS.get(platform, CYAN)
            print(f"{color}{platform}: {count}{RESET}  ", end='')
        print()

def main():
    """Main streaming loop"""
    print(f"{BOLD}{GREEN}Starting OracleXBT Live Trades Terminal...{RESET}")
    print(f"{DIM}Connecting to http://localhost:5001{RESET}")
    time.sleep(1)
    
    seen_trades = set()
    trade_count = 0
    
    while True:
        try:
            clear_screen()
            display_header()
            
            # Fetch and display trades
            trades = fetch_trades()
            
            if trades:
                for trade in trades[:25]:  # Show last 25 trades
                    trade_id = f"{trade.get('order_id', '')}{trade.get('time', '')}"
                    if trade_id not in seen_trades:
                        seen_trades.add(trade_id)
                        trade_count += 1
                    
                    print(format_trade(trade))
                
                # Keep seen_trades manageable
                if len(seen_trades) > 1000:
                    seen_trades.clear()
            else:
                print(f"{DIM}  Waiting for trades...{RESET}")
            
            # Display stats
            stats = fetch_stats()
            display_stats(stats)
            
            # Footer
            print(f"\n{DIM}{'─'*180}{RESET}")
            print(f"{DIM}  📡 Live streaming │ Trades seen: {trade_count} │ Refresh: 2s │ Press Ctrl+C to exit{RESET}")
            print(f"{DIM}{'─'*180}{RESET}")
            
            time.sleep(2)  # Update every 2 seconds
            
        except KeyboardInterrupt:
            print(f"\n\n{BOLD}{YELLOW}Stopping live trades stream...{RESET}")
            print(f"{GREEN}Total trades seen: {trade_count}{RESET}\n")
            break
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")
            time.sleep(2)

if __name__ == '__main__':
    main()
