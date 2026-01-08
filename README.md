<div align="center">
  <img src="assets/banner.png" alt="OracleXBT Banner" width="100%">
</div>

<br>

# OracleXBT

AI-powered prediction market intelligence platform with cross-chain trading capabilities.

## 📁 Project Structure

```
oraclexbt/
├── agent/              # AI agent core functionality
├── blockchain/         # Smart contract interfaces
├── examples/           # Usage examples
├── oraclyst_sdk/      # Prediction market SDK
├── bin/               # Executable scripts and tools
├── scripts/           # Setup and automation scripts
├── docs/              # Documentation
├── requirements-*.txt # Dependencies
└── README.md          # This file
```

## 🚀 Quick Start

### Installation

```bash
# Install trading dependencies
pip install -r requirements-trading.txt

# Install automation dependencies
pip install -r requirements-automation.txt
```

### Trading Terminal

Run the live trading terminal:

```bash
python bin/trading_terminal.py
```

### Web Dashboard

Start the comprehensive market intelligence dashboard:

```bash
python dashboard.py
```
Access the dashboard at http://localhost:8080

### Autonomous Agent

Run the fully automated tweeting and trading agent:

```bash
# Run with 10-minute tweet interval
export PYTHONPATH=$PYTHONPATH:$(pwd)
python bin/oracle_automation.py --hourly-interval 600
```

## 📚 Documentation
- [Agent Capabilities & Specs](docs/AGENT_CAPABILITIES.md) - **NEW**
- [Trading System Guide](docs/TRADING_SYSTEM.md)
- [Automation Guide](docs/AUTOMATION_GUIDE.md)
- [Trading Terminal](docs/TRADING_TERMINAL.md)
- [Live Trades Terminal](docs/LIVE_TRADES_TERMINAL.md)
- [Persistent Service Setup](docs/PERSISTENT_SERVICE.md)

## 🔧 Features

- **Cross-Chain Trading**: Execute trades across Polygon, Ethereum, and Arbitrum
- **AI Agent**: Intelligent market analysis and autonomous trading
- **Risk Management**: Position limits, exposure caps, and drawdown protection
- **Live Data Terminal**: Real-time market data visualization
- **Twitter Integration**: Automated social media updates
- **Prediction Market SDK**: Unified API for Polymarket, Kalshi, and Limitless

## 🛠️ SDK Usage

```python
from oraclyst_sdk import OraclystClient

# Create client
client = OraclystClient()

# List markets
markets = client.list_markets(limit=10)
for market in markets.data:
    print(f"{market.title}: Yes {market.yes_price:.1%}")

# Get specific market
market = client.get_market("pm-551963")
print(f"Volume: {market.volume}")
```

## 🤖 AI Agent

The AI agent provides intelligent market analysis and autonomous trading capabilities.
It autonomously scans prediction markets, identifies arbitrage, and engages on social media.

```bash
# Run the autonomous agent loop
python bin/oracle_automation.py
```

## 📊 Trading Terminal

Launch the full trading terminal with risk management:

```bash
python bin/trading_terminal.py
```

Features:
- Multi-chain execution
- Position tracking
- Risk controls
- Portfolio management

## 🌐 Live Market Data

Start the web server for live market data:

```bash
python bin/api_server.py
```

Visit http://localhost:7777 for real-time trades display.

## ⚙️ Setup Scripts

```bash
# Setup trading environment
./scripts/setup_trading.sh

# Setup persistent service (auto-start)
./scripts/setup_persistent.sh

# Start automation
./scripts/start_automation.sh
```

## 📖 Examples

Check the `examples/` directory for:
- Basic SDK usage
- Async operations
- Trading agent demos
- Twitter integration
- Market monitoring

## 📝 License

MIT License - see LICENSE file for details.

## 🔗 Links

- GitHub: https://github.com/OXBTAGENT/oraclexbt
- Twitter: [@OracleXBT](https://twitter.com/OracleXBT)
    print(orderbook.total_bid_size)  # 500.0
```

## API Reference

### OraclystClient / AsyncOraclystClient

| Method | Description |
|--------|-------------|
| `list_markets(limit, offset, filters, **kwargs)` | List markets with filtering |
| `iter_all_markets(page_size, filters)` | Iterate all markets (auto-pagination) |
| `get_market(market_id)` | Get single market details |
| `get_price_history(market_id, range)` | Get price history |
| `get_ticker()` | Get live ticker data |
| `get_arb_scanner()` | Get arbitrage opportunities |
| `get_orderbook(venue, token_id)` | Get orderbook data |

### Time Ranges

- `"1m"` - 1 minute
- `"5m"` - 5 minutes
- `"1h"` - 1 hour (default)
- `"4h"` - 4 hours
- `"1d"` - 1 day

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy oraclyst_sdk

# Linting
ruff check oraclyst_sdk
```

## License

MIT License - see LICENSE file for details.

## Links

- [Oraclyst Platform](https://oraclyst.app)
- [API Documentation](https://docs.oraclyst.app)
