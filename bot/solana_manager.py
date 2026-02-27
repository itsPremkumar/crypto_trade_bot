import logging
import base58
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from bot.config import Config

logger = logging.getLogger(__name__)

class SolanaManager:
    """Manages Solana wallet and RPC interactions."""
    
    def __init__(self):
        self.keypair: Keypair = None
        self.client = AsyncClient(Config.SOLANA_RPC_URL)
        self._load_wallet()

    def _load_wallet(self):
        """Loads the Solana wallet from the private key in config."""
        try:
            if Config.SOLANA_PRIVATE_KEY:
                # Solana keys can be base58 encoded or a byte array string
                try:
                    # Attempt base58 decoding
                    key_bytes = base58.b58decode(Config.SOLANA_PRIVATE_KEY)
                    self.keypair = Keypair.from_bytes(key_bytes)
                except Exception:
                    # Attempt byte array parsing if it's in form [1,2,3...]
                    import json
                    key_bytes = bytes(json.loads(Config.SOLANA_PRIVATE_KEY))
                    self.keypair = Keypair.from_bytes(key_bytes)
                
                logger.info("Solana wallet successfully loaded.")
            else:
                logger.warning("No SOLANA_PRIVATE_KEY provided. Generating a temporary test wallet...")
                self.keypair = Keypair()
                logger.warning(f"Test Solana Address: {self.get_address()}")
                logger.warning("Do NOT send real funds to this test address.")
        except Exception as e:
            logger.error(f"Failed to load Solana wallet: {e}")
            self.keypair = Keypair() # Fallback to new key pair

    def get_address(self) -> str:
        """Returns the public address of the Solana wallet."""
        if not self.keypair:
            raise ValueError("Solana wallet not loaded")
        return str(self.keypair.pubkey())

    async def get_balance(self) -> float:
        """Returns the SOL balance of the wallet."""
        try:
            response = await self.client.get_balance(self.keypair.pubkey())
            # Result is in lamports (1 SOL = 10^9 lamports)
            return response.value / 10**9
        except Exception as e:
            logger.error(f"Failed to fetch Solana balance: {e}")
            return 0.0

    async def close(self):
        """Closes the RPC client."""
        await self.client.close()
