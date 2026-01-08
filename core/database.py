"""
Database models and management for OracleXBT
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import threading

class Database:
    """SQLite database manager with thread-safe operations"""
    
    def __init__(self, db_path: str = "data/oraclexbt.db"):
        self.db_path = db_path
        self.local = threading.local()
        
        # Create data directory if it doesn't exist
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_db()
    
    def _get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn
    
    def _init_db(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Agents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                wallet_address TEXT NOT NULL,
                platforms TEXT NOT NULL,
                strategy TEXT NOT NULL,
                max_position REAL NOT NULL,
                min_profit REAL NOT NULL,
                max_trades INTEGER NOT NULL,
                stop_loss REAL NOT NULL,
                active INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE NOT NULL,
                agent_id TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                market TEXT NOT NULL,
                buy_platform TEXT,
                sell_platform TEXT,
                size REAL NOT NULL,
                total_volume REAL NOT NULL,
                expected_profit REAL NOT NULL,
                platform_fee REAL NOT NULL,
                net_profit REAL NOT NULL,
                spread REAL,
                buy_order_id TEXT,
                sell_order_id TEXT,
                success INTEGER DEFAULT 1,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
            )
        ''')
        
        # Platform fees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS platform_fees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                fee_amount REAL NOT NULL,
                trade_id TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
            )
        ''')
        
        # Agent stats table (cached)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_stats (
                agent_id TEXT PRIMARY KEY,
                total_trades INTEGER DEFAULT 0,
                total_volume REAL DEFAULT 0,
                gross_profit REAL DEFAULT 0,
                platform_fees_paid REAL DEFAULT 0,
                net_profit REAL DEFAULT 0,
                last_updated TEXT NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
            )
        ''')
        
        # System stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_fees_collected REAL DEFAULT 0,
                total_volume REAL DEFAULT 0,
                total_trades INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # Initialize system stats if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO system_stats (id, total_fees_collected, total_volume, total_trades, last_updated)
            VALUES (1, 0, 0, 0, ?)
        ''', (datetime.now().isoformat(),))
        
        conn.commit()
    
    def register_agent(self, agent_config: Dict) -> bool:
        """Register a new agent"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO agents (
                    agent_id, wallet_address, platforms, strategy,
                    max_position, min_profit, max_trades, stop_loss,
                    active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent_config['agent_id'],
                agent_config['wallet_address'],
                json.dumps(agent_config['platforms']),
                agent_config['strategy'],
                agent_config['max_position'],
                agent_config['min_profit'],
                agent_config['max_trades'],
                agent_config['stop_loss'],
                0,
                now,
                now
            ))
            
            # Initialize agent stats
            cursor.execute('''
                INSERT INTO agent_stats (agent_id, total_trades, total_volume, gross_profit, 
                                       platform_fees_paid, net_profit, last_updated)
                VALUES (?, 0, 0, 0, 0, 0, ?)
            ''', (agent_config['agent_id'], now))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error registering agent: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agents WHERE agent_id = ?', (agent_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'agent_id': row['agent_id'],
                    'wallet_address': row['wallet_address'],
                    'platforms': json.loads(row['platforms']),
                    'strategy': row['strategy'],
                    'max_position': row['max_position'],
                    'min_profit': row['min_profit'],
                    'max_trades': row['max_trades'],
                    'stop_loss': row['stop_loss'],
                    'active': bool(row['active']),
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
        except Exception as e:
            print(f"Error getting agent: {e}")
            return None
    
    def update_agent_status(self, agent_id: str, active: bool) -> bool:
        """Update agent active status"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE agents SET active = ?, updated_at = ?
                WHERE agent_id = ?
            ''', (1 if active else 0, datetime.now().isoformat(), agent_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating agent status: {e}")
            return False
    
    def save_trade(self, trade: Dict) -> bool:
        """Save a trade to database"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            trade_id = f"{trade['agent_id']}_{int(datetime.now().timestamp()*1000)}"
            
            cursor.execute('''
                INSERT INTO trades (
                    trade_id, agent_id, trade_type, market, buy_platform, sell_platform,
                    size, total_volume, expected_profit, platform_fee, net_profit,
                    spread, buy_order_id, sell_order_id, success, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_id,
                trade['agent_id'],
                trade.get('type', 'arbitrage'),
                trade['market'],
                trade.get('buy_platform'),
                trade.get('sell_platform'),
                trade['size'],
                trade.get('total_volume', trade['size'] * 2),
                trade.get('expected_profit', 0),
                trade.get('platform_fee', 0),
                trade.get('net_profit', 0),
                trade.get('spread'),
                trade.get('buy_order_id'),
                trade.get('sell_order_id'),
                1 if trade.get('success', True) else 0,
                trade.get('timestamp', datetime.now().isoformat())
            ))
            
            # Record platform fee
            if trade.get('platform_fee', 0) > 0:
                cursor.execute('''
                    INSERT INTO platform_fees (agent_id, fee_amount, trade_id, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (
                    trade['agent_id'],
                    trade['platform_fee'],
                    trade_id,
                    trade.get('timestamp', datetime.now().isoformat())
                ))
            
            # Update agent stats
            self._update_agent_stats(trade['agent_id'], cursor)
            
            # Update system stats
            self._update_system_stats(trade, cursor)
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving trade: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _update_agent_stats(self, agent_id: str, cursor):
        """Update agent statistics"""
        cursor.execute('''
            UPDATE agent_stats SET
                total_trades = (SELECT COUNT(*) FROM trades WHERE agent_id = ?),
                total_volume = (SELECT COALESCE(SUM(total_volume), 0) FROM trades WHERE agent_id = ?),
                gross_profit = (SELECT COALESCE(SUM(expected_profit), 0) FROM trades WHERE agent_id = ?),
                platform_fees_paid = (SELECT COALESCE(SUM(platform_fee), 0) FROM trades WHERE agent_id = ?),
                net_profit = (SELECT COALESCE(SUM(net_profit), 0) FROM trades WHERE agent_id = ?),
                last_updated = ?
            WHERE agent_id = ?
        ''', (agent_id, agent_id, agent_id, agent_id, agent_id, datetime.now().isoformat(), agent_id))
    
    def _update_system_stats(self, trade: Dict, cursor):
        """Update system-wide statistics"""
        cursor.execute('''
            UPDATE system_stats SET
                total_fees_collected = total_fees_collected + ?,
                total_volume = total_volume + ?,
                total_trades = total_trades + 1,
                last_updated = ?
            WHERE id = 1
        ''', (
            trade.get('platform_fee', 0),
            trade.get('total_volume', 0),
            datetime.now().isoformat()
        ))
    
    def get_agent_stats(self, agent_id: str) -> Optional[Dict]:
        """Get agent statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM agent_stats WHERE agent_id = ?', (agent_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'agent_id': row['agent_id'],
                    'total_trades': row['total_trades'],
                    'total_volume': row['total_volume'],
                    'gross_profit': row['gross_profit'],
                    'platform_fees_paid': row['platform_fees_paid'],
                    'net_profit': row['net_profit'],
                    'last_updated': row['last_updated']
                }
            return None
        except Exception as e:
            print(f"Error getting agent stats: {e}")
            return None
    
    def get_agent_trades(self, agent_id: str, limit: int = 10) -> List[Dict]:
        """Get recent trades for an agent"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM trades WHERE agent_id = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (agent_id, limit))
            
            rows = cursor.fetchall()
            trades = []
            
            for row in rows:
                trades.append({
                    'trade_id': row['trade_id'],
                    'agent_id': row['agent_id'],
                    'type': row['trade_type'],
                    'market': row['market'],
                    'buy_platform': row['buy_platform'],
                    'sell_platform': row['sell_platform'],
                    'size': row['size'],
                    'total_volume': row['total_volume'],
                    'expected_profit': row['expected_profit'],
                    'platform_fee': row['platform_fee'],
                    'net_profit': row['net_profit'],
                    'spread': row['spread'],
                    'buy_order_id': row['buy_order_id'],
                    'sell_order_id': row['sell_order_id'],
                    'success': bool(row['success']),
                    'timestamp': row['timestamp']
                })
            
            return trades
        except Exception as e:
            print(f"Error getting agent trades: {e}")
            return []
    
    def get_system_stats(self) -> Dict:
        """Get system-wide statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM system_stats WHERE id = 1')
            row = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*) as total_agents FROM agents')
            total_agents = cursor.fetchone()['total_agents']
            
            cursor.execute('SELECT COUNT(*) as active_agents FROM agents WHERE active = 1')
            active_agents = cursor.fetchone()['active_agents']
            
            return {
                'total_agents': total_agents,
                'active_agents': active_agents,
                'total_trades': row['total_trades'],
                'total_volume': row['total_volume'],
                'total_fees_collected': row['total_fees_collected'],
                'last_updated': row['last_updated']
            }
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {}

# Global database instance
db = Database()
