import pytest
from bot.risk.risk_manager import RiskManager
from bot.execution.gas_optimizer import GasOptimizer
from bot.llm.decision_parser import TradeDecision

class MockDBManager:
    def get_bot_state(self):
        class State:
            circuit_breaker_active = False
            daily_pnl_usd = 0.0
            mode = "auto"
        return State()

class MockGasOptimizer(GasOptimizer):
    def __init__(self):
        pass
    def get_estimated_gas_cost_usd(self, chain, **kwargs):
        # High gas specifically for polygon mock failure
        if chain == 'polygon': return 0.50 
        return 0.01

@pytest.fixture
def risk_manager():
    return RiskManager(MockGasOptimizer(), MockDBManager())

def test_risk_manager_gas_limit(risk_manager):
    decision = TradeDecision(
        action="BUY", chain="polygon", token_in="USDC", token_out="MATIC",
        amount_usd=5.0, reason="test", confidence=0.8, stop_loss_pct=2.0, take_profit_pct=1.0, urgency="normal", raw_response="{}"
    )
    
    # Polygon gas mocked to $0.50, which > Config.MAX_GAS_USD (0.30 by default env)
    # So it should be overridden
    is_safe = risk_manager.validate(decision, portfolio_value=10.0)
    assert is_safe is False
    assert decision.was_overridden is True
    assert "Gas cost" in decision.override_reason

def test_risk_manager_max_trade_size(risk_manager):
    decision = TradeDecision(
        action="BUY", chain="bsc", token_in="USDC", token_out="BNB",
        amount_usd=5.0, reason="test", confidence=0.8, stop_loss_pct=2.0, take_profit_pct=1.0, urgency="normal", raw_response="{}"
    )
    
    # Trade size $5.0 > 20% of $10 ($2.0)
    is_safe = risk_manager.validate(decision, portfolio_value=10.0)
    assert is_safe is False
    assert decision.was_overridden is True
    assert "exceeds max allowed" in decision.override_reason

def test_risk_manager_valid_trade(risk_manager):
    decision = TradeDecision(
        action="BUY", chain="base", token_in="USDC", token_out="ETH",
        amount_usd=1.5, reason="test", confidence=0.8, stop_loss_pct=2.0, take_profit_pct=1.0, urgency="normal", raw_response="{}"
    )
    
    is_safe = risk_manager.validate(decision, portfolio_value=10.0)
    assert is_safe is True
    assert decision.was_overridden is False
