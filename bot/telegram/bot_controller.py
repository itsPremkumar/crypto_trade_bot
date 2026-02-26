import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from bot.config import Config
from bot.telegram.message_formatter import MessageFormatter, escape_md
from bot.telegram.keyboards import Keyboards

logger = logging.getLogger(__name__)

class BotController:
    """Main Telegram bot interface managing commands, pairing, and LLM chat."""
    
    def __init__(self, db_manager, brain):
        self.db = db_manager
        self.brain = brain
        self.app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
        
    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("pair", self.cmd_pair))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("setmode", self.cmd_setmode))
        self.app.add_handler(CommandHandler("stop", self.cmd_stop))
        self.app.add_handler(CommandHandler("help", self.cmd_help))

        # Handle UI buttons
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Handle chat messages (LLM Reply)
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_chat))

    async def _require_auth(self, update: Update) -> bool:
        """Dynamic auth check against DB-stored admin_chat_id."""
        state = self.db.get_bot_state()
        chat_id = str(update.effective_chat.id)
        
        if not state.is_paired:
            if update.message and "/pair" not in update.message.text:
                msg = "⚠️ *Bot not paired\\.*\n\nPlease use `/pair <code>` to authorize this chat\\."
                await update.effective_message.reply_text(msg, parse_mode='MarkdownV2')
            return False
            
        if chat_id != state.admin_chat_id:
            await update.effective_message.reply_text("⛔ *Unauthorized\\.* Only the paired admin can use this bot\\.", parse_mode='MarkdownV2')
            return False
            
        return True

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        state = self.db.get_bot_state()
        if not state.is_paired:
            msg = "👋 *Welcome to Crypto Bot\\!*\n\nThis bot is currently *UNPAIRED*\\. To begin, please send:\n`/pair <your_pairing_code>`"
            await update.message.reply_text(msg, parse_mode='MarkdownV2')
            return

        if not await self._require_auth(update): return
        
        msg = f"🚀 *Crypto Bot Active*\n\nCurrent Mode: `{escape_md(state.mode.upper())}`\nUse the menu below to navigate\\."
        await update.message.reply_text(msg, reply_markup=Keyboards.main_menu_keyboard(), parse_mode='MarkdownV2')

    async def cmd_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        state = self.db.get_bot_state()
        if state.is_paired:
            await update.message.reply_text("✅ Bot is already paired to an admin\\.")
            return

        if not context.args:
            await update.message.reply_text("❌ Usage: `/pair <code>`")
            return

        provided_code = context.args[0]
        if provided_code == state.pairing_code:
            chat_id = str(update.effective_chat.id)
            self.db.update_bot_state(admin_chat_id=chat_id, is_paired=True)
            await update.message.reply_text("✨ *Pairing Successful\\!*\n\nYou are now the authorized admin of this bot\\.", parse_mode='MarkdownV2')
            await self.cmd_start(update, context)
        else:
            await update.message.reply_text("❌ *Invalid pairing code\\.* Check your console or environment variables\\.", parse_mode='MarkdownV2')

    async def handle_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processes user messages using ClaudeBrain."""
        if not await self._require_auth(update): return
        
        user_text = update.message.text
        await update.message.reply_chat_action("typing")
        
        response = await self.brain.chat(user_text)
        await update.message.reply_text(escape_md(response), parse_mode='MarkdownV2')

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update): return
        
        state = self.db.get_bot_state()
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
            "🛑 *WARNING\\:* Emergency stop will pause all trading\\. Proceed?",
            reply_markup=Keyboards.confirm_stop_keyboard(),
            parse_mode='MarkdownV2'
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update): return
        help_txt = """
*Bot Commands\\:*
/start \- Main menu
/status \- Portfolio status
/setmode \- Change bot mode
/stop \- Emergency stop
/pair \- Authorization \(if not paired\)

_Simply type any message to chat with Claude for market insights\\!_
"""
        await update.message.reply_text(help_txt, parse_mode='MarkdownV2')

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
        elif data == "cancel_stop":
            await query.edit_message_text("Stop cancelled.")

    async def send_message(self, text: str, parse_mode: str = 'MarkdownV2', reply_markup=None):
        """Sends a notification to the paired admin."""
        state = self.db.get_bot_state()
        if not state.is_paired or not state.admin_chat_id:
            logger.warning("Attempted to send message but bot is not paired.")
            return
            
        try:
            await self.app.bot.send_message(
                chat_id=state.admin_chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Failed to send telegram message: {e}")
