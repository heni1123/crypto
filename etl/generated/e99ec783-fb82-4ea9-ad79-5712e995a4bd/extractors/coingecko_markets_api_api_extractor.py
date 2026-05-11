import aiohttp
import asyncio
import logging
import os
from typing import Any, Dict, List

class CoingeckoMarketsApiExtractor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/5.0"}
        )
        self.api_key = os.getenv("API_KEY")
        self.base_url = self.config["url"]
        self.params = self.config["params"]

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            response = await self._fetch_page(self.params)
            return response
        except Exception as e:
            logging.error(f"Error during extraction: {e}")
            return []

    async def _fetch_page(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        url = self.base_url
        params["api_key"] = self.api_key
        response = await self._retry_with_backoff(self.session.get, url, params=params)
        if response.status == 200:
            data = await response.json()
            return data
        else:
            await self._handle_rate_limit(response)

    async def _handle_rate_limit(self, response: aiohttp.ClientResponse) -> None:
        if response.status == 429:
            wait_time = 60
            logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            await asyncio.sleep(wait_time)
            return await self._fetch_page(self.params)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except Exception as e:
                wait_time = 2 ** attempt
                logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds.")
                await asyncio.sleep(wait_time)
        raise Exception("Max retries exceeded")

    async def close(self) -> None:
        await self.session.close()