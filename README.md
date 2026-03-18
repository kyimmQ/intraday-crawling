# Intraday Alpha Space

A real-time intraday trading bot focusing on data ingestion and alpha research.

## Status
- **Phase**: Database Building / Verification

## Quick Start

### 1. Prerequisites
- Python 3.12+
- Go 1.21+
- Redis

### 2. Setup
```bash
# Install Python deps
pip install -r requirements.txt

# Configure Go deps
cd src/ingestion/fetcher
go mod download
```

### 3. Run
```bash
# Start Redis (docker)
docker run -d -p 6379:6379 redis

# Start Consumer
python run.py consumer

# (Optional) Combine data
python run.py combiner
```

## Documentation
See `docs/` for detailed architecture and roadmap.

## Structure
- `src/ingestion/`: Data pipeline
- `src/bot/`: Trading bot logic (future)
- `research/`: Strategy notebooks
