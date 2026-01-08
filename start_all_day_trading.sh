#!/bin/bash
# All-Day Trading - Simple Start Script

clear
echo "════════════════════════════════════════════════════════════════"
echo "  🤖 OracleXBT - Starting All-Day Trading Agent"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if server is running
if ! lsof -i :5001 > /dev/null 2>&1; then
    echo "⚠️  Server not running, starting it..."
    python3 bin/api_server.py > server.log 2>&1 &
    SERVER_PID=$!
    echo "   Server started (PID: $SERVER_PID)"
    sleep 3
else
    echo "✅ Server already running on port 5001"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  📊 Starting Agent - Will trade all day"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Status updates every 5 minutes"
echo "Logs: logs/agent_$(date +%Y%m%d).log"
echo ""
echo "Press Ctrl+C to stop and save session summary"
echo ""
echo "────────────────────────────────────────────────────────────────"
echo ""

# Run the agent
python3 run_agent_all_day.py

echo ""
echo "✅ Trading session complete!"
echo "Check logs/ directory for session summary"
