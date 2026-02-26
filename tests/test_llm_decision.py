import pytest
from bot.llm.decision_parser import DecisionParser, TradeDecision

def test_parser_valid_json():
    raw = '''
    {
      "action": "BUY",
      "chain": "polygon",
      "token_in": "USDC",
      "token_out": "MATIC",
      "amount_usd": 2.50,
      "reason": "Looking good",
      "confidence": 0.82,
      "stop_loss_pct": 2.0,
      "take_profit_pct": 1.5,
      "urgency": "normal",
      "risk_check": "passed"
    }
    '''
    decision = DecisionParser.parse(raw)
    assert decision.is_valid is True
    assert decision.action == "BUY"
    assert decision.amount_usd == 2.50
    assert decision.confidence == 0.82

def test_parser_invalid_json():
    raw = '''{ "action": BUY, missing quotes}'''
    decision = DecisionParser.parse(raw)
    assert decision.is_valid is False
    assert decision.action == "HOLD"
    assert "Fallback" in decision.reason

def test_parser_markdown_wrapper():
    raw = '''```json\n{"action":"SELL","amount_usd":1.0}\n```'''
    decision = DecisionParser.parse(raw)
    assert decision.is_valid is True
    assert decision.action == "SELL"
    assert decision.amount_usd == 1.0
