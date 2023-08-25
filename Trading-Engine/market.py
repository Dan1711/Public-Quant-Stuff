from enum import Enum

class BidOrAsk(Enum):
    Bid = 1
    Ask = 2

class TradingPair:
    tickers = ["BTC/USD", "ETH/USD", "XRP/USD", "SOL/USD", "DOGE/USD"]
    def __init__(self, base, quote):
        self.base = base
        self.quote = quote
    
    def market(self):
        return f"{self.base}/{self.quote}"
