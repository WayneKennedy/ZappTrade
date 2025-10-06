# Creating PostgreSQL Credential in n8n

## Step-by-Step Instructions

### 1. Access n8n UI
- Open browser: http://localhost:5678
- Login with:
  - Username: `admin`
  - Password: `admin`

### 2. Navigate to Credentials
- Look for the left sidebar menu
- Click on **"Credentials"** (usually has a key icon 🔑)

### 3. Create New Credential
- Click the **"+ Add Credential"** button (top right)
- In the search box, type: `postgres`
- Click on **"Postgres"** from the results

### 4. Fill in Connection Details

Enter the following values exactly as shown:

| Field | Value |
|-------|-------|
| **Credential Name** | `ZappTrade PostgreSQL` |
| **Host** | `zapp-stock-db` |
| **Database** | `zapp_stock_db` |
| **User** | `docker` |
| **Password** | `docker` |
| **Port** | `5432` |
| **SSL Mode** | `disable` or `prefer` |

### 5. Test Connection
- Click the **"Test"** button (bottom left)
- You should see: ✅ "Connection successful"
- If it fails, check:
  - Is `zapp-stock-db` container running? (`docker compose ps`)
  - Are the credentials correct?
  - Can n8n reach the database? (`docker compose exec n8n ping zapp-stock-db`)

### 6. Save Credential
- Click **"Save"** button (top right)
- The credential will now appear in your credentials list

## Verification

To verify the credential is working:

1. Go to **Workflows** → Create new workflow
2. Add a **Postgres** node
3. In the **Credential** dropdown, you should see `ZappTrade PostgreSQL`
4. Select it and try a simple query like: `SELECT COUNT(*) FROM stocks`
5. Click **Execute Node** - you should see results

## What This Credential Does

This credential allows n8n to:
- Connect to your PostgreSQL database (`zapp-stock-db`)
- Read stock list from `stocks` table
- Query last dates from `daily` table
- Insert new stock data records

## Important Notes

⚠️ **Security Considerations:**
- The default credentials (`docker`/`docker`) are for development only
- For production, create a dedicated database user with limited permissions
- Consider using environment variables for sensitive data

## Troubleshooting

### "Connection failed" error
```bash
# Check if database is running
docker compose ps zapp-stock-db

# Check if n8n can reach database
docker compose exec n8n ping zapp-stock-db

# Check database logs
docker compose logs zapp-stock-db
```

### "Host not found" error
- Make sure you use `zapp-stock-db` (the container name), NOT `localhost`
- Both containers must be on the same Docker network

### "Authentication failed" error
- Double-check username and password are both `docker`
- Verify credentials in database:
  ```bash
  docker compose exec zapp-stock-db psql -U docker -d zapp_stock_db -c "SELECT current_user;"
  ```

## Next Step

Once the credential is created and tested, proceed to [SETUP.md](SETUP.md) to import and configure the stock data loader workflow.
