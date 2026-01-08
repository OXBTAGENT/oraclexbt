# 🎮 OracleXBT Trading Terminal

## Cross-Chain Prediction Market Trading System

The OracleXBT Trading Terminal enables autonomous execution of trades across multiple prediction market platforms and blockchain networks. It provides secure wallet management, risk controls, and smart contract integration for on-chain trading.

## 🏗️ Architecture

```
OracleXBT Trading Terminal
├── Trading Engine
│   ├── Order Execution (Market & Limit)
│   ├── Position Management
│   └── P&L Tracking
├── Risk Management
│   ├── Position Size Limits
│   ├── Total Exposure Controls
│   └── Drawdown Protection
├── Blockchain Layer
│   ├── Polygon (Polymarket)
│   ├── Ethereum
│   └── Arbitrum
└── Cross-Chain Bridge
    └── USDC Transfers
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install web3 eth-account
```

### 2. Configure Wallets

Add to `.env`:

```bash
# Polygon wallet (for Polymarket)
POLYGON_WALLET_ADDRESS=0xYourWalletAddress
POLYGON_PRIVATE_KEY=your_private_key_here  # ⚠️ NEVER COMMIT THIS

# Risk settings
STARTING_BALANCE=10000
MAX_POSITION_SIZE=1000
MAX_TOTAL_EXPOSURE=5000
MAX_DRAWDOWN=0.20
```

**Security Warning**: Never commit private keys to git. Use environment variables or secure key management systems.

### 3. Launch Terminal

```bash
python3 trading_terminal.py
```

## 🎯 Features

### Automated Trading
- **Market Orders**: Instant execution at current price
- **Limit Orders**: Specify exact price targets
- **Arbitrage Execution**: Simultaneous trades across platforms

### Risk Management
- **Position Sizing**: Automatic limits per trade
- **Exposure Controls**: Total portfolio exposure caps
- **Drawdown Protection**: Auto-stop at configured loss threshold
- **Liquidity Checks**: Minimum volume requirements

### Multi-Chain Support
- **Polygon**: Polymarket CTF contracts (primary)
- **Ethereum**: Mainnet integration
- **Arbitrum**: L2 scaling
- **Cross-Chain Bridge**: USDC transfers between networks

### Portfolio Management
- Real-time P&L tracking
- Position monitoring
- Trade history
- Portfolio snapshots

## 📊 Usage Examples

### Interactive Terminal

```python
from trading_terminal import TradingTerminal

terminal = TradingTerminal()

# Place directional trade
terminal.place_directional_trade(
    market_id="0x1234...",
    platform="polymarket",
    side="yes",
    size=Decimal("500")
)

# Execute arbitrage
opportunity = {
    "market_a": {"platform": "polymarket", "price": 0.45, "market_id": "0x123..."},
    "market_b": {"platform": "kalshi", "price": 0.52, "market_id": "abc123"},
    "spread": 7.0,
    "size": 1000
}
terminal.execute_arbitrage(opportunity)

# Check portfolio
summary = terminal.get_portfolio_summary()
print(f"Total Value: ${summary['total_value']:,.2f}")
print(f"ROI: {summary['roi']:.2f}%")
```

### Agent Integration

```python
from agent.trading_tools import TRADING_TOOLS, place_trade, get_portfolio_status

# Add trading tools to agent
agent_tools = BASE_TOOLS + TRADING_TOOLS

# Agent can now execute trades
result = place_trade(
    market_id="0x1234...",
    platform="polymarket",
    side="yes",
    size=500
)

# Check positions
portfolio = get_portfolio_status()
```

## 🔐 Blockchain Integration

### Polymarket (Polygon)

The terminal integrates with Polymarket's Conditional Token Framework (CTF):

```python
from blockchain import BlockchainConnector, PolymarketContract

# Connect to Polygon
connector = BlockchainConnector(
    rpc_url="https://polygon-rpc.com",
    chain="polygon"
)

# Get USDC balance
usdc_balance = connector.usdc.get_balance(wallet_address)

# Get conditional token balance
token_balance = connector.polymarket.get_token_balance(wallet_address, token_id)
```

### Smart Contract Addresses (Polygon)

- **CTF Exchange**: `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E`
- **USDC**: `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
- **Conditional Tokens**: `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`

## ⚙️ Configuration

### Environment Variables

```bash
# Blockchain Wallets
POLYGON_WALLET_ADDRESS=        # Your Polygon wallet
POLYGON_PRIVATE_KEY=           # Private key (SECURE!)
POLYGON_RPC_URL=              # Polygon RPC endpoint

ETHEREUM_WALLET_ADDRESS=       # Ethereum wallet
ETHEREUM_PRIVATE_KEY=          # Private key
ETHEREUM_RPC_URL=             # Ethereum RPC

ARBITRUM_WALLET_ADDRESS=       # Arbitrum wallet
ARBITRUM_PRIVATE_KEY=          # Private key
ARBITRUM_RPC_URL=             # Arbitrum RPC

# Risk Management
STARTING_BALANCE=10000         # Initial capital ($)
MAX_POSITION_SIZE=1000         # Max per position ($)
MAX_TOTAL_EXPOSURE=5000        # Max total exposure ($)
MAX_DRAWDOWN=0.20              # Max drawdown (20%)
MIN_LIQUIDITY=10000            # Min market liquidity ($)
```

### Risk Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_POSITION_SIZE` | $1,000 | Maximum size for single position |
| `MAX_TOTAL_EXPOSURE` | $5,000 | Total portfolio exposure cap |
| `MAX_DRAWDOWN` | 20% | Auto-stop trading threshold |
| `MIN_LIQUIDITY` | $10,000 | Minimum market volume required |

## 🛠️ Trading Tools for Agent

The agent has access to 5 trading tools:

### 1. execute_arbitrage_trade
Execute arbitrage across platforms when spread detected.

```python
{
    "opportunity": {
        "market_a": {"platform": "polymarket", "price": 0.45, "market_id": "0x123"},
        "market_b": {"platform": "kalshi", "price": 0.52, "market_id": "abc"},
        "spread": 7.0,
        "size": 1000
    }
}
```

### 2. place_trade
Place directional trade on single platform.

```python
{
    "market_id": "0x1234...",
    "platform": "polymarket",
    "side": "yes",
    "size": 500,
    "price": 0.48  # Optional for limit order
}
```

### 3. get_portfolio_status
Get current portfolio metrics.

```python
{
    "balance": 10500.00,
    "total_value": 11250.00,
    "unrealized_pnl": 750.00,
    "num_positions": 3,
    "roi": 7.5
}
```

### 4. close_position
Close specific open position.

```python
{
    "market_id": "0x1234..."
}
```

### 5. check_risk_limits
Check risk exposure and limits.

```python
{
    "total_exposure": 3500,
    "max_exposure": 5000,
    "exposure_used_percent": 70,
    "current_drawdown": 5.2,
    "max_drawdown": 20,
    "trading_allowed": true
}
```

## 📈 Trading Strategies

### Arbitrage Strategy
1. Agent scans markets across platforms
2. Identifies price spreads > 3%
3. Checks liquidity meets minimum
4. Executes simultaneous trades
5. Captures spread profit

### Directional Trading
1. Agent analyzes market data
2. Applies prediction model
3. Sizes position within limits
4. Places market or limit order
5. Monitors P&L and exits

### Risk Management
- Every trade checked against limits
- Automatic position sizing
- Drawdown monitoring
- Emergency stop at threshold

## 🔒 Security Best Practices

1. **Never commit private keys** to version control
2. **Use hardware wallets** for production trading
3. **Set conservative limits** when starting
4. **Test on testnets** before mainnet
5. **Monitor gas prices** to avoid expensive trades
6. **Approve minimal amounts** for smart contracts
7. **Review transactions** before signing

## 🧪 Testing

### Testnet Setup

Test on Polygon Mumbai testnet before mainnet:

```bash
POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com
# Use Mumbai testnet tokens
```

### Manual Testing

```bash
# Launch terminal
python3 trading_terminal.py

# Commands:
# 1. View portfolio
# 2. Place trade
# 3. Execute arbitrage
# 4. View positions
# 5. Close position
# 6. Save state
```

## 📋 State Management

Terminal saves state to `trading_state.json`:

```json
{
  "timestamp": "2025-12-25T10:30:00",
  "balance": 10500.00,
  "positions": [
    {
      "market_id": "0x1234...",
      "platform": "polymarket",
      "side": "yes",
      "size": 500,
      "entry_price": 0.48,
      "pnl": 25.50
    }
  ],
  "portfolio": {
    "total_value": 10525.50,
    "roi": 5.26
  }
}
```

## 🚧 Current Limitations

### Implemented
- ✅ Risk management system
- ✅ Position tracking
- ✅ Portfolio management
- ✅ Multi-chain wallet support
- ✅ Smart contract interfaces

### In Progress
- 🚧 On-chain transaction execution
- 🚧 Order signature generation (EIP-712)
- 🚧 Cross-chain bridging
- 🚧 Gas optimization

### Planned
- ⏳ Hardware wallet integration
- ⏳ Advanced order types (stop-loss, take-profit)
- ⏳ Multiple position sizing strategies
- ⏳ Automated rebalancing

## 🔗 Integration with OracleXBT Agent

### Update agent/tools.py

Add trading tools to agent:

```python
from agent.trading_tools import TRADING_TOOLS

# In get_tools() function
all_tools = [
    # ... existing tools ...
] + TRADING_TOOLS
```

### Update agent/agent.py

Import trading functions:

```python
from agent.trading_tools import (
    execute_arbitrage_trade,
    place_trade,
    get_portfolio_status,
    close_position,
    check_risk_limits
)

# Add to tool_map
self.tool_map = {
    # ... existing tools ...
    "execute_arbitrage_trade": execute_arbitrage_trade,
    "place_trade": place_trade,
    "get_portfolio_status": get_portfolio_status,
    "close_position": close_position,
    "check_risk_limits": check_risk_limits
}
```

### Autonomous Trading Loop

```python
# Add to oracle_twitter_manager.py
from agent.trading_tools import get_portfolio_status, check_risk_limits

def trading_check():
    """Periodic trading check"""
    # Check risk limits
    risk_status = check_risk_limits()
    
    if not risk_status['trading_allowed']:
        print("⚠️ Trading halted - drawdown limit reached")
        return
    
    # Check for opportunities
    agent_response = agent.run("Scan markets for arbitrage opportunities")
    
    # Agent will automatically execute if good opportunities found

# Schedule trading checks
schedule.every(15).minutes.do(trading_check)
```

## 📞 Support

Issues? Questions?
- Check logs: `trading_terminal.log`
- Review state: `trading_state.json`
- Test risk limits before live trading

## ⚖️ Legal Disclaimer

This software is for educational purposes. You are responsible for:
- Regulatory compliance in your jurisdiction
- Risk management and position sizing
- Security of private keys and funds
- Understanding smart contract risks

**Trade at your own risk. Not financial advice.**
