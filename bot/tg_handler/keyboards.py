from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Keyboards:
    
    @staticmethod
    def main_menu_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("📊 Status", callback_data="cmd_status"),
                InlineKeyboardButton("🤖 Force Decision", callback_data="cmd_decision")
            ],
            [
                InlineKeyboardButton("⚙️ Risk Settings", callback_data="cmd_risk"),
                InlineKeyboardButton("⛓️ Chains", callback_data="cmd_chains")
            ],
            [
                InlineKeyboardButton("🛑 EMERGENCY STOP", callback_data="cmd_stop")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def trade_approval_keyboard(decision_id: int):
        keyboard = [
            [
                InlineKeyboardButton("✅ APPROVE", callback_data=f"approve_{decision_id}"),
                InlineKeyboardButton("❌ REJECT", callback_data=f"reject_{decision_id}")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def mode_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("Auto", callback_data="mode_auto"),
                InlineKeyboardButton("Manual", callback_data="mode_manual"),
                InlineKeyboardButton("Paused", callback_data="mode_paused")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_stop_keyboard():
        keyboard = [
            [
                InlineKeyboardButton("⚠️ CONFIRM STOP ALL", callback_data="confirm_stop"),
                InlineKeyboardButton("Cancel", callback_data="cancel_stop")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
