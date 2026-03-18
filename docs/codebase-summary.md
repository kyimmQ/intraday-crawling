# Codebase Summary

## 1. Source Code (`src/`)
- **core/dataclass.py**: Defines the `TickData` dataclass.
- **ingestion/consumer.py**: Async Python consumer for Redis streams.
- **ingestion/fetcher/producer.go**: Go producer for SSI SignalR.
- **ingestion/storage/combine.py**: Script to merge morning/afternoon tick data.
- **run.py**: CLI entry point for running consumer and combiner.

## 2. Data (`data/`)
- **pubsub/**: Raw tick data in Feather format.
- **combined/**: Merged daily data.
- *(Note: `data/` is typically git-ignored).*

## 3. Research (`research/`)
- **notebooks/**: Jupyter notebooks for data analysis and strategy prototyping.

## 4. Configuration
- **requirements.txt**: Python dependencies.
- **src/ingestion/fetcher/.env**: Credentials for SSI (git-ignored).
