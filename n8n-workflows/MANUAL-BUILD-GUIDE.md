# Manual n8n Workflow Build Guide

Due to credential and expression compatibility issues with JSON import, it's easier to build the workflow manually. Follow these steps:

## Prerequisites
- PostgreSQL credential created (see [CREDENTIAL-SETUP.md](CREDENTIAL-SETUP.md))
- n8n UI open at http://localhost:5678

## Step 1: Create New Workflow

1. Click **"Workflows"** in left sidebar
2. Click **"+ New workflow"** button
3. Name it: `FTSE 100 Stock Data Loader`

## Step 2: Add Schedule Trigger

1. Click **"+ Add first step"**
2. Search for: `Schedule Trigger`
3. Select it
4. Configure:
   - **Trigger Interval**: Cron
   - **Cron Expression**: `*/10 * * * *` (every 10 minutes)
5. Click outside to save

## Step 3: Add "Get Stock List" Node

1. Click the **+** on the Schedule Trigger node
2. Search for: `Postgres`
3. Select it and configure:
   - **Credential**: Select `ZappTrade PostgreSQL`
   - **Operation**: Execute Query
   - **Query**:
     ```sql
     SELECT ticker, yahoo_ticker FROM stocks ORDER BY ticker LIMIT 1
     ```
   - **Note**: Start with LIMIT 1 for testing
4. Rename node to: `Get Stock List`

## Step 4: Add "Get Last Date" Node

1. Click **+** after Get Stock List
2. Search for: `Postgres`
3. Configure:
   - **Credential**: Select `ZappTrade PostgreSQL`
   - **Operation**: Execute Query
   - **Query**:
     ```sql
     SELECT COALESCE(MAX(date), '2000-01-01'::date) as last_date
     FROM daily
     WHERE ticker = '{{ $json.yahoo_ticker }}'
     ```
4. Rename to: `Get Last Date`

## Step 5: Add "Code" Node for Date Calculation

1. Click **+** after Get Last Date
2. Search for: `Code`
3. Configure with this JavaScript:
   ```javascript
   const ticker = $input.first().json.yahoo_ticker;
   const lastDate = $input.first().json.last_date;

   // Calculate start date (day after last date)
   const startDate = new Date(lastDate);
   startDate.setDate(startDate.getDate() + 1);

   const endDate = new Date();

   // Format dates as YYYY-MM-DD
   const start = startDate.toISOString().split('T')[0];
   const end = endDate.toISOString().split('T')[0];

   return [{
     json: {
       ticker: ticker,
       startDate: start,
       endDate: end,
       startTimestamp: Math.floor(startDate.getTime() / 1000),
       endTimestamp: Math.floor(endDate.getTime() / 1000)
     }
   }];
   ```
4. Rename to: `Calculate Dates`

## Step 6: Add "HTTP Request" Node

1. Click **+** after Calculate Dates
2. Search for: `HTTP Request`
3. Configure:
   - **Method**: GET
   - **URL**: `https://query1.finance.yahoo.com/v8/finance/chart/{{ $json.ticker }}`
   - **Send Query Parameters**: ON
   - Add these parameters:
     - `period1` = `{{ $json.startTimestamp }}`
     - `period2` = `{{ $json.endTimestamp }}`
     - `interval` = `1d`
     - `events` = `history`
   - **Response Format**: JSON
4. Rename to: `Fetch Yahoo Data`

## Step 7: Add "Code" Node for Data Transformation

1. Click **+** after Fetch Yahoo Data
2. Search for: `Code`
3. Configure with this JavaScript:
   ```javascript
   const ticker = $input.first().json.ticker;
   const yahooData = $input.first().json;

   if (!yahooData.chart || !yahooData.chart.result || !yahooData.chart.result[0]) {
     return [];
   }

   const data = yahooData.chart.result[0];
   const timestamps = data.timestamp || [];
   const quotes = data.indicators.quote[0];

   const records = [];

   for (let i = 0; i < timestamps.length; i++) {
     if (quotes.close[i] !== null) {
       const date = new Date(timestamps[i] * 1000);
       records.push({
         json: {
           date: date.toISOString().split('T')[0],
           ticker: ticker,
           high_price: quotes.high[i],
           low_price: quotes.low[i],
           open_price: quotes.open[i],
           close_price: quotes.close[i],
           volume: quotes.volume[i],
           adj_close_price: quotes.close[i]
         }
       });
     }
   }

   return records;
   ```
4. Rename to: `Transform Data`

## Step 8: Add "Insert to Database" Node

1. Click **+** after Transform Data
2. Search for: `Postgres`
3. Configure:
   - **Credential**: Select `ZappTrade PostgreSQL`
   - **Operation**: Insert
   - **Schema**: public
   - **Table**: daily
   - **Columns**: Click "Add Column" for each:
     - date → `{{ $json.date }}`
     - ticker → `{{ $json.ticker }}`
     - high_price → `{{ $json.high_price }}`
     - low_price → `{{ $json.low_price }}`
     - open_price → `{{ $json.open_price }}`
     - close_price → `{{ $json.close_price }}`
     - volume → `{{ $json.volume }}`
     - adj_close_price → `{{ $json.adj_close_price }}`
   - **Options** → **On Conflict**: Do Nothing
4. Rename to: `Insert to Database`

## Step 9: Test the Workflow

1. Click **"Test workflow"** button
2. Watch execution flow through each node
3. Check for errors
4. Verify data in database:
   ```sql
   SELECT COUNT(*) FROM daily;
   ```

## Step 10: Enable for Production

1. Remove `LIMIT 1` from Get Stock List query
2. Change to: `SELECT ticker, yahoo_ticker FROM stocks ORDER BY ticker`
3. Click **"Active"** toggle at top to enable
4. Workflow will run every 10 minutes

## Troubleshooting

### No data returned from Yahoo
- Check ticker format includes `.L` suffix
- Verify dates are valid (start < end)
- Yahoo may rate limit - wait and retry

### Database insert fails
- Check all column names match exactly
- Verify data types are correct
- Look at Transform Data output to debug

### Workflow runs but no new data
- Check if data already exists (ON CONFLICT DO NOTHING)
- Verify date calculation is correct
- Check Yahoo API response

## Next Steps

Once working:
- Remove or stop Python loader: `docker compose stop zapp-stock-loader`
- Monitor executions in n8n UI
- Adjust schedule if needed (cron expression)
