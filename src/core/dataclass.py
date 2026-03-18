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

@dataclass
class SnapshotData:
    timestamp: str = datetime.fromtimestamp(0).isoformat()
    symbol: str = ""
    isin: str = ""

    # Prices
    ceiling: float = 0.0
    floor: float = 0.0
    ref_price: float = 0.0
    open: float = 0.0
    close: float = 0.0
    high: float = 0.0
    low: float = 0.0
    avg_price: float = 0.0
    prior_val: float = 0.0
    last_price: float = 0.0
    change: float = 0.0
    ratio_change: float = 0.0
    est_matched_price: float = 0.0

    # Volume & Value
    last_vol: float = 0.0
    total_val: float = 0.0
    total_vol: float = 0.0

    # Market Depth (Bids)
    bid_price_1: float = 0.0
    bid_vol_1: float = 0.0
    bid_price_2: float = 0.0
    bid_vol_2: float = 0.0
    bid_price_3: float = 0.0
    bid_vol_3: float = 0.0
    bid_price_4: float = 0.0
    bid_vol_4: float = 0.0
    bid_price_5: float = 0.0
    bid_vol_5: float = 0.0
    bid_price_6: float = 0.0
    bid_vol_6: float = 0.0
    bid_price_7: float = 0.0
    bid_vol_7: float = 0.0
    bid_price_8: float = 0.0
    bid_vol_8: float = 0.0
    bid_price_9: float = 0.0
    bid_vol_9: float = 0.0
    bid_price_10: float = 0.0
    bid_vol_10: float = 0.0

    # Market Depth (Asks)
    ask_price_1: float = 0.0
    ask_vol_1: float = 0.0
    ask_price_2: float = 0.0
    ask_vol_2: float = 0.0
    ask_price_3: float = 0.0
    ask_vol_3: float = 0.0
    ask_price_4: float = 0.0
    ask_vol_4: float = 0.0
    ask_price_5: float = 0.0
    ask_vol_5: float = 0.0
    ask_price_6: float = 0.0
    ask_vol_6: float = 0.0
    ask_price_7: float = 0.0
    ask_vol_7: float = 0.0
    ask_price_8: float = 0.0
    ask_vol_8: float = 0.0
    ask_price_9: float = 0.0
    ask_vol_9: float = 0.0
    ask_price_10: float = 0.0
    ask_vol_10: float = 0.0

    # Market Status
    market_id: str = ""
    exchange: str = ""
    trading_session: str = ""
    trading_status: str = ""

    # Tracking
    msg_id: str = ""

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "isin": self.isin,
            "ceiling": self.ceiling,
            "floor": self.floor,
            "ref_price": self.ref_price,
            "open": self.open,
            "close": self.close,
            "high": self.high,
            "low": self.low,
            "avg_price": self.avg_price,
            "prior_val": self.prior_val,
            "last_price": self.last_price,
            "change": self.change,
            "ratio_change": self.ratio_change,
            "est_matched_price": self.est_matched_price,
            "last_vol": self.last_vol,
            "total_val": self.total_val,
            "total_vol": self.total_vol,
            "bid_price_1": self.bid_price_1,
            "bid_vol_1": self.bid_vol_1,
            "bid_price_2": self.bid_price_2,
            "bid_vol_2": self.bid_vol_2,
            "bid_price_3": self.bid_price_3,
            "bid_vol_3": self.bid_vol_3,
            "bid_price_4": self.bid_price_4,
            "bid_vol_4": self.bid_vol_4,
            "bid_price_5": self.bid_price_5,
            "bid_vol_5": self.bid_vol_5,
            "bid_price_6": self.bid_price_6,
            "bid_vol_6": self.bid_vol_6,
            "bid_price_7": self.bid_price_7,
            "bid_vol_7": self.bid_vol_7,
            "bid_price_8": self.bid_price_8,
            "bid_vol_8": self.bid_vol_8,
            "bid_price_9": self.bid_price_9,
            "bid_vol_9": self.bid_vol_9,
            "bid_price_10": self.bid_price_10,
            "bid_vol_10": self.bid_vol_10,
            "ask_price_1": self.ask_price_1,
            "ask_vol_1": self.ask_vol_1,
            "ask_price_2": self.ask_price_2,
            "ask_vol_2": self.ask_vol_2,
            "ask_price_3": self.ask_price_3,
            "ask_vol_3": self.ask_vol_3,
            "ask_price_4": self.ask_price_4,
            "ask_vol_4": self.ask_vol_4,
            "ask_price_5": self.ask_price_5,
            "ask_vol_5": self.ask_vol_5,
            "ask_price_6": self.ask_price_6,
            "ask_vol_6": self.ask_vol_6,
            "ask_price_7": self.ask_price_7,
            "ask_vol_7": self.ask_vol_7,
            "ask_price_8": self.ask_price_8,
            "ask_vol_8": self.ask_vol_8,
            "ask_price_9": self.ask_price_9,
            "ask_vol_9": self.ask_vol_9,
            "ask_price_10": self.ask_price_10,
            "ask_vol_10": self.ask_vol_10,
            "market_id": self.market_id,
            "exchange": self.exchange,
            "trading_session": self.trading_session,
            "trading_status": self.trading_status,
            "msg_id": self.msg_id
        }
