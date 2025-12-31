"""
Trading tools for OracleXBT agent
Enables autonomous execution of trades
"""

from typing import Dict, List, Any
from decimal import Decimal
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_terminal import TradingTerminal, OrderSide, OrderType

# Global terminal instance
_terminal = None

def get_terminal() -> TradingTerminal:
    """Get or create trading terminal instance"""
    global _terminal
    if _terminal is None:
        _terminal = TradingTerminal()
    return _terminal

def execute_arbitrage_trade(opportunity: Dict) -> Dict[str, Any]:
    """
    Execute arbitrage trade across platforms
    
    Args:
        opportunity: Dict with market_a, market_b, spread, size
    
    Returns:
        Dict with success status and details
    """
    terminal = get_terminal()
    
    try:
        success = terminal.execute_arbitrage(opportunity)
        
        return {
            "success": success,
            "opportunity": opportunity,
            "message": "Arbitrage trade executed" if success else "Trade failed risk checks"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Arbitrage execution failed: {e}"
        }

def place_trade(market_id: str, platform: str, side: str, size: float, price: float = None) -> Dict[str, Any]:
    """
    Place directional trade
    
    Args:
        market_id: Market identifier
        platform: Platform name (polymarket, kalshi, etc)
        side: yes/no or buy/sell
        size: Position size in dollars
        price: Optional limit price
    
    Returns:
        Dict with success status and order details
    """
    terminal = get_terminal()
    
    try:
        success = terminal.place_directional_trade(
            market_id=market_id,
            platform=platform,
            side=side,
            size=Decimal(size),
            price=Decimal(price) if price else None
        )
        
        return {
            "success": success,
            "market_id": market_id,
            "platform": platform,
            "side": side,
            "size": size,
            "price": price,
            "message": "Trade executed successfully" if success else "Trade failed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Trade execution failed: {e}"
        }

def get_portfolio_status() -> Dict[str, Any]:
    """
    Get current portfolio status
    
    Returns:
        Dict with balance, positions, P&L
    """
    terminal = get_terminal()
    
    try:
        summary = terminal.get_portfolio_summary()
        
        positions = []
        for pos in terminal.positions:
            positions.append({
                "market_id": pos.market_id,
                "platform": pos.platform,
                "side": pos.side,
                "size": float(pos.size),
                "entry_price": float(pos.entry_price),
                "current_price": float(pos.current_price),
                "pnl": float(pos.unrealized_pnl),
                "pnl_percent": pos.pnl_percent
            })
        
        return {
            "success": True,
            "portfolio": summary,
            "positions": positions,
            "num_positions": len(positions)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get portfolio status: {e}"
        }

def close_position(market_id: str) -> Dict[str, Any]:
    """
    Close specific position
    
    Args:
        market_id: Market identifier of position to close
    
    Returns:
        Dict with success status
    """
    terminal = get_terminal()
    
    try:
        # Find position
        position = None
        for pos in terminal.positions:
            if pos.market_id == market_id:
                position = pos
                break
        
        if not position:
            return {
                "success": False,
                "message": f"No open position found for market {market_id}"
            }
        
        success = terminal.close_position(position)
        
        return {
            "success": success,
            "market_id": market_id,
            "pnl": float(position.unrealized_pnl) if success else None,
            "message": "Position closed successfully" if success else "Failed to close position"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to close position: {e}"
        }

def check_risk_limits() -> Dict[str, Any]:
    """
    Check current risk limits and exposure
    
    Returns:
        Dict with risk metrics
    """
    terminal = get_terminal()
    
    try:
        total_exposure = sum(
            float(p.size * p.entry_price) 
            for p in terminal.positions
        )
        
        portfolio = terminal.get_portfolio_summary()
        drawdown = abs(portfolio['unrealized_pnl']) / float(terminal.starting_balance) if terminal.starting_balance > 0 else 0
        
        return {
            "success": True,
            "total_exposure": total_exposure,
            "max_exposure": float(terminal.risk_manager.max_total_exposure),
            "exposure_used_percent": (total_exposure / float(terminal.risk_manager.max_total_exposure)) * 100,
            "current_drawdown": drawdown * 100,
            "max_drawdown": float(terminal.risk_manager.max_drawdown) * 100,
            "trading_allowed": not terminal.risk_manager.should_stop_trading(
                Decimal(portfolio['unrealized_pnl']),
                terminal.starting_balance
            )
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to check risk limits: {e}"
        }

# Tool definitions for agent
TRADING_TOOLS = [
    {
        "name": "execute_arbitrage_trade",
        "description": "Execute arbitrage trade across prediction market platforms. Requires opportunity dict with market_a, market_b, spread, size.",
        "input_schema": {
            "type": "object",
            "properties": {
                "opportunity": {
                    "type": "object",
                    "description": "Arbitrage opportunity details including market_a, market_b, spread, size",
                    "properties": {
                        "market_a": {
                            "type": "object",
                            "description": "First market details"
                        },
                        "market_b": {
                            "type": "object",
                            "description": "Second market details"
                        },
                        "spread": {
                            "type": "number",
                            "description": "Price spread percentage"
                        },
                        "size": {
                            "type": "number",
                            "description": "Trade size in dollars"
                        }
                    }
                }
            },
            "required": ["opportunity"]
        }
    },
    {
        "name": "place_trade",
        "description": "Place directional trade on prediction market. Specify market_id, platform, side (yes/no), size in dollars, optional limit price.",
        "input_schema": {
            "type": "object",
            "properties": {
                "market_id": {
                    "type": "string",
                    "description": "Market identifier"
                },
                "platform": {
                    "type": "string",
                    "description": "Platform name (polymarket, kalshi, etc)"
                },
                "side": {
                    "type": "string",
                    "description": "Trade side: yes or no"
                },
                "size": {
                    "type": "number",
                    "description": "Position size in dollars"
                },
                "price": {
                    "type": "number",
                    "description": "Optional limit price (omit for market order)"
                }
            },
            "required": ["market_id", "platform", "side", "size"]
        }
    },
    {
        "name": "get_portfolio_status",
        "description": "Get current portfolio status including balance, open positions, and P&L",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "close_position",
        "description": "Close an open position on specified market",
        "input_schema": {
            "type": "object",
            "properties": {
                "market_id": {
                    "type": "string",
                    "description": "Market identifier of position to close"
                }
            },
            "required": ["market_id"]
        }
    },
    {
        "name": "check_risk_limits",
        "description": "Check current risk exposure, limits, and drawdown status",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]
