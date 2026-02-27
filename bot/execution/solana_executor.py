import logging
import aiohttp
import base64
import datetime
from typing import Optional, NamedTuple
from solana.rpc.async_api import AsyncClient
from solders.transaction import VersionedTransaction
from bot.solana_manager import SolanaManager

logger = logging.getLogger(__name__)

class TradeResult(NamedTuple):
    success: bool
    tx_hash: Optional[str] = None
    error: Optional[str] = None

class SolanaExecutor:
    """Executes trades on Solana using Jupiter Aggregator API."""
    
    JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
    JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"

    def __init__(self, solana_manager: SolanaManager):
        self.solana = solana_manager
        self.session = aiohttp.ClientSession()

    async def get_quote(self, input_mint: str, output_mint: str, amount: int, slippage_bps: int = 50):
        """Get a swap quote from Jupiter."""
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": slippage_bps
        }
        if "devnet" in str(self.solana.client._provider.endpoint_uri):
            logger.info("Devnet detected: Returning mock quote.")
            return {"mock": True, "inputMint": input_mint, "outputMint": output_mint, "amount": amount}
            
        async with self.session.get(self.JUPITER_QUOTE_API, params=params) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Jupiter Quote Error: {error_text}")
                return None
            return await response.json()

    async def execute_swap(self, quote_response: dict) -> TradeResult:
        """Execute a swap using a Jupiter quote."""
        try:
            if quote_response.get("mock"):
                tx_hash = "MOCK_TX_DEVNET_SUCCESS_" + base64.b64encode(str(datetime.datetime.now().timestamp()).encode()).decode()[:10]
                logger.info(f"Solana Trade Mock Executed: {tx_hash}")
                return TradeResult(True, tx_hash=tx_hash)

            # 1. Get swap transaction from Jupiter
            payload = {
                "quoteResponse": quote_response,
                "userPublicKey": self.solana.get_address(),
                "wrapAndUnwrapSol": True
            }
            
            async with self.session.post(self.JUPITER_SWAP_API, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return TradeResult(False, error=f"Jupiter Swap API Error: {error_text}")
                
                swap_data = await response.json()
                swap_transaction_base64 = swap_data["swapTransaction"]

            # 2. Deserialize and sign the transaction
            raw_transaction = base64.b64decode(swap_transaction_base64)
            transaction = VersionedTransaction.from_bytes(raw_transaction)
            
            # Sign with the Solana wallet keypair
            signature = self.solana.keypair.sign_message(transaction.message.to_bytes())
            signed_tx = VersionedTransaction.populate(transaction.message, [signature])

            # 3. Send the transaction
            result = await self.solana.client.send_raw_transaction(bytes(signed_tx))
            
            tx_hash = str(result.value)
            logger.info(f"Solana Trade Executed: {tx_hash}")
            return TradeResult(True, tx_hash=tx_hash)

        except Exception as e:
            logger.error(f"Error executing Solana swap: {e}")
            return TradeResult(False, error=str(e))

    async def close(self):
        """Close the aiohttp session."""
        await self.session.close()
