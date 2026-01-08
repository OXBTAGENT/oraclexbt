#!/usr/bin/env python3
"""
Quick Agent Status Checker
Run this anytime to check how your agent is performing
"""

import requests
import json
from datetime import datetime
import os

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

BASE_URL = "http://localhost:5001"

def get_stats():
    """Get trading statistics"""
    try:
        response = requests.get(f"{BASE_URL}/api/stats", timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_trades(limit=10):
    """Get recent trades"""
    try:
        response = requests.get(f"{BASE_URL}/api/trades", timeout=5)
        data = response.json()
        if isinstance(data, dict):
            trades = data.get('trades', [])
        else:
            trades = data if isinstance(data, list) else []
        return trades[:limit]
    except:
        return []

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(BASE_URL, timeout=2)
        return True
    except:
        return False

def display_quick_stats():
    """Display quick stats overview"""
    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN}{'🤖 OracleXBT Agent Status':^80}{RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")
    print(f"{BOLD}Time:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check server
    if not check_server():
        print(f"{RED}❌ Server is not running!{RESET}")
        print(f"{YELLOW}Start server with: python3 bin/api_server.py{RESET}\n")
        return
    
    print(f"{GREEN}✅ Server is running{RESET}\n")
    
    # Get stats
    stats = get_stats()
    
    if stats.get('error'):
        print(f"{RED}❌ Error fetching stats: {stats['error']}{RESET}\n")
        return
    
    # Display stats
    print(f"{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}Trading Statistics{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    print(f"  {BOLD}Total Trades:{RESET} {CYAN}{stats.get('total_trades', 0):,}{RESET}")
    print(f"  {BOLD}Total Volume:{RESET} {CYAN}${stats.get('total_volume', 0):,.2f}{RESET}")
    
    by_platform = stats.get('by_platform', {})
    if by_platform:
        print(f"\n  {BOLD}By Platform:{RESET}")
        for platform, count in sorted(by_platform.items(), key=lambda x: x[1], reverse=True):
            if platform == 'Polymarket':
                color = BLUE
            elif platform == 'Kalshi':
                color = YELLOW
            else:
                color = MAGENTA
            
            percentage = (count / sum(by_platform.values())) * 100 if by_platform else 0
            bar_length = int(percentage / 2)
            bar = '█' * bar_length
            
            print(f"    {color}● {platform:12}{RESET} {count:4} trades {color}{bar}{RESET} {percentage:.1f}%")
    
    # Recent trades
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}Recent Trades (Last 10){RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    trades = get_trades(10)
    
    if not trades:
        print(f"  {YELLOW}No trades yet{RESET}")
    else:
        print(f"{BOLD}  {'Platform':<12} {'Market':<40} {'Side':<5} {'Value':<10}{RESET}")
        print(f"  {'-'*75}")
        
        for trade in trades:
            platform = trade.get('platform', 'Unknown')
            market = trade.get('market', 'Unknown')[:37] + "..." if len(trade.get('market', '')) > 40 else trade.get('market', 'Unknown')
            side = trade.get('side', 'N/A')
            value = trade.get('value', 0)
            
            if platform == 'Polymarket':
                color = BLUE
            elif platform == 'Kalshi':
                color = YELLOW
            else:
                color = MAGENTA
            
            side_color = GREEN if side == 'YES' else RED
            
            print(f"  {color}{platform:<12}{RESET} {market:<40} {side_color}{side:<5}{RESET} ${value:>8.2f}")
    
    # Check logs
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}Logs{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")
    
    log_dir = "logs"
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
        if log_files:
            latest_log = sorted(log_files)[-1]
            print(f"  Latest log: {CYAN}{log_dir}/{latest_log}{RESET}")
            
            # Show last few lines
            log_path = f"{log_dir}/{latest_log}"
            with open(log_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"\n  {BOLD}Last 5 log entries:{RESET}")
                    for line in lines[-5:]:
                        print(f"  {line.rstrip()}")
        else:
            print(f"  {YELLOW}No log files found{RESET}")
    else:
        print(f"  {YELLOW}No logs directory{RESET}")
    
    print(f"\n{BOLD}{'='*80}{RESET}\n")
    print(f"{GREEN}✅ Agent is operational{RESET}")
    print(f"{CYAN}Run this script anytime to check status{RESET}\n")

if __name__ == "__main__":
    display_quick_stats()
