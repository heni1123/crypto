import aiohttp
import asyncio
import logging
import os
from typing import List, Dict, Any

class DataExtractor:
    BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"
    MAX_RETRIES = 3
    TIMEOUT = (10, 30)
    USER_AGENT = "ETL-Agent/5.0"

    def __init__(self) -> None:
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(*self.TIMEOUT),
            headers={"User-Agent": self.USER_AGENT}
        )
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "price_change_percentage": "7d"
        }
        for attempt in range(self.MAX_RETRIES):
            try:
                async with self.session.get(self.BASE_URL, params=params) as response:
                    if response.status == 429:
                        wait_time = 60
                        logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
                        await asyncio.sleep(wait_time)
                        continue
                    response.raise_for_status()
                    data = await response.json()
                    return data
            except aiohttp.ClientError as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 ** attempt)
        raise Exception("Max retries exceeded for API request.")

    async def close(self) -> None:
        await self.session.close()