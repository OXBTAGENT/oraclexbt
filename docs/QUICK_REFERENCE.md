# Quick Reference: Real Trading Integration

## Demo Mode (Default - Safe)

**No credentials needed** → Orders are simulated

```javascript
// Register agent without credentials
const response = await fetch('http://localhost:7777/api/agent/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        wallet: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        platforms: { polymarket: true, kalshi: false, limitless: false },
        strategy: 'arbitrage',
        maxPosition: 100,
        minProfit: 2.5,
        maxTrades: 20,
        stopLoss: 5
    })
});

// Result: Orders execute in simulation mode
// Check response: order.simulated === true
```

## Real Trading Mode - Polymarket

**Requires:** Polygon wallet private key

```javascript
// Register with private key for real Web3 execution
const response = await fetch('http://localhost:7777/api/agent/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        wallet: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        platforms: { polymarket: true, kalshi: false, limitless: false },
        strategy: 'arbitrage',
        maxPosition: 10,  // Start small!
        minProfit: 2.5,
        maxTrades: 5,
        stopLoss: 5,
        
        // Add private key for real execution
        privateKey: '0xabcdef...'  // ⚠️ Never hardcode - use secure input
    })
});

// Result: Orders execute on Polygon blockchain
// Check response: order.simulated === false or undefined
```

**Backend Flow:**
```python
# trading_engine.py
account = Account.from_key(agent_config.private_key)
result = polymarket.create_order(
    wallet=account,
    market_id='0x123...',
    side='YES',
    size=100,
    price=0.55
)
# → Submits to https://clob.polymarket.com/order
# → Returns real order ID from Polymarket
```

## Real Trading Mode - Kalshi

**Requires:** Kalshi API key + secret

```javascript
// Register with Kalshi credentials
const response = await fetch('http://localhost:7777/api/agent/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        wallet: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        platforms: { polymarket: false, kalshi: true, limitless: false },
        strategy: 'arbitrage',
        maxPosition: 10,
        minProfit: 2.5,
        maxTrades: 5,
        stopLoss: 5,
        
        // Add Kalshi credentials
        kalshiApiKey: 'your_api_key',
        kalshiApiSecret: 'your_api_secret'
    })
});

// Result: Orders execute via Kalshi REST API
```

**Backend Flow:**
```python
# trading_engine.py
connector = KalshiConnector()
connector.authenticate(api_key, api_secret)
result = connector.create_order(
    market_ticker='TICKER-2024',
    side='YES',
    size=10,
    order_type='market'
)
# → POSTs to https://trading-api.kalshi.com/trade-api/v2/portfolio/orders
# → Returns real order ID from Kalshi
```

## Cross-Platform Trading

**Mix credentials** for multi-platform arbitrage:

```javascript
const response = await fetch('http://localhost:7777/api/agent/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        wallet: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        
        // Enable multiple platforms
        platforms: { 
            polymarket: true,  // Will use privateKey
            kalshi: true,      // Will use kalshiApiKey/Secret
            limitless: false 
        },
        
        strategy: 'arbitrage',
        maxPosition: 50,
        minProfit: 3.0,
        maxTrades: 10,
        stopLoss: 10,
        
        // Provide credentials for both
        privateKey: '0xabcdef...',
        kalshiApiKey: 'your_api_key',
        kalshiApiSecret: 'your_api_secret'
    })
});

// Result: Agent can arbitrage between Polymarket and Kalshi
// Buy cheap on Polymarket (Web3) → Sell expensive on Kalshi (API)
```

## Check Order Status

```javascript
// Get agent status
const status = await fetch('http://localhost:7777/api/agent/status/agent_0x742d35_1234567890');
const data = await status.json();

console.log('Active:', data.agent.active);
console.log('Total Trades:', data.stats.total_trades);
console.log('Profit:', data.stats.total_profit);

// Check recent positions
data.recent_positions.forEach(pos => {
    console.log('Market:', pos.market);
    console.log('Buy Order:', pos.buy_order_id);
    console.log('Sell Order:', pos.sell_order_id);
    console.log('Simulated:', pos.buy_order_id.includes('SIM')); // Check if demo mode
});
```

## Detect Trading Mode

```python
# Backend: trading_engine.py
def _execute_order(self, wallet, platform, side, size, market, agent_config):
    # Automatically detects mode based on credentials
    
    if platform == 'polymarket':
        if agent_config.private_key:
            # REAL MODE: Execute on Polygon
            return self._execute_polymarket_order(...)
        else:
            # DEMO MODE: Simulate
            return self._simulate_order(...)
    
    elif platform == 'kalshi':
        if agent_config.kalshi_api_key and agent_config.kalshi_api_secret:
            # REAL MODE: Execute via API
            return self._execute_kalshi_order(...)
        else:
            # DEMO MODE: Simulate
            return self._simulate_order(...)
```

## Security Checklist

### ❌ DON'T
- Store private keys in localStorage
- Send credentials in URL parameters
- Log private keys to console
- Commit keys to git
- Use production keys in development

### ✅ DO
- Use environment variables for credentials
- Prompt for keys at runtime (secure input)
- Validate key format before sending
- Clear keys from memory after use
- Start with testnet before mainnet
- Use small position sizes initially

## Error Handling

```javascript
// Check for errors in order execution
const response = await fetch('http://localhost:7777/api/agent/status/agent_123');
const data = await response.json();

data.recent_positions.forEach(pos => {
    if (!pos.success) {
        console.error('Order failed:', pos.error);
        
        // Common errors:
        // - "Invalid signature" → Wrong private key
        // - "Authentication failed" → Wrong Kalshi credentials
        // - "Insufficient balance" → Need to fund wallet
    }
});
```

## Testing Progression

### 1. Demo Mode (Safe)
```bash
# No credentials → All simulated
python3 test_trading.py
```

### 2. Testnet (Polygon Mumbai)
```python
# Update RPC in trading_engine.py
self.w3 = Web3(Web3.HTTPProvider('https://rpc-mumbai.maticvigil.com'))

# Use testnet private key
# Get test MATIC from faucet
```

### 3. Mainnet (Real Money)
```python
# Use real credentials
# Start with small positions
# Monitor closely
```

## Quick Commands

```bash
# Install dependencies
pip install web3 eth-account

# Run test suite
python3 test_trading.py

# Start API server
python3 bin/api_server.py

# Check agent status
curl http://localhost:7777/api/agent/status/agent_0x123_456

# View logs
tail -f /tmp/api_server.log
```

## Support

**Documentation:**
- Full setup: [TRADING_CONFIG.md](TRADING_CONFIG.md)
- Implementation: [WEB3_INTEGRATION_SUMMARY.md](WEB3_INTEGRATION_SUMMARY.md)

**Test Mode:** Default demo mode is safe for testing

**Real Trading:** Only execute when you understand the risks and have tested thoroughly
