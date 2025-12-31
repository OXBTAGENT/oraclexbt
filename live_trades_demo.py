"""
OracleXBT Live Trades Terminal (Demo Mode)
Real-time display of simulated prediction market trades
"""

import os
import sys
import time
import random
from datetime import datetime, timedelta
from typing import List
from dataclasses import dataclass
from collections import deque

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
except ImportError:
    print("Installing rich...")
    os.system("pip install rich -q")
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text

@dataclass
class Trade:
    timestamp: datetime
    market_title: str
    platform: str
    side: str
    price: float
    size: float
    value: float

class LiveTradesTerminal:
    """Real-time trades terminal with simulated data"""
    
    SAMPLE_MARKETS = [
        {"title": "Will Trump win the 2024 Presidential Election?", "platform": "polymarket", "price": 0.52},
        {"title": "Bitcoin above $100K by March 2026?", "platform": "kalshi", "price": 0.67},
        {"title": "Will AI achieve AGI by 2027?", "platform": "limitless", "price": 0.23},
        {"title": "Democrats win Senate majority in 2026?", "platform": "polymarket", "price": 0.48},
        {"title": "Ethereum above $5K by June 2026?", "platform": "kalshi", "price": 0.58},
        {"title": "US Federal Reserve cuts rates by March 2026?", "platform": "polymarket", "price": 0.71},
        {"title": "SpaceX successfully lands on Mars by 2028?", "platform": "limitless", "price": 0.15},
        {"title": "Will the NY Knicks make the NBA Finals 2026?", "platform": "polymarket", "price": 0.12},
        {"title": "US GDP growth above 3% in Q1 2026?", "platform": "kalshi", "price": 0.45},
        {"title": "Tesla stock above $400 by end of 2026?", "platform": "polymarket", "price": 0.62},
        {"title": "Will ChatGPT-5 be released by June 2026?", "platform": "limitless", "price": 0.78},
        {"title": "Apple Vision Pro sales exceed 5M by 2027?", "platform": "polymarket", "price": 0.35},
        {"title": "Will XRP be classified as a security?", "platform": "kalshi", "price": 0.29},
        {"title": "Super Bowl 2026: Chiefs win", "platform": "polymarket", "price": 0.18},
        {"title": "Inflation above 2.5% by end of Q1 2026?", "platform": "kalshi", "price": 0.66},
    ]
    
    def __init__(self, max_trades: int = 50):
        self.console = Console()
        self.trades: deque = deque(maxlen=max_trades)
        self.stats = {
            "total_trades": 0,
            "total_volume": 0.0,
            "platforms": {"polymarket": 0, "kalshi": 0, "limitless": 0},
            "last_update": datetime.now()
        }
        self.running = True
    
    def generate_trade(self) -> Trade:
        """Generate a simulated trade"""
        market = random.choice(self.SAMPLE_MARKETS)
        
        # Random recent time (last 10 seconds)
        seconds_ago = random.randint(0, 10)
        trade_time = datetime.now().replace(microsecond=0) - timedelta(seconds=seconds_ago)
        
        # Random side
        side = random.choice(["YES", "NO"])
        
        # Price with variation
        price = market["price"] + random.uniform(-0.05, 0.05)
        price = max(0.01, min(0.99, price))
        
        # Random size
        size = random.uniform(100, 5000)
        value = size * price
        
        return Trade(
            timestamp=trade_time,
            market_title=market["title"],
            platform=market["platform"],
            side=side,
            price=price,
            size=size,
            value=value
        )
    
    def add_trade(self, trade: Trade):
        """Add a trade to the feed"""
        self.trades.appendleft(trade)
        self.stats["total_trades"] += 1
        self.stats["total_volume"] += trade.value
        self.stats["platforms"][trade.platform] = self.stats["platforms"].get(trade.platform, 0) + 1
        self.stats["last_update"] = datetime.now()
    
    def create_header(self) -> Panel:
        """Create header panel"""
        header_text = Text()
        header_text.append("OracleXBT ", style="bold magenta")
        header_text.append("Live Trades Terminal", style="bold cyan")
        header_text.append(" ", style="")
        header_text.append("●", style="bold green blink")
        header_text.append(" LIVE", style="bold green")
        header_text.append(" (Demo Mode)", style="dim yellow")
        
        return Panel(header_text, style="bold white on black", padding=(1, 2))
    
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
            time_str = trade.timestamp.strftime("%H:%M:%S")
            
            # Color code platform
            if trade.platform == "polymarket":
                platform_style = "bold blue"
            elif trade.platform == "kalshi":
                platform_style = "bold magenta"
            else:
                platform_style = "bold cyan"
            
            # Color code side
            side_style = "bold green" if trade.side == "YES" else "bold red"
            
            # Truncate market title
            market = trade.market_title[:38] + "..." if len(trade.market_title) > 40 else trade.market_title
            
            table.add_row(
                time_str,
                Text(trade.platform.upper(), style=platform_style),
                market,
                Text(trade.side, style=side_style),
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
    
    def run(self):
        """Run the live terminal"""
        self.console.clear()
        self.console.print("[yellow]Initializing live trades feed...[/yellow]")
        
        # Generate initial trades
        for _ in range(15):
            trade = self.generate_trade()
            self.add_trade(trade)
        
        # Start live display
        with Live(self.create_layout(), refresh_per_second=4, console=self.console) as live:
            try:
                while self.running:
                    # Generate 1-3 new trades every update
                    num_new = random.randint(1, 3)
                    for _ in range(num_new):
                        trade = self.generate_trade()
                        self.add_trade(trade)
                    
                    # Update display
                    live.update(self.create_layout())
                    
                    # Wait before next update (1-3 seconds)
                    time.sleep(random.uniform(1, 3))
            
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Shutting down...[/yellow]")
                self.running = False

def main():
    """Main entry point"""
    terminal = LiveTradesTerminal(max_trades=50)
    terminal.run()

if __name__ == "__main__":
    main()
