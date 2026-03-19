#!/usr/bin/env python3
# Run ingestion workflows
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_consumer(datatype="XTrade"):
    print(f"Starting Redis consumer for datatype {datatype}...")
    from ingestion.consumer import run_consumer as c
    import asyncio
    asyncio.run(c(datatype))

def run_combiner():
    print("Combining morning/afternoon data...")
    from ingestion.storage.combine import combine_files
    combine_files()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run ingestion workflows.")
    parser.add_argument("mode", choices=["consumer", "combiner"], help="Mode to run")
    parser.add_argument("--datatype", type=str, default="XTrade", choices=["XTrade", "XSnapshot"], help="Datatype to consume (for consumer mode)")

    args = parser.parse_args()

    if args.mode == "consumer":
        run_consumer(args.datatype)
    elif args.mode == "combiner":
        run_combiner()
