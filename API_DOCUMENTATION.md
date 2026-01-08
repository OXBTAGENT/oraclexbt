# OracleXBT API Documentation

## Base URL
```
Development: http://localhost:7777
Production: https://your-domain.com
```

## Authentication
Currently, no authentication required for public endpoints. Agent-specific operations use agent_id.

---

## 📊 Public Endpoints

### GET `/`
**Description**: Serve main website

**Response**: HTML page

---

### GET `/api/health`
**Description**: Health check endpoint for monitoring

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-31T12:00:00.000Z",
  "version": "1.0.0"
}
```

---

### GET `/api/trades`
**Description**: Get recent trades across all platforms

**Response**:
```json
{
  "trades": [
    {
      "id": "17351234567890_1234",
      "timestamp": "2025-12-31T12:00:00.000Z",
      "market": "Will Bitcoin reach $100k by 2026?",
      "platform": "Polymarket",
      "side": "YES",
      "price": 0.55,
      "size": 1000,
      "value": 550.00,
      "platform_fee": 5.50
    }
  ],
  "stats": {
    "total_trades": 150,
    "total_volume": 50000.00,
    "platform_fees_collected": 500.00,
    "by_platform": {
      "Polymarket": 100,
      "Kalshi": 40,
      "Limitless": 10
    }
  },
  "timestamp": "2025-12-31T12:00:00.000Z"
}
```

---

### GET `/api/stats`
**Description**: Get trading statistics

**Response**:
```json
{
  "total_trades": 150,
  "total_volume": 50000.00,
  "platform_fees_collected": 500.00,
  "by_platform": {
    "Polymarket": 100,
    "Kalshi": 40,
    "Limitless": 10
  }
}
```

---

### GET `/api/markets`
**Description**: Get available markets

**Query Parameters**:
- `search` (optional): Search term for filtering markets
- `limit` (optional): Number of results (default: 20)

**Example**: `/api/markets?search=bitcoin&limit=10`

**Response**:
```json
{
  "markets": [
    {
      "id": "pm-551963",
      "platform": "Polymarket",
      "title": "Will Bitcoin reach $100k by 2026?",
      "yes_price": 0.55,
      "no_price": 0.45,
      "volume": 1500000
    }
  ],
  "total": 10,
  "source": "polymarket_clob_api"
}
```

---

### GET `/api/platform/stats`
**Description**: Get platform-wide statistics including fees

**Response**:
```json
{
  "total_agents": 50,
  "active_agents": 15,
  "total_trades": 500,
  "total_volume": 150000.00,
  "total_fees_collected": 1500.00,
  "current_session": {
    "trades": 150,
    "volume": 50000.00,
    "fees_collected": 500.00
  },
  "fee_info": {
    "rate": 0.01,
    "rate_percentage": "1%",
    "description": "Platform takes 1% of all trading volume"
  }
}
```

---

## 🤖 Agent Management Endpoints

### POST `/api/agent/register`
**Description**: Register a new trading agent

**Request Body**:
```json
{
  "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "platforms": {
    "polymarket": true,
    "kalshi": true,
    "limitless": false
  },
  "strategy": "arbitrage",
  "maxPosition": 100,
  "minProfit": 2.0,
  "maxTrades": 50,
  "stopLoss": 5.0,
  "privateKey": "0xabc..." (optional),
  "kalshiApiKey": "your_key" (optional),
  "kalshiApiSecret": "your_secret" (optional)
}
```

**Response**:
```json
{
  "success": true,
  "agent_id": "agent_0x742d35_1735123456",
  "message": "Agent registered successfully"
}
```

**Validation Rules**:
- `wallet`: Must be valid Ethereum address (0x... 42 characters)
- `maxPosition`: Between $10 and $10,000
- `minProfit`: Between 0.1% and 50%
- `maxTrades`: Positive integer
- `stopLoss`: Positive number
- At least one platform must be enabled

**Rate Limit**: 5 requests per hour per IP

---

### POST `/api/agent/activate`
**Description**: Activate a trading agent

**Request Body**:
```json
{
  "agent_id": "agent_0x742d35_1735123456"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Agent activated successfully"
}
```

---

### POST `/api/agent/deactivate`
**Description**: Deactivate a trading agent

**Request Body**:
```json
{
  "agent_id": "agent_0x742d35_1735123456"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Agent deactivated successfully"
}
```

---

### GET `/api/agent/status/<agent_id>`
**Description**: Get agent status and statistics

**Example**: `/api/agent/status/agent_0x742d35_1735123456`

**Response**:
```json
{
  "success": true,
  "agent": {
    "id": "agent_0x742d35_1735123456",
    "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "active": true,
    "strategy": "arbitrage",
    "platforms": {
      "polymarket": true,
      "kalshi": true,
      "limitless": false
    }
  },
  "stats": {
    "total_trades": 25,
    "today_trades": 5,
    "total_volume": 5000.00,
    "gross_profit": 125.00,
    "platform_fees_paid": 50.00,
    "net_profit": 75.00,
    "fee_rate": 0.01
  },
  "recent_positions": [
    {
      "trade_id": "agent_0x742d35_1735123456_1234567890",
      "type": "arbitrage",
      "market": "Will Bitcoin reach $100k?",
      "buy_platform": "polymarket",
      "sell_platform": "kalshi",
      "size": 100,
      "total_volume": 200,
      "expected_profit": 5.00,
      "platform_fee": 2.00,
      "net_profit": 3.00,
      "spread": 2.5,
      "success": true,
      "timestamp": "2025-12-31T12:00:00.000Z"
    }
  ]
}
```

---

## 📈 Trading Endpoints

### POST `/api/place_order`
**Description**: Place a trading order (currently simulated)

**Request Body**:
```json
{
  "platform": "polymarket",
  "market_id": "pm-551963",
  "side": "YES",
  "order_type": "market",
  "size": 100,
  "price": 0.55 (optional for limit orders)
}
```

**Response**:
```json
{
  "success": true,
  "order_id": "POL-1735123456789",
  "message": "Order executed successfully",
  "order": {
    "order_id": "POL-1735123456789",
    "platform": "polymarket",
    "market_id": "pm-551963",
    "side": "YES",
    "order_type": "market",
    "size": 100,
    "price": 0.55,
    "status": "filled",
    "timestamp": "2025-12-31T12:00:00.000Z"
  }
}
```

**Rate Limit**: 50 requests per hour per agent

---

## 🚨 Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "ERROR_CODE" (optional),
  "details": {} (optional)
}
```

### Common HTTP Status Codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error

### Example Error Response:
```json
{
  "success": false,
  "message": "Missing required field: wallet",
  "error_code": "VALIDATION_ERROR"
}
```

---

## 📝 Rate Limiting

Rate limits are applied per IP address:

| Endpoint | Limit |
|----------|-------|
| Default | 100 requests/hour |
| `/api/agent/register` | 5 requests/hour |
| `/api/place_order` | 50 requests/hour |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1735126800
```

When rate limit is exceeded:
```json
{
  "success": false,
  "message": "Rate limit exceeded. Try again in 3600 seconds.",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

---

## 🔐 Security Best Practices

1. **HTTPS Only**: Always use HTTPS in production
2. **Credential Storage**: Never store private keys client-side
3. **Input Validation**: All inputs are validated server-side
4. **Demo Mode**: Use demo mode for testing without credentials
5. **API Keys**: Keep Kalshi API keys secure
6. **Wallet Addresses**: Validate wallet address format before submission

---

## 📊 WebSocket Support (Coming Soon)

Real-time updates via WebSocket:

```javascript
const socket = io('wss://your-domain.com');

socket.on('connect', () => {
  console.log('Connected');
});

socket.on('trade', (trade) => {
  console.log('New trade:', trade);
});

socket.on('agent_update', (update) => {
  console.log('Agent update:', update);
});
```

---

## 🧪 Testing

### Using cURL:

**Health Check**:
```bash
curl http://localhost:7777/api/health
```

**Register Agent**:
```bash
curl -X POST http://localhost:7777/api/agent/register \
  -H "Content-Type: application/json" \
  -d '{
    "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    "platforms": {"polymarket": true, "kalshi": false, "limitless": false},
    "strategy": "arbitrage",
    "maxPosition": 100,
    "minProfit": 2.0,
    "maxTrades": 50,
    "stopLoss": 5.0
  }'
```

**Get Agent Status**:
```bash
curl http://localhost:7777/api/agent/status/agent_0x742d35_1735123456
```

### Using JavaScript/Fetch:

```javascript
// Register agent
const response = await fetch('http://localhost:7777/api/agent/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    wallet: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
    platforms: { polymarket: true, kalshi: false, limitless: false },
    strategy: 'arbitrage',
    maxPosition: 100,
    minProfit: 2.0,
    maxTrades: 50,
    stopLoss: 5.0
  })
});

const result = await response.json();
console.log(result);
```

---

## 📚 Additional Resources

- [Production Deployment Guide](PRODUCTION_DEPLOY.md)
- [Configuration Reference](config.yaml)
- [Trading System Documentation](docs/TRADING_SYSTEM.md)
- [Quick Reference Guide](QUICK_REFERENCE.md)

---

## 💬 Support

For API issues or questions:
- GitHub Issues: https://github.com/OXBTAGENT/oraclexbt/issues
- Documentation: https://github.com/OXBTAGENT/oraclexbt/docs
