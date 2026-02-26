import anthropic
import json
import logging
from typing import Dict, Any
from bot.config import Config
from bot.llm.prompt_templates import PromptTemplates
from bot.llm.decision_parser import DecisionParser, TradeDecision

logger = logging.getLogger(__name__)

class ClaudeBrain:
    """Core decision engine communicating asynchronously with Anthropic API."""

    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.LLM_MODEL
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.temperature = Config.LLM_TEMPERATURE

    async def analyze_market(self, context: Dict[str, Any]) -> TradeDecision:
        """Sends full JSON context to Claude and safely parses the response."""
        system_prompt = PromptTemplates.SYSTEM_PROMPT
        user_message = json.dumps(context, indent=2)

        try:
            logger.info(f"Querying {self.model} for market decision...")
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Access the text response from Claude
            raw_text = response.content[0].text
            decision = DecisionParser.parse(raw_text)
            
            logger.info(f"Claude returned decision: Action={decision.action}, Amount=${decision.amount_usd}")
            return decision

        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            return DecisionParser.fallback(raw="", reason=f"API Error: {str(e)}")
