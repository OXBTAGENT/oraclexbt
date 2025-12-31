# 🤖 OracleXBT Hourly Tweeting & Auto-Reply System

## Quick Start

Your agent is now configured to:
- **Tweet every hour** with diverse prediction market content
- **Reply to EVERY tweet** from 25+ monitored prediction market accounts

### Run the Full System

```bash
./start_automation.sh
```

Or with Python:
```bash
python3 oracle_automation.py
```

That's it! Your agent will now:
1. Post engaging tweets every hour automatically
2. Monitor and reply to all tweets from key prediction market accounts

### Test Before Running

```bash
# Test one monitoring cycle
python3 oracle_realtime_monitor.py once

# Generate one test tweet
python3 -c "
from agent import PredictionMarketAgent
from agent.tweet_scheduler import HourlyTweetScheduler
agent = PredictionMarketAgent()
scheduler = HourlyTweetScheduler(agent)
print(scheduler.generate_hourly_tweet())
"
```

## What Gets Tweeted Automatically?

Every hour, your agent posts one of these tweet types (rotated):
- 📊 Market updates with current prices and volume
- 💰 Arbitrage alerts for price discrepancies
- 📈 Data insights and interesting patterns
- 📚 Educational content about prediction markets
- 💹 Price movement analysis
- 📉 Volume and liquidity analysis
- ⚖️ Platform comparisons
- ⚠️ Risk management insights
- 📍 Trend analysis
- 💬 Engaging conversation starters

## Who Gets Auto-Replied To?

Your agent monitors and replies to tweets from:
- **Platforms**: Polymarket, Kalshi, Manifold Markets, PredictIt
- **Executives**: CEOs and founders of major platforms
- **Traders**: Top prediction market traders and analysts
- **Analysts**: Nate Silver, political analysts, crypto analysts
- **Data Sources**: Election odds aggregators

**Total: 25+ accounts monitored continuously**

## Customization

### Change Tweet Frequency

```bash
# Tweet every 30 minutes instead of 1 hour
python3 oracle_automation.py --hourly-interval 1800
```

### Change Monitoring Frequency

```bash
# Check for new tweets every 2 minutes
python3 oracle_automation.py --monitoring-interval 120
```

### Configure in .env

Add to your `.env` file:
```bash
HOURLY_TWEET_INTERVAL=3600  # Seconds between tweets
MONITORING_CHECK_INTERVAL=300  # Seconds between monitoring checks
MAX_DAILY_TWEETS=24
MAX_DAILY_REPLIES=100
```

## Monitoring & Stats

View real-time statistics:
```bash
python3 oracle_automation.py --stats-only
```

Check logs:
```bash
tail -f oraclexbt.log
```

## Production Deployment

### Run in Background (Screen)

```bash
screen -S oraclexbt
./start_automation.sh
# Press Ctrl+A then D to detach
# Reattach: screen -r oraclexbt
```

### Run as System Service

See [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) for systemd/launchd setup.

## Safety Features

✅ **Duplicate Prevention** - Never replies to the same tweet twice  
✅ **Rate Limit Protection** - Automatic delays between API calls  
✅ **Error Recovery** - Automatic retry on failures  
✅ **Graceful Shutdown** - Clean stop on Ctrl+C  
✅ **Comprehensive Logging** - All activity tracked  

## Troubleshooting

**Tweets not posting?**
- Check Twitter credentials in `.env`
- Verify API permissions
- Check `oraclexbt.log` for errors

**Replies not working?**
- Ensure monitored accounts are public
- Check rate limits
- Verify `tweepy` is installed: `pip install tweepy`

**Need more help?**
See [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md) for comprehensive documentation.

## Files

- `oracle_automation.py` - Main orchestration system
- `agent/tweet_scheduler.py` - Hourly tweet generator
- `oracle_realtime_monitor.py` - Real-time reply monitor
- `start_automation.sh` - Quick start script
- `AUTOMATION_GUIDE.md` - Complete documentation

## Examples

### Generated Tweets

```
"Polymarket Bitcoin ETF market showing 76% probability, up from 68% yesterday. 
Volume jumped 180% to $2.3M. Major traders accumulating Yes shares."

"Arbitrage alert: Election market showing 3.2% spread between Polymarket and 
Kalshi. $4.5M liquidity on both platforms."
```

### Generated Replies

Original tweet: "Bitcoin ETF odds looking interesting on Polymarket"

Your agent's reply:
```
"Currently at 73.2% (+5% from yesterday). Volume is $2.1M with strong bid 
support at 72%. Kalshi showing 71.8% - slight arbitrage opportunity."
```

---

**Ready to start?** Run `./start_automation.sh` and watch your agent come alive! 🚀
