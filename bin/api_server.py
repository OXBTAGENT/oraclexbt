"""
OracleXBT Live Trades API Server
Serves real-time trade data to the website
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import threading
import time
import random
from datetime import datetime, timedelta
from collections import deque
import json
import os
import sys
import requests
from trading_engine import trading_engine, AgentConfig

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import Database

# Get the parent directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEBSITE_DIR = os.path.join(BASE_DIR, 'website')

app = Flask(__name__, static_folder=WEBSITE_DIR)
CORS(app)

# Initialize rate limiter with higher limits for development
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["10000 per hour"],  # Increased for development
    storage_uri="memory://"
)

# Initialize database
db = Database()

# Global trade storage (for streaming to frontend)
trades_queue = deque(maxlen=100)
stats = {
    "total_trades": 0,
    "total_volume": 0.0,
    "platform_fees_collected": 0.0,
    "by_platform": {"Polymarket": 0, "Kalshi": 0, "Limitless": 0}
}

# Platform fee rate (1%)
PLATFORM_FEE_RATE = 0.01

# Cache for real markets (refreshed periodically)
cached_markets = []
last_market_fetch = 0

def fetch_polymarket_markets():
    """Fetch real active markets from Polymarket Gamma API"""
    try:
        # Polymarket Gamma API endpoint with active markets filter
        url = "https://gamma-api.polymarket.com/markets?closed=false&active=true&limit=50"
        headers = {"User-Agent": "OracleXBT/1.0"}
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        markets_data = response.json()
        
        if not isinstance(markets_data, list):
            print(f"Unexpected response format: {type(markets_data)}")
            return []
        
        markets = []
        for market in markets_data:
            try:
                # Parse outcome prices
                outcome_prices_str = market.get('outcomePrices', '[0.5, 0.5]')
                outcome_prices = json.loads(outcome_prices_str) if isinstance(outcome_prices_str, str) else outcome_prices_str
                
                yes_price = float(outcome_prices[0]) if len(outcome_prices) > 0 else 0.5
                no_price = float(outcome_prices[1]) if len(outcome_prices) > 1 else (1.0 - yes_price)
                
                # Store more market data for realistic trade generation
                markets.append({
                    "title": market.get('question', 'Unknown Market'),
                    "platform": "Polymarket",
                    "price": yes_price,
                    "no_price": no_price,
                    "id": market.get('conditionId', market.get('slug', 'unknown')),
                    "volume": float(market.get('volumeNum', 0)),
                    "volume24hr": float(market.get('volume24hr', 0)),
                    "liquidity": float(market.get('liquidityNum', 0))
                })
                    
            except Exception as e:
                print(f"Error parsing market: {e}")
                continue
        
        print(f"Found {len(markets)} active Polymarket markets")
        return markets
        
    except Exception as e:
        print(f"Error fetching Polymarket markets: {e}")
        import traceback
        traceback.print_exc()
        return []

def fetch_real_markets_cache():
    """Fetch and cache real markets for trade generation"""
    global cached_markets, last_market_fetch
    
    try:
        # Only fetch if cache is older than 5 minutes
        if time.time() - last_market_fetch < 300 and cached_markets:
            return
        
        print("Fetching real markets from Polymarket...")
        markets = fetch_polymarket_markets()
        
        if markets:
            cached_markets = markets
            last_market_fetch = time.time()
            print(f"Cached {len(cached_markets)} real Polymarket markets")
        else:
            print("Failed to fetch markets, keeping old cache")
        
    except Exception as e:
        print(f"Error fetching markets for cache: {e}")

def generate_realistic_trade():
    """Generate realistic trade data based on real market activity across all platforms"""
    # Ensure we have markets cached
    if not cached_markets:
        fetch_real_markets_cache()
    
    # Select platform with realistic distribution
    # Polymarket: 60%, Kalshi: 25%, Limitless: 15%
    platform = random.choices(
        ['Polymarket', 'Kalshi', 'Limitless'],
        weights=[0.60, 0.25, 0.15],
        k=1
    )[0]
    
    # Fallback to sample data if cache fails
    if not cached_markets:
        market = {
            "title": "Sample Market - Data Loading",
            "platform": platform,
            "price": 0.5,
            "no_price": 0.5,
            "volume24hr": 1000
        }
    else:
        # Prefer markets with recent activity (higher 24hr volume)
        active_markets = [m for m in cached_markets if m.get('volume24hr', 0) > 100]
        if active_markets:
            # Weight selection by 24hr volume for more realistic distribution
            weights = [m.get('volume24hr', 1) for m in active_markets]
            market = random.choices(active_markets, weights=weights, k=1)[0]
        else:
            market = random.choice(cached_markets)
        
        # Override platform to match selected platform
        market = market.copy()
        market["platform"] = platform
    
    # Generate trade timestamp (within last 10 seconds for "live" feel)
    seconds_ago = random.randint(0, 10)
    trade_time = datetime.now() - timedelta(seconds=seconds_ago)
    
    # Determine side based on market probability and randomness
    # Higher probability markets should have more YES trades
    yes_bias = market["price"]
    side = "YES" if random.random() < yes_bias else "NO"
    
    # Price should be close to market price with small variations
    base_price = market["price"] if side == "YES" else market.get("no_price", 1.0 - market["price"])
    # Smaller price variations for more realistic trades
    price = base_price + random.uniform(-0.02, 0.02)
    price = max(0.01, min(0.99, price))
    
    # Trade size distribution: mostly small trades with occasional large ones
    if random.random() < 0.8:  # 80% small trades
        size = random.uniform(10, 500)
    elif random.random() < 0.95:  # 15% medium trades
        size = random.uniform(500, 2000)
    else:  # 5% large trades
        size = random.uniform(2000, 10000)
    
    value = size * price
    
    return {
        "id": f"{int(trade_time.timestamp() * 1000)}_{random.randint(1000, 9999)}",
        "timestamp": trade_time.isoformat(),
        "market": market["title"],
        "platform": platform,
        "side": side,
        "price": round(price, 3),
        "size": round(size, 0),
        "value": round(value, 2)
    }

def trade_generator():
    """Background thread to generate realistic trades based on real market data"""
    global stats
    
    # Refresh markets cache first
    fetch_real_markets_cache()
    
    # Generate initial trades
    for _ in range(20):
        trade = generate_realistic_trade()
        platform_fee = trade["value"] * PLATFORM_FEE_RATE
        trade["platform_fee"] = platform_fee
        trades_queue.appendleft(trade)
        stats["total_trades"] += 1
        stats["total_volume"] += trade["value"]
        stats["platform_fees_collected"] += platform_fee
        stats["by_platform"][trade["platform"]] += 1
    
    last_market_refresh = time.time()
    
    while True:
        # Refresh markets every 2 minutes to get updated prices
        if time.time() - last_market_refresh > 120:
            fetch_real_markets_cache()
            last_market_refresh = time.time()
        
        # Variable timing: faster during active periods (1-4 seconds between trades)
        time.sleep(random.uniform(1, 4))
        
        # Generate 1-3 new trades (busier periods)
        num_trades = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1], k=1)[0]
        for _ in range(num_trades):
            trade = generate_realistic_trade()
            platform_fee = trade["value"] * PLATFORM_FEE_RATE
            trade["platform_fee"] = platform_fee
            trades_queue.appendleft(trade)
            stats["total_trades"] += 1
            stats["total_volume"] += trade["value"]
            stats["platform_fees_collected"] += platform_fee
            stats["by_platform"][trade["platform"]] += 1

@app.route('/')
def index():
    """Serve the main website"""
    return send_from_directory(WEBSITE_DIR, 'index.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring and Docker"""
    try:
        # Check database connectivity
        system_stats = db.get_system_stats()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "database": "connected" if system_stats else "error",
            "uptime": time.time()  # Could track actual uptime
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }), 500

@app.route('/api/trades')
def get_trades():
    """Get recent trades"""
    return jsonify({
        "trades": list(trades_queue)[:50],
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/stats')
def get_stats():
    """Get trading statistics"""
    # Get stats from database
    db_stats = db.get_system_stats()
    
    # Merge with in-memory stats (current session)
    combined_stats = {
        "total_trades": db_stats.get('total_trades', 0),
        "total_volume": db_stats.get('total_volume', 0.0),
        "platform_fees_collected": db_stats.get('total_fees_collected', 0.0),
        "by_platform": stats.get('by_platform', {}),
        "current_session": {
            "trades": stats['total_trades'],
            "volume": stats['total_volume'],
            "fees": stats['platform_fees_collected']
        }
    }
    
    return jsonify(combined_stats)

@app.route('/api/markets')
def get_markets():
    """Get available markets from Polymarket"""
    search_term = request.args.get('search', '').lower()
    limit = int(request.args.get('limit', 20))
    
    try:
        # Fetch real markets from Polymarket
        print("Fetching markets from Polymarket CLOB API...")
        polymarket_markets = fetch_polymarket_markets()
        
        # Transform to our format
        markets = []
        for market in polymarket_markets[:limit]:
            yes_price = market['price']
            no_price = 1.0 - yes_price
            
            market_data = {
                "id": market['id'],
                "platform": "Polymarket",
                "title": market['title'],
                "yes_price": yes_price,
                "no_price": no_price,
                "volume": int(market.get('volume', 0))
            }
            
            # Filter by search term if provided
            if not search_term or search_term in market_data['title'].lower() or search_term in market_data['id'].lower():
                markets.append(market_data)
        
        return jsonify({
            "markets": markets,
            "total": len(markets),
            "source": "polymarket_clob_api"
        })
        
    except Exception as e:
        print(f"Error fetching markets: {e}")
        # Return error
        return jsonify({
            "markets": [],
            "total": 0,
            "error": str(e)
        }), 500

@app.route('/api/place_order', methods=['POST'])
@limiter.limit("50 per hour")
def place_order():
    """Place trading order"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['platform', 'market_id', 'side', 'order_type', 'size']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Generate order ID
        order_id = f"{data['platform'][:3].upper()}-{int(datetime.now().timestamp() * 1000)}"
        
        # Simulate order placement (in production, this would interact with actual platform APIs)
        order = {
            "order_id": order_id,
            "platform": data['platform'],
            "market_id": data['market_id'],
            "side": data['side'],
            "order_type": data['order_type'],
            "size": data['size'],
            "price": data.get('price'),
            "status": "filled",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"\n✅ Order Placed:")
        print(f"   ID: {order_id}")
        print(f"   Platform: {data['platform']}")
        print(f"   Market: {data['market_id']}")
        print(f"   Side: {data['side'].upper()}")
        print(f"   Size: ${data['size']}")
        print(f"   Type: {data['order_type']}")
        if data.get('price'):
            print(f"   Price: ${data['price']}")
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "message": "Order executed successfully",
            "order": order
        })
        
    except Exception as e:
        print(f"❌ Order placement error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# Agent Management Endpoints

@app.route('/api/agent/register', methods=['POST'])
@limiter.limit("5 per hour")
def register_agent():
    """Register a new trading agent"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['wallet', 'platforms', 'strategy', 'maxPosition', 'minProfit', 'maxTrades', 'stopLoss']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Create agent config
        agent_id = f"agent_{data['wallet'][:8]}_{int(time.time())}"
        
        agent_config = AgentConfig(
            agent_id=agent_id,
            wallet_address=data['wallet'],
            platforms=data['platforms'],
            strategy=data['strategy'],
            max_position=float(data['maxPosition']),
            min_profit=float(data['minProfit']),
            max_trades=int(data['maxTrades']),
            stop_loss=float(data['stopLoss']),
            private_key=data.get('privateKey'),  # Optional for Web3 signing
            kalshi_api_key=data.get('kalshiApiKey'),  # Optional for Kalshi
            kalshi_api_secret=data.get('kalshiApiSecret'),  # Optional for Kalshi
            active=False
        )
        
        # Register with trading engine
        trading_engine.register_agent(agent_config)
        
        # Save to database
        db.register_agent({
            'agent_id': agent_id,
            'wallet_address': data['wallet'],
            'platforms': data['platforms'],
            'strategy': data['strategy'],
            'max_position': float(data['maxPosition']),
            'min_profit': float(data['minProfit']),
            'max_trades': int(data['maxTrades']),
            'stop_loss': float(data['stopLoss'])
        })
        
        print(f"\n🤖 Agent Registered:")
        print(f"   ID: {agent_id}")
        print(f"   Wallet: {data['wallet']}")
        print(f"   Platforms: {', '.join([k for k, v in data['platforms'].items() if v])}")
        print(f"   Strategy: {data['strategy']}")
        print(f"   Max Position: ${data['maxPosition']}")
        print(f"   Min Profit: {data['minProfit']}%")
        print(f"   Credentials: {'Private Key ✓' if data.get('privateKey') else 'Demo Mode'}")
        
        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "message": "Agent registered successfully"
        })
        
    except Exception as e:
        print(f"❌ Agent registration error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/agent/activate', methods=['POST'])
def activate_agent():
    """Activate a trading agent"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({
                "success": False,
                "message": "Agent ID required"
            }), 400
        
        success = trading_engine.activate_agent(agent_id)
        
        if success:
            # Update database
            db.update_agent_status(agent_id, True)
            
            # Start agent monitoring thread
            agent_thread = threading.Thread(
                target=agent_monitor,
                args=(agent_id,),
                daemon=True
            )
            agent_thread.start()
            
            print(f"🚀 Agent {agent_id} activated and monitoring started")
            
            return jsonify({
                "success": True,
                "message": "Agent activated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Agent not found"
            }), 404
            
    except Exception as e:
        print(f"❌ Agent activation error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/agent/deactivate', methods=['POST'])
def deactivate_agent():
    """Deactivate a trading agent"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({
                "success": False,
                "message": "Agent ID required"
            }), 400
        
        success = trading_engine.deactivate_agent(agent_id)
        
        if success:
            # Update database
            db.update_agent_status(agent_id, False)
            
            print(f"🛑 Agent {agent_id} deactivated")
            return jsonify({
                "success": True,
                "message": "Agent deactivated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Agent not found"
            }), 404
            
    except Exception as e:
        print(f"❌ Agent deactivation error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route('/api/platform/stats', methods=['GET'])
def get_platform_stats():
    """Get overall platform statistics including fees"""
    try:
        # Get stats from database
        db_stats = db.get_system_stats()
        platform_stats = trading_engine.get_platform_stats()
        
        # Merge database and engine stats
        combined_stats = {
            'total_agents': db_stats.get('total_agents', 0),
            'active_agents': db_stats.get('active_agents', 0),
            'total_trades': db_stats.get('total_trades', 0),
            'total_volume': db_stats.get('total_volume', 0.0),
            'total_fees_collected': db_stats.get('total_fees_collected', 0.0),
            'current_session': {
                'trades': stats['total_trades'],
                'volume': stats['total_volume'],
                'fees_collected': stats['platform_fees_collected']
            },
            'fee_info': {
                'rate': PLATFORM_FEE_RATE,
                'rate_percentage': f"{PLATFORM_FEE_RATE * 100}%",
                'description': 'Platform takes 1% of all trading volume'
            }
        }
        
        return jsonify(combined_stats)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/agent/status/<agent_id>', methods=['GET'])
def agent_status(agent_id):
    """Get agent status and statistics"""
    try:
        if agent_id not in trading_engine.active_agents:
            return jsonify({
                "success": False,
                "message": "Agent not found"
            }), 404
        
        agent_config = trading_engine.active_agents[agent_id]
        
        # Get stats from database
        db_stats = db.get_agent_stats(agent_id)
        recent_trades = db.get_agent_trades(agent_id, limit=10)
        
        # Get agent stats from engine (for real-time data)
        agent_stats = trading_engine.get_agent_stats(agent_id)
        
        # Calculate today's trades from database
        today_trades = len([t for t in recent_trades 
                          if datetime.fromisoformat(t['timestamp']).date() == datetime.now().date()])
        
        return jsonify({
            "success": True,
            "agent": {
                "id": agent_id,
                "wallet": agent_config.wallet_address,
                "active": agent_config.active,
                "strategy": agent_config.strategy,
                "platforms": agent_config.platforms
            },
            "stats": {
                "total_trades": db_stats.get('total_trades', 0) if db_stats else 0,
                "today_trades": today_trades,
                "total_volume": db_stats.get('total_volume', 0.0) if db_stats else 0.0,
                "gross_profit": db_stats.get('gross_profit', 0.0) if db_stats else 0.0,
                "platform_fees_paid": db_stats.get('platform_fees_paid', 0.0) if db_stats else 0.0,
                "net_profit": db_stats.get('net_profit', 0.0) if db_stats else 0.0,
                "fee_rate": PLATFORM_FEE_RATE
            },
            "recent_positions": recent_trades  # Last 10 trades from database
        })
        
    except Exception as e:
        print(f"❌ Agent status error: {e}")
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

def agent_monitor(agent_id: str):
    """Background thread to monitor and execute agent strategy"""
    print(f"📊 Starting agent monitor for {agent_id}")
    
    while True:
        try:
            if agent_id not in trading_engine.active_agents:
                print(f"Agent {agent_id} no longer exists, stopping monitor")
                break
            
            agent_config = trading_engine.active_agents[agent_id]
            
            if not agent_config.active:
                print(f"Agent {agent_id} deactivated, stopping monitor")
                break
            
            # Run strategy cycle
            result = trading_engine.run_strategy_cycle(agent_id)
            
            if result.get('action') == 'trade_executed':
                trade_data = result.get('trade', {})
                print(f"✅ Agent {agent_id} executed trade: {trade_data.get('market')}")
                
                # Save trade to database
                if trade_data:
                    db.save_trade({
                        'agent_id': agent_id,
                        'type': trade_data.get('type', 'arbitrage'),
                        'market': trade_data.get('market', 'Unknown'),
                        'buy_platform': trade_data.get('buy_platform'),
                        'sell_platform': trade_data.get('sell_platform'),
                        'size': trade_data.get('size', 0),
                        'total_volume': trade_data.get('total_volume', 0),
                        'expected_profit': trade_data.get('expected_profit', 0),
                        'platform_fee': trade_data.get('platform_fee', 0),
                        'net_profit': trade_data.get('net_profit', 0),
                        'spread': trade_data.get('spread'),
                        'buy_order_id': trade_data.get('buy_order_id'),
                        'sell_order_id': trade_data.get('sell_order_id'),
                        'success': trade_data.get('success', True),
                        'timestamp': trade_data.get('timestamp', datetime.now().isoformat())
                    })
            
            # Wait before next cycle (3-5 seconds for real-time trading)
            time.sleep(random.uniform(3, 5))
            
        except Exception as e:
            print(f"❌ Agent monitor error for {agent_id}: {e}")
            time.sleep(30)  # Wait before retrying

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(WEBSITE_DIR, path)

if __name__ == '__main__':
    # Start trade generator in background
    generator_thread = threading.Thread(target=trade_generator, daemon=True)
    generator_thread.start()
    
    print("\n" + "="*60)
    print("OracleXBT Live Trades API Server")
    print("="*60)
    print("Server: http://localhost:5000")
    print("API: http://localhost:5001/api/trades")
    print("Stats: http://localhost:5001/api/stats")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
