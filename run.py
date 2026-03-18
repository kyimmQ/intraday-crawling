#!/usr/bin/env python3
# Run ingestion workflows
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_consumer():
    print("Starting Redis consumer...")
    from ingestion.consumer import run_consumer as c
    import asyncio
    asyncio.run(c())

def run_combiner():
    print("Combining morning/afternoon data...")
    from ingestion.storage.combine import combine_files
    combine_files()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py [consumer|combiner]")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "consumer":
        run_consumer()
    elif mode == "combiner":
        run_combiner()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
