import os
import logging
import asyncio
import aiohttp
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import List, Dict, Any

class PipelineOrchestrator:
    def __init__(self) -> None:
        self.db_url = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.engine = create_engine(self.db_url)
        self.session = self.engine.connect()
        self.logger = self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("ETL Pipeline")
        return logger

    async def run(self) -> None:
        start_ts = datetime.utcnow()
        status = 'success'
        rows_loaded = 0

        try:
            records = await self._extract_phase()
            transformed_records = self._transform_phase(records)
            self._validate_phase(transformed_records)
            rows_loaded = self._load_phase(transformed_records)
        except Exception as e:
            self.logger.error(f"Error during ETL process: {e}")
            status = 'failed'
        finally:
            end_ts = datetime.utcnow()
            self._log_audit(start_ts, end_ts, status, rows_loaded)

    async def _extract_phase(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            markets_data = await self._fetch_data(session, "https://api.coingecko.com/api/v3/coins/markets", {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "page": 1, "price_change_percentage": "7d"})
            exchange_rates_data = await self._fetch_data(session, "https://open.er-api.com/v6/latest/USD", {})
            return self._merge_data(markets_data, exchange_rates_data)

    async def _fetch_data(self, session: aiohttp.ClientSession, url: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        retries = 3
        for attempt in range(retries):
            try:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    self.logger.error(f"Failed to fetch data from {url}: {e}")
                    raise

    def _merge_data(self, markets_List[Dict[str, Any]], exchange_rates_Dict[str, Any]) -> List[Dict[str, Any]]:
        rates = exchange_rates_data.get('rates', {})
        for market in markets_data:
            for currency in ['eur', 'gbp', 'jpy', 'chf', 'cad']:
                market[f'price_{currency}'] = market['current_price'] * rates.get(currency.upper(), 0)
        return markets_data

    def _transform_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for record in records:
            record['sentiment_label'] = self._apply_sentiment_label(record['price_change_percentage_24h'])
            record['market_cap_category'] = self._apply_market_cap_category(record['market_cap_usd'])
            record['volatility_flag'] = self._apply_volatility_flag(record['price_change_percentage_24h'])
            record['supply_emission_stage'] = self._apply_supply_emission_stage(record.get('supply_ratio', 0), record.get('max_supply'))
            record['weekly_trend'] = self._apply_weekly_trend(record['change_24h_pct'], record['change_7d_pct'])
            record['data_quality_flag'] = self._apply_data_quality_flag(record)
        return records

    def _apply_sentiment_label(self, price_change_percentage: float) -> str:
        if price_change_percentage > 5:
            return 'bullish'
        elif price_change_percentage < -5:
            return 'bearish'
        return 'neutral'

    def _apply_market_cap_category(self, market_cap_usd: float) -> str:
        if market_cap_usd > 10_000_000_000:
            return 'large_cap'
        elif market_cap_usd > 1_000_000_000:
            return 'mid_cap'
        return 'small_cap'

    def _apply_volatility_flag(self, price_change_percentage: float) -> bool:
        return abs(price_change_percentage) > 10

    def _apply_supply_emission_stage(self, supply_ratio: float, max_supply: float) -> str:
        if supply_ratio < 0.5:
            return 'early'
        elif supply_ratio < 0.8:
            return 'mid'
        elif supply_ratio < 1.0:
            return 'late'
        return 'capped' if max_supply is None else 'capped'

    def _apply_weekly_trend(self, change_24h_pct: float, change_7d_pct: float) -> str:
        if change_24h_pct > 0 and change_7d_pct > 0:
            return 'bullish_momentum'
        elif change_24h_pct < 0 and change_7d_pct < 0:
            return 'bearish_momentum'
        elif change_24h_pct > 0 and change_7d_pct < 0:
            return 'reversal_up'
        elif change_24h_pct < 0 and change_7d_pct > 0:
            return 'reversal_down'
        return 'neutral'

    def _apply_data_quality_flag(self, record: Dict[str, Any]) -> int:
        if record.get('coin_id') is None or record.get('price_usd') is None:
            return 2
        if all(record.get(field) is not None for field in ['coin_id', 'price_usd', 'market_cap', 'total_volume']):
            return 0
        return 1

    def _validate_phase(self, records: List[Dict[str, Any]]) -> None:
        if len(records) < 50:
            self.logger.warning("Warning: Less than 50 records fetched.")
        for record in records:
            if record.get('coin_id') is None or record.get('price_usd') is None:
                raise ValueError("Critical data missing in record.")

    def _load_phase(self, records: List[Dict[str, Any]]) -> int:
        try:
            with self.session.begin():
                self.session.execute(text("TRUNCATE TABLE manual.crypto_market_snapshot"))
                self.session.execute(text("INSERT INTO manual.crypto_market_snapshot (columns...) VALUES (:values...)"), records)
            return len(records)
        except SQLAlchemyError as e:
            self.logger.error(f"Error loading data into database: {e}")
            raise

    def _log_audit(self, start_ts: datetime, end_ts: datetime, status: str, rows_loaded: int) -> None:
        try:
            self.session.execute(text("INSERT INTO manual.pipeline_runs (run_ts, end_ts, status, rows_loaded) VALUES (:start_ts, :end_ts, :status, :rows_loaded)"),
                                 {'start_ts': start_ts, 'end_ts': end_ts, 'status': status, 'rows_loaded': rows_loaded})
            self.session.commit()
        except SQLAlchemyError as e:
            self.logger.error(f"Error logging audit information: {e}")
            self.session.rollback()