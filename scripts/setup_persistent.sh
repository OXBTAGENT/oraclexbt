#!/bin/bash
# OracleXBT Setup Script - Install Persistent Service

echo "🤖 OracleXBT Persistent Service Setup"
echo "======================================"
echo ""

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Make run script executable
chmod +x "$DIR/run_oracle.sh"
echo "✓ Made run_oracle.sh executable"

# Copy plist to LaunchAgents
PLIST_DEST="$HOME/Library/LaunchAgents/com.oraclexbt.agent.plist"
cp "$DIR/com.oraclexbt.agent.plist" "$PLIST_DEST"
echo "✓ Copied service configuration to LaunchAgents"

# Stop any existing instance
pkill -f "python3 oracle_twitter_manager.py" 2>/dev/null
echo "✓ Stopped any existing instances"

# Unload if already loaded
launchctl unload "$PLIST_DEST" 2>/dev/null

# Load the service
launchctl load "$PLIST_DEST"
echo "✓ Loaded OracleXBT service"

# Give it a moment to start
sleep 2

# Check if running
if pgrep -f "oracle_twitter_manager.py" > /dev/null; then
    echo ""
    echo "✅ SUCCESS! OracleXBT is now running persistently"
    echo ""
    echo "📊 Service Status:"
    echo "   • Auto-starts on login"
    echo "   • Auto-restarts on crash"
    echo "   • Survives system updates"
    echo ""
    echo "📝 Logs:"
    echo "   • Runtime: $DIR/oracle_runtime.log"
    echo "   • Stdout: $DIR/oracle_stdout.log"
    echo "   • Stderr: $DIR/oracle_stderr.log"
    echo ""
    echo "🔧 Management Commands:"
    echo "   Stop:    launchctl unload $PLIST_DEST"
    echo "   Start:   launchctl load $PLIST_DEST"
    echo "   Status:  launchctl list | grep oraclexbt"
    echo ""
else
    echo ""
    echo "⚠️  Service loaded but may not be running yet"
    echo "   Check logs in: $DIR/oracle_runtime.log"
fi
