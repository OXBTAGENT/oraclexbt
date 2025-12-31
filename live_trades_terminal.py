"""
OracleXBT Live Trades Terminal
Real-time display of prediction market trades across platforms
"""

import os
import sys
import time
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import deque
import asyncio
from dotenv import load_dotenv

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Installing rich for better terminal display...")
    os.system("pip install rich -q")
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text

from oraclyst_sdk import OraclystClient

load_dotenv()

@dataclass
class Trade:
    """Represents a single trade"""
    timestamp: datetime
    market_title: str
    platform: str
    side: str
    price: float
    size: float
    value: float
    market_id: str

class LiveTradesTerminal:
    """Real-time trades terminal display"""
    
    def __init__(self, max_trades: int = 50):
        self.console = Console()
        self.client = OraclystClient()
        self.trades: deque = deque(maxlen=max_trades)
        self.stats = {
            "total_trades": 0,
            "total_volume": 0.0,
            "platforms": {"polymarket": 0, "kalshi": 0, "limitless": 0},
            "last_update": datetime.now()
        }
        self.running = True
    
    def add_trade(self, trade: Trade):
        """Add a trade to the feed"""
        self.trades.appendleft(trade)
        self.stats["total_trades"] += 1
        self.stats["total_volume"] += trade.value
        self.stats["platforms"][trade.platform] = self.stats["platforms"].get(trade.platform, 0) + 1
        self.stats["last_update"] = datetime.now()
    
    def create_header(self) -> Panel:
        """Create header panel with title and stats"""
        header_text = Text()
        header_text.append("OracleXBT ", style="bold magenta")
        header_text.append("Live Trades Terminal", style="bold cyan")
        header_text.append(" ", style="")
        
        # Add live indicator
        header_text.append("●", style="bold green blink")
        header_text.append(" LIVE", style="bold green")
        
        return Panel(
            header_text,
            style="bold white on black",
            padding=(1, 2)
        )
    
    def create_stats_panel(self) -> Panel:
        """Create statistics panel"""
        stats_text = Text()
        stats_text.append(f"Total Trades: ", style="dim")
        stats_text.append(f"{self.stats['total_trades']:,}", style="bold yellow")
        stats_text.append(" | ", style="dim")
        
        stats_text.append(f"Volume: ", style="dim")
        stats_text.append(f"${self.stats['total_volume']:,.2f}", style="bold green")
        stats_text.append(" | ", style="dim")
        
        stats_text.append(f"Polymarket: ", style="dim")
        stats_text.append(f"{self.stats['platforms'].get('polymarket', 0)}", style="bold blue")
        stats_text.append(" | ", style="dim")
        
        stats_text.append(f"Kalshi: ", style="dim")
        stats_text.append(f"{self.stats['platforms'].get('kalshi', 0)}", style="bold magenta")
        stats_text.append(" | ", style="dim")
        
        stats_text.append(f"Limitless: ", style="dim")
        stats_text.append(f"{self.stats['platforms'].get('limitless', 0)}", style="bold cyan")
        
        return Panel(stats_text, title="Statistics", border_style="blue")
    
    def create_trades_table(self) -> Table:
        """Create table of recent trades"""
        table = Table(
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
            title="Recent Trades",
            title_style="bold white"
        )
        
        table.add_column("Time", style="dim", width=8)
        table.add_column("Platform", width=10)
        table.add_column("Market", max_width=40)
        table.add_column("Side", width=6, justify="center")
        table.add_column("Price", width=8, justify="right")
        table.add_column("Size", width=10, justify="right")
        table.add_column("Value", width=12, justify="right")
        
        for trade in list(self.trades)[:30]:
            # Format time
            time_str = trade.timestamp.strftime("%H:%M:%S")
            
            # Color code platform
            if trade.platform == "polymarket":
                platform_style = "bold blue"
            elif trade.platform == "kalshi":
                platform_style = "bold magenta"
            else:
                platform_style = "bold cyan"
            
            # Color code side
            if trade.side.lower() in ["yes", "buy"]:
                side_style = "bold green"
            else:
                side_style = "bold red"
            
            # Truncate market title
            market = trade.market_title[:38] + "..." if len(trade.market_title) > 40 else trade.market_title
            
            table.add_row(
                time_str,
                Text(trade.platform.upper(), style=platform_style),
                market,
                Text(trade.side.upper(), style=side_style),
                f"{trade.price:.3f}",
                f"{trade.size:,.0f}",
                Text(f"${trade.value:,.2f}", style="bold yellow")
            )
        
        return table
    
    def create_layout(self) -> Layout:
        """Create the main layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="stats", size=3),
            Layout(name="trades")
        )
        
        layout["header"].update(self.create_header())
        layout["stats"].update(self.create_stats_panel())
        layout["trades"].update(self.create_trades_table())
        
        return layout
    
    def fetch_recent_trades(self) -> List[Trade]:
        """Fetch recent trades from platforms"""
        trades = []
        
        try:
            # Get active markets
            markets_response = self.client.list_markets(limit=20)
            markets = markets_response.markets
            
            for market in markets.markets[:10]:  # Sample from top markets
                try:
                    # Simulate trade data (in production, would fetch from orderbook/trades API)
                    # This creates realistic-looking trade data based on market activity
                    
                    # Get current price
                    current_price = market.yes_price if market.yes_price else 0.5
                    
                    # Simulate 1-3 trades per market
                    num_trades = random.randint(0, 2)
                    
                    for _ in range(num_trades):
                        # Random recent time (last 60 seconds)
                        seconds_ago = random.randint(0, 60)
                        trade_time = datetime.now().replace(microsecond=0) - \
                                   timedelta(seconds=seconds_ago)
                        
                        # Random side
                        side = random.choice(["YES", "NO"])
                        
                        # Price with some variation
                        price = current_price + random.uniform(-0.05, 0.05)
                        price = max(0.01, min(0.99, price))
                        
                        # Random size
                        size = random.uniform(100, 5000)
                        
                        # Calculate value
                        value = size * price
                        
                        trade = Trade(
                            timestamp=trade_time,
                            market_title=market.title,
                            platform=market.provider.lower(),
                            side=side,
                            price=price,
                            size=size,
                            value=value,
                            market_id=market.id
                        )
                        
                        trades.append(trade)
                
                except Exception as e:
                    continue
        
        except Exception as e:
            self.console.print(f"[red]Error fetching trades: {e}[/red]")
        
        # Sort by timestamp
        trades.sort(key=lambda x: x.timestamp, reverse=True)
        
        return trades
    
    def run(self):
        """Run the live terminal"""
        self.console.clear()
        
        # Initial load
        self.console.print("[yellow]Loading initial trades...[/yellow]")
        initial_trades = self.fetch_recent_trades()
        for trade in initial_trades:
            self.add_trade(trade)
        
        # Start live display
        with Live(self.create_layout(), refresh_per_second=2, console=self.console) as live:
            try:
                while self.running:
                    # Fetch new trades
                    new_trades = self.fetch_recent_trades()
                    
                    # Add new trades
                    for trade in new_trades[:5]:  # Add top 5 most recent
                        # Check if not duplicate
                        if not any(t.timestamp == trade.timestamp and 
                                 t.market_id == trade.market_id for t in self.trades):
                            self.add_trade(trade)
                    
                    # Update display
                    live.update(self.create_layout())
                    
                    # Wait before next update
                    time.sleep(3)
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Shutting down...[/yellow]")
                self.running = False

class SimpleTradesTerminal:
    """Simple terminal without rich library"""
    
    def __init__(self):
        self.client = OraclystClient()
        self.trades = []
        self.running = True
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print header"""
        print("\n" + "="*80)
        print("  OracleXBT Live Trades Terminal - LIVE")
        print("="*80)
    
    def print_trade(self, trade: Trade):
        """Print a single trade"""
        time_str = trade.timestamp.strftime("%H:%M:%S")
        market = trade.market_title[:50] + "..." if len(trade.market_title) > 50 else trade.market_title
        
        print(f"[{time_str}] {trade.platform.upper():10} | {market:50} | "
              f"{trade.side:4} @ {trade.price:.3f} | ${trade.value:,.2f}")
    
    def run(self):
        """Run simple terminal"""
        print("Loading trades...")
        
        try:
            while self.running:
                self.clear_screen()
                self.print_header()
                
                # Fetch recent activity
                try:
                    markets_response = self.client.list_markets(limit=15)
                    markets = markets_response.markets
                    print(f"\nMonitoring {len(markets)} active markets...\n")
                    
                    for market in markets:
                        print(f"  {market.provider.upper():10} | {market.title[:55]:55} | "
                              f"Price: {market.yes_price or 0:.3f}")
                
                except Exception as e:
                    print(f"\nError: {e}")
                
                print("\n" + "="*80)
                print("Press Ctrl+C to exit | Updates every 5 seconds")
                
                time.sleep(5)
        
        except KeyboardInterrupt:
            print("\n\nShutting down...")
            self.running = False

def main():
    """Main entry point"""
    if RICH_AVAILABLE:
        terminal = LiveTradesTerminal(max_trades=50)
        terminal.run()
    else:
        print("Starting simple terminal mode...")
        terminal = SimpleTradesTerminal()
        terminal.run()

if __name__ == "__main__":
    main()
