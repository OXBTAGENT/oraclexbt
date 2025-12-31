"""
OracleXBT Autonomous Trading Manager
Extends autonomous system with trading capabilities
"""

import os
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

from agent import PredictionMarketAgent
from agent.branding import print_logo
from agent.trading_tools import get_portfolio_status, check_risk_limits

load_dotenv()

class TradingManager:
    """Manages autonomous trading operations"""
    
    def __init__(self):
        self.agent = PredictionMarketAgent()
        self.enabled = os.getenv("ENABLE_AUTONOMOUS_TRADING", "false").lower() == "true"
        self.max_daily_trades = int(os.getenv("MAX_DAILY_TRADES", "5"))
        self.trades_today = 0
        self.last_reset = datetime.now().date()
        
        print("\n🎮 OracleXBT Trading Manager Initialized")
        print(f"   Autonomous Trading: {'✅ ENABLED' if self.enabled else '❌ DISABLED'}")
        print(f"   Max Daily Trades: {self.max_daily_trades}")
        print(f"   Safety: Risk management active\n")
    
    def reset_daily_counter(self):
        """Reset trade counter at start of new day"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.trades_today = 0
            self.last_reset = today
            print(f"📅 New day: Trade counter reset")
    
    def scan_for_arbitrage(self):
        """Scan for arbitrage opportunities"""
        self.reset_daily_counter()
        
        if not self.enabled:
            print("⏸️  Trading disabled, skipping arbitrage scan")
            return
        
        if self.trades_today >= self.max_daily_trades:
            print(f"⏸️  Daily trade limit reached ({self.trades_today}/{self.max_daily_trades})")
            return
        
        print("\n" + "="*60)
        print(f"🔍 Arbitrage Scan - {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        try:
            # Check risk limits first
            risk = check_risk_limits()
            if not risk.get('trading_allowed', True):
                print("🛑 Trading halted - risk limits exceeded")
                return
            
            print(f"✅ Risk check passed - {risk.get('exposure_used_percent', 0):.1f}% exposure used")
            
            # Ask agent to scan
            query = "Scan for arbitrage opportunities across Polymarket and Kalshi. Focus on high-volume markets with >3% spread. If found, analyze the opportunity thoroughly."
            
            response = self.agent.run(query)
            print(f"\n📊 Agent Analysis:\n{response}\n")
            
            # Note: Agent will execute trades if it finds opportunities
            # and they pass risk checks
            
        except Exception as e:
            print(f"❌ Arbitrage scan failed: {e}")
    
    def portfolio_health_check(self):
        """Check portfolio health and positions"""
        print("\n" + "="*60)
        print(f"💼 Portfolio Health Check - {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        try:
            portfolio = get_portfolio_status()
            
            if portfolio['success']:
                p = portfolio['portfolio']
                print(f"\n📊 Portfolio Summary:")
                print(f"   Balance: ${p['balance']:,.2f}")
                print(f"   Total Value: ${p['total_value']:,.2f}")
                print(f"   Unrealized P&L: ${p['unrealized_pnl']:,.2f}")
                print(f"   ROI: {p['roi']:.2f}%")
                print(f"   Positions: {portfolio['num_positions']}")
                
                # Check if positions need attention
                if portfolio['num_positions'] > 0:
                    print("\n📍 Analyzing open positions...")
                    query = "Review my open positions. Identify any that should be closed based on market changes or profit targets."
                    response = self.agent.run(query)
                    print(f"\n{response}\n")
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
    
    def market_analysis(self):
        """Periodic market analysis for trading opportunities"""
        self.reset_daily_counter()
        
        if not self.enabled:
            return
        
        print("\n" + "="*60)
        print(f"📈 Market Analysis - {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        
        try:
            query = "Analyze the top 5 most active prediction markets. Look for: 1) Mispriced probabilities 2) Recent volatility 3) News catalysts. Recommend any strong directional trades."
            
            response = self.agent.run(query)
            print(f"\n{response}\n")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
    
    def start(self):
        """Start autonomous trading operations"""
        print_logo()
        
        if not self.enabled:
            print("\n⚠️  Autonomous trading is DISABLED")
            print("   To enable, set in .env:")
            print("   ENABLE_AUTONOMOUS_TRADING=true")
            print("\n   Running in monitoring mode only...\n")
        
        # Schedule jobs
        
        # Arbitrage scans every 30 minutes
        schedule.every(30).minutes.do(self.scan_for_arbitrage)
        
        # Portfolio health check every 2 hours
        schedule.every(2).hours.do(self.portfolio_health_check)
        
        # Market analysis twice daily
        schedule.every().day.at("09:00").do(self.market_analysis)
        schedule.every().day.at("15:00").do(self.market_analysis)
        
        # Initial checks
        print("🚀 Starting initial checks...\n")
        self.portfolio_health_check()
        time.sleep(2)
        self.scan_for_arbitrage()
        
        print("\n⏰ Schedule:")
        print("   • Arbitrage scans: Every 30 minutes")
        print("   • Portfolio checks: Every 2 hours")
        print("   • Market analysis: 9am, 3pm daily")
        print("\n📡 Running... (Ctrl+C to stop)\n")
        
        # Run scheduler
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                print("\n\n👋 Shutting down trading manager...")
                break
            except Exception as e:
                print(f"\n❌ Error in main loop: {e}")
                time.sleep(60)

def main():
    """Main entry point"""
    manager = TradingManager()
    manager.start()

if __name__ == "__main__":
    main()
