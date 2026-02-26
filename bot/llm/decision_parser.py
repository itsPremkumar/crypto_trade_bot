import json
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class TradeDecision:
    action: str
    chain: Optional[str]
    token_in: Optional[str]
    token_out: Optional[str]
    amount_usd: float
    reason: str
    confidence: float
    stop_loss_pct: float
    take_profit_pct: float
    urgency: str
    raw_response: str
    is_valid: bool = True

class DecisionParser:
    """Parses and validates Claude's JSON response."""

    @staticmethod
    def parse(raw_response: str) -> TradeDecision:
        try:
            # Claude sometimes adds markdown code block wrappers
            clean_str = raw_response.strip()
            if clean_str.startswith("```json"):
                clean_str = clean_str[7:]
            if clean_str.startswith("```"):
                clean_str = clean_str[3:]
            if clean_str.endswith("```"):
                clean_str = clean_str[:-3]
            clean_str = clean_str.strip()

            data = json.loads(clean_str)

            action = data.get("action", "HOLD").upper()
            if action not in ["BUY", "SELL", "HOLD"]:
                raise ValueError(f"Invalid action: {action}")

            return TradeDecision(
                action=action,
                chain=data.get("chain"),
                token_in=data.get("token_in"),
                token_out=data.get("token_out"),
                amount_usd=float(data.get("amount_usd", 0.0) or 0.0),
                reason=data.get("reason", "No reason provided"),
                confidence=float(data.get("confidence", 0.0)),
                stop_loss_pct=float(data.get("stop_loss_pct", 0.0) or 0.0),
                take_profit_pct=float(data.get("take_profit_pct", 0.0) or 0.0),
                urgency=data.get("urgency", "normal"),
                raw_response=raw_response,
                is_valid=True
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON: {e}\nRaw={raw_response}")
            return DecisionParser.fallback(raw_response, f"JSON Error: {e}")
        except Exception as e:
            logger.error(f"Failed to validate LLM decision schema: {e}\nRaw={raw_response}")
            return DecisionParser.fallback(raw_response, f"Validation Error: {e}")

    @staticmethod
    def fallback(raw: str, reason: str) -> TradeDecision:
        return TradeDecision(
            action="HOLD",
            chain=None,
            token_in=None,
            token_out=None,
            amount_usd=0.0,
            reason=f"Fallback to HOLD due to parser error: {reason}",
            confidence=0.0,
            stop_loss_pct=0.0,
            take_profit_pct=0.0,
            urgency="low",
            raw_response=raw,
            is_valid=False
        )
