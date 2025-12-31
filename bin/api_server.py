"""
OracleXBT Live Trades API Server
Serves real-time trade data to the website
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import threading
import time
import random
from datetime import datetime, timedelta
from collections import deque
import json

app = Flask(__name__, static_folder='website')
CORS(app)

# Global trade storage
trades_queue = deque(maxlen=100)
stats = {
    "total_trades": 0,
    "total_volume": 0.0,
    "by_platform": {"Polymarket": 0, "Kalshi": 0, "Limitless": 0}
}

SAMPLE_MARKETS = [
    {"title": "Will Trump win the 2024 Presidential Election?", "platform": "Polymarket", "price": 0.52},
    {"title": "Bitcoin above $100K by March 2026?", "platform": "Kalshi", "price": 0.67},
    {"title": "Will AI achieve AGI by 2027?", "platform": "Limitless", "price": 0.23},
    {"title": "Democrats win Senate majority in 2026?", "platform": "Polymarket", "price": 0.48},
    {"title": "Ethereum above $5K by June 2026?", "platform": "Kalshi", "price": 0.58},
    {"title": "US Federal Reserve cuts rates by March 2026?", "platform": "Polymarket", "price": 0.71},
    {"title": "SpaceX successfully lands on Mars by 2028?", "platform": "Limitless", "price": 0.15},
    {"title": "Will the NY Knicks make the NBA Finals 2026?", "platform": "Polymarket", "price": 0.12},
    {"title": "US GDP growth above 3% in Q1 2026?", "platform": "Kalshi", "price": 0.45},
    {"title": "Tesla stock above $400 by end of 2026?", "platform": "Polymarket", "price": 0.62},
]

def generate_trade():
    """Generate a simulated trade"""
    market = random.choice(SAMPLE_MARKETS)
    
    seconds_ago = random.randint(0, 5)
    trade_time = datetime.now() - timedelta(seconds=seconds_ago)
    
    side = random.choice(["YES", "NO"])
    price = market["price"] + random.uniform(-0.05, 0.05)
    price = max(0.01, min(0.99, price))
    size = random.uniform(100, 5000)
    value = size * price
    
    return {
        "id": f"{int(trade_time.timestamp() * 1000)}_{random.randint(1000, 9999)}",
        "timestamp": trade_time.isoformat(),
        "market": market["title"],
        "platform": market["platform"],
        "side": side,
        "price": round(price, 3),
        "size": round(size, 0),
        "value": round(value, 2)
    }

def trade_generator():
    """Background thread to generate trades"""
    global stats
    
    # Generate initial trades
    for _ in range(20):
        trade = generate_trade()
        trades_queue.appendleft(trade)
        stats["total_trades"] += 1
        stats["total_volume"] += trade["value"]
        stats["by_platform"][trade["platform"]] += 1
    
    while True:
        time.sleep(random.uniform(1, 3))
        
        # Generate 1-2 new trades
        num_trades = random.randint(1, 2)
        for _ in range(num_trades):
            trade = generate_trade()
            trades_queue.appendleft(trade)
            stats["total_trades"] += 1
            stats["total_volume"] += trade["value"]
            stats["by_platform"][trade["platform"]] += 1

@app.route('/')
def index():
    """Serve the main website"""
    return send_from_directory('website', 'index.html')

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
    return jsonify(stats)

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('website', path)

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
