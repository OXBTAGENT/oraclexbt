"""
Smart contract interfaces for cross-chain prediction market trading
Supports Polymarket CTF (Conditional Token Framework) and other protocols
"""

from web3 import Web3
from typing import Dict, Optional, List
from decimal import Decimal
import json

# Polymarket CTF Exchange ABI (simplified)
CTF_EXCHANGE_ABI = [
    {
        "inputs": [
            {"name": "order", "type": "tuple"},
            {"name": "signature", "type": "bytes"}
        ],
        "name": "fillOrder",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "tokenId", "type": "uint256"}
        ],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# ERC1155 ABI for token transfers
ERC1155_ABI = [
    {
        "inputs": [
            {"name": "account", "type": "address"},
            {"name": "id", "type": "uint256"}
        ],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "id", "type": "uint256"},
            {"name": "amount", "type": "uint256"},
            {"name": "data", "type": "bytes"}
        ],
        "name": "safeTransferFrom",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

class PolymarketContract:
    """Interface to Polymarket smart contracts on Polygon"""
    
    # Polygon mainnet addresses
    CTF_EXCHANGE_ADDRESS = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
    USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
    CONDITIONAL_TOKENS_ADDRESS = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
    
    def __init__(self, web3: Web3):
        self.web3 = web3
        self.exchange = web3.eth.contract(
            address=self.CTF_EXCHANGE_ADDRESS,
            abi=CTF_EXCHANGE_ABI
        )
        self.conditional_tokens = web3.eth.contract(
            address=self.CONDITIONAL_TOKENS_ADDRESS,
            abi=ERC1155_ABI
        )
    
    def get_token_balance(self, wallet_address: str, token_id: int) -> int:
        """Get balance of conditional token"""
        try:
            balance = self.conditional_tokens.functions.balanceOf(
                wallet_address,
                token_id
            ).call()
            return balance
        except Exception as e:
            print(f"Error getting token balance: {e}")
            return 0
    
    def create_order_signature(self, order: Dict, private_key: str) -> str:
        """Create signature for Polymarket order"""
        # Implement EIP-712 signature
        # This is a simplified version - actual implementation needs full EIP-712 encoding
        order_hash = self.web3.keccak(text=json.dumps(order))
        signed = self.web3.eth.account.signHash(order_hash, private_key=private_key)
        return signed.signature.hex()
    
    def fill_order(self, order: Dict, signature: str, from_address: str, private_key: str) -> str:
        """Execute order on Polymarket"""
        try:
            # Build transaction
            txn = self.exchange.functions.fillOrder(
                order,
                bytes.fromhex(signature)
            ).build_transaction({
                'from': from_address,
                'gas': 300000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(from_address),
            })
            
            # Sign transaction
            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.transactionHash.hex()
            
        except Exception as e:
            print(f"Error filling order: {e}")
            raise

class USDCContract:
    """Interface to USDC stablecoin contract"""
    
    # ERC20 ABI (simplified)
    ERC20_ABI = [
        {
            "inputs": [{"name": "account", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"name": "spender", "type": "address"},
                {"name": "amount", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"name": "recipient", "type": "address"},
                {"name": "amount", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    
    def __init__(self, web3: Web3, usdc_address: str):
        self.web3 = web3
        self.contract = web3.eth.contract(
            address=usdc_address,
            abi=self.ERC20_ABI
        )
    
    def get_balance(self, wallet_address: str) -> Decimal:
        """Get USDC balance (returns in USDC, accounting for 6 decimals)"""
        try:
            balance = self.contract.functions.balanceOf(wallet_address).call()
            return Decimal(balance) / Decimal(10**6)
        except Exception as e:
            print(f"Error getting USDC balance: {e}")
            return Decimal(0)
    
    def approve(self, spender_address: str, amount: int, from_address: str, private_key: str) -> str:
        """Approve spender to use USDC"""
        try:
            txn = self.contract.functions.approve(
                spender_address,
                amount
            ).build_transaction({
                'from': from_address,
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(from_address),
            })
            
            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return receipt.transactionHash.hex()
            
        except Exception as e:
            print(f"Error approving USDC: {e}")
            raise

class BlockchainConnector:
    """Main connector for blockchain interactions"""
    
    def __init__(self, rpc_url: str, chain: str = "polygon"):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.chain = chain
        
        if not self.web3.is_connected():
            raise ConnectionError(f"Failed to connect to {chain} RPC: {rpc_url}")
        
        # Initialize contracts
        if chain == "polygon":
            self.polymarket = PolymarketContract(self.web3)
            self.usdc = USDCContract(self.web3, PolymarketContract.USDC_ADDRESS)
        
        print(f"✅ Connected to {chain} network")
    
    def get_gas_price(self) -> int:
        """Get current gas price"""
        return self.web3.eth.gas_price
    
    def get_wallet_balance(self, address: str) -> Decimal:
        """Get native token balance (MATIC for Polygon)"""
        balance_wei = self.web3.eth.get_balance(address)
        return Decimal(self.web3.from_wei(balance_wei, 'ether'))
    
    def estimate_transaction_cost(self, gas_used: int) -> Decimal:
        """Estimate transaction cost in native token"""
        gas_price = self.get_gas_price()
        cost_wei = gas_used * gas_price
        return Decimal(self.web3.from_wei(cost_wei, 'ether'))

class CrossChainBridge:
    """Handle cross-chain transfers and bridging"""
    
    def __init__(self):
        self.supported_chains = ["polygon", "ethereum", "arbitrum"]
        self.connectors: Dict[str, BlockchainConnector] = {}
    
    def add_connector(self, chain: str, rpc_url: str):
        """Add blockchain connector"""
        try:
            connector = BlockchainConnector(rpc_url, chain)
            self.connectors[chain] = connector
            print(f"✅ {chain.capitalize()} connector added")
        except Exception as e:
            print(f"❌ Failed to add {chain} connector: {e}")
    
    def get_connector(self, chain: str) -> Optional[BlockchainConnector]:
        """Get connector for specific chain"""
        return self.connectors.get(chain)
    
    def bridge_usdc(self, from_chain: str, to_chain: str, amount: Decimal) -> bool:
        """Bridge USDC between chains"""
        print(f"\n🌉 Bridging ${amount:,.2f} USDC")
        print(f"   From: {from_chain}")
        print(f"   To: {to_chain}")
        
        # TODO: Implement actual bridging logic
        # This would use protocols like:
        # - Polygon Bridge for Polygon <-> Ethereum
        # - Hop Protocol for L2 <-> L2
        # - Circle's CCTP for native USDC transfers
        
        print("⚠️  Bridge not yet implemented - requires integration with:")
        print("   - Polygon Bridge (for Polygon <-> Ethereum)")
        print("   - Hop Protocol (for L2 <-> L2)")
        print("   - Circle CCTP (for native USDC)")
        
        return False
