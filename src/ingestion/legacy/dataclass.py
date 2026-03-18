from dataclasses import dataclass
from datetime import datetime

@dataclass
class TickData:
    timestamp: str = datetime.fromtimestamp(0).isoformat()
    symbol: str = ""
    match_price: float = 0.0
    match_volume: int = 0
    total_volume: int = 0
    high_price: float = 0.0
    low_price: float = 0.0
    price_change: float = 0.0
    price_change_percent: float = 0.0

    # Limits
    ceiling_price: float = 0.0
    floor_price: float = 0.0
    reference_price: float = 0.0

    # Order Book - Bids
    bid_price_1: float = 0.0
    bid_volume_1: int = 0
    bid_price_2: float = 0.0
    bid_volume_2: int = 0
    bid_price_3: float = 0.0
    bid_volume_3: int = 0

    # Order Book - Asks
    ask_price_1: float = 0.0
    ask_volume_1: int = 0
    ask_price_2: float = 0.0
    ask_volume_2: int = 0
    ask_price_3: float = 0.0
    ask_volume_3: int = 0

    # Foreigner trading
    foreign_buy_volume: int = 0
    foreign_sell_volume: int = 0
    foreign_room: int = 0

    # Tracking
    msg_id: str = ""

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "match_price": self.match_price,
            "match_volume": self.match_volume,
            "total_volume": self.total_volume,
            "high_price": self.high_price,
            "low_price": self.low_price,
            "price_change": self.price_change,
            "price_change_percent": self.price_change_percent,
            "ceiling_price": self.ceiling_price,
            "floor_price": self.floor_price,
            "reference_price": self.reference_price,
            "bid_price_1": self.bid_price_1,
            "bid_volume_1": self.bid_volume_1,
            "bid_price_2": self.bid_price_2,
            "bid_volume_2": self.bid_volume_2,
            "bid_price_3": self.bid_price_3,
            "bid_volume_3": self.bid_volume_3,
            "ask_price_1": self.ask_price_1,
            "ask_volume_1": self.ask_volume_1,
            "ask_price_2": self.ask_price_2,
            "ask_volume_2": self.ask_volume_2,
            "ask_price_3": self.ask_price_3,
            "ask_volume_3": self.ask_volume_3,
            "foreign_buy_volume": self.foreign_buy_volume,
            "foreign_sell_volume": self.foreign_sell_volume,
            "foreign_room": self.foreign_room,
            "msg_id": self.msg_id
        }
