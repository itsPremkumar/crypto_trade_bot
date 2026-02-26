import asyncio
import sys
import os
import aiohttp

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import Config
from bot.llm.ollama_brain import OllamaBrain

async def test_ollama():
    print("--- Ollama Connection Test ---")
    print(f"Provider: {Config.LLM_PROVIDER}")
    print(f"Base URL: {Config.OLLAMA_BASE_URL}")
    print(f"Model: {Config.OLLAMA_MODEL}")
    
    brain = OllamaBrain()
    
    print("\n1. Testing Chat functionality...")
    chat_response = await brain.chat("Hello! Are you working?")
    print(f"Response: {chat_response}")
    
    print("\n2. Testing Market Analysis interface...")
    # Mock context
    context = {
        "portfolio": {"balance_usd": 10.0},
        "market_data": {"chain": "polygon", "token": "MATIC", "rsi": 30}
    }
    decision = await brain.analyze_market(context)
    print(f"Decision Action: {decision.action}")
    print(f"Reason: {decision.reason}")
    print(f"Confidence: {decision.confidence}")
    
    if decision.action != "HOLD" or "Error" not in chat_response:
        print("\n✅ Ollama appears to be working correctly with the custom brain!")
    else:
        print("\n❌ Something might be wrong. Check if Ollama is running and model is pulled.")

if __name__ == "__main__":
    asyncio.run(test_ollama())
