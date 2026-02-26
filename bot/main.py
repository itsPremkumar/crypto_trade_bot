import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.config import Config
from bot.database.db_manager import DBManager
from bot.database.models import Trade, LLMDecision
from bot.wallet import WalletManager
from bot.chain_manager import ChainManager
from bot.data.price_feed import PriceFeed
from bot.data.market_analyzer import MarketAnalyzer
from bot.llm.claude_brain import ClaudeBrain
from bot.llm.ollama_brain import OllamaBrain
from bot.llm.context_builder import ContextBuilder
from bot.execution.gas_optimizer import GasOptimizer
from bot.execution.trade_executor import TradeExecutor
from bot.risk.risk_manager import RiskManager
from bot.telegram.bot_controller import BotController
from bot.telegram.message_formatter import MessageFormatter

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CryptoBot:
    def __init__(self):
        logger.info("Initializing Decentralized Crypto Trading Bot ($10 Capital Focus)")
        Config.validate()
        
        self.db = DBManager()
        self.wallet = WalletManager()
        self.chains = ChainManager()
        
        self.price_feed = PriceFeed()
        self.analyzer = MarketAnalyzer(self.price_feed)
        
        # Dynamic LLM Provider Selection
        if Config.LLM_PROVIDER == "ollama":
            self.brain = OllamaBrain()
        else:
            self.brain = ClaudeBrain()
            
        self.context_builder = ContextBuilder(self.db, self.wallet, self.analyzer)
        
        self.gas_optimizer = GasOptimizer(self.chains.get_all_w3())
        self.executor = TradeExecutor(self.wallet, self.chains, self.gas_optimizer)
        self.risk_manager = RiskManager(self.gas_optimizer, self.db)
        
        self.telegram = BotController(self.db, self.brain)
        
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    async def trading_cycle(self):
        """Main loop executed every 30 seconds."""
        state = self.db.get_bot_state()
        
        if state.mode == "paused":
            logger.debug("Bot is paused. Skipping cycle.")
            return
            
        logger.info("Starting trading cycle...")
        
        # 1. Gather mock portfolio mapping (in real-world, we'd query ERC20 balances via Web3)
        portfolio_balance = 10.0
        available_balance = 10.0
        open_positions = []
        
        # 2. Build gas context
        gas_costs = {}
        for chain in Config.ACTIVE_CHAINS:
            gas_costs[chain] = self.gas_optimizer.get_estimated_gas_cost_usd(chain)
            
        # 3. Build Full Context
        context = await self.context_builder.build(portfolio_balance, available_balance, open_positions, gas_costs)
        
        # 4. Ask Brain
        decision = await self.brain.analyze_market(context)
        
        # Save decision
        llm_dec = LLMDecision(
            raw_context_json=str(context),
            raw_response_json=decision.raw_response,
            action=decision.action,
            confidence=decision.confidence,
            reason=decision.reason
        )
        
        # 5. Risk Verification
        is_safe = self.risk_manager.validate(decision, portfolio_balance)
        if not is_safe:
            llm_dec.was_overridden = True
            llm_dec.override_reason = decision.override_reason
            self.db.log_llm_decision(llm_dec)
            
            msg = MessageFormatter.format_risk_override(decision, decision.override_reason)
            await self.telegram.send_message(msg)
            return
            
        self.db.log_llm_decision(llm_dec)
            
        if decision.action == "HOLD":
            return
            
        # 6. Execution Flow
        if state.mode == "manual":
            # Send approval request to Telegram
            msg = MessageFormatter.format_llm_decision(decision, True)
            await self.telegram.send_message(msg)
            logger.info("Sent manual approval request to Telegram.")
            # We wait for callback to execute...
            return
            
        elif state.mode == "auto":
            logger.info("Auto-executing trade...")
            # Using placeholder WEI amounts for demonstration. A robust build calculates this from amount_usd and oracle price.
            amount_in_wei = int(decision.amount_usd * 1e18) 
            min_out_wei = int(amount_in_wei * 0.95)
            
            result = await self.executor.execute(decision, amount_in_wei, min_out_wei)
            
            llm_dec.was_executed = result.success
            llm_dec.outcome = result.tx_hash if result.success else result.error
            self.db.log_llm_decision(llm_dec) # update
            
            trade = Trade(
                action=decision.action,
                token_in=decision.token_in,
                token_out=decision.token_out,
                amount_usd=decision.amount_usd,
                chain=decision.chain,
                tx_hash=result.tx_hash or "failed",
                status="open" if result.success else "failed"
            )
            self.db.log_trade(trade)
            
            if result.success:
                msg = MessageFormatter.format_trade_executed(decision, result.tx_hash)
                await self.telegram.send_message(msg)

    async def report_cycle(self):
        """Hourly reporting."""
        logger.info("Generating hourly report...")
        state = self.db.get_bot_state()
        stats = {
            "daily_pnl": state.daily_pnl_usd,
            "trade_count": len(self.db.get_recent_trades(100)),
            "win_rate": 55.5, # mock
            "gas_spent": 0.12 # mock
        }
        msg = MessageFormatter.format_daily_report(stats)
        await self.telegram.send_message(msg)

    async def start(self):
        """Start scheduler and telegram bot."""
        await self.telegram.app.initialize()
        await self.telegram.app.start()
        await self.telegram.app.updater.start_polling()
        
        self.scheduler.add_job(self.trading_cycle, 'interval', seconds=30)
        self.scheduler.add_job(self.report_cycle, 'interval', hours=1)
        self.scheduler.start()
        self.is_running = True
        
        await self.telegram.send_message("🟢 Bot online and scheduler started.")
        
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            await self.stop()

    async def stop(self):
        logger.info("Shutting down bot...")
        self.is_running = False
        self.scheduler.shutdown()
        await self.price_feed.close()
        await self.telegram.app.updater.stop()
        await self.telegram.app.stop()
        await self.telegram.app.shutdown()

async def run():
    bot = CryptoBot()
    await bot.start()

if __name__ == "__main__":
    if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run())
