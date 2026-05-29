# ZappTrade

This repository is an **archived prototype, intentionally reduced to this README**. It is
retained only as an *expression of intent* — it will not be extended, refactored, or
maintained, and no new work should be built on it. The original prototype source (a
containerized FTSE 100 daily-data pipeline) was removed in commit `21541a6` and remains fully
recoverable from git history (see `c8bb93d` and earlier).

The real ZappTrade is a **blank-sheet greenfield rewrite**, governed on **TarkaFlow** as the
**ZappTrade (ZTR)** project (org `zapp` / Zappfyre). All design intent now lives there as
stakeholder **statements** and architectural **decisions** — not in this repo.

## What ZTR is building

An application to **compose Day Trading strategies for real listed stocks** and **paper-trade
them against historical daily price movements**, to evaluate how they would have performed.
Daily granularity only — explicitly no minute/tick or high-frequency trading.

## Where the intent lives (TarkaFlow ZTR)

**Stakeholder statements** — the durable intent:

| Intent | Statement |
|---|---|
| Compose + paper-trade day-trading strategies on daily data (core vision) | `ZTR-STMT-001` |
| Real listed stocks across multiple markets/indices, with metadata | `ZTR-STMT-002` |
| Deep daily OHLCV + adjusted-close history (since ~2000) | `ZTR-STMT-003` |
| Free/public end-of-day data source to start | `ZTR-STMT-004` |
| Data kept current via scheduled incremental refresh | `ZTR-STMT-005` |
| Visualize strategies + paper-trade results (chart, entries/exits, performance) | `ZTR-STMT-006` |
| Multi-market correctness: per-market trading calendars + explicit currency | `ZTR-STMT-007` |
| No single-vendor lock-in: data via a provider-agnostic adapter layer | `ZTR-STMT-008` |

**Architectural decisions** — the greenfield direction:

- **`ZTR-DECISION-001` — tech stack.** Python 3.12 + FastAPI/Pydantic backend; declarative JSON
  strategy spec; custom vectorized daily backtest/paper-trade engine; PostgreSQL + TimescaleDB
  via SQLAlchemy 2.0 + Alembic; React + TypeScript + Vite frontend with TradingView Lightweight
  Charts; monorepo with an OpenAPI-generated typed client. Daily market data is ingested through
  a **provider-agnostic adapter interface** — no single vendor is a hard dependency and the
  concrete provider(s) are deliberately not pinned. Drops the prototype's PHP/Apache frontend,
  PostgREST, standalone Swagger, and n8n loader.
- **`ZTR-DECISION-002` — hosting.** Runs on k3s as new namespace(s)/context(s) on an existing
  cluster, replacing the prototype's Docker Compose model.

## How the prototype mapped to this intent

The prototype was a data-ingestion pipeline plus an unfinished chart UI — it never contained any
strategy or paper-trading logic. What it expressed, and where that intent now lives:

| The prototype expressed… | Captured as |
|---|---|
| Curated stock universe + metadata (FTSE 100 only) | `ZTR-STMT-002` (generalized to multi-market) |
| Deep daily OHLCV + adjusted close since 2000 | `ZTR-STMT-003` |
| Free EOD data (Yahoo via the `yfinance` library) | `ZTR-STMT-004` |
| Scheduled incremental refresh (only missing days) | `ZTR-STMT-005` |
| A charting web frontend (started, never finished) | `ZTR-STMT-006` |
| A hard-wired tie to one data vendor (the anti-pattern to avoid) | `ZTR-STMT-008` |

Strategy composition + paper trading (`ZTR-STMT-001`) and multi-market calendar/currency
normalization (`ZTR-STMT-007`) are forward intent — never present in the prototype.

> **On the data source:** the prototype pulled from Yahoo Finance via `yfinance`. Yahoo's
> official API was discontinued in 2017 and `yfinance` is an unofficial, breakage-prone scraper,
> so ZTR commits to a provider-agnostic adapter (`ZTR-STMT-008` / `ZTR-DECISION-001`) rather than
> any single vendor.
