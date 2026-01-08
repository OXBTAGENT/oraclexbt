#!/bin/bash
# Start All-Day Trading Session
# Run this in a dedicated terminal window

echo "🤖 Starting OracleXBT All-Day Trading Agent..."
echo "========================================"
echo ""
echo "This terminal will show live updates every 5 minutes"
echo "Keep this terminal open for continuous trading"
echo "Press Ctrl+C to stop gracefully"
echo ""
echo "In another terminal, run: python3 check_agent_status.py"
echo "to check status anytime without interrupting"
echo ""
echo "========================================"
echo ""

# Run the agent
python3 run_agent_all_day.py

echo ""
echo "✅ Agent session completed"
