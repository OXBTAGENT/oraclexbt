# OracleXBT Hourly Tweeting & Real-Time Reply System

## Overview

This implementation adds two powerful automation features to your OracleXBT agent:

1. **Hourly Tweet Generation** - Automatically posts diverse, engaging prediction market content every hour
2. **Real-Time Reply Monitoring** - Monitors ALL tweets from 25+ prediction market accounts and replies to EVERY relevant tweet with valuable insights

## Architecture

### Components

1. **`agent/tweet_scheduler.py`** - Hourly tweet generation system
   - 10 different tweet content types (market updates, arbitrage alerts, data insights, educational, etc.)
   - Rotates through content types for variety
   - Automatic retry logic
   - Stats tracking

2. **`oracle_realtime_monitor.py`** - Real-time tweet monitoring and reply system
   - Monitors 25+ prediction market accounts continuously
   - Replies to ALL relevant tweets from monitored accounts
   - Deduplication to prevent duplicate replies
   - Priority-based account handling

3. **`oracle_automation.py`** - Integrated orchestration system
   - Runs both systems concurrently in separate threads
   - Graceful startup and shutdown
   - Comprehensive logging and statistics
   - Configurable intervals

## Quick Start

### 1. Install Dependencies

Ensure you have the required packages:

```bash
pip install tweepy anthropic schedule python-dotenv
```

### 2. Configure Environment

Add these optional settings to your `.env` file:

```bash
# Automation Settings (all optional - defaults shown)
ENABLE_HOURLY_TWEETS=true
HOURLY_TWEET_INTERVAL=3600  # 1 hour in seconds
ENABLE_REALTIME_MONITORING=true
MONITORING_CHECK_INTERVAL=300  # 5 minutes in seconds
MAX_DAILY_TWEETS=24
MAX_DAILY_REPLIES=100
```

### 3. Run the System

**Full automation (recommended):**
```bash
python3 oracle_automation.py
```

**With custom intervals:**
```bash
# Tweet every 30 minutes, monitor every 2 minutes
python3 oracle_automation.py --hourly-interval 1800 --monitoring-interval 120
```

**Just view stats:**
```bash
python3 oracle_automation.py --stats-only
```

## Features in Detail

### Hourly Tweet Scheduler

The scheduler automatically generates and posts varied content types every hour:

#### Tweet Content Types

1. **MARKET_UPDATE** - Current market overview with active markets and volume
2. **ARBITRAGE_ALERT** - Cross-platform price discrepancy alerts
3. **DATA_INSIGHT** - Interesting patterns in prediction market data
4. **EDUCATIONAL** - Teaching content about prediction markets
5. **PRICE_MOVEMENT** - Analysis of significant price changes
6. **VOLUME_ANALYSIS** - Trading volume patterns and liquidity
7. **PLATFORM_COMPARISON** - Objective comparison of different platforms
8. **RISK_ANALYSIS** - Risk management insights and advice
9. **TREND_ANALYSIS** - Market trends and patterns over time
10. **ENGAGEMENT** - Fun facts and interesting content to engage audience

#### Example Generated Tweets

```
"Polymarket Bitcoin ETF market at $100k+ showing 76% probability, up from 68% 
yesterday. Volume jumped 180% to $2.3M. Major traders accumulating Yes shares."

"Arbitrage opportunity: Election market showing 3.2% spread between Polymarket 
(58.3%) and Kalshi (55.1%). $4.5M liquidity on both platforms."

"Volume spike alert: Crypto markets seeing 240% increase today. Bitcoin halving 
predictions now at $3.8M daily volume across all platforms."
```

### Real-Time Reply Monitor

Continuously monitors tweets from these accounts and replies to EVERY relevant tweet:

#### Monitored Accounts (25+)

**Platform Accounts:**
- @Polymarket, @Kalshi, @ManifoldMarkets, @PredictIt, @GoodJudgmentInc

**Executives:**
- @shayne_coplan (Polymarket CEO)
- @CalebBrown412 (Kalshi CEO)
- @AustinGingerKirk (Manifold founder)

**Traders & Analysts:**
- @nabeelqureshi, @RyanBerckmans, @maxbmckinnon, @NateSilver538
- @ElectionBettingOdds, @loomdart, @CryptoHayes, @APompliano
- And 10+ more...

#### Reply Intelligence

The system generates intelligent replies that:
- Add specific market data, probabilities, and insights
- Reference cross-platform comparisons
- Provide historical context and patterns
- Sound professional and analytical (not promotional)
- Include numbers and concrete information
- Are contextually relevant to the original tweet

#### Example Replies

Original: "Bitcoin ETF odds looking interesting on Polymarket"
Reply: "Currently at 73.2% (+5% from yesterday). Volume is $2.1M with strong bid 
support at 72%. Kalshi showing 71.8% - slight arbitrage opportunity. Options 
traders piling into Yes shares."

Original: "What are everyone's thoughts on the election markets?"
Reply: "Polymarket leading with $45M daily volume. Top market at 52.3% showing 
tight race. Historical accuracy on similar races is 83%. Volume surge in 
battleground state markets worth watching."

## Usage Examples

### Example 1: Run with Default Settings

```python
from oracle_automation import OracleXBTAutomationSystem

# Initialize with defaults (1 hour tweets, 5 min monitoring)
system = OracleXBTAutomationSystem()

# Start the automation
system.start()
```

### Example 2: Custom Configuration

```python
from oracle_automation import OracleXBTAutomationSystem

# Tweet every 2 hours, monitor every 10 minutes
system = OracleXBTAutomationSystem(
    hourly_interval=7200,  # 2 hours
    monitoring_interval=600  # 10 minutes
)

system.start()
```

### Example 3: Run Individual Components

**Just hourly tweets:**
```python
from agent import PredictionMarketAgent
from agent.tweet_scheduler import HourlyTweetScheduler

agent = PredictionMarketAgent()
scheduler = HourlyTweetScheduler(agent)

# Post one tweet
scheduler.post_hourly_tweet()
```

**Just monitoring:**
```python
from oracle_realtime_monitor import RealtimeTweetMonitor

monitor = RealtimeTweetMonitor(check_interval=300)
monitor.start_continuous_monitoring()
```

## Command Line Usage

```bash
# Run full automation
python3 oracle_automation.py

# Custom intervals (seconds)
python3 oracle_automation.py --hourly-interval 1800 --monitoring-interval 180

# View statistics only
python3 oracle_automation.py --stats-only

# Run one monitoring cycle (for testing)
python3 oracle_realtime_monitor.py once

# View monitoring stats
python3 oracle_realtime_monitor.py stats
```

## Production Deployment

### Running as a Background Service (Linux/macOS)

**Using systemd (Linux):**

Create `/etc/systemd/system/oraclexbt.service`:

```ini
[Unit]
Description=OracleXBT Automation System
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/oraclyst-python-sdk-main
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python3 oracle_automation.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable oraclexbt
sudo systemctl start oraclexbt
sudo systemctl status oraclexbt
```

**Using screen (simple method):**

```bash
screen -S oraclexbt
python3 oracle_automation.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r oraclexbt
```

**Using launchd (macOS):**

The existing `com.oraclexbt.agent.plist` can be updated to use the new automation system.

### Monitoring and Logs

The system logs to both console and `oraclexbt.log`:

```bash
# View live logs
tail -f oraclexbt.log

# Check for errors
grep ERROR oraclexbt.log

# View statistics
grep "STATISTICS" oraclexbt.log
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_HOURLY_TWEETS` | true | Enable/disable hourly tweeting |
| `HOURLY_TWEET_INTERVAL` | 3600 | Seconds between tweets (3600 = 1 hour) |
| `ENABLE_REALTIME_MONITORING` | true | Enable/disable reply monitoring |
| `MONITORING_CHECK_INTERVAL` | 300 | Seconds between monitoring cycles |
| `MAX_DAILY_TWEETS` | 24 | Maximum tweets per day |
| `MAX_DAILY_REPLIES` | 100 | Maximum replies per day |

### Tweet Scheduler Configuration

```python
config = {
    'content_types': [TweetContentType.MARKET_UPDATE, ...],  # Which types to post
    'randomize_order': True,  # Randomize content order
    'include_threads': False,  # Allow multi-tweet threads
    'max_retries': 3  # Retry attempts for failed tweets
}

scheduler = HourlyTweetScheduler(agent, config=config)
```

## Statistics and Monitoring

The system tracks comprehensive statistics:

- **Total tweets posted** - Hourly tweets generated
- **Total replies posted** - Replies to monitored accounts
- **Success rates** - Tweet/reply success percentages
- **Per-account stats** - Replies per monitored account
- **Uptime** - System running duration
- **Last activity** - Timestamps of last tweet/reply

Access stats:
```python
system.print_statistics()
# or
stats = system.get_status()
```

## Best Practices

1. **Start Conservatively** - Begin with longer intervals (2-3 hours for tweets, 10 min for monitoring) and adjust based on engagement

2. **Monitor Rate Limits** - Twitter has rate limits. The system includes delays but monitor your usage

3. **Review Generated Content** - Periodically check the quality of generated tweets and replies

4. **Track Engagement** - Monitor which tweet types get the most engagement and adjust content_types accordingly

5. **Use Logging** - Keep logs enabled to track system behavior and troubleshoot issues

6. **Backup Reply History** - The `oracle_reply_history.json` file prevents duplicates - back it up regularly

## Troubleshooting

### "Twitter client not available"
- Verify Twitter API credentials in `.env`
- Ensure `tweepy` is installed: `pip install tweepy`

### Tweets not posting
- Check Twitter API rate limits
- Verify account has tweet permissions
- Check logs for specific errors

### Replies not being posted
- Ensure monitored accounts are public
- Check if tweets meet relevance criteria
- Verify reply history file is writable

### High CPU usage
- Increase monitoring interval
- Reduce number of monitored accounts
- Check for infinite loops in logs

## Advanced Customization

### Add Custom Tweet Types

Edit `agent/tweet_scheduler.py`:

```python
class TweetContentType(Enum):
    # Add your custom type
    CUSTOM_INSIGHT = "custom_insight"

# Add prompt in _get_prompt_for_content_type method
TweetContentType.CUSTOM_INSIGHT: """
Your custom prompt here...
""",
```

### Add Monitored Accounts

Edit `oracle_realtime_monitor.py`:

```python
{
    "username": "NewAccount",
    "priority": "high",
    "type": "trader",
    "description": "Description"
}
```

### Customize Reply Logic

Modify `_should_reply_to_tweet()` in `oracle_realtime_monitor.py` to adjust which tweets get replies.

## Performance Considerations

- **Memory**: System uses ~200-400MB RAM
- **CPU**: Minimal when idle, spikes during LLM calls
- **Network**: Depends on monitoring frequency and number of accounts
- **API Costs**: LLM API calls for each tweet/reply generation

## Support and Issues

For issues or questions:
1. Check logs in `oraclexbt.log`
2. Verify configuration in `.env`
3. Test individual components separately
4. Review Twitter API status and rate limits

## Future Enhancements

Potential improvements:
- Machine learning for optimal tweet timing
- Sentiment analysis for reply prioritization
- A/B testing for tweet formats
- Analytics dashboard
- Multi-account support
- Advanced rate limit handling
