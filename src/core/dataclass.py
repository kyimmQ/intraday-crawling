from dataclasses import dataclass
from datetime import datetime

@dataclass
class TickData:
    timestamp: str = datetime.fromtimestamp(0).isoformat()
    symbol: str = ""
    match_price: float = 0.0
    match_volume: int = 0
    total_volume: int = 0
    total_value: float = 0.0
    high_price: float = 0.0
    low_price: float = 0.0
    price_change: float = 0.0
    price_change_percent: float = 0.0

    # Limits
    ceiling_price: float = 0.0
    floor_price: float = 0.0
    reference_price: float = 0.0

    # Market State
    trading_status: str = ""
    side: str = ""

    # Tracking
    msg_id: str = ""

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "match_price": self.match_price,
            "match_volume": self.match_volume,
            "total_volume": self.total_volume,
            "total_value": self.total_value,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "price_change": self.price_change,
            "price_change_percent": self.price_change_percent,
            "ceiling_price": self.ceiling_price,
            "floor_price": self.floor_price,
            "reference_price": self.reference_price,
            "trading_status": self.trading_status,
            "side": self.side,
            "msg_id": self.msg_id
        }
