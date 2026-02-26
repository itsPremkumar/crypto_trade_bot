import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Wallet Security
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "")
    KEYSTORE_PASSWORD: str = os.getenv("KEYSTORE_PASSWORD", "")

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "claude") # claude, ollama
    
    # Anthropic LLM
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022") 
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "500"))

    # Ollama (Local LLM)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # RPC URLs
    POLYGON_RPC_URL: str = os.getenv("POLYGON_RPC_URL", "")
    BSC_RPC_URL: str = os.getenv("BSC_RPC_URL", "")
    BASE_RPC_URL: str = os.getenv("BASE_RPC_URL", "")

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "") # Optional if using pairing
    TELEGRAM_PAIRING_CODE: str = os.getenv("TELEGRAM_PAIRING_CODE", "123")
    BOT_MODE: str = os.getenv("BOT_MODE", "manual") # auto, manual, paused

    # Risk Parameters
    MIN_BALANCE_USD: float = float(os.getenv("MIN_BALANCE_USD", "7.00"))
    MIN_TRADE_USD: float = float(os.getenv("MIN_TRADE_USD", "1.00"))
    MAX_DAILY_LOSS_PERCENT: float = float(os.getenv("MAX_DAILY_LOSS_PERCENT", "5.0"))
    MAX_TRADE_PERCENT: float = float(os.getenv("MAX_TRADE_PERCENT", "20.0"))
    SLIPPAGE_TOLERANCE: float = float(os.getenv("SLIPPAGE_TOLERANCE", "0.015"))
    MAX_GAS_USD: float = float(os.getenv("MAX_GAS_USD", "0.30"))
    CIRCUIT_BREAKER_LOSSES: int = int(os.getenv("CIRCUIT_BREAKER_LOSSES", "3"))
    CIRCUIT_BREAKER_PAUSE_MINUTES: int = int(os.getenv("CIRCUIT_BREAKER_PAUSE_MINUTES", "60"))

    # Active chains
    ACTIVE_CHAINS: List[str] = [c.strip().lower() for c in os.getenv("ACTIVE_CHAINS", "polygon,bsc,base").split(",") if c.strip()]

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///trades.db")

    @classmethod
    def validate(cls):
        """Validate critical configuration fields."""
        missing = []
        if not cls.PRIVATE_KEY:
            missing.append("PRIVATE_KEY")
        
        if cls.LLM_PROVIDER == "claude" and not cls.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY (required for Claude)")
        elif cls.LLM_PROVIDER == "ollama" and not cls.OLLAMA_MODEL:
            missing.append("OLLAMA_MODEL (required for Ollama)")
            
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
        
        if missing:
            raise ValueError(f"Missing critical configuration variables: {', '.join(missing)}")
