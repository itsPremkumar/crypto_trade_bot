import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from bot.config import Config
from bot.telegram.message_formatter import MessageFormatter
from bot.telegram.keyboards import Keyboards

logger = logging.getLogger(__name__)

class BotController:
    """Main Telegram bot interface managing commands and callbacks."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
        
    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("setmode", self.cmd_setmode))
        self.app.add_handler(CommandHandler("stop", self.cmd_stop))
        self.app.add_handler(CommandHandler("help", self.cmd_help))

        # Handle UI buttons
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))

    async def _require_auth(self, update: Update) -> bool:
        if str(update.effective_chat.id) != Config.TELEGRAM_CHAT_ID:
            await update.effective_message.reply_text("Unauthorized.")
            return False
        return True

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update): return
        
        state = self.db.get_bot_state()
        msg = f"🚀 Crypto Bot Started\n\nCurrent Mode: {state.mode.upper()}\nUse the menu below to navigate."
        await update.message.reply_text(msg, reply_markup=Keyboards.main_menu_keyboard())

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update): return
        
        state = self.db.get_bot_state()
        # Mock portfolio for telegram output
        portfolio = {"total_balance_usd": 10.0, "available_usd": 10.0}
        msg = MessageFormatter.format_portfolio_status(portfolio, state)
        
        await update.message.reply_text(msg, parse_mode='MarkdownV2')

    async def cmd_setmode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update): return
        
        args = context.args
        if args and args[0].lower() in ['auto', 'manual', 'paused']:
            new_mode = args[0].lower()
            self.db.update_bot_state(mode=new_mode)
            await update.message.reply_text(f"Mode set to: {new_mode.upper()}")
        else:
            await update.message.reply_text("Select bot mode:", reply_markup=Keyboards.mode_keyboard())

    async def cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update): return
        await update.message.reply_text(
            "🛑 WARNING: Emergency stop will pause all trading and attempt to close open positions. Proceed?",
            reply_markup=Keyboards.confirm_stop_keyboard()
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update): return
        help_txt = """
/start - Main menu
/status - Portfolio and bot status
/decision - Force LLM analysis (Not implemented in stub)
/setmode [auto|manual|paused] - Change execution mode
/stop - Emergency stop trading
"""
        await update.message.reply_text(help_txt)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if not await self._require_auth(update): return

        data = query.data
        if data == "cmd_status":
            await self.cmd_status(update, context)
        elif data.startswith("mode_"):
            new_mode = data.split("_")[1]
            self.db.update_bot_state(mode=new_mode)
            await query.edit_message_text(f"Mode updated to: {new_mode.upper()}")
        elif data == "confirm_stop":
            self.db.update_bot_state(mode="paused")
            await query.edit_message_text("🛑 BOT PAUSED. Automatic execution stopped.")
        elif data == "cmd_stop":
            await query.edit_message_text(
                "🛑 WARNING: Emergency stop will pause all trading. Proceed?",
                reply_markup=Keyboards.confirm_stop_keyboard()
            )
        elif data == "cancel_stop":
            await query.edit_message_text("Stop cancelled.")

    async def send_message(self, text: str, parse_mode: str = 'MarkdownV2', reply_markup=None):
        """Sends a notification to the configured admin chat."""
        try:
            await self.app.bot.send_message(
                chat_id=Config.TELEGRAM_CHAT_ID,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to send telegram message: {e}")

    def run_polling(self):
        """Used if running in a separate thread. For APScheduler we use run_polling separately."""
        self.app.run_polling()
