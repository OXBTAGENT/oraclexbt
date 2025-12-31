#!/usr/bin/env python3
"""
Test script for OracleXBT Automation System
Verifies all components are working correctly
"""

import sys
import os
from datetime import datetime

print("=" * 70)
print("🧪 OracleXBT Automation System Test Suite")
print("=" * 70)
print()

# Test 1: Environment variables
print("Test 1: Checking environment variables...")
required_vars = [
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET", 
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_TOKEN_SECRET",
    "ANTHROPIC_API_KEY"
]

missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ FAIL: Missing environment variables: {', '.join(missing_vars)}")
    print("   Please add them to your .env file")
    sys.exit(1)
else:
    print("✅ PASS: All required environment variables present")
print()

# Test 2: Python packages
print("Test 2: Checking Python packages...")
required_packages = [
    ("tweepy", "Twitter API"),
    ("anthropic", "Anthropic LLM"),
    ("schedule", "Scheduling"),
    ("dotenv", "Environment loading")
]

missing_packages = []
for package, description in required_packages:
    try:
        __import__(package.replace("-", "_"))
        print(f"   ✓ {package} ({description})")
    except ImportError:
        missing_packages.append(package)
        print(f"   ✗ {package} ({description}) - MISSING")

if missing_packages:
    print(f"\n❌ FAIL: Missing packages: {', '.join(missing_packages)}")
    print(f"   Install with: pip install {' '.join(missing_packages)}")
    sys.exit(1)
else:
    print("✅ PASS: All required packages installed")
print()

# Test 3: Agent initialization
print("Test 3: Initializing PredictionMarketAgent...")
try:
    from agent import PredictionMarketAgent
    agent = PredictionMarketAgent()
    print("✅ PASS: Agent initialized successfully")
except Exception as e:
    print(f"❌ FAIL: Could not initialize agent: {e}")
    sys.exit(1)
print()

# Test 4: Twitter client
print("Test 4: Testing Twitter client...")
try:
    from agent.twitter_tools import TwitterTools
    twitter = TwitterTools()
    if twitter.twitter_client.is_ready:
        print("✅ PASS: Twitter client connected")
    else:
        print("❌ FAIL: Twitter client not ready")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: Twitter client error: {e}")
    sys.exit(1)
print()

# Test 5: Tweet scheduler
print("Test 5: Testing tweet scheduler...")
try:
    from agent.tweet_scheduler import HourlyTweetScheduler
    scheduler = HourlyTweetScheduler(agent)
    
    print("   Generating test tweet...")
    test_tweet = scheduler.generate_hourly_tweet()
    
    if test_tweet and len(test_tweet) > 0:
        print(f"   Generated: {test_tweet[:100]}...")
        print("✅ PASS: Tweet scheduler working")
    else:
        print("❌ FAIL: Could not generate tweet")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: Tweet scheduler error: {e}")
    sys.exit(1)
print()

# Test 6: Real-time monitor
print("Test 6: Testing real-time monitor...")
try:
    from oracle_realtime_monitor import RealtimeTweetMonitor
    monitor = RealtimeTweetMonitor(check_interval=60)
    
    account_count = len(monitor.monitored_accounts)
    print(f"   Monitoring {account_count} accounts")
    
    if account_count >= 20:
        print("✅ PASS: Monitor initialized with accounts")
    else:
        print(f"⚠️  WARNING: Only {account_count} accounts configured")
except Exception as e:
    print(f"❌ FAIL: Monitor error: {e}")
    sys.exit(1)
print()

# Test 7: Automation system
print("Test 7: Testing automation system...")
try:
    from oracle_automation import OracleXBTAutomationSystem
    system = OracleXBTAutomationSystem(
        hourly_interval=3600,
        monitoring_interval=300
    )
    
    status = system.get_status()
    print(f"   System status: {status}")
    print("✅ PASS: Automation system initialized")
except Exception as e:
    print(f"❌ FAIL: Automation system error: {e}")
    sys.exit(1)
print()

# Test 8: Configuration
print("Test 8: Testing configuration...")
try:
    from agent.config import AgentConfig
    config = AgentConfig.from_env()
    
    print(f"   Hourly tweets: {config.enable_hourly_tweets}")
    print(f"   Tweet interval: {config.hourly_tweet_interval}s")
    print(f"   Monitoring: {config.enable_realtime_monitoring}")
    print(f"   Monitoring interval: {config.monitoring_check_interval}s")
    print("✅ PASS: Configuration loaded")
except Exception as e:
    print(f"❌ FAIL: Configuration error: {e}")
    sys.exit(1)
print()

# Summary
print("=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print()
print("Your OracleXBT Automation System is ready to run!")
print()
print("Next steps:")
print("  1. Test single tweet:    python3 -c \"from agent import PredictionMarketAgent; from agent.tweet_scheduler import HourlyTweetScheduler; agent = PredictionMarketAgent(); scheduler = HourlyTweetScheduler(agent); print(scheduler.generate_hourly_tweet())\"")
print("  2. Test monitoring:      python3 oracle_realtime_monitor.py once")
print("  3. Run full system:      ./start_automation.sh")
print()
print("For more info: See AUTOMATION_QUICKSTART.md")
print()
