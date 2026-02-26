import logging
from abc import ABC, abstractmethod
from web3 import Web3

logger = logging.getLogger(__name__)

class BaseDex(ABC):
    """Abstract base class for all DEX integrations."""

    def __init__(self, w3: Web3, router_address: str):
        self.w3 = w3
        self.router_address = Web3.to_checksum_address(router_address)
    
    @abstractmethod
    async def build_swap_transaction(self, 
                                     wallet_address: str, 
                                     token_in: str, 
                                     token_out: str, 
                                     amount_in_wei: int, 
                                     min_amount_out_wei: int, 
                                     deadline: int) -> dict:
        """Builds the raw transaction dictionary for a swap."""
        pass

    @abstractmethod
    def get_token_address(self, token_symbol: str) -> str:
        """Resolves token symbol to its contract address for the specific chain."""
        pass
