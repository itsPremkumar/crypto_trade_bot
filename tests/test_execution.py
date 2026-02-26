import pytest
from unittest.mock import MagicMock
from bot.llm.decision_parser import TradeDecision
from bot.execution.trade_executor import TradeExecutor

@pytest.mark.asyncio
async def test_execution_routing():
    mock_wallet = MagicMock()
    mock_wallet.get_address.return_value = "0xMockAddress"
    
    mock_chains = MagicMock()
    mock_chains.get_all_w3.return_value = {'polygon': MagicMock()}
    mock_chains.get_w3.return_value = MagicMock()
    
    mock_gas = MagicMock()
    
    executor = TradeExecutor(mock_wallet, mock_chains, mock_gas)
    
    # Needs UniV3 mock because w3_poly is mocked
    dex_mock = MagicMock()
    executor.dex_map['polygon'] = dex_mock
    
    decision = TradeDecision(
        action="BUY", chain="polygon", token_in="USDC", token_out="MATIC",
        amount_usd=2.5, reason="test", confidence=0.8, stop_loss_pct=2.0, take_profit_pct=1.0, urgency="normal", raw_response="{}"
    )
    
    # Should attempt to build tx and fail on eth broadcasting without proper w3 objects, 
    # but the routing to DEX should occur
    result = await executor.execute(decision, 2500000, 2400000)
    
    dex_mock.build_swap_transaction.assert_called_once()
