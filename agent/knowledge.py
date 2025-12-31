"""Training data and knowledge base for OracleXBT."""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MarketPattern:
    """A learned pattern in prediction markets."""
    name: str
    description: str
    indicators: List[str]
    confidence: float
    examples: List[str]
    strategy: str

@dataclass
class TradingStrategy:
    """A trading strategy pattern."""
    name: str
    description: str
    conditions: List[str]
    risk_level: str
    success_rate: float
    examples: List[Dict[str, Any]]

@dataclass
class ArbitragePattern:
    """Common arbitrage opportunity patterns."""
    type: str
    description: str
    platforms: List[str]
    typical_spread: float
    risk_factors: List[str]

# ====================
# MARKET PATTERNS
# ====================

MARKET_PATTERNS = [
    MarketPattern(
        name="Election Volatility Spike",
        description="Markets become highly volatile 24-48 hours before major political events",
        indicators=[
            "Volume increase >300% from 7-day average",
            "Price movements >10% in 4-hour windows",
            "Multiple platforms showing similar volatility",
            "News catalysts (debates, scandals, polls)"
        ],
        confidence=0.85,
        examples=[
            "2024 Presidential Election final week",
            "UK Brexit referendum final days",
            "French Election runoffs"
        ],
        strategy="Avoid entering new positions; close risk-sensitive trades; monitor for post-event mean reversion"
    ),
    
    MarketPattern(
        name="Crypto Correlation",
        description="Crypto prediction markets often correlate with Bitcoin price movements",
        indicators=[
            "BTC price change >5% in 24h",
            "Crypto adoption markets moving in same direction",
            "Regulatory news affecting both BTC and prediction platforms"
        ],
        confidence=0.72,
        examples=[
            "Bitcoin ETF approval affecting platform tokens",
            "Regulatory crackdowns correlating with crypto market pessimism"
        ],
        strategy="Monitor BTC price for leading indicators on crypto-related prediction markets"
    ),
    
    MarketPattern(
        name="Platform Migration",
        description="Users migrate between platforms based on liquidity and fees",
        indicators=[
            "One platform showing declining volume",
            "Similar markets with >10% price differences",
            "New platform launches or fee changes"
        ],
        confidence=0.68,
        examples=[
            "Users moving from PredictIt due to withdrawal issues",
            "Polymarket gaining share from traditional platforms"
        ],
        strategy="Follow liquidity to the dominant platform; arbitrage during transition periods"
    ),
    
    MarketPattern(
        name="Weekend Effect",
        description="Lower trading volumes and wider spreads on weekends",
        indicators=[
            "Volume drops 40-60% Saturday/Sunday",
            "Bid-ask spreads widen significantly",
            "Fewer arbitrage opportunities get filled"
        ],
        confidence=0.79,
        examples=[
            "Polymarket weekend volume patterns",
            "Kalshi reduced activity on non-trading days"
        ],
        strategy="Place limit orders on Friday for weekend execution; avoid market orders on weekends"
    )
]

# ====================
# TRADING STRATEGIES
# ====================

TRADING_STRATEGIES = [
    TradingStrategy(
        name="Cross-Platform Arbitrage",
        description="Exploit price differences for the same event across platforms",
        conditions=[
            "Price difference >5% for identical events",
            "Sufficient liquidity on both platforms",
            "Low transaction costs/fees",
            "Fast execution capability"
        ],
        risk_level="Medium",
        success_rate=0.73,
        examples=[
            {
                "event": "2024 Presidential Election",
                "polymarket_price": 0.65,
                "kalshi_price": 0.58,
                "spread": 0.07,
                "profit": "~5-6% after fees"
            }
        ]
    ),
    
    TradingStrategy(
        name="Mean Reversion",
        description="Buy oversold markets, sell overbought markets after news events",
        conditions=[
            "Price moves >15% in <2 hours",
            "No fundamental change in underlying probability",
            "High volume spike indicates emotional trading",
            "Historical pattern of reversion"
        ],
        risk_level="High",
        success_rate=0.61,
        examples=[
            {
                "event": "Debate performance overreaction",
                "initial_move": "-20% in 30 minutes",
                "reversion_time": "6-12 hours",
                "typical_reversion": "60-80% of initial move"
            }
        ]
    ),
    
    TradingStrategy(
        name="Volume Momentum",
        description="Follow markets with increasing volume and clear trends",
        conditions=[
            "Volume >200% of 7-day average",
            "Clear price trend >3% same direction",
            "News catalyst supporting direction",
            "Cross-platform confirmation"
        ],
        risk_level="Medium",
        success_rate=0.68,
        examples=[
            {
                "trigger": "Major news announcement",
                "volume_increase": "400%",
                "trend_duration": "1-3 days",
                "typical_gain": "8-15%"
            }
        ]
    )
]

# ====================
# ARBITRAGE PATTERNS
# ====================

ARBITRAGE_PATTERNS = [
    ArbitragePattern(
        type="Simple Arbitrage",
        description="Direct price differences for identical events",
        platforms=["Polymarket", "Kalshi"],
        typical_spread=0.03,
        risk_factors=[
            "Settlement rule differences",
            "Timing differences",
            "Liquidity constraints",
            "Platform counterparty risk"
        ]
    ),
    
    ArbitragePattern(
        type="Synthetic Arbitrage",
        description="Create synthetic positions using related markets",
        platforms=["Multiple"],
        typical_spread=0.05,
        risk_factors=[
            "Correlation breakdown",
            "Multiple execution risk",
            "Complex position management",
            "Higher transaction costs"
        ]
    ),
    
    ArbitragePattern(
        type="Time Arbitrage",
        description="Same event with different resolution dates",
        platforms=["Polymarket", "Metaculus"],
        typical_spread=0.02,
        risk_factors=[
            "Time value of money",
            "Information flow timing",
            "Platform reliability differences"
        ]
    )
]

# ====================
# PLATFORM KNOWLEDGE
# ====================

PLATFORM_KNOWLEDGE = {
    "polymarket": {
        "strengths": ["Highest liquidity", "Crypto-native", "Fast settlements", "Wide market variety"],
        "weaknesses": ["Crypto barrier", "Regulatory uncertainty", "Gas fees"],
        "best_for": ["Large trades", "Crypto markets", "Quick execution"],
        "typical_fees": "~2% (gas + platform)",
        "settlement_speed": "Fast (on-chain)",
        "user_type": "Crypto-savvy traders"
    },
    
    "kalshi": {
        "strengths": ["CFTC regulated", "Fiat deposits", "Professional interface", "Institutional backing"],
        "weaknesses": ["Limited markets", "US-only", "Higher fees"],
        "best_for": ["Regulated environment", "Fiat traders", "Professional use"],
        "typical_fees": "~3-5%",
        "settlement_speed": "Medium (traditional)",
        "user_type": "Traditional traders, institutions"
    },
    
    "manifold": {
        "strengths": ["Open market creation", "Play money", "Great for research", "Community-driven"],
        "weaknesses": ["Not real money", "Lower quality info", "Meme markets"],
        "best_for": ["Research", "Testing strategies", "Market discovery"],
        "typical_fees": "None (play money)",
        "settlement_speed": "Variable",
        "user_type": "Researchers, hobbyists"
    },
    
    "metaculus": {
        "strengths": ["High-quality forecasters", "Long-term focus", "Calibrated predictions", "Research backing"],
        "weaknesses": ["Not trading platform", "No money involved", "Slower resolution"],
        "best_for": ["Research", "Calibration", "Long-term forecasts"],
        "typical_fees": "None",
        "settlement_speed": "Slow (research-focused)",
        "user_type": "Forecasters, researchers"
    }
}

# ====================
# MARKET CATEGORIES
# ====================

MARKET_CATEGORIES = {
    "politics": {
        "volatility": "High",
        "best_platforms": ["Polymarket", "Kalshi", "PredictIt"],
        "key_factors": ["Polls", "Debates", "Scandals", "Economic data"],
        "trading_hours": "24/7 with lower weekend volume",
        "seasonal_patterns": ["Election cycles", "Debate seasons", "Convention periods"]
    },
    
    "crypto": {
        "volatility": "Very High", 
        "best_platforms": ["Polymarket", "Manifold"],
        "key_factors": ["Bitcoin price", "Regulation", "Adoption news", "Tech developments"],
        "trading_hours": "24/7",
        "seasonal_patterns": ["Bull/bear cycles", "Regulatory seasons", "Conference periods"]
    },
    
    "sports": {
        "volatility": "Medium",
        "best_platforms": ["Kalshi", "Insight"],
        "key_factors": ["Player health", "Team performance", "Weather", "Coaching changes"],
        "trading_hours": "Event-dependent",
        "seasonal_patterns": ["Sports seasons", "Playoffs", "Draft periods"]
    },
    
    "economics": {
        "volatility": "Low-Medium",
        "best_platforms": ["Kalshi", "Metaculus"],
        "key_factors": ["Fed policy", "Economic data", "Inflation", "Employment"],
        "trading_hours": "Business hours heavy",
        "seasonal_patterns": ["Fed meetings", "Earnings seasons", "Data releases"]
    }
}

# ====================
# TRAINING EXAMPLES
# ====================

TRAINING_EXAMPLES = [
    {
        "user_query": "Find arbitrage opportunities",
        "analysis_steps": [
            "Search for same events across platforms",
            "Calculate price differences after fees",
            "Check liquidity on both sides", 
            "Verify settlement terms are identical",
            "Calculate potential profit and risk"
        ],
        "response_template": """Found {num} arbitrage opportunities:

**Best Opportunity: {event}**
- Platform A: {price_a} ({volume_a} volume)
- Platform B: {price_b} ({volume_b} volume) 
- Spread: {spread}% ({profit_potential})
- Risk factors: {risks}
- Execution difficulty: {difficulty}

Strategy: {recommended_action}"""
    },
    
    {
        "user_query": "Analyze this market trend",
        "analysis_steps": [
            "Get current price and recent history",
            "Calculate volume and volatility metrics",
            "Identify news catalysts and events",
            "Compare to similar historical markets",
            "Assess technical and fundamental factors"
        ],
        "response_template": """Market Analysis: {market_name}

**Current Status:**
- Price: {current_price} ({price_change} 24h)
- Volume: {volume} ({volume_change} vs avg)
- Trend: {trend_direction} ({confidence})

**Key Drivers:**
{key_drivers}

**Technical Analysis:**
- Support: {support_level}
- Resistance: {resistance_level}
- Momentum: {momentum}

**Outlook:** {outlook_summary}"""
    }
]

def get_knowledge_for_query(query: str) -> Dict[str, Any]:
    """Get relevant knowledge for a user query."""
    query_lower = query.lower()
    
    relevant_patterns = []
    relevant_strategies = []
    relevant_platforms = []
    
    # Match patterns
    for pattern in MARKET_PATTERNS:
        if any(keyword in query_lower for keyword in pattern.name.lower().split()):
            relevant_patterns.append(pattern)
    
    # Match strategies  
    for strategy in TRADING_STRATEGIES:
        if any(keyword in query_lower for keyword in strategy.name.lower().split()):
            relevant_strategies.append(strategy)
    
    # Match platforms
    for platform, info in PLATFORM_KNOWLEDGE.items():
        if platform in query_lower:
            relevant_platforms.append({platform: info})
    
    return {
        "patterns": relevant_patterns,
        "strategies": relevant_strategies, 
        "platforms": relevant_platforms,
        "categories": MARKET_CATEGORIES
    }