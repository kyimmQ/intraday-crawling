# Code Standards

## 1. Project Structure
```
src/
├── bot/               # Trading bot logic
│   ├── executor/      # Order execution
│   ├── risk/          # Risk management
│   └── strategies/    # Trading strategies
├── core/              # Shared core models
│   └── dataclass.py   # TickData definition
├── ingestion/         # Data pipeline
│   ├── fetcher/       # Go fetcher
│   ├── processor/     # (Future) Processing logic
│   ├── storage/       # Storage utilities (combine.py)
│   └── consumer.py    # Main consumer script
└── utils/             # Shared utilities
```

## 2. Python Standards
- **Type Hints**: Use Python 3.10+ type hints (`list[str]`, `dict[str, int]`).
- **Async**: Use `asyncio` for I/O-bound tasks (consumer).
- **Data Classes**: Use `@dataclass` for structured data (TickData).
- **Dependencies**: Pin versions in `requirements.txt`.

## 3. Go Standards
- **Modules**: Use `go.mod`.
- **Error Handling**: Explicit error handling (no exceptions).
- **Environment**: Use `os.Getenv` with defaults for config.

## 4. Naming Conventions
- **Files**: snake_case (`my_script.py`, `my_module.go`)
- **Classes**: PascalCase (`TickData`, `RedisClient`)
- **Functions**: snake_case (`combine_files`, `run_consumer`)

## 5. Git
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`).
- **Branches**: `feature/description`, `fix/description`.
