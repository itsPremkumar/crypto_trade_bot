import aiohttp
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PriceFeed:
    """
    Fetches market prices and OHLCV k-lines for technical indicator calculation.
    Uses public Binance REST API for reliable, free data. 
    (Execution is purely on-chain, but historical data requires an indexer/CEX API).
    """

    BINANCE_API_URL = "https://api.binance.com/api/v3"

    def __init__(self):
        self.session = None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def fetch_klines(self, symbol: str, interval: str = "15m", limit: int = 50) -> list:
        """Fetch historical k-lines (OHLCV) for indicator calculation."""
        # Binance symbol format: MATICUSDT, BNBUSDT, ETHUSDT
        b_symbol = symbol.replace("/", "").replace("USDC", "USDT")
        url = f"{self.BINANCE_API_URL}/klines?symbol={b_symbol}&interval={interval}&limit={limit}"
        
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Format: [Open time, Open, High, Low, Close, Volume, ...]
                    return [
                        {
                            "timestamp": int(candle[0]),
                            "open": float(candle[1]),
                            "high": float(candle[2]),
                            "low": float(candle[3]),
                            "close": float(candle[4]),
                            "volume": float(candle[5])
                        }
                        for candle in data
                    ]
                else:
                    logger.error(f"Failed to fetch klines for {symbol}: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            return []

    async def fetch_current_price_24h_stats(self, symbol: str) -> Dict[str, Any]:
        """Fetch current price and 24h change."""
        b_symbol = symbol.replace("/", "").replace("USDC", "USDT")
        url = f"{self.BINANCE_API_URL}/ticker/24hr?symbol={b_symbol}"
        
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "price": float(data['lastPrice']),
                        "change_24h_pct": float(data['priceChangePercent']),
                        "volume_24h_usd": float(data['quoteVolume'])
                    }
                return {}
        except Exception as e:
            logger.error(f"Error fetching 24h stats for {symbol}: {e}")
            return {}

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
