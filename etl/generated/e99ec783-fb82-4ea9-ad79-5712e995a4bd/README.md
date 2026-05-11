# ETL Pipeline for Cryptocurrency Data

## Overview
This project implements an ETL pipeline for cryptocurrency data, extracting information from the CoinGecko Markets API and the Open Exchange Rates API. The data is transformed according to specific business rules and loaded into a PostgreSQL 15 database.

## Architecture
- **Stack**: Python 3.10+, pandas, SQLAlchemy 2.0, psycopg2, requests
- **Data Sources**:
  - CoinGecko Markets API: https://api.coingecko.com/api/v3/coins/markets (1 call/run, 50 coins)
  - CoinGecko Detail API: STUBBED in POC (returns NULL for categories/genesis_date/description)
  - Open Exchange Rates: https://open.er-api.com/v6/latest/USD (1 call/run, broadcast on 50 lines)
- **Target**: PostgreSQL 15, schema `manual`, tables `crypto_market_snapshot` (44 columns) + `pipeline_runs` (audit)
- **Load Pattern**: TRUNCATE then INSERT in a single atomic transaction (rollback if 1 row fails out of 50)

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/heni1123/crypto.git
   cd crypto
   ```
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration
Create a `.env` file in the root directory with the following variables:
```
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
ETL_ENV=development
GITHUB_TOKEN=your_github_token
GITHUB_OWNER=your_github_owner
GITHUB_REPO=your_github_repo
```

## Run
To execute the ETL pipeline, run the following command:
```
python crypto_etl.py
```
The pipeline is scheduled to run every hour using a cron job:
```
0 * * * * /usr/bin/python3 /path/to/crypto/crypto_etl.py
```

## Testing
To test the ETL pipeline, ensure that the environment is set up correctly and run:
```
pytest
```
This will execute all unit tests defined in the `tests` directory.

## API Sources
- **CoinGecko Markets API**: 
  - URL: https://api.coingecko.com/api/v3/coins/markets
  - Method: GET
  - Auth: None
- **CoinGecko Detail API**: 
  - URL: https://api.coingecko.com/api/v3/coins/{id}
  - Method: GET
  - Auth: None
- **Open Exchange Rates**: 
  - URL: https://open.er-api.com/v6/latest/USD
  - Method: GET
  - Auth: None

## Troubleshooting
- Ensure that all environment variables are set correctly in the `.env` file.
- Check the database connection settings and privileges.
- Review the logs in the `pipeline_runs` table for any errors during execution.
- If the API calls fail, verify the network connection and API availability.