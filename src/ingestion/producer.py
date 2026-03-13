#!/usr/bin/env python
# coding: utf-8

# # Producer: WebSocket to Redis Stream

# In[11]:


# Imports
import asyncio
import json
import websockets
import redis.asyncio as redis
from datetime import datetime
import os


# ## Configuration

# In[ ]:


# Config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
STREAM_KEY = "market:ticks"
WS_URL = "wss://iboard-pushstream.ssi.com.vn/realtime"

# Stock list (default or passed)
STOCKS = ["41I1G3000", "41I1G4000"]


# ## Parser Logic

# In[13]:


def parse_message(msg):
    """
    Parse pipe-delimited message.
    Example: MAIN|S#41I1G3000|1767.6|10|...
    """
    try:
        parts = msg.split('|')
        if len(parts) < 10:
            return None

        # Extract fields based on reference
        raw_symbol = parts[1]
        # Remove S# prefix if present
        symbol = raw_symbol[2:] if raw_symbol.startswith("S#") else raw_symbol

        # Placeholder parsing - adjust indices based on actual SSI protocol
        # For now, returning the raw parts and a timestamp
        return {
            "symbol": symbol,
            "raw": msg,
            "timestamp": datetime.now().isoformat(),
            "parsed_at": parts[0]  # Placeholder
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return None


# ## Producer Task

# In[14]:


async def run_producer():
    """Connects to WebSocket and pushes to Redis, retrying on connection errors."""
    r = redis.from_url(REDIS_URL)

    while True:
        try:
            print(f"Connecting to {WS_URL}...")
            async with websockets.connect(WS_URL, ping_interval=60, ping_timeout=None) as ws:
                print("Connected!")

                # Subscribe logic (simplified)
                subscribe_msg = {
                    "type": "sub",
                    "topic": "stockRealtimeByListV2",
                    "component": "priceTableEquities",
                    "variables": STOCKS
                }
                await ws.send(json.dumps(subscribe_msg))
                print(f"Subscribed to {STOCKS}")

                async for message in ws:
                    # Push raw message to Redis for processing by Consumer
                    await r.xadd(STREAM_KEY, {"raw": message})
        except Exception as e:
            print(f"WebSocket error: {e}")
            print("Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

    await r.close()


# In[15]:


# Run the producer
if __name__ == '__main__':
    asyncio.run(run_producer())
