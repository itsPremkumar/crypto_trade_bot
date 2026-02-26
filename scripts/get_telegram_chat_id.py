import asyncio
import sys
import os

# Add project root to path to import config if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from telegram import Bot
except ImportError:
    print("Error: 'python-telegram-bot' package not found. Please run: pip install python-telegram-bot")
    sys.exit(1)

async def get_chat_id(token):
    bot = Bot(token=token)
    print(f"Checking for messages to bot with token: {token}")
    print("Please send a message to your bot on Telegram now...")
    
    while True:
        try:
            updates = await bot.get_updates(timeout=10)
            if updates:
                last_update = updates[-1]
                chat_id = last_update.message.chat_id
                username = last_update.message.from_user.username
                print(f"\nSuccess! found message from @{username}")
                print(f"Your TELEGRAM_CHAT_ID is: {chat_id}")
                print("\nAdd this to your .env file:")
                print(f"TELEGRAM_CHAT_ID={chat_id}")
                return
            else:
                print(".", end="", flush=True)
                await asyncio.sleep(2)
        except Exception as e:
            print(f"\nError: {e}")
            print("Make sure your token is correct and you have an internet connection.")
            return

if __name__ == "__main__":
    token = input("Enter your Telegram Bot Token (from BotFather): ").strip()
    if not token:
        print("Token is required.")
        sys.exit(1)
        
    asyncio.run(get_chat_id(token))
