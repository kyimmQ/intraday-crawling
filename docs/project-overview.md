# Project Overview

## 1. Project Summary
- **Project Name**: Intraday Alpha Space
- **Type**: Trading Bot / Data Ingestion System
- **Core Functionality**: Real-time market data ingestion from SSI (via SignalR) to Redis, processed and stored as Feather files.
- **Current State**: Database building phase (Ingestion pipeline verified).

## 2. Technology Stack
- **Language**: Python (3.12+), Go (1.21+)
- **Data Ingestion**: Go (Producer), Python (Consumer)
- **Message Queue**: Redis Streams
- **Storage**: Feather (Apache Arrow) for tick data; Target: Database (PostgreSQL/TimescaleDB)
- **Data Analysis**: Pandas, PyArrow
- **Infrastructure**: Docker (optional)

## 3. System Architecture
- **Fetcher (Go)**: Connects to SSI SignalR hub, subscribes to stock symbols, pushes raw JSON to Redis.
- **Processor (Python)**: Consumes Redis stream, parses JSON, converts to `TickData` dataclass.
- **Storage**: Writes batches to Feather files (`data/pubsub/{symbol}/{date}.fea`).
- **Combiner**: Merges morning/afternoon session files into daily files.

## 4. Roadmap
- **Phase 1**: Data Ingestion (Completed)
- **Phase 2**: Database Integration (In Progress - verifying data integrity)
- **Phase 3**: Strategy Research (Not started - `research/notebooks`)
- **Phase 4**: Bot Implementation (Not started - `src/bot`)
