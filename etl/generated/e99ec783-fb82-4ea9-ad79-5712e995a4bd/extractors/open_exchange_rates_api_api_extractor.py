import aiohttp
import asyncio
import logging
import os
from typing import Any, Dict, List

class OpenExchangeRatesApiExtractor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/5.0"}
        )
        self.api_key = os.getenv("API_KEY")
        self.base_url = self.config["url"]
        self.logger = logging.getLogger(__name__)

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            response = await self._fetch_page({})
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            return []

    async def _fetch_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        url = self.base_url
        return await self._retry_with_backoff(self._make_request, url, params)

    async def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        async with self.session.get(url, params=params, headers={"Authorization": f"Bearer {self.api_key}"}) as response:
            await self._handle_rate_limit(response)
            response.raise_for_status()
            return await response.json()

    async def _handle_rate_limit(self, response) -> None:
        if response.status == 429:
            self.logger.warning("Rate limit exceeded, handling backoff.")
            await asyncio.sleep(60)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except Exception as e:
                if attempt < 2:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds.")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries exceeded for {func.__name__}.")
                    raise

    async def close(self) -> None:
        await self.session.close()

    def _parse_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        rates = response.get("rates", {})
        return [
            {
                "EUR": rates.get("EUR"),
                "GBP": rates.get("GBP"),
                "JPY": rates.get("JPY"),
                "CHF": rates.get("CHF"),
                "CAD": rates.get("CAD"),
            }
        ] if rates else []