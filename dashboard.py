#!/usr/bin/env python3
"""
Oracle XBT Dashboard - Web Interface
Mock data version for demonstration
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import random
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)

# Mock data cache
MOCK_MARKETS = None
MOCK_ARBITRAGE = None

def generate_mock_markets():
    """Generate realistic mock market data"""
    titles = [
        "Will Trump win 2024 re-election?",
        "Bitcoin above $50k by Dec 2024?",
        "US inflation below 3% in Q4 2024?",
        "Netflix subscriber growth positive?",
        "Fed cuts rates again in Dec 2024?",
        "Donald Trump indictment conviction?",
        "S&P 500 ends 2024 above 6000?",
        "Will AI cause mass unemployment by 2025?",
        "Elon Musk becomes world's richest person?",
        "Taylor Swift breaks revenue record 2024?",
        "Will there be a government shutdown?",
        "Gold reaches $2200/oz by year end?",
        "Will Ethereum outperform Bitcoin?",
        "UK recession by end of 2024?",
        "Meta stock breaks $500?",
        "Apple iPhone 16 sales beat expectations?",
        "Russia-Ukraine conflict ends in 2025?",
        "US debt ceiling deal reached?",
        "Oil prices drop below $70/barrel?",
        "China GDP grows above 5% in 2024?",
    ]
    
    categories = ["Politics", "Crypto", "Economics", "Technology", "Entertainment", "Sports"]
    platforms = ["Polymarket", "Kalshi", "Metaculus", "Manifold"]
    
    markets = []
    for i, title in enumerate(titles):
        yes_price = random.uniform(0.3, 0.7)
        markets.append({
            'id': f'market-{i}',
            'title': title,
            'platform': random.choice(platforms),
            'category': random.choice(categories),
            'yes_price': yes_price,
            'no_price': 1 - yes_price,
            'volume': random.uniform(10000, 1000000),
            'liquidity': random.uniform(5000, 500000),
            'url': f'https://polymarket.com/market/{i}'
        })
    return markets

def generate_mock_arbitrage():
    """Generate realistic mock arbitrage opportunities"""
    events = [
        "Bitcoin above $50k",
        "Trump 2024 Election",
        "Fed Rate Cut",
        "Inflation Data",
        "AI Advancement",
        "Tech Stock Rally",
        "Crypto Recovery",
        "Economic Recession",
        "Oil Crisis",
        "Meta AI Success",
    ]
    
    opportunities = []
    for event in events:
        price1 = random.uniform(0.45, 0.65)
        price2 = price1 + random.uniform(0.01, 0.08)
        spread = ((price2 - price1) / price1) * 100
        
        if spread >= 1:
            opportunities.append({
                'event': event,
                'spread': spread,
                'platform1': 'Polymarket',
                'platform2': 'Kalshi',
                'price1': price1,
                'price2': price2,
                'outcome1': 'YES',
                'outcome2': 'YES'
            })
    
    return sorted(opportunities, key=lambda x: x['spread'], reverse=True)[:10]

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('website/index.html')

@app.route('/docs')
def docs():
    """Documentation page"""
    return render_template('website/docs.html')

@app.route('/api/thoughts')
def get_thoughts():
    """Get AI agent thoughts/stream"""
    # In a real app, this would query the agent's memory or recent logs
    # simulating agent thought process
    thoughts = [
        {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "topic": "MARKET DYNAMICS",
            "sentiment": "neutral",
            "content": "Analyzing volume spikes in 'US Election' markets. Significant divergence detected between Polymarket (crypto-native) and Kalshi (regulated) order books."
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=2)).strftime("%H:%M:%S"),
            "topic": "ARBITRAGE ALERT",
            "sentiment": "bullish",
            "content": "Potential spread detected on 'Fed Rate Cut'. Polymarket pricing 65% probability vs Kalshi 58%. Execution window narrowing."
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=15)).strftime("%H:%M:%S"),
            "topic": "PATTERN RECOGNITION",
            "sentiment": "bearish",
            "content": "Weekend volume dip observed across Tech markets. Historical data suggests mean reversion by Monday 08:00 UTC."
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=45)).strftime("%H:%M:%S"),
            "topic": "SYSTEM",
            "sentiment": "neutral",
            "content": "Ingested 1,500 new data points from Twitter sentiment analysis. Correlation with prediction market odds: 0.82."
        }
    ]
    return jsonify({'success': True, 'data': thoughts})

@app.route('/api/markets')
def get_markets():
    """Get list of markets"""
    try:
        global MOCK_MARKETS
        if MOCK_MARKETS is None:
            MOCK_MARKETS = generate_mock_markets()
        
        limit = request.args.get('limit', 20, type=int)
        category = request.args.get('category', None)
        
        markets = MOCK_MARKETS
        if category:
            markets = [m for m in markets if m['category'] == category]
        
        return jsonify({
            'success': True,
            'data': markets[:limit],
            'count': len(markets[:limit])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/market/<market_id>')
def get_market(market_id):
    """Get specific market details"""
    try:
        global MOCK_MARKETS
        if MOCK_MARKETS is None:
            MOCK_MARKETS = generate_mock_markets()
        
        market = next((m for m in MOCK_MARKETS if m['id'] == market_id), None)
        if not market:
            return jsonify({'success': False, 'error': 'Market not found'}), 404
        
        market['description'] = 'A prediction about future market movements and events.'
        market['ends_at'] = (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat()
        
        return jsonify({
            'success': True,
            'data': market
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/arbitrage')
def get_arbitrage():
    """Get arbitrage opportunities"""
    try:
        global MOCK_ARBITRAGE
        if MOCK_ARBITRAGE is None:
            MOCK_ARBITRAGE = generate_mock_arbitrage()
        
        min_spread = request.args.get('min_spread', 1.0, type=float)
        limit = request.args.get('limit', 10, type=int)
        
        opportunities = [o for o in MOCK_ARBITRAGE if o['spread'] >= min_spread]
        
        return jsonify({
            'success': True,
            'data': opportunities[:limit],
            'count': len(opportunities[:limit])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories')
def get_categories():
    """Get available categories"""
    categories = [
        'Politics',
        'Crypto',
        'Sports',
        'Science',
        'Economics',
        'Entertainment',
        'Technology'
    ]
    return jsonify({'success': True, 'data': categories})

if __name__ == '__main__':
    print("🔮 Oracle XBT Dashboard Starting...")
    print("📊 Opening dashboard at http://localhost:8080")
    print("⚡ Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)
