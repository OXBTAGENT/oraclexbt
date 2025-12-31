#!/usr/bin/env python3
"""
Oracle XBT Web Dashboard
A simple web interface to view prediction markets and opportunities
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Demo mode - use mock data
DEMO_MODE = True

def generate_mock_markets(limit=20, category=None):
    """Generate mock market data for demo"""
    categories = ['Politics', 'Crypto', 'Sports', 'Science', 'Economics', 'Technology']
    platforms = ['Polymarket', 'Kalshi', 'Limitless', 'Manifold']
    
    market_templates = [
        "Will {topic} happen by {date}?",
        "{candidate} to win {event}",
        "Will {metric} exceed {value} in {year}?",
        "{team} to win {championship}",
        "Bitcoin to reach ${price}K by {date}",
        "Will there be a {event} in {year}?",
    ]
    
    topics = [
        ("Trump re-election", "2024"), ("Bitcoin $100K", "Q1 2026"), ("AI breakthrough", "2025"),
        ("Fed rate cut", "March 2026"), ("Lakers championship", "2025"), ("Tech stock rally", "2026"),
        ("Ethereum $5K", "2025"), ("Economic recession", "2026"), ("New vaccine approval", "2025"),
        ("Major tech merger", "2025"), ("Climate agreement", "2026"), ("Space mission success", "2025")
    ]
    
    markets = []
    for i in range(limit):
        if category and random.random() > 0.3:
            cat = category
        else:
            cat = random.choice(categories)
        
        topic, date = random.choice(topics)
        title = f"{topic} {random.choice(['by', 'in', 'before'])} {date}"
        
        yes_price = random.uniform(0.15, 0.85)
        no_price = 1.0 - yes_price
        
        markets.append({
            'id': f"demo-{i+1}",
            'title': title,
            'platform': random.choice(platforms),
            'category': cat,
            'yes_price': yes_price,
            'no_price': no_price,
            'volume': random.randint(10000, 5000000),
            'liquidity': random.randint(5000, 1000000),
            'url': f"https://example.com/market/{i+1}"
        })
    
    return markets

def generate_mock_arbitrage(min_spread=1.0, limit=10):
    """Generate mock arbitrage opportunities"""
    events = [
        "Trump wins 2024 election",
        "Bitcoin reaches $100K",
        "Fed cuts rates in March",
        "Lakers win championship",
        "Ethereum reaches $5K",
        "Tech stocks rally 20%",
        "Major recession in 2026",
        "New COVID variant emerges",
        "AI regulation passes Congress",
        "Apple releases VR headset"
    ]
    
    platforms = ['Polymarket', 'Kalshi', 'Limitless', 'Manifold', 'PredictIt']
    outcomes = ['Yes', 'No']
    
    opportunities = []
    for i in range(limit):
        spread = random.uniform(min_spread, 8.0)
        price1 = random.uniform(0.4, 0.7)
        price2 = price1 + (spread / 100)
        
        if price2 > 0.95:
            price1 = random.uniform(0.2, 0.5)
            price2 = price1 + (spread / 100)
        
        opportunities.append({
            'event': random.choice(events),
            'spread': spread,
            'platform1': random.choice(platforms),
            'platform2': random.choice([p for p in platforms if p != opportunities[i-1]['platform1'] if i > 0 else platforms]),
            'price1': price1,
            'price2': price2,
            'outcome1': random.choice(outcomes),
            'outcome2': random.choice(outcomes)
        })
    
    return sorted(opportunities, key=lambda x: x['spread'], reverse=True)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/markets')
def get_markets():
    """Get list of markets"""
    try:
        limit = request.args.get('limit', 20, type=int)
        category = request.args.get('category', None)
        
        if DEMO_MODE:
            markets_data = generate_mock_markets(limit, category)
        else:
            client = get_client()
            markets = client.list_markets(limit=limit, category=category)
            markets_data = [
                {
                    'id': m.id,
                    'title': m.title,
                    'platform': m.platform,
                    'category': m.category,
                    'yes_price': m.yes_price,
                    'no_price': m.no_price,
                    'volume': m.volume,
                    'liquidity': m.liquidity,
                    'url': m.url
                }
                for m in markets.data
            ]
        
        return jsonify({
            'success': True,
            'data': markets_data,
            'count': len(markets_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/market/<market_id>')
def get_market(market_id):
    """Get specific market details"""
    try:
        if DEMO_MODE:
            # Return mock data
            return jsonify({
                'success': True,
                'data': {
                    'id': market_id,
                    'title': "Sample Market - Demo Mode",
                    'description': "This is demo data. Connect to real API for live data.",
                    'platform': 'Polymarket',
                    'category': 'Politics',
                    'yes_price': 0.65,
                    'no_price': 0.35,
                    'volume': 1500000,
                    'liquidity': 250000,
                    'url': 'https://example.com',
                    'ends_at': None
                }
            })
        
        client = get_client()
        market = client.get_market(market_id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': market.id,
                'title': market.title,
                'description': market.description,
                'platform': market.platform,
                'category': market.category,
                'yes_price': market.yes_price,
                'no_price': market.no_price,
                'volume': market.volume,
                'liquidity': market.liquidity,
                'url': market.url,
                'ends_at': market.ends_at.isoformat() if market.ends_at else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/price-history/<market_id>')
def get_price_history(market_id):
    """Get price history for a market"""
    try:
        range_param = request.args.get('range', '24h')
        
        if DEMO_MODE:
            # Generate mock price history
            points = []
            now = datetime.now()
            for i in range(24):
                timestamp = now - timedelta(hours=23-i)
                yes_price = 0.5 + (random.random() - 0.5) * 0.3
                points.append({
                    'timestamp': timestamp.isoformat(),
                    'yes_price': yes_price,
                    'no_price': 1.0 - yes_price,
                    'yes_percent': yes_price * 100,
                    'no_percent': (1.0 - yes_price) * 100
                })
            
            return jsonify({
                'success': True,
                'data': {'points': points}
            })
        
        client = get_client()
        history = client.get_price_history(market_id, range=range_param)
        
        return jsonify({
            'success': True,
            'data': {
                'points': [
                    {
                        'timestamp': p.timestamp.isoformat(),
                        'yes_price': p.yes_price,
                        'no_price': p.no_price,
                        'yes_percent': p.yes_percent,
                        'no_percent': p.no_percent
                    }
                    for p in history.points
                ] if history.points else []
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/arbitrage')
def get_arbitrage():
    """Get arbitrage opportunities"""
    try:
        min_spread = request.args.get('min_spread', 1.0, type=float)
        limit = request.args.get('limit', 10, type=int)
        
        if DEMO_MODE:
            opportunities = generate_mock_arbitrage(min_spread, limit)
        else:
            client = get_client()
            ticker = client.get_arb_scanner()
            
            opportunities = []
            for item in ticker[:limit]:
                if item.spread >= min_spread:
                    opportunities.append({
                        'event': item.event,
                        'spread': item.spread,
                        'platform1': item.platform1,
                        'platform2': item.platform2,
                        'price1': item.price1,
                        'price2': item.price2,
                        'outcome1': item.outcome1,
                        'outcome2': item.outcome2
                    })
        
        return jsonify({
            'success': True,
            'data': opportunities,
            'count': len(opportunities)
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

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Close client on shutdown"""
    if not DEMO_MODE:
        global client
        if client is not None:
            client.close()
            client = None

if __name__ == '__main__':
    print("🔮 Oracle XBT Dashboard Starting...")
    if DEMO_MODE:
        print("📊 Running in DEMO MODE with mock data")
    print("📊 Opening dashboard at http://localhost:8080")
    print("⚡ Press Ctrl+C to stop")
    app.run(debug=True, host='0.0.0.0', port=8080)
