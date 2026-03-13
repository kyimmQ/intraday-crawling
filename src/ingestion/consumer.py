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

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_batch(symbol, date_str, messages):
    if not messages:
        return

    dir_path = os.path.join(DATA_DIR, symbol)
    ensure_dir(dir_path)

    file_path = os.path.join(dir_path, f"{date_str}.fea")

    df_new = pd.DataFrame(messages)

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

def read_message(msg):
    """
    Optimized parser for pipe-delimited message from SSI.
    Uses descriptive field names for downstream processing.
    """
    L = msg.split('|')

    # Ensure the message is long enough to contain our target data
    if len(L) < 100:
        return None

    # Fast casting helpers
    def to_float(val):
        return float(val) if val else 0.0

    def to_int(val):
        return int(val) if val else 0

    try:
        # 1. Basic Info
        raw_symbol = L[1]
        symbol = raw_symbol[2:] if raw_symbol.startswith("S#") else raw_symbol

        # 2. Extract Server Timestamp (Index 99 is epoch in ms)
        try:
            tm = datetime.fromtimestamp(int(L[99]) / 1000.0)
        except:
            tm = datetime.now()

        # 3. Match Data & Stats
        match_price = to_float(L[42]) / 1000
        match_volume = to_int(L[43])
        high_price = to_float(L[44]) / 1000
        low_price = to_float(L[46]) / 1000
        price_change = to_float(L[52]) / 1000
        price_change_percent = to_float(L[53])
        total_volume = to_int(L[54])

        # 4. Limits & Reference
        ceiling_price = to_float(L[59]) / 1000
        floor_price = to_float(L[60]) / 1000
        reference_price = to_float(L[61]) / 1000

        # 5. Order Book Top 3 (Bid: 2-7, Ask: 22-27)
        bid_price_1 = to_float(L[2]) / 1000
        bid_volume_1 = to_int(L[3])
        bid_price_2 = to_float(L[4]) / 1000
        bid_volume_2 = to_int(L[5])
        bid_price_3 = to_float(L[6]) / 1000
        bid_volume_3 = to_int(L[7])

        ask_price_1 = to_float(L[22]) / 1000
        ask_volume_1 = to_int(L[23])
        ask_price_2 = to_float(L[24]) / 1000
        ask_volume_2 = to_int(L[25])
        ask_price_3 = to_float(L[26]) / 1000
        ask_volume_3 = to_int(L[27])

        # 6. Foreigner flow
        foreign_buy_volume = to_int(L[48])
        foreign_sell_volume = to_int(L[50])
        foreign_room = to_int(L[65]) if len(L) > 65 else 0

        # Construct and return the dictionary
        return {
            'timestamp': tm.isoformat(),
            'symbol': symbol,

            # Match & Market Stats
            'match_price': match_price,
            'match_volume': match_volume,
            'total_volume': total_volume,
            'high_price': high_price,
            'low_price': low_price,
            'price_change': price_change,
            'price_change_percent': price_change_percent,

            # Limits
            'ceiling_price': ceiling_price,
            'floor_price': floor_price,
            'reference_price': reference_price,

            # Order Book - Bids
            'bid_price_1': bid_price_1, 'bid_volume_1': bid_volume_1,
            'bid_price_2': bid_price_2, 'bid_volume_2': bid_volume_2,
            'bid_price_3': bid_price_3, 'bid_volume_3': bid_volume_3,

            # Order Book - Asks
            'ask_price_1': ask_price_1, 'ask_volume_1': ask_volume_1,
            'ask_price_2': ask_price_2, 'ask_volume_2': ask_volume_2,
            'ask_price_3': ask_price_3, 'ask_volume_3': ask_volume_3,

            # Foreigner trading
            'foreign_buy_volume': foreign_buy_volume,
            'foreign_sell_volume': foreign_sell_volume,
            'foreign_room': foreign_room
        }

    except Exception as e:
        return None


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
                raw_msg_bytes = fields.get(b'raw')
                if not raw_msg_bytes:
                    print(f"Skipping message {msg_id} - no raw data")
                    continue

                raw_msg = str(raw_msg_bytes.decode('utf-8'))

                # Parse message using read_message
                data = read_message(raw_msg)

                if data is None:
                    continue

                symbol = data.get('symbol')
                timestamp = data.get('timestamp')

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
                data['msg_id'] = str(msg_id)
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
