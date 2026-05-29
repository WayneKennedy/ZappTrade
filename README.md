# ZappTrade

> ## ⚠️ Legacy prototype — not carried forward
>
> **This repository is an archived prototype, retained only as an _expression of intent_.**
> It will **not** be extended, refactored, or maintained. Do not build new work on top of it.
>
> The real ZappTrade is a **blank-sheet greenfield rewrite**, governed on TarkaFlow as the
> **ZappTrade (ZTR)** project (org `zapp` / Zappfyre). The intent that this codebase expresses
> has been mined and re-captured there as stakeholder **statements** and architectural **decisions**.
>
> **What ZTR is building** (broader than this prototype): an application to **compose Day Trading
> strategies for real listed stocks** and **paper-trade them against historical _daily_ price
> movements**. Daily granularity only — explicitly no minute/tick/high-frequency trading.
>
> **How this prototype maps to captured intent:**
>
> | This prototype expresses… | Captured as |
> |---|---|
> | Curated stock universe + metadata (was FTSE 100 only) | `ZTR-STMT-002` (generalized to multi-market) |
> | Deep daily OHLCV + adjusted-close history since 2000 | `ZTR-STMT-003` |
> | Free/public end-of-day data source (Yahoo via yfinance) | `ZTR-STMT-004` |
> | Scheduled incremental refresh (fetch only missing days) | `ZTR-STMT-005` |
> | Charting web frontend (started, never finished) | `ZTR-STMT-006` |
> | _Not present in this code — forward intent only:_ strategy composition + paper trading | `ZTR-STMT-001` |
> | _Not present in this code — forward intent only:_ multi-market currency/calendar normalization | `ZTR-STMT-007` |
>
> **Greenfield direction** (`ZTR-DECISION-001` / `-002`): Python 3.12 + FastAPI/Pydantic backend;
> declarative JSON strategy spec; custom vectorized daily backtest/paper-trade engine; PostgreSQL +
> TimescaleDB via SQLAlchemy 2.0 + Alembic; React + TypeScript + Vite frontend with TradingView
> Lightweight Charts; hosted on k3s. This **drops** the prototype's PHP/Apache frontend, PostgREST,
> standalone Swagger, and n8n loader.
>
> Everything below documents the **legacy prototype** for reference only.

---

A containerized stock market data pipeline that fetches, stores, and visualizes FTSE 100 stock data.

## Architecture

This project consists of 6 Docker services:

1. **zapp-stock-db** - TimescaleDB database for time-series stock data
2. **zapp-stock-loader** - Python service that fetches FTSE 100 data from Yahoo Finance
3. **n8n** - Workflow automation alternative to Python loader
4. **zapp-stock-rest** - PostgREST API server for database access
5. **zapp-stock-swagger** - Swagger UI for API documentation
6. **zapp-stock-website** - Apache/PHP web frontend for data visualization

## Prerequisites

- Docker (with Docker Compose V2)
- Works on AMD64 (x86_64) and ARM64 architectures

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd ZappTrade
```

2. Start all services:
```bash
docker compose up -d
```

3. Access the services:
   - Web Interface: http://localhost:1337
   - REST API: http://localhost:3000
   - API Documentation: http://localhost:8080
   - n8n Workflow Automation: http://localhost:5678
   - Database: localhost:5432

## Services

### Database (zapp-stock-db)
- **Technology:** TimescaleDB (PostgreSQL 16 with time-series extensions)
- **Port:** 5432
- **Database:** zapp_stock_db
- **Credentials:** docker/docker (⚠️ change for production)

**Schema:**
- `stocks` - Stock metadata (ticker, index, company name)
- `daily` - OHLCV daily price data (hypertable)

### Data Loader (zapp-stock-loader)
- **Technology:** Python 3.12
- **Dependencies:** psycopg2, pytickersymbols, pandas, yfinance
- **Functionality:**
  - Fetches FTSE 100 stock list
  - Downloads daily OHLCV data from Yahoo Finance using yfinance
  - Runs every 10 minutes
  - Performs incremental loads (only fetches missing data)
  - Loads historical data from 2000 onwards

### n8n Workflow Automation (n8n)
- **Technology:** n8n (latest)
- **Port:** 5678
- **Credentials:** admin/admin (⚠️ change for production)
- **Functionality:**
  - Alternative to Python data loader using visual workflows
  - Same data fetching capabilities via HTTP requests to Yahoo Finance
  - Runs on configurable schedule (default: every 10 minutes)
  - Workflow stored as JSON in `/n8n-workflows/`
  - See [n8n Setup Guide](n8n-workflows/SETUP.md) for configuration

### REST API (zapp-stock-rest)
- **Technology:** PostgREST v12.2.3
- **Port:** 3000
- **Base URL:** http://localhost:3000

Example endpoints:
- GET `/stocks` - List all stocks
- GET `/daily` - Query daily price data
- GET `/daily?ticker=eq.AAL.L&order=date.desc&limit=30` - Last 30 days for AAL

### API Documentation (zapp-stock-swagger)
- **Technology:** Swagger UI v5.17.14
- **Port:** 8080
- **URL:** http://localhost:8080

### Web Frontend (zapp-stock-website)
- **Technology:** Apache, PHP 8.3, Bootstrap 4, Chart.js
- **Port:** 1337
- **Status:** ⚠️ Under development

## Data Flow

```
PyTickerSymbols → Data Loader → Yahoo Finance API
                       ↓
                  TimescaleDB
                       ↓
                   PostgREST API
                       ↓
                  Web Interface
```

## Development

### Project Structure
```
ZappTrade/
├── docker-compose.yml
├── zapp-stock-db/
│   ├── Dockerfile
│   └── init.sql
├── zapp-stock-loader/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       └── dataloader.py
└── zapp-stock-web/
    ├── Dockerfile
    └── src/
        ├── index.html
        └── js/
            └── app.js
```

### Viewing Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f zapp-stock-loader
```

### Stopping Services
```bash
docker compose down

# Remove volumes (deletes all data)
docker compose down -v
```

### Rebuilding After Changes
```bash
docker compose up -d --build
```

## Database Access

Connect to PostgreSQL:
```bash
docker compose exec zapp-stock-db psql -U docker -d zapp_stock_db
```

Example queries:
```sql
-- List all stocks
SELECT * FROM stocks;

-- Get recent data for a ticker
SELECT * FROM daily
WHERE ticker = 'AAL.L'
ORDER BY date DESC
LIMIT 10;

-- Get price ranges for all stocks today
SELECT ticker, MIN(low_price), MAX(high_price), close_price
FROM daily
WHERE date = CURRENT_DATE
GROUP BY ticker, close_price;
```

## API Examples

Using curl:
```bash
# Get all stocks
curl http://localhost:3000/stocks

# Get latest daily data
curl "http://localhost:3000/daily?order=date.desc&limit=10"

# Filter by ticker
curl "http://localhost:3000/daily?ticker=eq.AAL.L"

# Get specific date range
curl "http://localhost:3000/daily?date=gte.2024-01-01&date=lte.2024-12-31"
```

## Known Issues

- ⚠️ Hardcoded database credentials (not suitable for production)
- ⚠️ Web frontend incomplete (chart visualization not implemented)
- ⚠️ No authentication on API endpoints
- ⚠️ No health checks or restart policies
- ⚠️ Some delisted stocks may show warnings in loader logs

## Roadmap

- [x] Migrate from deprecated pandas_datareader to yfinance
- [x] Update to latest LTS versions (Python 3.12, PHP 8.3, PostgreSQL 16)
- [x] Multi-architecture support (AMD64 and ARM64)
- [x] Add n8n workflow automation as alternative data loader
- [ ] Implement web frontend chart visualization
- [ ] Add environment variable configuration
- [ ] Implement authentication/authorization
- [ ] Add health checks and restart policies
- [ ] Add unit tests
- [ ] Improve error handling and logging
- [ ] Add data retention policies

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
