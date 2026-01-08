# Mainnet Deployment Guide

## 🟢 Live Trading is Now Active

Your OracleXBT trading agent is configured for **Polygon Mainnet** and ready for live trading with real funds.

## Current Configuration

### Blockchain Networks
- **Polymarket**: Polygon Mainnet (Chain ID: 137)
- **Kalshi**: Production API (`https://trading-api.kalshi.com/trade-api/v2`)
- **Limitless**: Multi-chain mainnet support

### RPC Endpoints
```python
# Polygon Mainnet
RPC_URL = "https://polygon-rpc.com"

# Alternative RPCs (for redundancy):
# - https://polygon-mainnet.infura.io/v3/YOUR_KEY
# - https://rpc-mainnet.maticvigil.com
# - https://polygon-bor.publicnode.com
```

### Smart Contracts
```python
# Polymarket CTF Exchange (Polygon Mainnet)
EXCHANGE_ADDRESS = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"

# Conditional Tokens Framework
CTF_ADDRESS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
```

## Pre-Launch Checklist

### ✅ Security Setup

- [ ] Use a **dedicated trading wallet** with limited funds
- [ ] Never store more than you're willing to lose in the trading wallet
- [ ] Keep private keys in a secure password manager or hardware wallet
- [ ] Enable 2FA on all exchange accounts (Kalshi)
- [ ] Review and understand gas fees on Polygon
- [ ] Set up alerts for wallet balance and position limits

### ✅ Credential Configuration

**For Polymarket/Limitless (Web3)**:
```javascript
{
  "privateKey": "0xYOUR_PRIVATE_KEY_HERE",  // NEVER commit to git
  "wallet": "0xYOUR_WALLET_ADDRESS"
}
```

**For Kalshi (API)**:
```javascript
{
  "kalshiApiKey": "YOUR_API_KEY",
  "kalshiApiSecret": "YOUR_API_SECRET"
}
```

### ✅ Agent Configuration

Recommended starting parameters:
```javascript
{
  "maxPosition": 50,        // Start small ($50 max per position)
  "minProfit": 3.0,         // Higher threshold (3% minimum)
  "maxTrades": 10,          // Limit daily trades
  "stopLoss": 5.0,          // 5% stop loss
  "platforms": {
    "polymarket": true,     // Highest liquidity
    "kalshi": true,         // Regulated, USD-based
    "limitless": false      // Enable after testing
  }
}
```

### ✅ Wallet Funding

**Polygon Mainnet Requirements**:
1. **USDC** for trading on Polymarket
   - Bridge from Ethereum: https://wallet.polygon.technology/
   - Buy directly: Use exchanges like Coinbase, Binance
   
2. **MATIC** for gas fees
   - Needed for transaction fees on Polygon
   - ~0.5 MATIC should cover hundreds of trades
   - Get from exchanges or bridge

**Kalshi Requirements**:
1. USD balance in Kalshi account
2. Complete KYC verification
3. Link bank account for deposits

## Starting Live Trading

### Step 1: Fund Your Wallet

```bash
# Check wallet balance
curl -X POST https://polygon-rpc.com \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBalance","params":["YOUR_WALLET_ADDRESS","latest"],"id":1}'

# Check USDC balance (6 decimals)
# USDC on Polygon: 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
```

### Step 2: Configure Agent

1. Open http://localhost:5001/#agent
2. Connect your wallet (MetaMask or paste address)
3. Add your private key in the "Polygon Private Key" field
4. For Kalshi, add API credentials
5. Set conservative risk parameters (small positions)
6. Save configuration

### Step 3: Activate & Monitor

1. Toggle the agent switch to **ON**
2. Monitor the Activity Feed for trades
3. Check wallet balance regularly
4. Review P&L metrics

## Monitoring Your Agent

### Real-Time Metrics

Access agent status:
```bash
curl http://localhost:5001/api/agent/status/YOUR_AGENT_ID
```

Returns:
```json
{
  "agent": {
    "id": "agent_0x123_456",
    "wallet": "0x...",
    "active": true
  },
  "stats": {
    "total_trades": 15,
    "today_trades": 5,
    "total_profit": 45.23
  },
  "recent_positions": [...]
}
```

### Transaction Verification

**Polymarket Orders**:
- Check on Polygonscan: https://polygonscan.com/address/YOUR_WALLET
- View in Polymarket UI: https://polymarket.com/

**Kalshi Orders**:
- Log in to Kalshi account
- View order history: https://kalshi.com/portfolio

### Logging

All trades are logged to:
```bash
tail -f /tmp/api_server.log

# Filter for your agent
grep "agent_YOUR_ID" /tmp/api_server.log
```

## Risk Management

### Position Limits

The agent automatically enforces:
- **Max Position Size**: Prevents any single trade from exceeding your limit
- **Daily Trade Limit**: Stops after reaching max trades per day
- **Stop Loss**: Automatically closes positions at loss threshold
- **Min Profit**: Only executes when spread meets minimum

### Emergency Shutdown

**Immediately stop trading**:
```bash
# Method 1: Toggle off in UI
# Navigate to http://localhost:5001/#agent
# Switch agent toggle to OFF

# Method 2: API call
curl -X POST http://localhost:5001/api/agent/deactivate \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "YOUR_AGENT_ID"}'

# Method 3: Kill server
pkill -f api_server.py
```

**Manual position closure**:
- Polymarket: Close positions at https://polymarket.com/
- Kalshi: Close positions at https://kalshi.com/portfolio

## Gas Fee Management

### Polygon Mainnet Gas

Current typical costs:
- Simple transfer: ~0.001 MATIC ($0.001)
- Token swap: ~0.005 MATIC ($0.005)
- Polymarket order: ~0.01-0.02 MATIC ($0.01-0.02)

**Monitor gas prices**:
- https://polygonscan.com/gastracker
- https://gasstation.polygon.technology/

**Gas optimization**:
- Trade during low-activity hours
- Batch orders when possible
- Keep 0.5-1 MATIC buffer

## Common Issues & Solutions

### Issue: "Insufficient MATIC for gas"
**Solution**: Bridge more MATIC to your wallet
```bash
# Check MATIC balance
# Visit: https://wallet.polygon.technology/
```

### Issue: "Order execution failed"
**Possible causes**:
1. Insufficient USDC balance
2. Market moved (price changed)
3. Order size too small (minimum requirements)
4. Network congestion

**Solution**: Check wallet balance and retry with adjusted parameters

### Issue: "Kalshi authentication failed"
**Solution**: 
1. Verify API credentials are correct
2. Check if API key has trading permissions
3. Ensure account is fully verified (KYC)

### Issue: "Agent not executing trades"
**Check**:
1. Is agent toggle ON?
2. Are platforms enabled?
3. Is min_profit threshold too high?
4. Any opportunities matching criteria?
5. Check logs for errors

## Performance Optimization

### Best Practices

1. **Start Conservative**
   - Small position sizes ($10-50)
   - Higher min profit (3-5%)
   - Limited daily trades (5-10)
   - Monitor for 24 hours

2. **Gradual Scaling**
   - Increase positions after successful week
   - Lower min profit as you gain confidence
   - Enable more platforms progressively

3. **Regular Monitoring**
   - Check activity feed daily
   - Review P&L weekly
   - Adjust parameters based on performance
   - Track gas costs vs profits

4. **Platform Selection**
   - **Polymarket**: Best liquidity, lowest slippage
   - **Kalshi**: USD-based, regulated, good for US users
   - **Limitless**: Multi-chain, more volatile

## Advanced Configuration

### Multiple Agents

Run multiple agents with different strategies:
```javascript
// Conservative agent
{
  maxPosition: 50,
  minProfit: 5.0,
  strategy: "arbitrage"
}

// Aggressive agent
{
  maxPosition: 200,
  minProfit: 2.0,
  strategy: "momentum"
}
```

### Custom RPC Provider

For better reliability, use your own RPC:
```python
# In trading_engine.py
self.w3 = Web3(Web3.HTTPProvider('YOUR_INFURA_OR_ALCHEMY_URL'))
```

### API Rate Limiting

Adjust based on your needs:
```python
# In api_server.py
limiter = Limiter(
    app=app,
    default_limits=["10000 per hour"],  # Current setting
    storage_uri="memory://"
)
```

## Support & Resources

### Documentation
- Polymarket API: https://docs.polymarket.com/
- Kalshi API: https://trading-api.kalshi.com/trade-api/v2/docs
- Polygon Network: https://docs.polygon.technology/

### Block Explorers
- Polygonscan: https://polygonscan.com/
- Polymarket Markets: https://polymarket.com/

### Community
- Discord: [Your Discord]
- Telegram: [Your Telegram]
- GitHub: https://github.com/your-repo

## Disclaimer

⚠️ **Trading involves substantial risk of loss**

- You are responsible for all trading decisions
- Never trade with funds you cannot afford to lose
- Past performance does not guarantee future results
- The agent is provided as-is without warranties
- Always monitor your positions and adjust risk parameters
- Gas fees and platform fees will reduce net profits
- Market conditions can change rapidly

**By using mainnet trading, you acknowledge these risks and take full responsibility for your trading activity.**

---

## Quick Start Commands

```bash
# Check agent status
curl http://localhost:5001/api/agent/status/agent_0x123_456

# View recent trades
curl http://localhost:5001/api/trades | python3 -m json.tool

# Check server health
curl http://localhost:5001/api/health

# View logs
tail -f /tmp/api_server.log

# Emergency stop
curl -X POST http://localhost:5001/api/agent/deactivate \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "YOUR_AGENT_ID"}'
```

## Ready to Trade

Your system is now configured for mainnet. Remember:
1. ✅ Start small
2. ✅ Monitor closely
3. ✅ Adjust parameters based on results
4. ✅ Keep security in mind

Happy trading! 🚀
