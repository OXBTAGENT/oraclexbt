"""
Test script for OracleXBT Trading Terminal
Validates configuration and basic functionality
"""

import os
import sys
from decimal import Decimal
from dotenv import load_dotenv

# Load environment
load_dotenv()

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def test_imports():
    """Test required imports"""
    print_header("Testing Imports")
    
    try:
        from trading_terminal import TradingTerminal, OrderSide, OrderType
        print("✅ Trading terminal imports")
        
        from blockchain import BlockchainConnector, PolymarketContract
        print("✅ Blockchain modules")
        
        from agent.trading_tools import TRADING_TOOLS
        print("✅ Agent trading tools")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("\nInstall dependencies: pip install web3 eth-account")
        return False

def test_configuration():
    """Test configuration"""
    print_header("Testing Configuration")
    
    # Check trading settings
    settings = {
        "STARTING_BALANCE": os.getenv("STARTING_BALANCE", "10000"),
        "MAX_POSITION_SIZE": os.getenv("MAX_POSITION_SIZE", "1000"),
        "MAX_TOTAL_EXPOSURE": os.getenv("MAX_TOTAL_EXPOSURE", "5000"),
        "MAX_DRAWDOWN": os.getenv("MAX_DRAWDOWN", "0.20"),
    }
    
    print("\n💰 Trading Settings:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
    
    # Check wallet configuration
    print("\n🔐 Wallet Configuration:")
    wallets = {
        "Polygon": os.getenv("POLYGON_WALLET_ADDRESS"),
        "Ethereum": os.getenv("ETHEREUM_WALLET_ADDRESS"),
        "Arbitrum": os.getenv("ARBITRUM_WALLET_ADDRESS"),
    }
    
    configured = 0
    for chain, address in wallets.items():
        if address and address.strip():
            print(f"  ✅ {chain}: {address[:10]}...")
            configured += 1
        else:
            print(f"  ⚠️  {chain}: Not configured")
    
    if configured == 0:
        print("\n⚠️  No wallets configured. Trading will run in simulation mode.")
        print("   To enable real trading, add wallet addresses to .env")
    
    return True

def test_terminal():
    """Test terminal initialization"""
    print_header("Testing Trading Terminal")
    
    try:
        from trading_terminal import TradingTerminal
        
        terminal = TradingTerminal()
        print("✅ Terminal initialized")
        
        # Test portfolio status
        portfolio = terminal.get_portfolio_summary()
        print(f"\n📊 Portfolio Status:")
        print(f"  Balance: ${portfolio['balance']:,.2f}")
        print(f"  Total Value: ${portfolio['total_value']:,.2f}")
        print(f"  Positions: {portfolio['num_positions']}")
        
        return True
    except Exception as e:
        print(f"❌ Terminal test failed: {e}")
        return False

def test_risk_management():
    """Test risk management"""
    print_header("Testing Risk Management")
    
    try:
        from trading_terminal import TradingTerminal
        
        terminal = TradingTerminal()
        rm = terminal.risk_manager
        
        print(f"\n⚙️ Risk Limits:")
        print(f"  Max Position: ${rm.max_position_size:,.2f}")
        print(f"  Max Exposure: ${rm.max_total_exposure:,.2f}")
        print(f"  Max Drawdown: {rm.max_drawdown*100:.0f}%")
        print(f"  Min Liquidity: ${rm.min_liquidity:,.2f}")
        
        # Test checks
        test_size = Decimal("500")
        can_trade = rm.check_position_size(test_size)
        print(f"\n✅ Position size check: ${test_size} - {'PASS' if can_trade else 'FAIL'}")
        
        return True
    except Exception as e:
        print(f"❌ Risk management test failed: {e}")
        return False

def test_agent_integration():
    """Test agent integration"""
    print_header("Testing Agent Integration")
    
    try:
        from agent.trading_tools import (
            get_portfolio_status,
            check_risk_limits,
            TRADING_TOOLS
        )
        
        print(f"\n🛠️  Trading Tools Available: {len(TRADING_TOOLS)}")
        for tool in TRADING_TOOLS:
            print(f"  • {tool['name']}")
        
        # Test portfolio status
        result = get_portfolio_status()
        if result['success']:
            print(f"\n✅ Portfolio status: ${result['portfolio']['balance']:,.2f}")
        
        # Test risk limits
        result = check_risk_limits()
        if result['success']:
            print(f"✅ Risk limits check passed")
            print(f"   Exposure: {result['exposure_used_percent']:.1f}%")
        
        return True
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False

def test_blockchain_connection():
    """Test blockchain connection (if configured)"""
    print_header("Testing Blockchain Connection")
    
    polygon_rpc = os.getenv("POLYGON_RPC_URL")
    if not polygon_rpc:
        print("⚠️  No RPC URL configured, skipping")
        return True
    
    try:
        from blockchain import BlockchainConnector
        
        print(f"🔗 Connecting to Polygon: {polygon_rpc}")
        connector = BlockchainConnector(polygon_rpc, "polygon")
        
        gas_price = connector.get_gas_price()
        gas_gwei = gas_price / 10**9
        print(f"✅ Connected! Gas price: {gas_gwei:.2f} Gwei")
        
        # Test wallet balance if configured
        wallet_address = os.getenv("POLYGON_WALLET_ADDRESS")
        if wallet_address and wallet_address.strip():
            balance = connector.get_wallet_balance(wallet_address)
            print(f"✅ Wallet balance: {balance:.4f} MATIC")
        
        return True
    except Exception as e:
        print(f"❌ Blockchain connection failed: {e}")
        print("   Check RPC URL and network connectivity")
        return False

def main():
    """Run all tests"""
    print("\n🧪 OracleXBT Trading Terminal - Test Suite")
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Terminal", test_terminal),
        ("Risk Management", test_risk_management),
        ("Agent Integration", test_agent_integration),
        ("Blockchain Connection", test_blockchain_connection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print()
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Trading terminal is ready.")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
