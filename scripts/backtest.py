import asyncio
import logging
from bot.llm.context_builder import ContextBuilder
from bot.llm.claude_brain import ClaudeBrain

# Simple backtest scaffold
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_scenario():
    logger.info("Initializing Backtest Simulator...")
    brain = ClaudeBrain()
    
    mock_context = {
        "timestamp": "2024-01-01T12:00:00Z",
        "portfolio": {
            "total_balance_usd": 10.0,
            "available_usd": 10.0,
            "open_positions": [],
            "todays_pnl_usd": 0.0,
            "daily_loss_remaining_pct": 5.0
        },
        "market_data": {
            "MATIC/USDC": {
                "price": 0.91,
                "change_1h_pct": 2.5,
                "change_24h_pct": -5.0,
                "volume_24h_usd": 5000000,
                "rsi_14": 28.5,
                "ema_9": 0.90,
                "ema_21": 0.93,
                "bb_upper": 0.95,
                "bb_lower": 0.88,
                "bb_mid": 0.92
            }
        },
        "gas_costs": {
            "polygon": 0.01,
            "bsc": 0.08,
            "base": 0.005
        },
        "recent_trades": [],
        "consecutive_losses": 0,
        "circuit_breaker_active": False,
        "bot_mode": "auto"
    }

    logger.info("Sending historical tick to Claude Brain...")
    decision = await brain.analyze_market(mock_context)
    
    logger.info("---- BACKTEST RESULT ----")
    logger.info(f"Action: {decision.action}")
    logger.info(f"Size: ${decision.amount_usd}")
    logger.info(f"Reason: {decision.reason}")

if __name__ == "__main__":
    asyncio.run(run_scenario())
