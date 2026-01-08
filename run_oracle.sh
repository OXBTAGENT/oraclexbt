#!/bin/bash
# OracleXBT Auto-Restart Script
# This ensures the agent always runs

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Load environment variables
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Log file
LOG_FILE="$DIR/oracle_runtime.log"

echo "[$(date)] Starting OracleXBT..." >> "$LOG_FILE"

# Run with auto-restart on failure
while true; do
    echo "[$(date)] Launching oracle_twitter_manager..." >> "$LOG_FILE"
    
    # Run the agent
    /usr/bin/python3 "$DIR/oracle_twitter_manager.py" >> "$LOG_FILE" 2>&1
    
    EXIT_CODE=$?
    echo "[$(date)] Agent exited with code $EXIT_CODE" >> "$LOG_FILE"
    
    # If exit code is 0, it was intentional shutdown - don't restart
    if [ $EXIT_CODE -eq 0 ]; then
        echo "[$(date)] Clean shutdown detected. Exiting." >> "$LOG_FILE"
        break
    fi
    
    # Otherwise restart after brief delay
    echo "[$(date)] Restarting in 10 seconds..." >> "$LOG_FILE"
    sleep 10
done
