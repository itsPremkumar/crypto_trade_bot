import datetime
from typing import Dict, Any, List

class ContextBuilder:
    """Builds the comprehensive JSON market context representation sent to Claude."""
    
    def __init__(self, db_manager, wallet_manager, market_analyzer, solana_manager=None):
        self.db_manager = db_manager
        self.wallet = wallet_manager
        self.analyzer = market_analyzer
        self.solana = solana_manager

    async def build(self, portfolio_balance: float, available_balance: float, open_positions: List[Dict], gas_costs: Dict[str, Any]) -> Dict[str, Any]:
        """Assembles the state dictionary."""
        from bot.config import Config
        
        if Config.TRADING_MODE == "paper":
            portfolio_balance = self.db_manager.get_paper_balance('global', 'USD')
            available_balance = portfolio_balance
            # Calculate value of paper altcoins
            market_data_temp = await self.analyzer.analyze_all_markets()
            sol_price = market_data_temp.get("SOL/USDC", {}).get("price", 0.0)
            paper_sol = self.db_manager.get_paper_balance('solana', 'SOL')
            if paper_sol > 0:
                portfolio_balance += (paper_sol * sol_price)
                open_positions.append({"token": "SOL", "amount": paper_sol, "value_usd": paper_sol * sol_price})
                
            matic_price = market_data_temp.get("MATIC/USDC", {}).get("price", 0.0)
            paper_matic = self.db_manager.get_paper_balance('polygon', 'MATIC')
            if paper_matic > 0:
                portfolio_balance += (paper_matic * matic_price)
                open_positions.append({"token": "MATIC", "amount": paper_matic, "value_usd": paper_matic * matic_price})
        else:
            # Inject Solana balance if manager is present (Live Mode)
            sol_balance_usd = 0.0
            if self.solana:
                sol_qty = await self.solana.get_balance()
                market_data_temp = await self.analyzer.analyze_all_markets() # We need prices
                sol_price = market_data_temp.get("SOL/USDC", {}).get("price", 0.0)
                sol_balance_usd = sol_qty * sol_price
                portfolio_balance += sol_balance_usd
                available_balance += sol_balance_usd # Simplified for demo
        
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
