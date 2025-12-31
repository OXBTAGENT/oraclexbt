"""
OracleXBT Cross-Chain Trading Terminal
Enables autonomous trading across prediction market platforms
"""

import os
import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class Chain(Enum):
    POLYGON = "polygon"
    ETHEREUM = "ethereum"
    ARBITRUM = "arbitrum"

@dataclass
class Position:
    """Trading position"""
    market_id: str
    platform: str
    side: str
    size: Decimal
    entry_price: Decimal
    current_price: Decimal
    timestamp: datetime
    chain: Chain
    
    @property
    def unrealized_pnl(self) -> Decimal:
        """Calculate unrealized P&L"""
        if self.side == "yes":
            return (self.current_price - self.entry_price) * self.size
        else:
            return (self.entry_price - self.current_price) * self.size
    
    @property
    def pnl_percent(self) -> float:
        """P&L as percentage"""
        if self.entry_price == 0:
            return 0.0
        return float((self.unrealized_pnl / (self.entry_price * self.size)) * 100)

@dataclass
class Order:
    """Trading order"""
    order_id: str
    market_id: str
    platform: str
    order_type: OrderType
    side: OrderSide
    size: Decimal
    price: Optional[Decimal]
    chain: Chain
    status: str
    timestamp: datetime

class WalletManager:
    """Secure wallet management for cross-chain trading"""
    
    def __init__(self):
        self.wallets = {}
        self._load_wallets()
    
    def _load_wallets(self):
        """Load wallet configurations"""
        # Polygon wallet for Polymarket
        self.wallets[Chain.POLYGON] = {
            "address": os.getenv("POLYGON_WALLET_ADDRESS"),
            "private_key": os.getenv("POLYGON_PRIVATE_KEY"),  # NEVER commit this!
            "rpc_url": os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com")
        }
        
        # Ethereum wallet
        self.wallets[Chain.ETHEREUM] = {
            "address": os.getenv("ETHEREUM_WALLET_ADDRESS"),
            "private_key": os.getenv("ETHEREUM_PRIVATE_KEY"),
            "rpc_url": os.getenv("ETHEREUM_RPC_URL", "https://eth.llamarpc.com")
        }
        
        # Arbitrum wallet
        self.wallets[Chain.ARBITRUM] = {
            "address": os.getenv("ARBITRUM_WALLET_ADDRESS"),
            "private_key": os.getenv("ARBITRUM_PRIVATE_KEY"),
            "rpc_url": os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc")
        }
    
    def get_wallet(self, chain: Chain) -> Dict:
        """Get wallet for specific chain"""
        return self.wallets.get(chain, {})
    
    def is_configured(self, chain: Chain) -> bool:
        """Check if wallet is configured for chain"""
        wallet = self.wallets.get(chain, {})
        return wallet.get("address") is not None and wallet.get("private_key") is not None

class RiskManager:
    """Risk management system"""
    
    def __init__(self):
        self.max_position_size = Decimal(os.getenv("MAX_POSITION_SIZE", "1000"))
        self.max_total_exposure = Decimal(os.getenv("MAX_TOTAL_EXPOSURE", "5000"))
        self.max_drawdown = Decimal(os.getenv("MAX_DRAWDOWN", "0.20"))  # 20%
        self.min_liquidity = Decimal(os.getenv("MIN_LIQUIDITY", "10000"))
        
    def check_position_size(self, size: Decimal) -> bool:
        """Check if position size is within limits"""
        return size <= self.max_position_size
    
    def check_total_exposure(self, current_exposure: Decimal, new_size: Decimal) -> bool:
        """Check if total exposure is within limits"""
        return (current_exposure + new_size) <= self.max_total_exposure
    
    def check_liquidity(self, market_volume: Decimal) -> bool:
        """Check if market has sufficient liquidity"""
        return market_volume >= self.min_liquidity
    
    def should_stop_trading(self, current_pnl: Decimal, starting_balance: Decimal) -> bool:
        """Check if drawdown limit reached"""
        if starting_balance == 0:
            return False
        drawdown = abs(current_pnl) / starting_balance
        return drawdown >= self.max_drawdown

class PolymarketExecutor:
    """Execute trades on Polymarket (Polygon)"""
    
    def __init__(self, wallet_manager: WalletManager):
        self.wallet_manager = wallet_manager
        self.chain = Chain.POLYGON
        
    def place_market_order(self, market_id: str, side: OrderSide, size: Decimal) -> Order:
        """Place market order"""
        wallet = self.wallet_manager.get_wallet(self.chain)
        
        if not wallet.get("address"):
            raise ValueError("Polygon wallet not configured")
        
        # TODO: Implement actual on-chain transaction
        # This would use web3.py to interact with Polymarket CTF contracts
        
        order = Order(
            order_id=f"order_{datetime.now().timestamp()}",
            market_id=market_id,
            platform="polymarket",
            order_type=OrderType.MARKET,
            side=side,
            size=size,
            price=None,
            chain=self.chain,
            status="pending",
            timestamp=datetime.now()
        )
        
        print(f"[Polymarket] Placing {side.value} market order for {size} shares on {market_id}")
        print(f"[Wallet] Using address: {wallet['address'][:10]}...")
        
        return order
    
    def place_limit_order(self, market_id: str, side: OrderSide, size: Decimal, price: Decimal) -> Order:
        """Place limit order"""
        wallet = self.wallet_manager.get_wallet(self.chain)
        
        if not wallet.get("address"):
            raise ValueError("Polygon wallet not configured")
        
        order = Order(
            order_id=f"order_{datetime.now().timestamp()}",
            market_id=market_id,
            platform="polymarket",
            order_type=OrderType.LIMIT,
            side=side,
            size=size,
            price=price,
            chain=self.chain,
            status="pending",
            timestamp=datetime.now()
        )
        
        print(f"[Polymarket] Placing {side.value} limit order for {size} shares @ {price} on {market_id}")
        
        return order

class TradingTerminal:
    """Main trading terminal"""
    
    def __init__(self):
        self.wallet_manager = WalletManager()
        self.risk_manager = RiskManager()
        self.polymarket_executor = PolymarketExecutor(self.wallet_manager)
        
        self.positions: List[Position] = []
        self.orders: List[Order] = []
        self.trade_history = []
        
        self.starting_balance = Decimal(os.getenv("STARTING_BALANCE", "10000"))
        self.current_balance = self.starting_balance
        
        print("🚀 OracleXBT Trading Terminal Initialized")
        self._print_status()
    
    def _print_status(self):
        """Print terminal status"""
        print("\n" + "="*60)
        print("📊 Trading Terminal Status")
        print("="*60)
        print(f"Balance: ${self.current_balance:,.2f}")
        print(f"Positions: {len(self.positions)}")
        print(f"Active Orders: {len([o for o in self.orders if o.status == 'pending'])}")
        
        # Check wallet configurations
        print("\n🔐 Wallet Status:")
        for chain in [Chain.POLYGON, Chain.ETHEREUM, Chain.ARBITRUM]:
            status = "✅" if self.wallet_manager.is_configured(chain) else "❌"
            print(f"  {status} {chain.value.capitalize()}")
        
        print("\n⚙️ Risk Limits:")
        print(f"  Max Position: ${self.risk_manager.max_position_size:,.2f}")
        print(f"  Max Exposure: ${self.risk_manager.max_total_exposure:,.2f}")
        print(f"  Max Drawdown: {self.risk_manager.max_drawdown*100:.0f}%")
        print("="*60 + "\n")
    
    def execute_arbitrage(self, opportunity: Dict) -> bool:
        """Execute arbitrage trade across platforms"""
        try:
            market_a = opportunity["market_a"]
            market_b = opportunity["market_b"]
            spread = opportunity["spread"]
            size = opportunity["size"]
            
            # Risk checks
            if not self.risk_manager.check_position_size(Decimal(size)):
                print(f"❌ Position size ${size} exceeds limit")
                return False
            
            current_exposure = sum(p.size * p.entry_price for p in self.positions)
            if not self.risk_manager.check_total_exposure(current_exposure, Decimal(size)):
                print(f"❌ Total exposure would exceed limit")
                return False
            
            print(f"\n🎯 Executing Arbitrage Trade")
            print(f"  Buy {market_a['platform']} @ {market_a['price']}")
            print(f"  Sell {market_b['platform']} @ {market_b['price']}")
            print(f"  Spread: {spread:.2f}%")
            print(f"  Size: ${size:,.2f}")
            
            # Execute trades
            if market_a['platform'] == 'polymarket':
                buy_order = self.polymarket_executor.place_market_order(
                    market_a['market_id'],
                    OrderSide.BUY,
                    Decimal(size)
                )
                self.orders.append(buy_order)
            
            if market_b['platform'] == 'polymarket':
                sell_order = self.polymarket_executor.place_market_order(
                    market_b['market_id'],
                    OrderSide.SELL,
                    Decimal(size)
                )
                self.orders.append(sell_order)
            
            print("✅ Arbitrage trade executed")
            return True
            
        except Exception as e:
            print(f"❌ Arbitrage execution failed: {e}")
            return False
    
    def place_directional_trade(self, market_id: str, platform: str, side: str, size: Decimal, price: Optional[Decimal] = None) -> bool:
        """Place directional trade"""
        try:
            # Risk checks
            if not self.risk_manager.check_position_size(size):
                print(f"❌ Position size exceeds limit")
                return False
            
            print(f"\n📈 Placing Directional Trade")
            print(f"  Market: {market_id}")
            print(f"  Platform: {platform}")
            print(f"  Side: {side}")
            print(f"  Size: ${size:,.2f}")
            
            if platform == 'polymarket':
                order_side = OrderSide.BUY if side.lower() == "yes" else OrderSide.SELL
                
                if price:
                    order = self.polymarket_executor.place_limit_order(market_id, order_side, size, price)
                else:
                    order = self.polymarket_executor.place_market_order(market_id, order_side, size)
                
                self.orders.append(order)
                print("✅ Order placed successfully")
                return True
            
            print(f"❌ Platform {platform} not supported yet")
            return False
            
        except Exception as e:
            print(f"❌ Trade execution failed: {e}")
            return False
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        total_value = self.current_balance
        total_pnl = Decimal(0)
        
        for position in self.positions:
            total_value += position.unrealized_pnl
            total_pnl += position.unrealized_pnl
        
        return {
            "balance": float(self.current_balance),
            "total_value": float(total_value),
            "unrealized_pnl": float(total_pnl),
            "num_positions": len(self.positions),
            "roi": float((total_pnl / self.starting_balance) * 100) if self.starting_balance > 0 else 0
        }
    
    def close_position(self, position: Position) -> bool:
        """Close an existing position"""
        try:
            print(f"\n🔄 Closing Position")
            print(f"  Market: {position.market_id}")
            print(f"  P&L: ${position.unrealized_pnl:,.2f} ({position.pnl_percent:.2f}%)")
            
            # Execute closing trade
            if position.platform == 'polymarket':
                close_side = OrderSide.SELL if position.side == "yes" else OrderSide.BUY
                order = self.polymarket_executor.place_market_order(
                    position.market_id,
                    close_side,
                    position.size
                )
                self.orders.append(order)
            
            # Remove from positions
            self.positions.remove(position)
            
            # Update balance
            self.current_balance += position.unrealized_pnl
            
            print("✅ Position closed")
            return True
            
        except Exception as e:
            print(f"❌ Failed to close position: {e}")
            return False
    
    def save_state(self):
        """Save terminal state"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "balance": float(self.current_balance),
            "positions": [
                {
                    "market_id": p.market_id,
                    "platform": p.platform,
                    "side": p.side,
                    "size": float(p.size),
                    "entry_price": float(p.entry_price),
                    "pnl": float(p.unrealized_pnl)
                }
                for p in self.positions
            ],
            "portfolio": self.get_portfolio_summary()
        }
        
        with open("trading_state.json", "w") as f:
            json.dump(state, f, indent=2)
        
        print("💾 Trading state saved")

def main():
    """Interactive trading terminal"""
    terminal = TradingTerminal()
    
    print("\n🎮 OracleXBT Trading Terminal")
    print("Commands:")
    print("  1. View portfolio")
    print("  2. Place trade")
    print("  3. Execute arbitrage")
    print("  4. View positions")
    print("  5. Close position")
    print("  6. Save state")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nEnter command: ").strip()
            
            if choice == "0":
                terminal.save_state()
                print("👋 Goodbye!")
                break
            elif choice == "1":
                summary = terminal.get_portfolio_summary()
                print(f"\n💼 Portfolio Summary:")
                print(f"  Balance: ${summary['balance']:,.2f}")
                print(f"  Total Value: ${summary['total_value']:,.2f}")
                print(f"  Unrealized P&L: ${summary['unrealized_pnl']:,.2f}")
                print(f"  ROI: {summary['roi']:.2f}%")
            elif choice == "2":
                print("\n📝 Place Trade")
                market_id = input("Market ID: ")
                platform = input("Platform (polymarket): ") or "polymarket"
                side = input("Side (yes/no): ")
                size = Decimal(input("Size ($): "))
                terminal.place_directional_trade(market_id, platform, side, size)
            elif choice == "4":
                print(f"\n📊 Open Positions: {len(terminal.positions)}")
                for i, pos in enumerate(terminal.positions):
                    print(f"\n{i+1}. {pos.market_id[:30]}...")
                    print(f"   Side: {pos.side}, Size: ${pos.size:,.2f}")
                    print(f"   Entry: {pos.entry_price:.3f}, Current: {pos.current_price:.3f}")
                    print(f"   P&L: ${pos.unrealized_pnl:,.2f} ({pos.pnl_percent:.2f}%)")
            elif choice == "6":
                terminal.save_state()
            else:
                print("Invalid command")
                
        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            terminal.save_state()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
