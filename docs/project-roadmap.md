# Project Roadmap

## Completed
- [x] **Ingestion Pipeline**: Go producer -> Redis -> Python Consumer -> Feather Files.
- [x] **Data Structure**: Defined `TickData` model.
- [x] **Data Combination**: Merged morning/afternoon sessions.

## In Progress
- [ ] **Database Verification**: Testing database storage integration.
- [ ] **Data Quality**: Validating tick data integrity.

## Planned
- [ ] **Database Integration**: Replace Feather files with TimescaleDB.
- [ ] **Strategy Research**: Develop and backtest trading strategies in `research/notebooks`.
- [ ] **Bot Implementation**: Build execution engine in `src/bot`.
- [ ] **Paper Trading**: Initial testing with simulation.
- [ ] **Production**: Live trading deployment.

## Future Considerations
- **Infrastructure**: Dockerize services.
- **Monitoring**: Logging and metrics (Prometheus/Grafana).
- **Multi-asset Support**: Extend to derivatives/forex.
