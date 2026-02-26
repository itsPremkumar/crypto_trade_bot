import pandas as pd
import ta
import logging
from bot.data.price_feed import PriceFeed
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """
    Analyzes raw OHLCV price feed data and generates technical indicators
    using pandas and the 'ta' library.
    """

    def __init__(self, price_feed: PriceFeed):
        self.price_feed = price_feed
        self.target_pairs = ["MATIC/USDC", "BNB/USDC", "ETH/USDC"]

    async def analyze_all_markets(self) -> Dict[str, Dict[str, Any]]:
        """
        Fetches klines and 24h stats for all target pairs, computes indicators, 
        and returns a unified dictionary for the LLM Context.
        """
        market_data = {}
        for pair in self.target_pairs:
            try:
                klines = await self.price_feed.fetch_klines(pair, interval="15m", limit=50)
                stats = await self.price_feed.fetch_current_price_24h_stats(pair)
                
                if not klines or not stats:
                    logger.warning(f"Incomplete data for {pair}, skipping analysis.")
                    continue
                
                df = pd.DataFrame(klines)
                
                # Compute Indicators
                rsi = ta.momentum.RSIIndicator(close=df['close'], window=14)
                df['rsi_14'] = rsi.rsi()
                
                ema_9 = ta.trend.EMAIndicator(close=df['close'], window=9)
                df['ema_9'] = ema_9.ema_indicator()
                
                ema_21 = ta.trend.EMAIndicator(close=df['close'], window=21)
                df['ema_21'] = ema_21.ema_indicator()
                
                bb = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
                df['bb_upper'] = bb.bollinger_hband()
                df['bb_lower'] = bb.bollinger_lband()
                df['bb_mid'] = bb.bollinger_mavg()
                
                # 1h change estimate (using 4th candle back for 15m intervals)
                current_price = df['close'].iloc[-1]
                price_1h_ago = df['close'].iloc[-5] if len(df) >= 5 else df['close'].iloc[0]
                change_1h_pct = ((current_price - price_1h_ago) / price_1h_ago) * 100
                
                # Latest row
                latest = df.iloc[-1]
                
                market_data[pair] = {
                    "price": stats.get('price', current_price),
                    "change_1h_pct": round(change_1h_pct, 2),
                    "change_24h_pct": round(stats.get('change_24h_pct', 0.0), 2),
                    "volume_24h_usd": round(stats.get('volume_24h_usd', 0.0), 2),
                    "rsi_14": round(latest['rsi_14'], 2) if not pd.isna(latest['rsi_14']) else 50.0,
                    "ema_9": round(latest['ema_9'], 4) if not pd.isna(latest['ema_9']) else current_price,
                    "ema_21": round(latest['ema_21'], 4) if not pd.isna(latest['ema_21']) else current_price,
                    "bb_upper": round(latest['bb_upper'], 4) if not pd.isna(latest['bb_upper']) else current_price,
                    "bb_lower": round(latest['bb_lower'], 4) if not pd.isna(latest['bb_lower']) else current_price,
                    "bb_mid": round(latest['bb_mid'], 4) if not pd.isna(latest['bb_mid']) else current_price,
                }
            except Exception as e:
                logger.error(f"Error analyzing market for {pair}: {e}")
                
        return market_data
