"""
API Integration Guide for OracleXBT
Real-time data from all major prediction market platforms
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Any, Optional

# ===========================================
# 1. EXISTING INTEGRATIONS (via Oraclyst SDK)
# ===========================================

@dataclass
class APIConnectionGuide:
    platform: str
    status: str
    auth_method: str
    api_keys_needed: List[str]
    setup_instructions: str
    example_usage: str

# Current integrations
EXISTING_APIS = [
    APIConnectionGuide(
        platform="Polymarket",
        status="✅ Connected via Oraclyst SDK",
        auth_method="Public API (no key needed)",
        api_keys_needed=[],
        setup_instructions="Already working! Uses oraclyst_sdk.OraclystClient()",
        example_usage="""
from oraclyst_sdk import OraclystClient
client = OraclystClient()
markets = client.list_markets(provider="polymarket", limit=10)
"""
    ),
    
    APIConnectionGuide(
        platform="Kalshi",
        status="✅ Connected via Oraclyst SDK", 
        auth_method="Public API (no key needed for market data)",
        api_keys_needed=["KALSHI_API_KEY", "KALSHI_API_SECRET"],  # For trading only
        setup_instructions="Already working for market data! Add keys for trading.",
        example_usage="""
from oraclyst_sdk import OraclystClient
client = OraclystClient()
markets = client.list_markets(provider="kalshi", limit=10)
"""
    ),
    
    APIConnectionGuide(
        platform="Limitless",
        status="✅ Connected via Oraclyst SDK",
        auth_method="Public API (no key needed)",
        api_keys_needed=[],
        setup_instructions="Already working! Uses oraclyst_sdk.OraclystClient()",
        example_usage="""
from oraclyst_sdk import OraclystClient
client = OraclystClient()
markets = client.list_markets(provider="limitless", limit=10)
"""
    )
]

# ===========================================
# 2. NEW INTEGRATIONS TO ADD
# ===========================================

NEW_APIS = [
    APIConnectionGuide(
        platform="Manifold Markets",
        status="🟡 Available - needs setup",
        auth_method="API Key (optional, increases rate limits)",
        api_keys_needed=["MANIFOLD_API_KEY"],
        setup_instructions="""
1. Go to https://manifold.markets/profile
2. Click 'API' tab
3. Generate API key
4. Add to .env: MANIFOLD_API_KEY=your-key
""",
        example_usage="""
from agent.platforms import ManifoldClient
client = ManifoldClient()
markets = client.search_markets("Bitcoin")
"""
    ),
    
    APIConnectionGuide(
        platform="Metaculus",
        status="🟡 Available - needs setup",
        auth_method="API Key (optional, for personal forecasts)",
        api_keys_needed=["METACULUS_API_KEY"],
        setup_instructions="""
1. Go to https://www.metaculus.com/accounts/profile/
2. Generate API token
3. Add to .env: METACULUS_API_KEY=your-key
""",
        example_usage="""
from agent.platforms import MetaculusClient
client = MetaculusClient()
questions = client.get_questions(status="open")
"""
    ),
    
    APIConnectionGuide(
        platform="PredictIt",
        status="🔴 Limited - API deprecated",
        auth_method="OAuth 2.0 (complex setup)",
        api_keys_needed=["PREDICTIT_CLIENT_ID", "PREDICTIT_CLIENT_SECRET"],
        setup_instructions="""
⚠️  PredictIt API is mostly deprecated.
For market data only:
1. Use web scraping approach
2. Or partner API access (enterprise only)
""",
        example_usage="""
# Limited functionality
from agent.platforms import PredictItClient
client = PredictItClient()
markets = client.get_markets()  # Basic market list only
"""
    )
]

# ===========================================
# 3. REAL-TIME DATA SETUP
# ===========================================

def setup_realtime_data():
    """Set up real-time data connections for OracleXBT"""
    
    print("🔗 Setting up real-time prediction market data...")
    
    # Step 1: Test existing connections
    print("\\n1. Testing existing connections (Oraclyst SDK):")
    try:
        from oraclyst_sdk import OraclystClient
        client = OraclystClient()
        
        # Test each provider
        for provider in ["polymarket", "kalshi", "limitless"]:
            try:
                markets = client.list_markets(provider=provider, limit=1)
                print(f"   ✅ {provider.title()}: Connected")
            except Exception as e:
                print(f"   ❌ {provider.title()}: Error - {e}")
                
    except ImportError:
        print("   ❌ Oraclyst SDK not found")
    
    # Step 2: Check API keys in environment
    print("\\n2. Checking API key configuration:")
    
    required_keys = [
        "TWITTER_API_KEY", "TWITTER_API_SECRET", 
        "ANTHROPIC_API_KEY",  # or OPENAI_API_KEY
        "MANIFOLD_API_KEY",   # optional
        "METACULUS_API_KEY",  # optional
    ]
    
    for key in required_keys:
        if os.getenv(key):
            print(f"   ✅ {key}: Configured")
        else:
            status = "optional" if "MANIFOLD" in key or "METACULUS" in key else "REQUIRED"
            print(f"   ⚠️  {key}: Missing ({status})")
    
    # Step 3: Test aggregator
    print("\\n3. Testing unified aggregator:")
    try:
        from agent.platforms import PredictionMarketAggregator
        
        aggregator = PredictionMarketAggregator()
        results = aggregator.search_all("test", limit=1)
        
        print(f"   ✅ Aggregator working: Found {len(results)} results")
        
    except Exception as e:
        print(f"   ❌ Aggregator error: {e}")
    
    print("\\n🎯 Setup complete! Real-time data ready.")

# ===========================================
# 4. LIVE DATA EXAMPLES
# ===========================================

def get_live_data_examples():
    """Examples of getting live data from each platform"""
    
    examples = {
        "polymarket_live": """
# Get trending Polymarket markets
from oraclyst_sdk import OraclystClient

client = OraclystClient()
markets = client.list_markets(
    provider="polymarket",
    category="Politics", 
    limit=10,
    sort="volume"  # Most active
)

for market in markets:
    print(f"{market.title}: {market.probability:.1%} - ${market.volume:,.0f}")
""",
        
        "cross_platform_arbitrage": """
# Find arbitrage opportunities across platforms  
from agent.platforms import PredictionMarketAggregator

aggregator = PredictionMarketAggregator()
results = aggregator.search_all("Bitcoin", limit=20)

# Group by similar events
events = {}
for market in results:
    key = market.title.lower()
    if key not in events:
        events[key] = []
    events[key].append(market)

# Find arbitrage
for event, markets in events.items():
    if len(markets) > 1:
        prices = [m.probability for m in markets if m.probability]
        if prices and max(prices) - min(prices) > 0.05:  # 5%+ spread
            print(f"⚡ Arbitrage: {event}")
            for m in markets:
                print(f"  {m.platform}: {m.probability:.1%}")
""",
        
        "real_time_monitoring": """
# Set up real-time monitoring
import time
from agent import PredictionMarketAgent

agent = PredictionMarketAgent()

def monitor_markets():
    while True:
        # Check for new opportunities
        response = agent.chat("Find the top 3 arbitrage opportunities right now")
        
        if "arbitrage" in response.lower():
            # Post to Twitter
            agent.chat("Tweet about the best arbitrage opportunity you found")
            
        time.sleep(300)  # Check every 5 minutes

# Run monitoring (in production, use proper scheduling)
# monitor_markets()
""",
        
        "platform_aggregation": """
# Get data from all platforms at once
from agent.platforms import PredictionMarketAggregator

aggregator = PredictionMarketAggregator()

# Search across all platforms
all_bitcoin_markets = aggregator.search_all("Bitcoin", limit=50)

# Group by platform
by_platform = {}
for market in all_bitcoin_markets:
    if market.platform not in by_platform:
        by_platform[market.platform] = []
    by_platform[market.platform].append(market)

# Compare platform activity
for platform, markets in by_platform.items():
    total_volume = sum(m.volume or 0 for m in markets)
    avg_price = sum(m.probability or 0 for m in markets) / len(markets)
    
    print(f"{platform}: {len(markets)} markets, ${total_volume:,.0f} volume, {avg_price:.1%} avg")
"""
    }
    
    return examples

# ===========================================
# 5. API RATE LIMITS & BEST PRACTICES
# ===========================================

RATE_LIMITS = {
    "polymarket": {
        "requests_per_minute": 60,
        "requests_per_hour": 3600,
        "best_practice": "Use pagination, cache results, batch requests"
    },
    "kalshi": {
        "requests_per_minute": 100,
        "requests_per_hour": 6000,
        "best_practice": "Use WebSocket for real-time, REST for queries"
    },
    "manifold": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "best_practice": "Get API key for higher limits, use efficient queries"
    },
    "metaculus": {
        "requests_per_minute": 30,
        "requests_per_hour": 1000,
        "best_practice": "Focus on specific question sets, cache forecasts"
    }
}

if __name__ == "__main__":
    # Run the setup
    setup_realtime_data()
    
    print("\\n📚 Example usage:")
    examples = get_live_data_examples()
    print(examples["polymarket_live"])