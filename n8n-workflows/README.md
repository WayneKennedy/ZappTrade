# n8n Workflows

This directory contains n8n workflow definitions for the ZappTrade data loader.

## Workflows:
- `stock-data-loader.json` - Main workflow for fetching FTSE 100 stock data from Yahoo Finance

## Setup:
1. Access n8n at http://localhost:5678
2. Login with credentials: admin/admin (⚠️ change in production)
3. Import workflows from this directory
4. Configure database connection credentials
5. Activate the workflow

## Workflow Features:
- Runs every 10 minutes
- Fetches FTSE 100 stock list
- Checks last date per ticker in database
- Downloads missing data from Yahoo Finance
- Inserts records into PostgreSQL
