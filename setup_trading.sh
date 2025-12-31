#!/bin/bash
# Setup script for OracleXBT Trading Terminal

set -e

echo "🎮 Setting up OracleXBT Trading Terminal..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Install trading dependencies
echo ""
echo "📦 Installing blockchain dependencies..."
pip3 install -q web3>=6.11.0 eth-account>=0.10.0 eth-utils>=2.3.0 hexbytes>=0.3.1

echo "✅ Dependencies installed"
echo ""

# Check .env configuration
echo "🔐 Checking wallet configuration..."

if grep -q "POLYGON_WALLET_ADDRESS=$" .env 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: Wallets not configured!"
    echo ""
    echo "To enable trading, add to .env:"
    echo ""
    echo "POLYGON_WALLET_ADDRESS=0xYourWalletAddress"
    echo "POLYGON_PRIVATE_KEY=your_private_key_here"
    echo ""
    echo "⚠️  NEVER commit private keys to git!"
    echo ""
else
    echo "✅ Wallet configuration detected"
fi

# Test import
echo ""
echo "🧪 Testing terminal import..."
python3 -c "from trading_terminal import TradingTerminal; print('✅ Trading terminal ready')" 2>/dev/null || {
    echo "❌ Import failed - check dependencies"
    exit 1
}

echo ""
echo "🚀 Trading Terminal Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Configure wallets in .env (if not done)"
echo "  2. Test on testnet first: POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com"
echo "  3. Launch terminal: python3 trading_terminal.py"
echo "  4. Read docs: TRADING_TERMINAL.md"
echo ""
echo "⚡ Ready to trade!"
