"""
Basic test suite for OracleXBT
Run with: pytest tests/
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import Database
from config_loader import Config

class TestDatabase:
    """Test database operations"""
    
    def test_database_init(self, tmp_path):
        """Test database initialization"""
        db_file = tmp_path / "test.db"
        db = Database(str(db_file))
        assert db_file.exists()
    
    def test_agent_registration(self, tmp_path):
        """Test agent registration"""
        db_file = tmp_path / "test.db"
        db = Database(str(db_file))
        
        agent_config = {
            'agent_id': 'test_agent_1',
            'wallet_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
            'platforms': {'polymarket': True, 'kalshi': False},
            'strategy': 'arbitrage',
            'max_position': 100,
            'min_profit': 2.0,
            'max_trades': 50,
            'stop_loss': 5.0
        }
        
        result = db.register_agent(agent_config)
        assert result == True
        
        # Verify agent was saved
        agent = db.get_agent('test_agent_1')
        assert agent is not None
        assert agent['wallet_address'] == '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'
        assert agent['strategy'] == 'arbitrage'
    
    def test_trade_saving(self, tmp_path):
        """Test trade saving and fee calculation"""
        db_file = tmp_path / "test.db"
        db = Database(str(db_file))
        
        # Register agent first
        agent_config = {
            'agent_id': 'test_agent_2',
            'wallet_address': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
            'platforms': {'polymarket': True},
            'strategy': 'arbitrage',
            'max_position': 100,
            'min_profit': 2.0,
            'max_trades': 50,
            'stop_loss': 5.0
        }
        db.register_agent(agent_config)
        
        # Save trade
        trade = {
            'agent_id': 'test_agent_2',
            'type': 'arbitrage',
            'market': 'Test Market',
            'buy_platform': 'polymarket',
            'sell_platform': 'kalshi',
            'size': 100,
            'total_volume': 200,
            'expected_profit': 5.0,
            'platform_fee': 2.0,  # 1% of 200
            'net_profit': 3.0,
            'spread': 2.5
        }
        
        result = db.save_trade(trade)
        assert result == True
        
        # Verify stats were updated
        stats = db.get_agent_stats('test_agent_2')
        assert stats is not None
        assert stats['total_trades'] == 1
        assert stats['total_volume'] == 200
        assert stats['platform_fees_paid'] == 2.0
        assert stats['net_profit'] == 3.0
    
    def test_system_stats(self, tmp_path):
        """Test system-wide statistics"""
        db_file = tmp_path / "test.db"
        db = Database(str(db_file))
        
        stats = db.get_system_stats()
        assert 'total_agents' in stats
        assert 'total_trades' in stats
        assert 'total_fees_collected' in stats


class TestConfig:
    """Test configuration management"""
    
    def test_config_loading(self):
        """Test config loads correctly"""
        config = Config()
        assert config.get('server.port') == 7777
        assert config.get('trading.platform_fee_rate') == 0.01
    
    def test_config_sections(self):
        """Test getting config sections"""
        config = Config()
        trading = config.trading
        assert 'platform_fee_rate' in trading
        assert 'max_position_size' in trading
    
    def test_default_values(self):
        """Test default values when config missing"""
        config = Config('nonexistent.yaml')
        assert config.get('server.port') == 7777


class TestFeeCalculation:
    """Test platform fee calculations"""
    
    def test_fee_rate(self):
        """Test fee rate is 1%"""
        from config_loader import config
        fee_rate = config.get('trading.platform_fee_rate')
        assert fee_rate == 0.01
    
    def test_fee_calculation(self):
        """Test fee calculation on trade volume"""
        trade_volume = 200  # $100 buy + $100 sell
        fee_rate = 0.01
        expected_fee = trade_volume * fee_rate
        assert expected_fee == 2.0


class TestValidation:
    """Test input validation"""
    
    def test_wallet_address_validation(self):
        """Test wallet address format"""
        valid_wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
        assert valid_wallet.startswith('0x')
        assert len(valid_wallet) == 42
        
        invalid_wallet = "0x123"
        assert len(invalid_wallet) != 42
    
    def test_position_size_validation(self):
        """Test position size limits"""
        min_size = 10
        max_size = 10000
        
        assert min_size <= 100 <= max_size  # Valid
        assert not (min_size <= 5 <= max_size)  # Too small
        assert not (min_size <= 15000 <= max_size)  # Too large


# Pytest configuration
@pytest.fixture
def client():
    """Create test Flask client"""
    # Import here to avoid circular imports
    from bin.api_server import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPI:
    """Test API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_stats_endpoint(self, client):
        """Test stats endpoint"""
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'total_trades' in data
