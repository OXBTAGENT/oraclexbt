# 🤖 OracleXBT All-Day Trading - Local Testing Guide

## Overview
Run your trading agent continuously in VSC to test before pushing to production.

## Quick Start

### 1. Start All-Day Trading
Open a terminal and run:
```bash
./start_trading.sh
```

This will:
- Register your agent with wallet `0xd3d03f57c60bBEFE645cd6Bb14f1CE2c1915e898`
- Activate trading across Polymarket, Kalshi, and Limitless
- Show status updates every 5 minutes
- Log all activity to `logs/` directory
- Run until you press Ctrl+C

### 2. Check Status Anytime
In a separate terminal, run:
```bash
python3 check_agent_status.py
```

This shows:
- Current trade count and volume
- Trades per platform with visual bars
- Recent 10 trades
- Latest log entries

### 3. Watch Live Trades
For real-time streaming display:
```bash
python3 bin/live_trades_terminal.py
```

## All-Day Trading Features

### ✅ Automatic Monitoring
- Status updates every 5 minutes
- Tracks total trades, volume, and performance
- Calculates trades per hour
- Shows recent trades

### ✅ Comprehensive Logging
All logs saved to `logs/` directory:
- `agent_YYYYMMDD.log` - Detailed activity log
- `session_YYYYMMDD_HHMMSS.json` - Session summaries

### ✅ Graceful Shutdown
Press Ctrl+C anytime to:
- Stop agent gracefully
- Save complete session summary
- Show final statistics

### ✅ Performance Metrics
Tracks:
- Total trades executed
- Total volume traded
- Trades per hour rate
- Platform distribution
- Average trade value

## Trading Configuration

**Current Settings:**
- Wallet: `0xd3d03f57c60bBEFE645cd6Bb14f1CE2c1915e898`
- Strategy: Arbitrage
- Max Position: $50
- Min Profit: 5%
- Max Trades: 10,000 (no daily limit)
- Stop Loss: 10%
- Scan Interval: 3-5 seconds
- Success Rate: 95%
- Trades per Scan: 2-4

**Platforms:**
- ✅ Polymarket (~60% of trades)
- ✅ Kalshi (~25% of trades)
- ✅ Limitless (~15% of trades)

## Expected Performance

With current aggressive settings:
- **~12-20 trades per minute** when active
- **~720-1200 trades per hour**
- **~8,640-14,400 trades per 12 hours**
- **~17,280-28,800 trades per day**

## File Structure

```
oraclyst-python-sdk-main/
├── start_trading.sh          # Start all-day trading
├── run_agent_all_day.py      # Main all-day agent script
├── check_agent_status.py     # Quick status checker
├── test_agent_local.py       # 60-second test script
├── bin/
│   ├── api_server.py         # Trading engine server
│   ├── trading_engine.py     # Trade generation logic
│   └── live_trades_terminal.py # Real-time display
└── logs/
    ├── agent_20260104.log    # Daily activity logs
    └── session_*.json        # Session summaries
```

## Common Commands

### Start Server (if not running)
```bash
python3 bin/api_server.py &
```

### Quick Test (60 seconds)
```bash
python3 test_agent_local.py
```

### Check Server Status
```bash
lsof -i :5001
```

### Stop Everything
```bash
pkill -f api_server.py
pkill -f run_agent_all_day.py
pkill -f live_trades_terminal.py
```

### View Logs
```bash
tail -f logs/agent_$(date +%Y%m%d).log
```

### Check Session Summaries
```bash
ls -lh logs/session_*.json
cat logs/session_*.json | jq '.'
```

## Monitoring During the Day

### Terminal 1: Main Trading Agent
```bash
./start_trading.sh
```
Keep this running - shows status updates every 5 minutes

### Terminal 2: Live Trades Stream
```bash
python3 bin/live_trades_terminal.py
```
Watch trades in real-time with colors

### Terminal 3: Ad-hoc Status Checks
```bash
python3 check_agent_status.py
```
Run anytime to see current stats without interrupting

## Session Management

### View Today's Activity
```bash
cat logs/agent_$(date +%Y%m%d).log
```

### Get Current Stats
```bash
curl http://localhost:5001/api/stats | jq '.'
```

### Get Recent Trades
```bash
curl http://localhost:5001/api/trades | jq '.trades[:10]'
```

## Before Production Deployment

After all-day testing, verify:

1. ✅ **Stability**: Agent runs for hours without crashes
2. ✅ **Performance**: Consistent trades per hour rate
3. ✅ **Logging**: All trades properly logged
4. ✅ **Memory**: No memory leaks over time
5. ✅ **Error Handling**: Graceful recovery from issues

Check final session summary in `logs/session_*.json` for complete statistics.

## Troubleshooting

### Server Not Running
```bash
python3 bin/api_server.py &
sleep 3
curl http://localhost:5001/
```

### Agent Won't Start
Check logs:
```bash
tail -20 logs/agent_$(date +%Y%m%d).log
```

### No Trades Appearing
1. Verify server is running: `lsof -i :5001`
2. Check agent is activated: `python3 check_agent_status.py`
3. Review logs for errors

### High CPU Usage
This is normal with aggressive trading (3-5s scans). For testing, this validates the system can handle production load.

## Tips for All-Day Testing

1. **Start in the morning** to get full day of data
2. **Check status every few hours** using `check_agent_status.py`
3. **Keep logs** for analysis and debugging
4. **Monitor system resources** to ensure stability
5. **Test graceful shutdown** with Ctrl+C before end of day

## Ready for Production?

After successful all-day testing:
- ✅ Review session summary JSON files
- ✅ Verify total trades and volume are as expected
- ✅ Check logs for any errors or warnings
- ✅ Confirm all platforms are working
- ✅ Push website with confidence!

---

**Need Help?**
- Check logs: `logs/agent_*.log`
- Review status: `python3 check_agent_status.py`
- See recent trades: `curl http://localhost:5001/api/trades`
