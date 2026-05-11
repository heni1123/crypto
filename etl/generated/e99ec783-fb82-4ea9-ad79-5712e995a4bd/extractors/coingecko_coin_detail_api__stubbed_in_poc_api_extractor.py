import aiohttp
import asyncio
import logging
import os
from typing import Any, Dict, List

class CoingeckoCoinDetailApiStubbedInPocExtractor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/5.0"}
        )
        self.api_key = os.getenv("API_KEY")
        self.base_url = self.config["url"]
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        coin_ids = ["bitcoin", "ethereum", "ripple"]  # Example coin IDs
        tasks = [self._fetch_page({"id": coin_id}) for coin_id in coin_ids]
        results = await asyncio.gather(*tasks)
        return results

    async def _fetch_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = self.base_url.format(id=params["id"])
        return await self._retry_with_backoff(self._make_request, url)

    async def _make_request(self, url: str) -> Dict[str, Any]:
        async with self.session.get(url, headers={"Authorization": f"Bearer {self.api_key}"}) as response:
            if response.status == 429:
                await self._handle_rate_limit(response)
            response.raise_for_status()
            return await response.json()

    async def _handle_rate_limit(self, response) -> None:
        wait_time = 60  # seconds
        logging.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
        await asyncio.sleep(wait_time)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except aiohttp.ClientError as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise

    async def close(self) -> None:
        await self.session.close()