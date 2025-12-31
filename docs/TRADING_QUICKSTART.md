# 🎮 OracleXBT Trading System - Quick Start

## What You Just Built

You now have a complete **cross-chain prediction market trading system** that enables OracleXBT to:

- ✅ Execute trades on Polymarket (Polygon), Kalshi, and other platforms
- ✅ Detect and execute arbitrage opportunities automatically
- ✅ Manage risk with position limits and drawdown protection
- ✅ Track portfolio, positions, and P&L in real-time
- ✅ Operate autonomously with scheduled scans
- ✅ Integrate with existing agent for intelligent trading

## 📁 New Files

```
trading_terminal.py          # Main trading engine
blockchain/
  ├── contracts.py            # Smart contract interfaces
  └── __init__.py
agent/
  └── trading_tools.py        # Trading tools for agent
oracle_trading_manager.py    # Autonomous trading scheduler
examples/
  └── trading_agent_demo.py  # Interactive demo
test_trading_terminal.py     # Test suite
setup_trading.sh             # Setup script
requirements-trading.txt     # Dependencies
TRADING_TERMINAL.md          # Full documentation
```

## 🚀 Quick Start

### 1. Setup (1 minute)

```bash
# Run automated setup
bash setup_trading.sh

# Or manual install
pip install web3 eth-account eth-utils hexbytes
```

### 2. Configure (Optional for testing)

Trading works in **simulation mode** by default. To enable real trading:

```bash
# Add to .env
POLYGON_WALLET_ADDRESS=0xYourAddress
POLYGON_PRIVATE_KEY=your_key_here  # ⚠️ NEVER commit!

# Risk settings (already configured with safe defaults)
STARTING_BALANCE=10000
MAX_POSITION_SIZE=1000
MAX_TOTAL_EXPOSURE=5000
MAX_DRAWDOWN=0.20
```

### 3. Test It

```bash
# Run test suite
python3 test_trading_terminal.py

# Try interactive demo
python3 examples/trading_agent_demo.py

# Simulate a trade
python3 examples/trading_agent_demo.py --simulate-trade
```

## 💡 Usage Modes

### Mode 1: Interactive Terminal

Launch manual trading interface:

```bash
python3 trading_terminal.py
```

Commands:
- `1` - View portfolio
- `2` - Place trade
- `3` - Execute arbitrage
- `4` - View positions
- `5` - Close position
- `6` - Save state

### Mode 2: Agent-Powered Trading

Let the AI agent analyze and execute trades:

```bash
python3 examples/trading_agent_demo.py
```

Try commands like:
- "Check my portfolio"
- "Find arbitrage opportunities on election markets"
- "Analyze the top Bitcoin prediction markets"
- "What's my risk exposure?"

### Mode 3: Autonomous Trading

Set up automated trading with scheduled scans:

```bash
python3 oracle_trading_manager.py
```

Runs automatically:
- 🔄 Arbitrage scans every 30 minutes
- 📊 Portfolio health checks every 2 hours
- 📈 Market analysis at 9am and 3pm daily

**Enable autonomous trading:**
```bash
# Add to .env
ENABLE_AUTONOMOUS_TRADING=true
MAX_DAILY_TRADES=5
```

## 🛡️ Safety Features

Your trading system has built-in protection:

### Risk Management
- ✅ **Position Size Limit**: Max $1,000 per trade (default)
- ✅ **Total Exposure Cap**: Max $5,000 total (default)
- ✅ **Drawdown Protection**: Auto-stop at 20% loss
- ✅ **Liquidity Requirements**: Min $10,000 market volume

### Before Every Trade
1. Check position size against limit
2. Check total exposure against cap
3. Verify market liquidity
4. Confirm drawdown within acceptable range
5. Only proceed if ALL checks pass

### Simulation Mode
- Runs without real funds by default
- Test strategies risk-free
- Perfect for development and testing

## 📊 What the Agent Can Do

The agent now has 5 new trading tools:

1. **execute_arbitrage_trade** - Execute cross-platform arbitrage
2. **place_trade** - Directional market/limit orders
3. **get_portfolio_status** - View positions and P&L
4. **close_position** - Exit specific position
5. **check_risk_limits** - Verify trading is allowed

Example agent queries:
```
"Scan for arbitrage opportunities with >5% spread"
"Place a $500 YES bet on Trump winning if price is below 0.50"
"Show me my current positions and their P&L"
"Close my position on the Bitcoin halving market"
"Am I within my risk limits?"
```

## 🔗 Blockchain Integration

### Supported Networks

| Chain | Purpose | Status |
|-------|---------|--------|
| **Polygon** | Polymarket trading | ✅ Ready |
| **Ethereum** | Mainnet protocols | ✅ Ready |
| **Arbitrum** | L2 scaling | ✅ Ready |

### Smart Contract Integration

Pre-configured for Polymarket:
- CTF Exchange: `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E`
- USDC Token: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
- Conditional Tokens: `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`

## 🧪 Testing Strategy

### 1. Start with Simulation
```bash
# No wallet needed
python3 trading_terminal.py
# Place simulated trades
```

### 2. Test on Testnet
```bash
# Update .env
POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com
# Use Mumbai testnet tokens (free)
```

### 3. Mainnet with Small Amounts
```bash
# Start with $100-500
STARTING_BALANCE=500
MAX_POSITION_SIZE=50
MAX_TOTAL_EXPOSURE=200
```

## 📈 Trading Strategies

### Arbitrage Strategy
Agent automatically:
1. Scans markets across platforms
2. Identifies price differences >3%
3. Checks liquidity and risk
4. Executes simultaneous trades
5. Captures spread profit

### Directional Trading
Agent can:
1. Analyze market fundamentals
2. Identify mispriced probabilities
3. Size positions appropriately
4. Enter at target prices
5. Monitor and exit at profit

### Risk-First Approach
- Conservative position sizing
- Diversification across markets
- Quick stops on losses
- Profit taking discipline

## ⚙️ Configuration Reference

### Trading Settings (.env)

```bash
# Capital and sizing
STARTING_BALANCE=10000         # Starting capital
MAX_POSITION_SIZE=1000         # Max per trade
MAX_TOTAL_EXPOSURE=5000        # Max total exposure

# Risk controls
MAX_DRAWDOWN=0.20              # 20% max loss
MIN_LIQUIDITY=10000            # Min market volume

# Autonomous trading
ENABLE_AUTONOMOUS_TRADING=false  # Safety default
MAX_DAILY_TRADES=5               # Daily trade limit

# Blockchain (Polygon)
POLYGON_WALLET_ADDRESS=          # Your wallet
POLYGON_PRIVATE_KEY=             # Private key (SECURE!)
POLYGON_RPC_URL=https://polygon-rpc.com
```

### Adjust Risk Tolerance

**Conservative** (recommended for start):
```bash
MAX_POSITION_SIZE=500
MAX_TOTAL_EXPOSURE=2000
MAX_DRAWDOWN=0.10
```

**Moderate**:
```bash
MAX_POSITION_SIZE=1000
MAX_TOTAL_EXPOSURE=5000
MAX_DRAWDOWN=0.20
```

**Aggressive** (experienced only):
```bash
MAX_POSITION_SIZE=2000
MAX_TOTAL_EXPOSURE=10000
MAX_DRAWDOWN=0.30
```

## 🔐 Security Checklist

Before trading with real funds:

- [ ] Test thoroughly in simulation mode
- [ ] Verify on testnet with fake tokens
- [ ] Use a dedicated trading wallet (not main holdings)
- [ ] Never commit private keys to git
- [ ] Start with small amounts (<$500)
- [ ] Enable 2FA on exchange accounts
- [ ] Review transactions before signing
- [ ] Monitor gas prices to avoid expensive trades
- [ ] Set conservative risk limits
- [ ] Have exit strategy planned

## 📚 Learn More

- **Full Documentation**: `TRADING_TERMINAL.md`
- **Architecture**: See code comments in `trading_terminal.py`
- **Blockchain Layer**: `blockchain/contracts.py`
- **Agent Integration**: `agent/trading_tools.py`
- **Risk Management**: `RiskManager` class in trading_terminal.py

## 🐛 Troubleshooting

### "Import failed" error
```bash
pip install web3 eth-account
```

### "Blockchain connection failed"
- Check `POLYGON_RPC_URL` in .env
- Try alternative RPC: `https://polygon-rpc.com`
- Verify network connectivity

### "Trading tools not available"
```bash
# Install dependencies
pip install -r requirements-trading.txt
```

### Agent not executing trades
1. Check `ENABLE_AUTONOMOUS_TRADING=true` in .env
2. Verify risk limits not exceeded
3. Check daily trade limit: `MAX_DAILY_TRADES`
4. Review agent logs for errors

## 💬 Example Session

```bash
$ python3 examples/trading_agent_demo.py

🎮 OracleXBT Trading Agent - Autonomous Trading Demo

💬 You: check my portfolio

🤖 Agent: Your portfolio is currently worth $10,000 with no open 
positions. You have full trading capacity available with 0% exposure 
used. Your risk limits allow for up to $5,000 total exposure and 
$1,000 per position.

💬 You: find arbitrage opportunities on election markets

🤖 Agent: I found a promising arbitrage opportunity:

Market: Trump 2024 Election Win
- Polymarket: 52¢ (YES)
- Kalshi: 57¢ (YES)
- Spread: 5% profit potential
- Liquidity: $2.5M on Polymarket, $800K on Kalshi

This represents a risk-free profit opportunity if executed 
simultaneously on both platforms. Would you like me to proceed 
with a $500 arbitrage trade?

💬 You: yes, proceed

🤖 Agent: Executing arbitrage trade...
[Uses execute_arbitrage_trade tool]

✅ Trade executed successfully:
- Bought 500 shares @ $0.52 on Polymarket
- Sold 500 shares @ $0.57 on Kalshi
- Captured $25 profit (5% spread)
- Total exposure: $260

Your portfolio is now worth $10,025 with 2 open positions.
```

## 🎯 Next Steps

1. **Test the system**: Run `python3 test_trading_terminal.py`
2. **Try the demo**: Run `python3 examples/trading_agent_demo.py`
3. **Read full docs**: Open `TRADING_TERMINAL.md`
4. **Configure wallet**: Add addresses to `.env` (testnet first!)
5. **Enable trading**: Set `ENABLE_AUTONOMOUS_TRADING=true`
6. **Start small**: Begin with $100-500 to learn
7. **Monitor closely**: Watch logs and portfolio status
8. **Scale gradually**: Increase limits as you gain confidence

## ⚖️ Legal Disclaimer

- **Not Financial Advice**: This is educational software
- **You Are Responsible**: For all trades and risk management
- **Regulatory Compliance**: Check laws in your jurisdiction
- **Smart Contract Risk**: Blockchain transactions are irreversible
- **Market Risk**: Prediction markets can be volatile
- **No Guarantees**: Past performance doesn't predict future results

**Trade responsibly. Never risk more than you can afford to lose.**

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  OracleXBT Agent                    │
│  (Anthropic Claude - Intelligent Decision Making)  │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴──────────┐
        │                      │
┌───────▼────────┐    ┌───────▼────────┐
│ Analysis Tools │    │ Trading Tools  │
│  • Markets     │    │  • Execute     │
│  • Arbitrage   │    │  • Risk Check  │
│  • Orderbook   │    │  • Portfolio   │
└────────────────┘    └───────┬────────┘
                              │
                    ┌─────────▼─────────┐
                    │ Trading Terminal  │
                    │  • Risk Manager   │
                    │  • Position Track │
                    │  • Order Exec     │
                    └─────────┬─────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐         ┌───────▼────────┐
        │   Blockchain   │         │   Platforms    │
        │  • Polygon     │         │  • Polymarket  │
        │  • Ethereum    │         │  • Kalshi      │
        │  • Arbitrum    │         │  • Limitless   │
        └────────────────┘         └────────────────┘
```

**Ready to trade! 🚀**
