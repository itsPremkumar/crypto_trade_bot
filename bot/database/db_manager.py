import logging
import json
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from bot.database.models import Base, Trade, LLMDecision, BotState, PortfolioSnapshot, PaperWallet
from bot.config import Config

logger = logging.getLogger(__name__)

class DBManager:
    """Manages SQLite database connections and operations."""

    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._initialize_state()

    def get_session(self) -> Session:
        return self.SessionLocal()

    def _initialize_state(self):
        with self.get_session() as session:
            state = session.query(BotState).first()
            if not state:
                # Get pairing code from environment if provided, else None
                pairing_code = os.getenv("TELEGRAM_PAIRING_CODE")
                state = BotState(
                    mode=Config.BOT_MODE,
                    pairing_code=pairing_code,
                    is_paired=False
                )
                session.add(state)
                session.commit()
                logger.info(f"Initialized BotState in DB. Pairing Code: {pairing_code}")
                
            paper_wallet = session.query(PaperWallet).filter_by(chain='global', token='USD').first()
            if not paper_wallet:
                initial_paper = PaperWallet(
                    chain='global',
                    token='USD',
                    balance=Config.PAPER_START_BALANCE_USD
                )
                session.add(initial_paper)
                session.commit()
                logger.info(f"Initialized PaperWallet starting balance: ${Config.PAPER_START_BALANCE_USD}")

    def get_bot_state(self) -> BotState:
        with self.get_session() as session:
            state = session.query(BotState).first()
            session.expunge(state)
            return state

    def update_bot_state(self, **kwargs):
        with self.get_session() as session:
            state = session.query(BotState).first()
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            session.commit()
            logger.info("Bot state updated in DB.")

    def log_trade(self, trade: Trade):
        with self.get_session() as session:
            session.add(trade)
            session.commit()
            
    def get_recent_trades(self, limit=5):
        with self.get_session() as session:
            trades = session.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()
            for t in trades:
                session.expunge(t)
            return trades

    def log_llm_decision(self, decision: LLMDecision):
        with self.get_session() as session:
            session.add(decision)
            session.commit()

    def save_portfolio_snapshot(self, total_usd: float, available_usd: float, positions: list):
        with self.get_session() as session:
            snap = PortfolioSnapshot(
                total_usd=total_usd,
                available_usd=available_usd,
                positions_json=json.dumps(positions)
            )
            session.add(snap)
            session.commit()

    def get_paper_balance(self, chain: str, token: str) -> float:
        with self.get_session() as session:
            wallet = session.query(PaperWallet).filter_by(chain=chain, token=token).first()
            if wallet:
                return wallet.balance
            return 0.0

    def update_paper_balance(self, chain: str, token: str, amount: float):
        # amount can be positive or negative
        with self.get_session() as session:
            wallet = session.query(PaperWallet).filter_by(chain=chain, token=token).first()
            if not wallet:
                wallet = PaperWallet(chain=chain, token=token, balance=0.0)
                session.add(wallet)
            
            wallet.balance += amount
            session.commit()
