# OracleXBT Persistent Service Management

## Quick Setup (One-Time)

Run the setup script to install the persistent service:

```bash
cd ~/oraclexbt
chmod +x setup_persistent.sh
./setup_persistent.sh
```

That's it! OracleXBT will now:
- ✅ Auto-start when you log in
- ✅ Auto-restart if it crashes
- ✅ Survive system updates and reboots
- ✅ Run 24/7 without manual intervention

## Management Commands

### Check Status
```bash
# See if service is loaded
launchctl list | grep oraclexbt

# Check if agent is running
pgrep -f oracle_twitter_manager
```

### Stop Service
```bash
launchctl unload ~/Library/LaunchAgents/com.oraclexbt.agent.plist
```

### Start Service
```bash
launchctl load ~/Library/LaunchAgents/com.oraclexbt.agent.plist
```

### Restart Service
```bash
launchctl unload ~/Library/LaunchAgents/com.oraclexbt.agent.plist
launchctl load ~/Library/LaunchAgents/com.oraclexbt.agent.plist
```

### View Logs
```bash
# Runtime log (start/stop/restart events)
tail -f ~/oraclexbt/oracle_runtime.log

# Agent output
tail -f ~/oraclexbt/oracle_stdout.log

# Errors
tail -f ~/oraclexbt/oracle_stderr.log
```

## After Code Updates

When you update the agent code, the service will automatically use the new code on next restart. You can:

1. **Let it restart naturally** - Wait for the next scheduled restart
2. **Force restart** - Run: `launchctl unload ~/Library/LaunchAgents/com.oraclexbt.agent.plist && launchctl load ~/Library/LaunchAgents/com.oraclexbt.agent.plist`

## Uninstall Service

To completely remove the persistent service:

```bash
# Stop and unload
launchctl unload ~/Library/LaunchAgents/com.oraclexbt.agent.plist

# Remove plist
rm ~/Library/LaunchAgents/com.oraclexbt.agent.plist

# Kill any running instances
pkill -f oracle_twitter_manager.py
```

## How It Works

- **launchd**: macOS system daemon manager (like systemd on Linux)
- **KeepAlive**: Automatically restarts if process crashes
- **RunAtLoad**: Starts automatically when you log in
- **ThrottleInterval**: Prevents rapid restart loops

## Logs Location

All logs are stored in the project directory:
- `oracle_runtime.log` - Service lifecycle events
- `oracle_stdout.log` - Agent stdout
- `oracle_stderr.log` - Agent errors
