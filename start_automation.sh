#!/bin/bash

# OracleXBT Automation Quick Start Script
# Starts the hourly tweeting and real-time reply monitoring system

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        OracleXBT Prediction Market Agent Automation          ║"
echo "║    Hourly Tweets + Real-Time Reply Monitoring System         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your API credentials."
    echo "See .env.example for reference."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed!"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import tweepy, anthropic, schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies detected. Installing..."
    pip3 install tweepy anthropic schedule python-dotenv
fi

echo "✅ Dependencies OK"
echo ""

# Display configuration
echo "⚙️  Configuration:"
echo "   - Hourly tweets: Every 1 hour"
echo "   - Monitoring check: Every 5 minutes"
echo "   - Monitored accounts: 25+"
echo ""

# Parse command line arguments
MODE="full"
if [ "$1" == "tweets-only" ]; then
    MODE="tweets"
    echo "📝 Running in TWEETS ONLY mode"
elif [ "$1" == "monitor-only" ]; then
    MODE="monitor"
    echo "👁️  Running in MONITOR ONLY mode"
elif [ "$1" == "test" ]; then
    MODE="test"
    echo "🧪 Running in TEST mode (one cycle)"
elif [ "$1" == "stats" ]; then
    MODE="stats"
    echo "📊 Showing statistics..."
fi

echo ""
echo "🚀 Starting OracleXBT Automation..."
echo "   Press Ctrl+C to stop gracefully"
echo ""
sleep 2

# Run based on mode
case $MODE in
    "full")
        python3 oracle_automation.py
        ;;
    "tweets")
        python3 -c "
from agent import PredictionMarketAgent
from agent.tweet_scheduler import HourlyTweetScheduler
import time

agent = PredictionMarketAgent()
scheduler = HourlyTweetScheduler(agent)

print('Starting hourly tweet scheduler...')
while True:
    scheduler.post_hourly_tweet()
    print('Waiting 1 hour until next tweet...')
    time.sleep(3600)
"
        ;;
    "monitor")
        python3 oracle_realtime_monitor.py
        ;;
    "test")
        echo "Running one monitoring cycle..."
        python3 oracle_realtime_monitor.py once
        echo ""
        echo "Testing tweet generation..."
        python3 -c "
from agent import PredictionMarketAgent
from agent.tweet_scheduler import HourlyTweetScheduler

agent = PredictionMarketAgent()
scheduler = HourlyTweetScheduler(agent)
tweet = scheduler.generate_hourly_tweet()
print(f'Generated tweet: {tweet}')
"
        ;;
    "stats")
        python3 oracle_automation.py --stats-only
        ;;
esac

echo ""
echo "✅ OracleXBT Automation stopped"
