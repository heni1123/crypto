import os
import logging
import asyncio
import aiohttp
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)

async def fetch(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    for attempt in range(3):
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            await asyncio.sleep(2 ** attempt)
    return {}

async def fetch_coingecko_markets(session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1&price_change_percentage=7d"
    return await fetch(session, url)

async def fetch_exchange_rates(session: aiohttp.ClientSession) -> Dict[str, Any]:
    url = "https://open.er-api.com/v6/latest/USD"
    return await fetch(session, url)

async def ingest_data() -> None:
    async with aiohttp.ClientSession() as session:
        markets_data, exchange_rates_data = await asyncio.gather(
            fetch_coingecko_markets(session),
            fetch_exchange_rates(session)
        )
        await process_data(markets_data, exchange_rates_data)

async def process_data(markets_List[Dict[str, Any]], exchange_rates_Dict[str, Any]) -> None:
    if not markets_data or 'rates' not in exchange_rates_data:
        logger.error("No data to process or exchange rates missing.")
        return

    rates = exchange_rates_data['rates']
    processed_data = []

    for coin in markets_data:
        coin_data = {
            "coin_id": coin.get("id"),
            "current_price": coin.get("current_price"),
            "market_cap_usd": coin.get("market_cap"),
            "total_volume": coin.get("total_volume"),
            "price_eur": coin.get("current_price") * rates.get("EUR", 0),
            "price_gbp": coin.get("current_price") * rates.get("GBP", 0),
            "price_jpy": coin.get("current_price") * rates.get("JPY", 0),
            "price_chf": coin.get("current_price") * rates.get("CHF", 0),
            "price_cad": coin.get("current_price") * rates.get("CAD", 0),
        }
        processed_data.append(coin_data)

    await load_data(processed_data)

async def load_data(List[Dict[str, Any]]) -> None:
    if not data:
        logger.warning("No data to load.")
        return

    try:
        with engine.begin() as connection:
            connection.execute("TRUNCATE TABLE manual.crypto_market_snapshot")
            connection.execute(
                "INSERT INTO manual.crypto_market_snapshot (coin_id, current_price, market_cap_usd, total_volume, price_eur, price_gbp, price_jpy, price_chf, price_cad) VALUES (:coin_id, :current_price, :market_cap_usd, :total_volume, :price_eur, :price_gbp, :price_jpy, :price_chf, :price_cad)",
                data
            )
            logger.info(f"Loaded {len(data)} rows into the database.")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")

if __name__ == "__main__":
    asyncio.run(ingest_data())