import datetime
from typing import Dict, Any, List

class ContextBuilder:
    """Builds the comprehensive JSON market context representation sent to Claude."""
    
    def __init__(self, db_manager, wallet_manager, market_analyzer):
        self.db_manager = db_manager
        self.wallet = wallet_manager
        self.analyzer = market_analyzer

    async def build(self, portfolio_balance: float, available_balance: float, open_positions: List[Dict], gas_costs: Dict[str, Any]) -> Dict[str, Any]:
        """Assembles the state dictionary."""
        
        # Get market data from analyzer
        market_data = await self.analyzer.analyze_all_markets()
        
        # Get bot state
        state = self.db_manager.get_bot_state()
        
        # Get recent trades
        recent_trades_orm = self.db_manager.get_recent_trades(limit=3)
        recent_trades = [
            {
                "action": t.action,
                "token": f"{t.token_in} to {t.token_out}",
                "amount_usd": t.amount_usd,
                "result": t.status,
                "timestamp": t.timestamp.isoformat()
            } for t in recent_trades_orm
        ]

        # Calculate daily loss remaining pct roughly based on Config
        # In a real impl we'd read daily_pnl from DB
        
        context = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "portfolio": {
                "total_balance_usd": portfolio_balance,
                "available_usd": available_balance,
                "open_positions": open_positions,
                "todays_pnl_usd": state.daily_pnl_usd,
                "daily_loss_remaining_pct": 5.0 # hardcoded placeholder pending RiskManager impl
            },
            "market_data": market_data,
            "gas_costs": gas_costs,
            "recent_trades": recent_trades,
            "consecutive_losses": state.consecutive_losses,
            "circuit_breaker_active": state.circuit_breaker_active,
            "bot_mode": state.mode
        }
        return context
