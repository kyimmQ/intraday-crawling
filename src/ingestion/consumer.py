#!/usr/bin/env python
# coding: utf-8

# # Consumer: Redis Stream to Disk

# In[1]:


# Imports
import asyncio
import json
import os
from datetime import datetime
import redis.asyncio as redis


# ## Configuration

# In[2]:


# Config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
GROUP_NAME = "ingestion_group"
CONSUMER_NAME = "consumer_1"
BASE_DATA_DIR = "./data/pubsub"  # Pub/Sub crawl path

BATCH_SIZE = 500
BATCH_TIMEOUT = 2  # seconds


# ## Writer Logic

# In[3]:


import pyarrow.feather as feather
import pandas as pd
from core.dataclass import TickData, SnapshotData
from typing import Union

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_batch(symbol: str, date_str: str, messages: list[Union[TickData, SnapshotData]], data_dir: str):
    if not messages:
        return

    dir_path = os.path.join(data_dir, symbol)
    ensure_dir(dir_path)

    file_path = os.path.join(dir_path, f"{date_str}.fea")

    df_new = pd.DataFrame([msg.to_dict() for msg in messages])

    # Append mode: read existing, concat, write
    if os.path.exists(file_path):
        df_existing = pd.read_feather(file_path)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = df_new

    # Save to feather
    feather.write_feather(df, file_path)


# In[ ]:


from datetime import datetime

def read_message(msg: str) -> TickData:
    """
    Parses JSON message from the Go producer (XTradeData).
    """
    try:
        data = json.loads(msg)
    except json.JSONDecodeError:
        return TickData()

    def to_float(val) -> float:
        try:
            return float(val) if val is not None else 0.0
        except:
            return 0.0

    def to_int(val) -> int:
        try:
            return int(float(val)) if val is not None else 0
        except:
            return 0

    try:
        # Basic Info
        symbol = data.get("Symbol", "")

        # Extract timestamp (TradingDate: "DD/MM/YYYY", Time: "HH:MM:SS")
        trading_date_str = data.get("TradingDate", "")
        time_str = data.get("Time", "")

        try:
            if trading_date_str and time_str:
                dt = datetime.strptime(f"{trading_date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
                tm = dt.isoformat()
            else:
                tm = datetime.now().isoformat()
        except:
            tm = datetime.now().isoformat()

        # Match Data & Stats
        match_price = to_float(data.get("LastPrice"))
        match_volume = to_int(data.get("LastVol"))
        total_volume = to_int(data.get("TotalVol"))
        total_value = to_float(data.get("TotalVal"))
        high_price = to_float(data.get("Highest"))
        low_price = to_float(data.get("Lowest"))
        price_change = to_float(data.get("Change"))
        price_change_percent = to_float(data.get("RatioChange"))

        # Limits & Reference
        ceiling_price = to_float(data.get("Ceiling"))
        floor_price = to_float(data.get("Floor"))
        reference_price = to_float(data.get("RefPrice"))

        # Market State
        trading_status = str(data.get("TradingStatus", ""))
        side = str(data.get("Side", ""))

        # Construct and return the dictionary
        return TickData(
            timestamp=tm,
            symbol=symbol,
            match_price=match_price,
            match_volume=match_volume,
            total_volume=total_volume,
            total_value=total_value,
            high_price=high_price,
            low_price=low_price,
            price_change=price_change,
            price_change_percent=price_change_percent,
            ceiling_price=ceiling_price,
            floor_price=floor_price,
            reference_price=reference_price,
            trading_status=trading_status,
            side=side
        )

    except Exception as e:
        import logging
        logging.error(f"Error parsing XTrade message: {e}")
        return TickData()


def read_snapshot_message(msg: str) -> SnapshotData:
    """
    Parses JSON message from the Go producer (XSnapshotData).
    """
    try:
        data = json.loads(msg)
    except json.JSONDecodeError:
        return SnapshotData()

    def to_float(val) -> float:
        try:
            return float(val) if val is not None else 0.0
        except:
            return 0.0

    try:
        symbol = data.get("Symbol", "")
        trading_date_str = data.get("TradingDate", "")
        time_str = data.get("Time", "")

        try:
            if trading_date_str and time_str:
                dt = datetime.strptime(f"{trading_date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
                tm = dt.isoformat()
            else:
                tm = datetime.now().isoformat()
        except:
            tm = datetime.now().isoformat()

        return SnapshotData(
            timestamp=tm,
            symbol=symbol,
            isin=str(data.get("Isin", "")),
            ceiling=to_float(data.get("Ceiling")),
            floor=to_float(data.get("Floor")),
            ref_price=to_float(data.get("RefPrice")),
            open=to_float(data.get("Open")),
            close=to_float(data.get("Close")),
            high=to_float(data.get("High")),
            low=to_float(data.get("Low")),
            avg_price=to_float(data.get("AvgPrice")),
            prior_val=to_float(data.get("PriorVal")),
            last_price=to_float(data.get("LastPrice")),
            change=to_float(data.get("Change")),
            ratio_change=to_float(data.get("RatioChange")),
            est_matched_price=to_float(data.get("EstMatchedPrice")),
            last_vol=to_float(data.get("LastVol")),
            total_val=to_float(data.get("TotalVal")),
            total_vol=to_float(data.get("TotalVol")),
            bid_price_1=to_float(data.get("BidPrice1")),
            bid_vol_1=to_float(data.get("BidVol1")),
            bid_price_2=to_float(data.get("BidPrice2")),
            bid_vol_2=to_float(data.get("BidVol2")),
            bid_price_3=to_float(data.get("BidPrice3")),
            bid_vol_3=to_float(data.get("BidVol3")),
            bid_price_4=to_float(data.get("BidPrice4")),
            bid_vol_4=to_float(data.get("BidVol4")),
            bid_price_5=to_float(data.get("BidPrice5")),
            bid_vol_5=to_float(data.get("BidVol5")),
            bid_price_6=to_float(data.get("BidPrice6")),
            bid_vol_6=to_float(data.get("BidVol6")),
            bid_price_7=to_float(data.get("BidPrice7")),
            bid_vol_7=to_float(data.get("BidVol7")),
            bid_price_8=to_float(data.get("BidPrice8")),
            bid_vol_8=to_float(data.get("BidVol8")),
            bid_price_9=to_float(data.get("BidPrice9")),
            bid_vol_9=to_float(data.get("BidVol9")),
            bid_price_10=to_float(data.get("BidPrice10")),
            bid_vol_10=to_float(data.get("BidVol10")),
            ask_price_1=to_float(data.get("AskPrice1")),
            ask_vol_1=to_float(data.get("AskVol1")),
            ask_price_2=to_float(data.get("AskPrice2")),
            ask_vol_2=to_float(data.get("AskVol2")),
            ask_price_3=to_float(data.get("AskPrice3")),
            ask_vol_3=to_float(data.get("AskVol3")),
            ask_price_4=to_float(data.get("AskPrice4")),
            ask_vol_4=to_float(data.get("AskVol4")),
            ask_price_5=to_float(data.get("AskPrice5")),
            ask_vol_5=to_float(data.get("AskVol5")),
            ask_price_6=to_float(data.get("AskPrice6")),
            ask_vol_6=to_float(data.get("AskVol6")),
            ask_price_7=to_float(data.get("AskPrice7")),
            ask_vol_7=to_float(data.get("AskVol7")),
            ask_price_8=to_float(data.get("AskPrice8")),
            ask_vol_8=to_float(data.get("AskVol8")),
            ask_price_9=to_float(data.get("AskPrice9")),
            ask_vol_9=to_float(data.get("AskVol9")),
            ask_price_10=to_float(data.get("AskPrice10")),
            ask_vol_10=to_float(data.get("AskVol10")),
            market_id=str(data.get("MarketId", "")),
            exchange=str(data.get("Exchange", "")),
            trading_session=str(data.get("TradingSession", "")),
            trading_status=str(data.get("TradingStatus", ""))
        )
    except Exception as e:
        import logging
        logging.error(f"Error parsing XSnapshot message: {e}")
        return SnapshotData()


# In[5]:


async def run_consumer(datatype: str = "XTrade"):
    r = redis.from_url(REDIS_URL)

    stream_key = f"market:ticks:{datatype.lower()}"
    data_dir = os.path.join(BASE_DATA_DIR, datatype.lower())
    group_name = f"{GROUP_NAME}_{datatype.lower()}"

    # Create consumer group if not exists
    try:
        await r.xgroup_create(stream_key, group_name, id="0", mkstream=True)
        print(f"Created group {group_name} for {stream_key}")
    except Exception as e:
        if "BUSYGROUP" in str(e):
            print(f"Group {group_name} already exists")
        else:
            print(f"Error creating group: {e}")

    print(f"Consumer started for {datatype} on stream {stream_key}...")

    while True:
        try:
            # Read messages
            messages = await r.xreadgroup(
                group_name,
                CONSUMER_NAME,
                {stream_key: ">"},
                count=BATCH_SIZE,
                block=BATCH_TIMEOUT * 1000
            )

            if not messages:
                continue

            # Process messages
            stream_data = messages[0][1]  # List of (id, dict)

            # Group by symbol and date
            batches = {}

            for msg_id, fields in stream_data:
                # Get raw message - handle potential missing key
                raw_msg_bytes = fields.get(b'data')
                if not raw_msg_bytes:
                    print(f"Skipping message {msg_id} - no data field")
                    continue

                raw_msg = str(raw_msg_bytes.decode('utf-8'))

                # Parse message based on datatype
                if datatype == "XTrade":
                    data = read_message(raw_msg)
                else:
                    data = read_snapshot_message(raw_msg)

                if data is None or data.symbol == "":
                    continue

                symbol = data.symbol
                timestamp = data.timestamp

                # Determine date string
                try:
                    dt = datetime.fromisoformat(timestamp)
                    date_str = dt.strftime("%Y-%m-%d")
                except:
                    date_str = datetime.now().strftime("%Y-%m-%d")

                key = (symbol, date_str)
                if key not in batches:
                    batches[key] = []

                # Add ID for tracking
                data.msg_id = str(msg_id)
                batches[key].append(data)

            # Write to disk
            for (symbol, date_str), msgs in batches.items():
                write_batch(symbol, date_str, msgs, data_dir)
                print(f"Wrote {len(msgs)} messages for {symbol} on {date_str}")

            # Acknowledge
            msg_ids = [msg_id for msg_id, _ in stream_data]
            if msg_ids:
                await r.xack(stream_key, group_name, *msg_ids)

        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)

    await r.close()


# In[6]:


# Duplicate cell removed - logic is in cell-7


# In[7]:


# Run the consumer
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Consumer for market data.")
    parser.add_argument("--datatype", type=str, default="XTrade", choices=["XTrade", "XSnapshot"], help="Datatype to consume")
    args = parser.parse_args()

    asyncio.run(run_consumer(args.datatype))
