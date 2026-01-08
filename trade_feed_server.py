#!/usr/bin/env python3
"""
OracleXBT Trade Feed Server
Provides live trade data for the website dashboard
"""

from flask import Flask, jsonify
from flask_cors import CORS
import random
import time
from datetime import datetime, timedelta
import threading

app = Flask(__name__)
CORS(app)

# In-memory trade storage
trades = []
trade_counter = 1

# Market titles
MARKETS = [
    "Trump 2024 Election Win",
    "Bitcoin above $50k by Dec 2024",
    "US Inflation below 3% Q4 2024",
    "Netflix subscriber growth positive",
    "Fed cuts rates in Dec 2024",
    "S&P 500 ends 2024 above 6000",
    "Ethereum outperforms Bitcoin",
    "Gold reaches $2200/oz",
    "US Government shutdown",
    "UK recession by end of 2024",
]

PLATFORMS = ["Polymarket", "Kalshi", "Limitless"]

def generate_trade():
    """Generate a realistic mock trade"""
    global trade_counter
    
    market = random.choice(MARKETS)
    platform = random.choice(PLATFORMS)
    side = random.choice(["YES", "NO"])
    price = random.uniform(0.35, 0.75)
    size = random.randint(10, 500)
    value = price * size
    
    trade = {
        "id": trade_counter,
        "timestamp": datetime.now().isoformat(),
        "platform": platform,
        "market": market,
        "side": side,
        "price": price,
        "size": size,
        "value": value
    }
    
    trade_counter += 1
    return trade

def trade_generator():
    """Background thread that generates trades"""
    while True:
        # Generate 1-3 trades every 5-15 seconds
        time.sleep(random.uniform(5, 15))
        num_trades = random.randint(1, 3)
        
        for _ in range(num_trades):
            trade = generate_trade()
            trades.insert(0, trade)  # Add to beginning
            
            # Keep only last 100 trades
            if len(trades) > 100:
                trades.pop()

@app.route('/api/trades')
def get_trades():
    """Get recent trades"""
    total_volume = sum(t['value'] for t in trades)
    
    return jsonify({
        "success": True,
        "trades": trades[:50],  # Return last 50 trades
        "stats": {
            "total_trades": len(trades),
            "total_volume": total_volume
        }
    })

@app.route('/api/agent/register', methods=['POST'])
def register_agent():
    """Register a new agent (mock endpoint)"""
    agent_id = f"agent-{int(time.time())}"
    return jsonify({
        "success": True,
        "agent_id": agent_id,
        "message": "Agent registered successfully"
    })

@app.route('/api/agent/activate', methods=['POST'])
def activate_agent():
    """Activate agent (mock endpoint)"""
    return jsonify({
        "success": True,
        "message": "Agent activated"
    })

@app.route('/api/agent/deactivate', methods=['POST'])
def deactivate_agent():
    """Deactivate agent (mock endpoint)"""
    return jsonify({
        "success": True,
        "message": "Agent deactivated"
    })

@app.route('/api/agent/status/<agent_id>')
def agent_status(agent_id):
    """Get agent status (mock endpoint)"""
    return jsonify({
        "success": True,
        "stats": {
            "today_trades": random.randint(10, 50),
            "net_profit": random.uniform(-50, 200)
        },
        "recent_positions": []
    })

if __name__ == '__main__':
    # Generate initial trades
    print("🔮 Generating initial trades...")
    for _ in range(20):
        trades.append(generate_trade())
    
    # Start background trade generator
    print("⚡ Starting trade generator...")
    generator_thread = threading.Thread(target=trade_generator, daemon=True)
    generator_thread.start()
    
    print("🚀 OracleXBT Trade Feed Server starting...")
    print("📊 API available at http://localhost:7777")
    print("⚡ Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=7777, debug=False, threaded=True)
