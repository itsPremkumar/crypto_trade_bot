from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String(10)) # BUY, SELL
    token_in = Column(String(50))
    token_out = Column(String(50))
    amount_usd = Column(Float)
    price = Column(Float)
    chain = Column(String(20))
    tx_hash = Column(String(100))
    status = Column(String(20)) # open, closed, failed
    pnl_usd = Column(Float, default=0.0)
    pnl_pct = Column(Float, default=0.0)
    gas_cost_usd = Column(Float, default=0.0)
    closed_at = Column(DateTime, nullable=True)

class LLMDecision(Base):
    __tablename__ = 'llm_decisions'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_context_json = Column(String)
    raw_response_json = Column(String)
    action = Column(String(10)) # BUY, SELL, HOLD
    confidence = Column(Float)
    reason = Column(String)
    was_overridden = Column(Boolean, default=False)
    override_reason = Column(String, nullable=True)
    was_executed = Column(Boolean, default=False)
    outcome = Column(String, nullable=True)

class BotState(Base):
    __tablename__ = 'bot_state'
    id = Column(Integer, primary_key=True)
    mode = Column(String(20), default="manual") # auto, manual, paused
    admin_chat_id = Column(String(50), nullable=True) # Authorized user
    pairing_code = Column(String(10), nullable=True) # Code for pairing
    is_paired = Column(Boolean, default=False)
    circuit_breaker_active = Column(Boolean, default=False)
    consecutive_losses = Column(Integer, default=0)
    daily_pnl_usd = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PortfolioSnapshot(Base):
    __tablename__ = 'portfolio_snapshots'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_usd = Column(Float)
    available_usd = Column(Float)
    positions_json = Column(String) # Serialized JSON array of open positions
