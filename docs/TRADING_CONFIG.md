# Real Trading Configuration Guide

## Overview

The trading engine now supports **real Web3 and exchange API integrations** for live trading across:
- **Polymarket** (Polygon blockchain)
- **Kalshi** (Centralized REST API)  
- **Limitless** (Multi-chain DeFi)

## Setup Instructions

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install -r requirements.txt
```

This installs:
- `web3` - Web3.py for Ethereum/Polygon interactions
- `eth-account` - Transaction signing with private keys
- `py-clob-client` - Polymarket CLOB API client
- `flask`, `flask-cors`, `requests` - API server

### 2. Configure Agent Credentials

When registering an agent via the UI, you can optionally provide credentials for real trading:

#### Polymarket (Web3)
- **Private Key**: Your wallet's private key for signing transactions on Polygon
- **Usage**: Sent as `privateKey` in the agent registration payload
- **Security**: ⚠️ NEVER expose private keys in production - use secure key management

#### Kalshi (API)
- **API Key**: Your Kalshi account API key
- **API Secret**: Your Kalshi account API secret
- **Usage**: Sent as `kalshiApiKey` and `kalshiApiSecret` in registration
- **Get credentials**: https://kalshi.com/settings/api

### 3. Demo Mode vs Real Trading

The trading engine automatically detects whether credentials are provided:

#### Demo Mode (Default)
- If **no credentials** provided → Orders are **simulated**
- Safe for testing and development
- No real money at risk
- Trade results marked with `"simulated": true`

#### Real Trading Mode
- If **credentials provided** → Orders execute on **real platforms**
- Private key enables Web3 transaction signing for Polymarket
- API keys enable REST API calls to Kalshi
- Real orders placed, real money at risk

### 4. Example Agent Registration (Frontend)

Add optional credential fields to your agent configuration form:

```javascript
// Basic config (demo mode)
const agentConfig = {
    wallet: '0x1234...', // MetaMask address
    platforms: { polymarket: true, kalshi: false },
    strategy: 'arbitrage',
    maxPosition: 100,
    minProfit: 2.5,
    maxTrades: 20,
    stopLoss: 5
};

// Real trading mode (with credentials)
const agentConfigReal = {
    ...agentConfig,
    privateKey: '0xabcd...', // For Polymarket Web3 signing
    kalshiApiKey: 'your_kalshi_key',
    kalshiApiSecret: 'your_kalshi_secret'
};

// Register agent
fetch('http://localhost:7777/api/agent/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(agentConfigReal)
});
```

### 5. Platform-Specific Details

#### Polymarket Integration

**How it works:**
1. Agent config includes Polygon wallet private key
2. When arbitrage opportunity found, engine calls `_execute_polymarket_order()`
3. Creates Web3 account from private key: `Account.from_key(private_key)`
4. Signs order message using EIP-712
5. Submits to Polymarket CLOB API: `https://clob.polymarket.com/order`
6. Returns order ID and status

**Network:** Polygon mainnet (`https://polygon-rpc.com`)
**Contracts:** 
- CTF Exchange: `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E`
- Conditional Tokens: `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045`

#### Kalshi Integration

**How it works:**
1. Agent config includes Kalshi API key + secret
2. Engine creates `KalshiConnector` instance per agent
3. Authenticates with HMAC signature: `KALSHI-ACCESS-SIGNATURE`
4. Gets session token from `/login` endpoint
5. Places orders via `POST /portfolio/orders`
6. Returns order ID and status

**API Base:** `https://trading-api.kalshi.com/trade-api/v2`
**Authentication:** HMAC-SHA256 signing of timestamp + method + path

#### Limitless Integration

**Status:** Placeholder (needs DeFi contract details)
**Plan:** Similar Web3 approach to Polymarket with multi-chain support

## Order Execution Flow

### Arbitrage Strategy Example

1. **Scan Opportunities:**
   - Fetch markets from enabled platforms
   - Compare prices across platforms
   - Calculate spread percentage

2. **Filter by Min Profit:**
   - Only execute if spread ≥ `min_profit` threshold

3. **Execute Paired Orders:**
   ```python
   # Buy YES on cheaper platform
   buy_result = _execute_order(
       agent_config=config,
       platform='polymarket',
       side='YES',
       size=100,
       market='0x123abc...'
   )
   
   # Sell NO on expensive platform  
   sell_result = _execute_order(
       agent_config=config,
       platform='kalshi',
       side='NO',
       size=100,
       market='TICKER-2024'
   )
   ```

4. **Track Position:**
   - Record both legs in `agent_positions`
   - Calculate expected P&L
   - Monitor for settlement

## Security Best Practices

### 🔒 Private Key Management

**DON'T:**
- ❌ Hardcode private keys in code
- ❌ Store keys in localStorage/client-side
- ❌ Send keys in URL parameters
- ❌ Commit keys to version control

**DO:**
- ✅ Use environment variables: `os.getenv('PRIVATE_KEY')`
- ✅ Use secure key management services (AWS KMS, HashiCorp Vault)
- ✅ Prompt user for key at runtime (encrypted input)
- ✅ Store encrypted keys with separate passphrase

### 🔒 API Credentials

- Store Kalshi API keys server-side only
- Never expose in frontend JavaScript
- Use environment variables or secure config files
- Rotate keys regularly

### 🔒 Production Deployment

For production trading bots:

1. **Use dedicated trading wallets** with limited funds
2. **Implement rate limiting** to prevent API abuse
3. **Add circuit breakers** to stop trading on errors
4. **Monitor positions** and set automatic stop-losses
5. **Log all transactions** for audit trail
6. **Use testnet first** before mainnet deployment

## Testing

### Local Testing (Demo Mode)

```bash
# Start API server (no credentials needed)
python bin/api_server.py

# Open website
open http://localhost:7777/#agent

# Register agent without private key
# Trades will be simulated
```

### Testnet Testing (Polygon Mumbai)

```bash
# Update RPC in trading_engine.py:
# self.w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.maticvigil.com'))

# Use testnet private key (with test MATIC)
# Trades execute on testnet with no real value
```

### Mainnet Production

```bash
# Use real private keys and API credentials
# Monitor positions closely
# Start with small position sizes
```

## Monitoring & Debugging

### Check Agent Status

```bash
curl http://localhost:7777/api/agent/status/agent_0x123abc_1234567890
```

Returns:
- Active status
- Total trades
- Today's trades  
- P&L
- Recent positions

### View Order Results

Each order execution returns:
```json
{
  "success": true,
  "order_id": "POL-123456",
  "platform": "polymarket",
  "status": "submitted",
  "simulated": false,
  "timestamp": "2024-01-15T12:34:56"
}
```

### Common Errors

**"Polymarket execution error: Invalid signature"**
- Private key doesn't match wallet address
- Check key format (should start with 0x)

**"Kalshi authentication failed"**
- API key/secret incorrect
- Check credentials at https://kalshi.com/settings/api

**"Insufficient balance"**
- Wallet lacks USDC for trade
- Fund wallet on Polygon for Polymarket

## Support

For issues or questions:
- Check logs in terminal running `api_server.py`
- Review order history in agent status endpoint
- Test in demo mode first before real trading
- Start with small positions to verify setup

## Disclaimer

⚠️ **Trading involves risk of loss. This software is provided for educational purposes. Users are responsible for their own trading decisions and security of credentials. Never risk more than you can afford to lose.**
