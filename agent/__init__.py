"""
OracleXBT - Prediction Market Agent

The all-seeing Oracle for prediction markets. An LLM-powered agent for
researching, analyzing, and reasoning about prediction markets across
Polymarket, Kalshi, Limitless, and more.

Now with X/Twitter integration for sharing insights and engaging
with the prediction market community.

Example:
    from agent import PredictionMarketAgent
    
    agent = PredictionMarketAgent()
    response = agent.chat("What are the best political markets right now?")
    print(response)
    
    # Post to Twitter
    response = agent.chat("Find an interesting market and tweet about it")
"""

from agent.config import AgentConfig
from agent.agent import PredictionMarketAgent
from agent.tools import AgentTools
from agent.analyzer import MarketAnalyzer
from agent.twitter import TwitterClient, TwitterConfig, TweetComposer
from agent.twitter_tools import TwitterTools

__all__ = [
    "PredictionMarketAgent",
    "AgentConfig", 
    "AgentTools",
    "MarketAnalyzer",
    "TwitterClient",
    "TwitterConfig",
    "TweetComposer",
    "TwitterTools",
]
