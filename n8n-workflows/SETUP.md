# n8n Stock Data Loader Setup Instructions

## Prerequisites
- n8n service running (via docker-compose)
- Access to n8n UI at http://localhost:5678
- PostgreSQL database accessible from n8n container

## Step 1: Access n8n

1. Open your browser and navigate to: http://localhost:5678
2. Login with credentials:
   - Username: `admin`
   - Password: `admin`

## Step 2: Create PostgreSQL Credential

1. Click on **Credentials** in the left sidebar
2. Click **Add Credential**
3. Search for and select **Postgres**
4. Fill in the connection details:
   - **Name:** `ZappTrade PostgreSQL`
   - **Host:** `zapp-stock-db`
   - **Database:** `zapp_stock_db`
   - **User:** `docker`
   - **Password:** `docker`
   - **Port:** `5432`
   - **SSL:** Disabled
5. Click **Test** to verify connection
6. Click **Save**

## Step 3: Import Workflow

1. Click on **Workflows** in the left sidebar
2. Click the **+** button to create a new workflow
3. Click the **⋮** (three dots) menu in the top right
4. Select **Import from File**
5. Navigate to `/home/node/.n8n/workflows/stock-data-loader.json`
6. The workflow will be imported

## Step 4: Configure Workflow

The workflow should automatically use the PostgreSQL credential you created. Verify:

1. Click on each **Postgres** node (Get Stock List, Get Last Date, Insert to Database)
2. Ensure the **Credential** dropdown shows `ZappTrade PostgreSQL`
3. If not, select it from the dropdown

## Step 5: Test the Workflow

1. Click **Execute Workflow** button (play icon) at the bottom
2. Watch the execution flow through each node
3. Check for any errors in the output panels
4. Verify data is being inserted into the database:
   ```sql
   SELECT COUNT(*) FROM daily;
   ```

## Step 6: Activate the Workflow

1. Toggle the **Active** switch at the top of the workflow to ON
2. The workflow will now run every 10 minutes automatically

## Workflow Logic

The workflow executes the following steps:

1. **Schedule Trigger** - Runs every 10 minutes (cron: `*/10 * * * *`)
2. **Get Stock List** - Queries all tickers from `stocks` table
3. **Extract Ticker** - Extracts the yahoo_ticker for each stock
4. **Get Last Date** - Finds the most recent date for each ticker in `daily` table
5. **Calculate Date Range** - Determines start date (last date + 1 day or 2000-01-01) and end date (today)
6. **Check If Data Needed** - Only proceeds if start date < end date
7. **Fetch Yahoo Finance Data** - Calls Yahoo Finance API for historical data
8. **Transform Yahoo Data** - Converts JSON response to database format
9. **Insert to Database** - Inserts records with ON CONFLICT DO NOTHING

## Troubleshooting

### Workflow fails on PostgreSQL nodes
- Verify database credentials are correct
- Check that zapp-stock-db container is running
- Ensure database has `stocks` and `daily` tables

### Yahoo Finance API returns errors
- Check ticker format (should include `.L` suffix for London stocks)
- Verify date range is valid
- API may rate limit - wait a few minutes and retry

### No data is being inserted
- Check the **Transform Yahoo Data** node output
- Verify the date format matches PostgreSQL expectations
- Ensure ON CONFLICT handling is working correctly

## Monitoring

View workflow execution history:
1. Click **Executions** in the left sidebar
2. See all past runs with success/failure status
3. Click any execution to see detailed node outputs

## Disable Python Loader

Once the n8n workflow is working correctly, you can disable the Python loader:

```bash
docker compose stop zapp-stock-loader
```

Or remove it from docker-compose.yml entirely.
