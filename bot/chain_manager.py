import logging
from web3 import Web3
try:
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware
except ImportError:
    from web3.middleware import geth_poa_middleware
from bot.config import Config

logger = logging.getLogger(__name__)

class ChainManager:
    """Manages multi-chain Web3 connections."""
    
    CHAIN_IDS = {
        'polygon': 137,
        'bsc': 56,
        'base': 8453
    }
    
    def __init__(self):
        self.w3_instances = {}
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize RPC connections based on active chains."""
        rpc_map = {
            'polygon': Config.POLYGON_RPC_URL,
            'bsc': Config.BSC_RPC_URL,
            'base': Config.BASE_RPC_URL
        }

        for chain in Config.ACTIVE_CHAINS:
            if chain not in rpc_map:
                logger.warning(f"Unknown chain configuring skipped: {chain}")
                continue
            
            url = rpc_map[chain]
            if not url:
                logger.error(f"RPC URL missing for {chain}")
                continue
            
            w3 = Web3(Web3.HTTPProvider(url))
            if chain in ['polygon', 'bsc']:
                # Inject PoA middleware for chains with PoA consensus (BSC, Polygon)
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            if w3.is_connected():
                self.w3_instances[chain] = w3
                logger.info(f"Connected to {chain.upper()} (Chain ID: {self.CHAIN_IDS[chain]})")
            else:
                logger.error(f"Failed to connect to {chain.upper()} RPC.")

    def get_w3(self, chain_name: str) -> Web3:
        """Get the connected Web3 instance for a specific chain."""
        chain_name = chain_name.lower()
        if chain_name not in self.w3_instances:
            raise ValueError(f"Chain {chain_name} is not active or not connected.")
        return self.w3_instances[chain_name]
    
    def get_all_w3(self) -> dict:
        """Get dictionary of all connected Web3 instances."""
        return self.w3_instances
