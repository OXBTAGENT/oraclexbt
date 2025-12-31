# Live Trades Terminal

Real-time display of prediction market trades across Polymarket, Kalshi, and Limitless.

## Features

- Live streaming trade feed with beautiful terminal UI
- Color-coded platforms (Polymarket, Kalshi, Limitless)
- Real-time statistics (total trades, volume, platform breakdown)
- Trade details: timestamp, market, side, price, size, value
- Auto-updating display (1-3 second refresh)

## Quick Start

```bash
# Run demo version (simulated data)
python3 live_trades_demo.py

# Run with real API (when available)
python3 live_trades_terminal.py
```

## Display

```
╭──────────────────────────────────────────────────────────╮
│  OracleXBT Live Trades Terminal ● LIVE (Demo Mode)      │
╰──────────────────────────────────────────────────────────╯

╭──────────────── Statistics ────────────────╮
│ Total Trades: 41 | Volume: $46,972.57     │
│ Polymarket: 16 | Kalshi: 14 | Limitless: 11│
╰────────────────────────────────────────────╯

┏━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━┳━━━━━┳━━━━━━┳━━━━━━━┓
┃ Time  ┃ Platform ┃ Market  ┃Side┃Price┃ Size ┃ Value ┃
┡━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━╇━━━━━╇━━━━━━╇━━━━━━━┩
│ 12:34 │ POLYMARKET│ Bitcoin...│YES │0.67 │2,340 │$1,568│
│ 12:33 │ KALSHI   │ Election..│NO  │0.48 │1,250 │$600  │
│ 12:32 │ LIMITLESS│ AGI 2027..│YES │0.23 │3,100 │$713  │
└───────┴──────────┴─────────┴────┴─────┴──────┴───────┘
```

## Features

### Color Coding

- **Platforms**:
  - Polymarket: Blue
  - Kalshi: Magenta
  - Limitless: Cyan

- **Trade Sides**:
  - YES/BUY: Green
  - NO/SELL: Red

- **Values**: Yellow

### Live Updates

- Generates 1-3 new trades every 1-3 seconds
- Displays up to 30 most recent trades
- Tracks cumulative statistics
- Real-time volume and trade count

### Sample Markets

The demo includes realistic markets:
- Presidential Election 2024
- Bitcoin price predictions
- AI/AGI timeline
- Economic indicators
- Sports predictions
- Tech stock forecasts

## Requirements

```bash
pip install rich
```

## Controls

- **Ctrl+C**: Exit the terminal

## Use Cases

### Development & Testing
- Test trading strategies with simulated data
- Validate UI/UX for live feeds
- Demo the terminal capabilities

### Monitoring
- Watch market activity in real-time
- Track trade volume across platforms
- Identify high-activity markets

### Integration
- Base for building trading alerts
- Feed data to analytics dashboard
- Monitor for arbitrage opportunities

## Customization

### Add Markets

Edit `SAMPLE_MARKETS` in `live_trades_demo.py`:

```python
SAMPLE_MARKETS = [
    {"title": "Your market title", "platform": "polymarket", "price": 0.50},
    # Add more...
]
```

### Adjust Update Speed

Change refresh timing:

```python
# In run() method
time.sleep(random.uniform(1, 3))  # Adjust min/max seconds
```

### Change Display Limit

```python
terminal = LiveTradesTerminal(max_trades=100)  # Show up to 100 trades
```

## Real API Integration

To connect with real market data (when Oraclyst API is available):

```python
# In fetch_recent_trades()
markets_response = self.client.list_markets(limit=20)
for market in markets_response.markets:
    # Process real market data
    # Fetch actual trades from orderbook/trades endpoint
```

## Tips

- Keep terminal window large for best display
- Watch for high-value trades (bright yellow)
- Monitor platform distribution for market sentiment
- Track volume trends over time

## Coming Soon

- WebSocket support for real-time data
- Trade filtering by market/platform
- Historical trade replay
- Export to CSV/JSON
- Trade alerts and notifications
- Integration with OracleXBT trading terminal

## Related

- `trading_terminal.py` - Execute trades
- `oracle_trading_manager.py` - Autonomous trading
- `website/index.html` - Web interface
