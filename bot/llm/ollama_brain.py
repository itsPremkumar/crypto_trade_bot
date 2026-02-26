import aiohttp
import json
import logging
from typing import Dict, Any
from bot.config import Config
from bot.llm.prompt_templates import PromptTemplates
from bot.llm.decision_parser import DecisionParser, TradeDecision

logger = logging.getLogger(__name__)

class OllamaBrain:
    """Decision engine using a local Ollama instance."""

    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL.rstrip('/')
        self.model = Config.OLLAMA_MODEL
        self.temperature = Config.LLM_TEMPERATURE

    async def analyze_market(self, context: Dict[str, Any]) -> TradeDecision:
        """Sends full JSON context to local Ollama and safely parses the response."""
        system_prompt = PromptTemplates.SYSTEM_PROMPT
        user_message = json.dumps(context, indent=2)
        
        # Combine system and user prompt for Ollama generate endpoint
        full_prompt = f"{system_prompt}\n\nMarket Context:\n{user_message}"

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature
            },
            "format": "json"
        }

        try:
            logger.info(f"Querying local Ollama ({self.model}) for market decision...")
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama returned status {response.status}: {error_text}")
                    
                    result = await response.json()
                    raw_text = result.get("response", "")
                    
                    decision = DecisionParser.parse(raw_text)
                    logger.info(f"Ollama returned decision: Action={decision.action}")
                    return decision

        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return DecisionParser.fallback(raw="", reason=f"Ollama Error: {str(e)}")

    async def chat(self, message: str) -> str:
        """Handles general chat messages from the user using local Ollama."""
        payload = {
            "model": self.model,
            "prompt": f"You are a helpful crypto trading assistant. Acknowledge that you are the local brain (Ollama) of this trading bot. Keep responses concise and helpful.\n\nUser: {message}",
            "stream": False,
            "options": {
                "temperature": 0.7
            }
        }

        try:
            logger.info(f"Querying local Ollama ({self.model}) for chat response...")
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status != 200:
                        return f"Ollama Error: Status {response.status}"
                    
                    result = await response.json()
                    return result.get("response", "No response from local brain.")
        except Exception as e:
            logger.error(f"Ollama chat query failed: {e}")
            return f"Error communicating with local brain: {str(e)}"
