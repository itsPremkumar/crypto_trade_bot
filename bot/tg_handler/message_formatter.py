import datetime
from typing import Dict, Any
from bot.llm.decision_parser import TradeDecision

def escape_md(text: str) -> str:
    """Escapes special characters for Telegram MarkdownV2."""
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    # Escape backslashes first, then other characters
    res = text.replace('\\', '\\\\')
    for char in escape_chars:
        res = res.replace(char, f'\\{char}')
    return res

class MessageFormatter:
    
    @staticmethod
    def format_portfolio_status(portfolio: Dict[str, Any], state: Any) -> str:
        tot = f"${portfolio.get('total_balance_usd', 0.0):.2f}"
        avail = f"${portfolio.get('available_usd', 0.0):.2f}"
        todays_pnl = f"${state.daily_pnl_usd:.2f}"
        
        mode = escape_md(state.mode.upper())
        cb = escape_md("🟢 SAFE" if not state.circuit_breaker_active else "🔴 ACTIVE")
        
        status = f"""📊 *PORTFOLIO STATUS*
        
*Total Balance:* {escape_md(tot)}
*Available Capital:* {escape_md(avail)}
*Today's PnL:* {escape_md(todays_pnl)}

*Bot Mode:* {mode}
*Circuit Breaker:* {escape_md(cb)}
*Consecutive Losses:* {state.consecutive_losses}
"""
        return status

    @staticmethod
    def format_llm_decision(decision: TradeDecision, is_manual_request: bool = False, is_paper: bool = False) -> str:
        conf = f"{decision.confidence * 100:.1f}%"
        amt = f"${decision.amount_usd:.2f}"
        
        emoji = "🤖" if decision.action == "HOLD" else ("🟢" if decision.action == "BUY" else "🔴")
        paper_tag = "[PAPER] " if is_paper else ""
        
        msg = f"""{emoji} *{escape_md(paper_tag)}CLAUDE RECOMMENDS:* {escape_md(decision.action)}

*Token:* {escape_md(decision.token_in)} \-\> {escape_md(decision.token_out)}
*Amount:* {escape_md(amt)}
*Chain:* {escape_md(decision.chain)}
*Confidence:* {escape_md(conf)}

*Reason:*
_{escape_md(decision.reason)}_
"""
        return msg

    @staticmethod
    def format_trade_executed(decision: TradeDecision, tx_hash: str, is_paper: bool = False) -> str:
        amt = f"${decision.amount_usd:.2f}"
        paper_tag = "[PAPER] " if is_paper else ""
        msg = f"""🟢 *{escape_md(paper_tag)}TRADE EXECUTED*
        
*Action:* {escape_md(decision.action)} {escape_md(decision.token_out)}
*Amount:* {escape_md(amt)}
*Chain:* {escape_md(decision.chain)}

*Tx Hash:* `{escape_md(tx_hash)}`

🤖 *Claude's Reasoning:*
_{escape_md(decision.reason)}_
"""
        return msg

    @staticmethod
    def format_risk_override(decision: TradeDecision, reason: str) -> str:
        msg = f"""⚠️ *LLM DECISION OVERRIDDEN*

*Claude Wanted:* {escape_md(decision.action)} {escape_md(decision.token_out)} \(${decision.amount_usd:.2f}\)
*Override Reason:* {escape_md(reason)}
*Action Taken:* HOLD
"""
        return msg

    @staticmethod
    def format_trade_closed(token: str, pnl_usd: float, pnl_pct: float) -> str:
        emoji = "✅" if pnl_usd > 0 else "❌"
        msg = f"""{emoji} *POSITION CLOSED*

*Token:* {escape_md(token)}
*PnL:* {escape_md(f"${pnl_usd:.2f}")} \({escape_md(f"{pnl_pct:.1f}%")}\)
"""
        return msg

    @staticmethod
    def format_daily_report(stats: Dict[str, Any]) -> str:
        pnl = f"${stats.get('daily_pnl', 0.0):.2f}"
        win_rate = f"{stats.get('win_rate', 0.0):.1f}%"
        gas = f"${stats.get('gas_spent', 0.0):.3f}"
        
        msg = f"""📝 *DAILY PERFORMANCE REPORT*
        
*Total PnL Today:* {escape_md(pnl)}
*Trades Executed:* {stats.get('trade_count', 0)}
*Win Rate:* {escape_md(win_rate)}
*Gas Spent:* {escape_md(gas)}
"""
        return msg
