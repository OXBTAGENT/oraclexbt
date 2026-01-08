"""
Configuration loader for OracleXBT
"""

import yaml
import os
from typing import Dict, Any
from pathlib import Path

class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            print(f"✅ Loaded configuration from {self.config_file}")
            return config
        except FileNotFoundError:
            print(f"⚠️  Config file {self.config_file} not found, using defaults")
            return self._default_config()
        except Exception as e:
            print(f"❌ Error loading config: {e}, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'server': {
                'host': '0.0.0.0',
                'port': 7777,
                'debug': False
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/oraclexbt.db'
            },
            'trading': {
                'platform_fee_rate': 0.01,
                'max_position_size': 10000,
                'min_position_size': 10,
                'default_slippage_tolerance': 0.02
            },
            'risk': {
                'max_daily_trades_per_agent': 100,
                'max_drawdown': 0.20,
                'circuit_breaker_loss': 0.50,
                'require_balance_check': True
            },
            'rate_limiting': {
                'enabled': True,
                'default_limit': '100 per hour',
                'agent_register_limit': '5 per hour',
                'order_limit': '50 per hour'
            },
            'market_data': {
                'cache_ttl': 300,
                'fetch_interval': 60,
                'max_markets': 100
            },
            'platforms': {
                'polymarket': {
                    'enabled': True,
                    'api_url': 'https://gamma-api.polymarket.com',
                    'clob_url': 'https://clob.polymarket.com',
                    'rpc_url': 'https://polygon-rpc.com'
                },
                'kalshi': {
                    'enabled': True,
                    'api_url': 'https://trading-api.kalshi.com/trade-api/v2'
                },
                'limitless': {
                    'enabled': False,
                    'api_url': 'https://api.limitless.exchange'
                }
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/oraclexbt.log',
                'max_bytes': 10485760,
                'backup_count': 5,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'security': {
                'require_https': False,
                'session_timeout': 3600,
                'max_key_age': 86400,
                'allow_demo_mode': True
            },
            'monitoring': {
                'health_check_enabled': True,
                'metrics_enabled': False
            },
            'development': {
                'cors_enabled': True,
                'reload_on_change': False
            }
        }
    
    def get(self, key_path: str, default=None):
        """
        Get configuration value using dot notation
        Example: config.get('server.port') -> 7777
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict:
        """Get entire configuration section"""
        return self._config.get(section, {})
    
    @property
    def server(self):
        return self._config.get('server', {})
    
    @property
    def database(self):
        return self._config.get('database', {})
    
    @property
    def trading(self):
        return self._config.get('trading', {})
    
    @property
    def risk(self):
        return self._config.get('risk', {})
    
    @property
    def platforms(self):
        return self._config.get('platforms', {})
    
    @property
    def logging_config(self):
        return self._config.get('logging', {})
    
    @property
    def security(self):
        return self._config.get('security', {})

# Global config instance
config = Config()
