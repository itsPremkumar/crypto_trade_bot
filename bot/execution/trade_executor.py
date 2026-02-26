import time
import logging
from typing import Dict, Any, Optional
from web3 import Web3
from bot.llm.decision_parser import TradeDecision
from bot.wallet import WalletManager
from bot.chain_manager import ChainManager
from bot.execution.gas_optimizer import GasOptimizer
from bot.dex.uniswap_v3 import UniswapV3
from bot.dex.pancakeswap_v3 import PancakeSwapV3

logger = logging.getLogger(__name__)

class TradeResult:
    def __init__(self, success: bool, tx_hash: Optional[str] = None, error: Optional[str] = None):
        self.success = success
        self.tx_hash = tx_hash
        self.error = error

class TradeExecutor:
    """Executes validated TradeDecision objects on the appropriate DEX."""

    def __init__(self, wallet: WalletManager, chain_manager: ChainManager, gas_optimizer: GasOptimizer):
        self.wallet = wallet
        self.chain_manager = chain_manager
        self.gas_optimizer = gas_optimizer
        
        # Initialize DEX interfaces lazily or upfront. Doing it upfront:
        w3_poly = self.chain_manager.get_w3('polygon') if 'polygon' in self.chain_manager.get_all_w3() else None
        w3_bsc = self.chain_manager.get_w3('bsc') if 'bsc' in self.chain_manager.get_all_w3() else None
        w3_base = self.chain_manager.get_w3('base') if 'base' in self.chain_manager.get_all_w3() else None
        
        self.dex_map = {}
        if w3_poly: self.dex_map['polygon'] = UniswapV3(w3_poly, 'polygon')
        if w3_base: self.dex_map['base'] = UniswapV3(w3_base, 'base')
        if w3_bsc: self.dex_map['bsc'] = PancakeSwapV3(w3_bsc)

    async def execute(self, decision: TradeDecision, amount_in_wei: int, min_amount_out_wei: int) -> TradeResult:
        """Routes and executes the trade."""
        if not decision.is_valid or decision.action not in ["BUY", "SELL"]:
            return TradeResult(False, error="Invalid decision for execution")
            
        chain = decision.chain.lower()
        if chain not in self.dex_map:
            return TradeResult(False, error=f"DEX router not configured for {chain}")
            
        dex = self.dex_map[chain]
        w3 = self.chain_manager.get_w3(chain)
        
        try:
            deadline = int(time.time()) + 60 # 60 seconds
            
            # 1. Build Transaction
            tx = await dex.build_swap_transaction(
                wallet_address=self.wallet.get_address(),
                token_in=decision.token_in,
                token_out=decision.token_out,
                amount_in_wei=amount_in_wei,
                min_amount_out_wei=min_amount_out_wei,
                deadline=deadline
            )
            
            # 2. Inject Gas Params
            gas_params = self.gas_optimizer.build_gas_params(chain)
            tx.update(gas_params)
            
            # Estimate gas limit
            try:
                gas_limit = w3.eth.estimate_gas(tx)
                tx['gas'] = int(gas_limit * 1.2) # 20% bumper
            except Exception as e:
                logger.warning(f"Gas estimation failed, using safe fallback: {e}")
                tx['gas'] = 300000 
                
            # 3. Sign Transaction
            signed_tx = self.wallet.sign_transaction(tx)
            
            # 4. Broadcast
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            hex_hash = w3.to_hex(tx_hash)
            logger.info(f"Transaction broadcasted on {chain}: {hex_hash}")
            
            # Wait for receipt
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            if receipt.status == 1:
                return TradeResult(True, tx_hash=hex_hash)
            else:
                return TradeResult(False, tx_hash=hex_hash, error="Transaction reverted by EVM")
                
        except Exception as e:
            logger.error(f"Execution failed on {chain}: {e}")
            return TradeResult(False, error=str(e))
