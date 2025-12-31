"""Market analysis utilities for the Prediction Market Agent."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class Trend(Enum):
    """Price trend direction."""
    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    SIDEWAYS = "sideways"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"


class LiquidityRating(Enum):
    """Market liquidity rating."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class Confidence(Enum):
    """Market confidence level based on price."""
    VERY_HIGH_YES = "very_high_yes"  # >90% yes
    HIGH_YES = "high_yes"  # 70-90% yes
    UNCERTAIN = "uncertain"  # 30-70%
    HIGH_NO = "high_no"  # 10-30% yes
    VERY_HIGH_NO = "very_high_no"  # <10% yes


@dataclass
class MarketAnalysis:
    """Comprehensive market analysis result."""
    market_id: str
    title: str
    
    # Current state
    current_yes_price: float
    current_no_price: float
    confidence: Confidence
    
    # Trend analysis  
    trend: Trend
    price_change_24h: Optional[float]
    price_change_7d: Optional[float]
    volatility: float
    
    # Volume analysis
    total_volume: float
    volume_24h: Optional[float]
    liquidity_rating: LiquidityRating
    
    # Derived insights
    insights: list[str]
    risks: list[str]
    
    # Metadata
    analyzed_at: datetime
    expiry_date: Optional[str]


@dataclass
class ArbitrageOpportunity:
    """An arbitrage opportunity across platforms."""
    event: str
    spread_percent: float
    platform_a: str
    platform_a_price: float
    platform_b: str
    platform_b_price: float
    estimated_profit_percent: float
    risk_factors: list[str]


class MarketAnalyzer:
    """
    Advanced market analysis utilities.
    
    Provides statistical analysis, trend detection, and
    opportunity identification for prediction markets.
    """
    
    @staticmethod
    def analyze_confidence(yes_price: float) -> Confidence:
        """Determine market confidence level from yes price."""
        if yes_price >= 0.9:
            return Confidence.VERY_HIGH_YES
        elif yes_price >= 0.7:
            return Confidence.HIGH_YES
        elif yes_price >= 0.3:
            return Confidence.UNCERTAIN
        elif yes_price >= 0.1:
            return Confidence.HIGH_NO
        else:
            return Confidence.VERY_HIGH_NO
    
    @staticmethod
    def analyze_trend(prices: list[float]) -> Trend:
        """
        Analyze price trend from a list of historical prices.
        
        Args:
            prices: List of prices from oldest to newest
        """
        if len(prices) < 2:
            return Trend.SIDEWAYS
        
        # Calculate overall change
        change = prices[-1] - prices[0]
        
        # Calculate recent momentum (last 20% of data)
        recent_idx = max(1, len(prices) - len(prices) // 5)
        recent_change = prices[-1] - prices[recent_idx]
        
        # Determine trend
        if change > 0.15 and recent_change > 0:
            return Trend.STRONG_BULLISH
        elif change > 0.05:
            return Trend.BULLISH
        elif change < -0.15 and recent_change < 0:
            return Trend.STRONG_BEARISH
        elif change < -0.05:
            return Trend.BEARISH
        else:
            return Trend.SIDEWAYS
    
    @staticmethod
    def calculate_volatility(prices: list[float]) -> float:
        """
        Calculate price volatility (standard deviation).
        
        Returns volatility as a decimal (0.1 = 10% volatility).
        """
        if len(prices) < 2:
            return 0.0
        
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        return variance ** 0.5
    
    @staticmethod
    def rate_liquidity(volume: float, volume_24h: Optional[float] = None) -> LiquidityRating:
        """Rate market liquidity based on volume."""
        if volume >= 500000:
            return LiquidityRating.HIGH
        elif volume >= 50000:
            return LiquidityRating.MEDIUM
        elif volume >= 5000:
            return LiquidityRating.LOW
        else:
            return LiquidityRating.VERY_LOW
    
    @staticmethod
    def calculate_arbitrage_profit(
        price_a: float,
        price_b: float,
        fees_percent: float = 2.0
    ) -> float:
        """
        Calculate potential arbitrage profit.
        
        Assumes buying YES on cheaper platform, NO on expensive platform.
        """
        if price_a >= price_b:
            return 0.0
        
        # Buy YES at price_a, sell NO (buy YES) at price_b
        # Profit = (price_b - price_a) - fees
        gross_profit = (price_b - price_a) * 100
        net_profit = gross_profit - fees_percent
        
        return max(0.0, net_profit)
    
    @staticmethod
    def generate_insights(
        yes_price: float,
        trend: Trend,
        volatility: float,
        liquidity: LiquidityRating,
        price_change_24h: Optional[float] = None
    ) -> list[str]:
        """Generate human-readable insights about a market."""
        insights = []
        
        # Price insights
        if yes_price > 0.95:
            insights.append("Market strongly expects YES outcome (>95%)")
        elif yes_price > 0.8:
            insights.append("Market leans heavily toward YES (~{:.0f}%)".format(yes_price * 100))
        elif yes_price < 0.05:
            insights.append("Market strongly expects NO outcome (>95%)")
        elif yes_price < 0.2:
            insights.append("Market leans heavily toward NO (~{:.0f}% for YES)".format(yes_price * 100))
        elif 0.45 < yes_price < 0.55:
            insights.append("Market is highly uncertain - essentially a coin flip")
        
        # Trend insights
        if trend == Trend.STRONG_BULLISH:
            insights.append("Strong upward momentum - price rising significantly")
        elif trend == Trend.BULLISH:
            insights.append("Moderate upward trend")
        elif trend == Trend.STRONG_BEARISH:
            insights.append("Strong downward momentum - price falling significantly")
        elif trend == Trend.BEARISH:
            insights.append("Moderate downward trend")
        
        # Volatility insights
        if volatility > 0.15:
            insights.append("High volatility - significant price swings")
        elif volatility > 0.08:
            insights.append("Moderate volatility")
        elif volatility < 0.02:
            insights.append("Low volatility - price relatively stable")
        
        # 24h change insights
        if price_change_24h is not None:
            if abs(price_change_24h) > 10:
                direction = "up" if price_change_24h > 0 else "down"
                insights.append(f"Large 24h move: {direction} {abs(price_change_24h):.1f}%")
        
        # Liquidity insights
        if liquidity == LiquidityRating.VERY_LOW:
            insights.append("⚠️ Very low liquidity - may have significant slippage")
        elif liquidity == LiquidityRating.LOW:
            insights.append("Low liquidity - consider order size carefully")
        elif liquidity == LiquidityRating.HIGH:
            insights.append("High liquidity - good for larger positions")
        
        return insights
    
    @staticmethod
    def generate_risks(
        yes_price: float,
        trend: Trend,
        volatility: float,
        liquidity: LiquidityRating,
        days_to_expiry: Optional[int] = None
    ) -> list[str]:
        """Generate risk warnings for a market."""
        risks = []
        
        # Liquidity risk
        if liquidity in (LiquidityRating.LOW, LiquidityRating.VERY_LOW):
            risks.append("Liquidity risk: May be difficult to exit position at desired price")
        
        # Volatility risk
        if volatility > 0.15:
            risks.append("Volatility risk: Price could move significantly against position")
        
        # Extreme price risk
        if yes_price > 0.9 or yes_price < 0.1:
            risks.append("Asymmetric risk: Small probability of large loss if market flips")
        
        # Time decay (if near expiry)
        if days_to_expiry is not None and days_to_expiry < 3:
            risks.append("Time risk: Market expires soon - limited time for position to work out")
        
        # Contrarian risk
        if trend in (Trend.STRONG_BULLISH, Trend.STRONG_BEARISH):
            risks.append("Momentum risk: Strong trend may continue or reverse sharply")
        
        return risks
    
    @classmethod
    def full_analysis(
        cls,
        market_id: str,
        title: str,
        yes_price: float,
        no_price: float,
        volume: float,
        volume_24h: Optional[float] = None,
        price_history: Optional[list[float]] = None,
        expiry_date: Optional[str] = None
    ) -> MarketAnalysis:
        """
        Perform comprehensive market analysis.
        
        Args:
            market_id: Market identifier
            title: Market title
            yes_price: Current YES price (0-1)
            no_price: Current NO price (0-1)
            volume: Total trading volume
            volume_24h: 24-hour volume (optional)
            price_history: Historical prices from oldest to newest
            expiry_date: Market expiration date
        """
        prices = price_history or [yes_price]
        
        # Calculate metrics
        confidence = cls.analyze_confidence(yes_price)
        trend = cls.analyze_trend(prices)
        volatility = cls.calculate_volatility(prices)
        liquidity = cls.rate_liquidity(volume, volume_24h)
        
        # Price changes
        price_change_24h = None
        price_change_7d = None
        if len(prices) >= 2:
            price_change_7d = (prices[-1] - prices[0]) * 100
            # Estimate 24h as last ~15% of 7d data
            idx_24h = max(0, len(prices) - len(prices) // 7)
            if idx_24h < len(prices) - 1:
                price_change_24h = (prices[-1] - prices[idx_24h]) * 100
        
        # Generate insights and risks
        insights = cls.generate_insights(
            yes_price, trend, volatility, liquidity, price_change_24h
        )
        risks = cls.generate_risks(
            yes_price, trend, volatility, liquidity
        )
        
        return MarketAnalysis(
            market_id=market_id,
            title=title,
            current_yes_price=yes_price,
            current_no_price=no_price,
            confidence=confidence,
            trend=trend,
            price_change_24h=price_change_24h,
            price_change_7d=price_change_7d,
            volatility=volatility,
            total_volume=volume,
            volume_24h=volume_24h,
            liquidity_rating=liquidity,
            insights=insights,
            risks=risks,
            analyzed_at=datetime.now(),
            expiry_date=expiry_date
        )
