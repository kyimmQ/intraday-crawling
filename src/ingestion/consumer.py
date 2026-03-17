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
STREAM_KEY = "market:ticks"
GROUP_NAME = "ingestion_group"
CONSUMER_NAME = "consumer_1"
DATA_DIR = "./data/pubsub"  # Pub/Sub crawl path

BATCH_SIZE = 500
BATCH_TIMEOUT = 2  # seconds


# ## Writer Logic

# In[3]:


import pyarrow.feather as feather
import pandas as pd
from dataclass import TickData

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_batch(symbol: str, date_str: str, messages: list[TickData]):
    if not messages:
        return

    dir_path = os.path.join(DATA_DIR, symbol)
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

    # Fast casting helpers
    def to_float(val) -> float:
        try:
            return float(val) if val is not None else 0.0
        except:
            return 0.0

    try:
        # Basic Info
        symbol = data.get("Symbol", "")

        # Extract timestamp (using current time as fallback since format from Time/TradingDate may vary)
        tm = datetime.now().isoformat()

        # Match Data & Stats
        match_price = to_float(data.get("LastPrice"))
        match_volume = to_float(data.get("LastVol"))
        total_volume = to_float(data.get("TotalVol"))
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
        return TickData()


# In[5]:


async def run_consumer():
    r = redis.from_url(REDIS_URL)

    # Create consumer group if not exists
    try:
        await r.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
        print(f"Created group {GROUP_NAME}")
    except Exception as e:
        if "BUSYGROUP" in str(e):
            print(f"Group {GROUP_NAME} already exists")
        else:
            print(f"Error creating group: {e}")

    print("Consumer started...")

    while True:
        try:
            # Read messages
            messages = await r.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                {STREAM_KEY: ">"},
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

                # Parse message using read_message
                data = read_message(raw_msg)

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
                write_batch(symbol, date_str, msgs)
                print(f"Wrote {len(msgs)} messages for {symbol} on {date_str}")

            # Acknowledge
            msg_ids = [msg_id for msg_id, _ in stream_data]
            if msg_ids:
                await r.xack(STREAM_KEY, GROUP_NAME, *msg_ids)

        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(1)

    await r.close()


# In[6]:


# Duplicate cell removed - logic is in cell-7


# In[7]:


# Run the consumer
if __name__ == '__main__':
    asyncio.run(run_consumer())
