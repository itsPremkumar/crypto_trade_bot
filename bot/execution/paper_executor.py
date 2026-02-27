import logging
import uuid
import datetime
import base64
from typing import NamedTuple, Optional
from bot.database.models import LLMDecision
from bot.database.db_manager import DBManager
from bot.data.market_analyzer import MarketAnalyzer

logger = logging.getLogger(__name__)

class TradeResult(NamedTuple):
    success: bool
    tx_hash: Optional[str] = None
    error: Optional[str] = None

class PaperExecutor:
    """Simulates trade execution using real market prices against a virtual wallet."""
    
    def __init__(self, db_manager: DBManager, analyzer: MarketAnalyzer):
        self.db = db_manager
        self.analyzer = analyzer

    async def execute(self, decision: LLMDecision) -> TradeResult:
        try:
            # 1. Fetch current realistic price
            token_id = decision.token_out if decision.action == "BUY" else decision.token_in
            if token_id in ["WSOL", "SOL"]:
                token_id = "solana"
            elif token_id in ["WMATIC", "MATIC"]:
                token_id = "matic-network"
            elif token_id in ["WBNB", "BNB"]:
                token_id = "binancecoin"
                
            market_data_dict = await self.analyzer.analyze_all_markets()
            
            # Map token_id to the key returned by analyze_all_markets (e.g. solana -> SOL/USDC)
            market_key = None
            if token_id == "solana": market_key = "SOL/USDC"
            elif token_id == "matic-network": market_key = "MATIC/USDC"
            elif token_id == "binancecoin": market_key = "BNB/USDC"
            
            market_data = market_data_dict.get(market_key, {}) if market_key else {}
            
            if not market_data or market_data.get('price', 0) <= 0:
                # If we lack price data, we can't accurately simulate
                return TradeResult(False, error=f"Could not fetch realistic price for {token_id} to simulate trade.")

            current_price = market_data['price']

            # 2. Calculate Slippage & Gas (Simulated)
            # Simulated 0.1% slippage for conservatism
            simulated_gas_usd = 0.005 if decision.chain == "solana" else 0.05
            
            # 3. Process execution
            if decision.action == "BUY":
                # We are spending USD to get tokens
                required_usd = decision.amount_usd + simulated_gas_usd
                
                # Check paper balance
                available_usd = self.db.get_paper_balance('global', 'USD')
                if available_usd < required_usd:
                    return TradeResult(False, error=f"Insufficient Paper Balance. Have ${available_usd:.2f}, Need ${required_usd:.2f}")
                
                # Execute Deductions
                # Calculate tokens acquired (subtract slippage)
                tokens_acquired = (decision.amount_usd / current_price) * 0.999 
                
                self.db.update_paper_balance('global', 'USD', -required_usd)
                self.db.update_paper_balance(decision.chain, decision.token_out, tokens_acquired)
                logger.info(f"[PAPER TRADE] Bought {tokens_acquired:.6f} {decision.token_out} for ${decision.amount_usd:.2f} + ${simulated_gas_usd} gas.")
                
            elif decision.action == "SELL":
                # We are selling tokens to get USD
                tokens_to_sell = decision.amount_usd / current_price # Assuming the LLM uses amount_usd conceptually
                
                available_tokens = self.db.get_paper_balance(decision.chain, decision.token_in)
                if available_tokens <= 0:
                   return TradeResult(False, error=f"Insufficient Paper {decision.token_in} balance.")
                
                # If amount to sell is larger than balance, just sell balance
                if tokens_to_sell > available_tokens:
                    tokens_to_sell = available_tokens
                    
                usd_acquired = (tokens_to_sell * current_price) * 0.999 - simulated_gas_usd
                
                self.db.update_paper_balance(decision.chain, decision.token_in, -tokens_to_sell)
                self.db.update_paper_balance('global', 'USD', usd_acquired)
                logger.info(f"[PAPER TRADE] Sold {tokens_to_sell:.6f} {decision.token_in} for ${usd_acquired:.2f} (post-gas).")

            else:
                return TradeResult(False, error="Unknown action")

            # 4. Generate Mock TX Hash
            tx_hash = "PAPER_TX_" + base64.b64encode(str(datetime.datetime.now().timestamp()).encode()).decode()[:12]
            return TradeResult(True, tx_hash=tx_hash)

        except Exception as e:
            logger.error(f"Paper execution failed: {e}")
            return TradeResult(False, error=str(e))
