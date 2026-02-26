import logging
from bot.config import Config
from bot.llm.decision_parser import TradeDecision
from bot.execution.gas_optimizer import GasOptimizer

logger = logging.getLogger(__name__)

class RiskManager:
    """Hard-coded risk rules that ALWAYS override the LLM."""
    
    def __init__(self, gas_optimizer: GasOptimizer, db_manager):
        self.gas_optimizer = gas_optimizer
        self.db = db_manager

    def validate(self, decision: TradeDecision, portfolio_value: float) -> bool:
        """
        Returns True if the trade is approved by Risk rules.
        If False, updates the decision object with the override reason.
        """
        if decision.action == "HOLD":
            return True # Holds are always safe
            
        if not decision.is_valid:
            return False

        try:
            # Rule 1: Circuit breaker
            state = self.db.get_bot_state()
            if state.circuit_breaker_active:
                decision.was_overridden = True
                decision.override_reason = "Circuit Breaker is active"
                logger.warning(f"Risk Override: {decision.override_reason}")
                return False

            # Rule 2: Minimum portfolio balance
            if portfolio_value < Config.MIN_BALANCE_USD:
                decision.was_overridden = True
                decision.override_reason = f"Portfolio value ${portfolio_value} below minimum ${Config.MIN_BALANCE_USD}"
                logger.warning(f"Risk Override: {decision.override_reason}")
                return False

            # Rule 3: Max single trade risk
            max_allowed = portfolio_value * (Config.MAX_TRADE_PERCENT / 100.0)
            if decision.amount_usd > max_allowed:
                # Instead of overriding, we could cap it, but spec says "Confirm amount_usd <= max allowed... If any check fails: override with HOLD"
                decision.was_overridden = True
                decision.override_reason = f"Trade size ${decision.amount_usd} exceeds max allowed ${max_allowed}"
                logger.warning(f"Risk Override: {decision.override_reason}")
                return False

            # Rule 4: Minimum trade size
            if decision.amount_usd < Config.MIN_TRADE_USD:
                decision.was_overridden = True
                decision.override_reason = f"Trade size ${decision.amount_usd} is below minimum ${Config.MIN_TRADE_USD}"
                logger.warning(f"Risk Override: {decision.override_reason}")
                return False

            # Rule 5: Gas cost vs Expected Profit threshold (3x profit vs gas cost as per Prompt, but here we enforce hard MAX_GAS_USD)
            gas_cost_usd = self.gas_optimizer.get_estimated_gas_cost_usd(decision.chain)
            if gas_cost_usd > Config.MAX_GAS_USD:
                decision.was_overridden = True
                decision.override_reason = f"Gas cost ${gas_cost_usd:.3f} exceeds maximum ${Config.MAX_GAS_USD}"
                logger.warning(f"Risk Override: {decision.override_reason}")
                return False
                
            # Rule 6: Daily loss limit
            if state.daily_pnl_usd < 0:
                loss_pct = abs(state.daily_pnl_usd) / portfolio_value * 100
                if loss_pct >= Config.MAX_DAILY_LOSS_PERCENT:
                    decision.was_overridden = True
                    decision.override_reason = f"Daily loss limit reached: {loss_pct:.1f}%"
                    logger.warning(f"Risk Override: {decision.override_reason}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Risk Manager crashed during validation: {e}")
            decision.was_overridden = True
            decision.override_reason = f"Risk Exception: {e}"
            return False
