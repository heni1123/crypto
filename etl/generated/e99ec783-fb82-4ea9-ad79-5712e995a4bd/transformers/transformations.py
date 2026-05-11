import logging
from typing import List, Dict, Any
from datetime import datetime

class DataTransformer:
    def __init__(self, exchange_rates: Dict[str, float]):
        self.exchange_rates = exchange_rates

    async def transform_batch(self, records: List[Dict]) -> List[Dict]:
        transformed_records = []
        for record in records:
            transformed_record = self._apply_all(record)
            transformed_records.append(transformed_record)
        return transformed_records

    def _apply_all(self, record: Dict) -> Dict:
        return {
            "symbol": self._symbol(record),
            "ath_date": self._ath_date(record),
            "atl_date": self._atl_date(record),
            "last_updated": self._last_updated(record),
            "price_eur": self._price_eur(record),
            "price_gbp": self._price_gbp(record),
            "price_jpy": self._price_jpy(record),
            "price_chf": self._price_chf(record),
            "price_cad": self._price_cad(record),
            "mcap_fdv_ratio": self._mcap_fdv_ratio(record),
            "volume_to_mcap_ratio": self._volume_to_mcap_ratio(record),
            "ath_drawdown_pct": self._ath_drawdown_pct(record),
            "atl_upside_pct": self._atl_upside_pct(record),
            "sentiment_label": self._sentiment_label(record),
            "market_cap_category": self._market_cap_category(record),
            "volatility_flag": self._volatility_flag(record),
            "supply_emission_stage": self._supply_emission_stage(record),
            "weekly_trend": self._weekly_trend(record),
            "data_quality_flag": self._data_quality_flag(record),
        }

    def _symbol(self, record: Dict) -> str:
        return record.get("symbol", "").upper()

    def _ath_date(self, record: Dict) -> Any:
        return self._convert_to_timestamptz(record.get("ath_date"))

    def _atl_date(self, record: Dict) -> Any:
        return self._convert_to_timestamptz(record.get("atl_date"))

    def _last_updated(self, record: Dict) -> Any:
        return self._convert_to_timestamptz(record.get("last_updated"))

    def _price_eur(self, record: Dict) -> Any:
        return round(self.exchange_rates.get("EUR", 0) * record.get("current_price", 0), 2) if self.exchange_rates else None

    def _price_gbp(self, record: Dict) -> Any:
        return round(self.exchange_rates.get("GBP", 0) * record.get("current_price", 0), 2) if self.exchange_rates else None

    def _price_jpy(self, record: Dict) -> Any:
        return round(self.exchange_rates.get("JPY", 0) * record.get("current_price", 0), 2) if self.exchange_rates else None

    def _price_chf(self, record: Dict) -> Any:
        return round(self.exchange_rates.get("CHF", 0) * record.get("current_price", 0), 2) if self.exchange_rates else None

    def _price_cad(self, record: Dict) -> Any:
        return round(self.exchange_rates.get("CAD", 0) * record.get("current_price", 0), 2) if self.exchange_rates else None

    def _mcap_fdv_ratio(self, record: Dict) -> Any:
        market_cap = record.get("market_cap", 0)
        fdv = record.get("fully_diluted_valuation", 0)
        return round(market_cap / fdv, 2) if fdv > 0 else None

    def _volume_to_mcap_ratio(self, record: Dict) -> Any:
        total_volume = record.get("total_volume", 0)
        market_cap = record.get("market_cap", 0)
        return round(total_volume / market_cap, 2) if market_cap > 0 else None

    def _ath_drawdown_pct(self, record: Dict) -> Any:
        current_price = record.get("current_price", 0)
        ath = record.get("ath", 0)
        return round(((current_price - ath) / ath) * 100, 2) if ath > 0 else None

    def _atl_upside_pct(self, record: Dict) -> Any:
        current_price = record.get("current_price", 0)
        atl = record.get("atl", 0)
        return round(((current_price - atl) / atl) * 100, 2) if atl > 0 else None

    def _sentiment_label(self, record: Dict) -> str:
        change_24h_pct = record.get("price_change_percentage_24h", 0)
        if change_24h_pct > 5:
            return "bullish"
        elif change_24h_pct < -5:
            return "bearish"
        return "neutral"

    def _market_cap_category(self, record: Dict) -> str:
        market_cap_usd = record.get("market_cap_usd", 0)
        if market_cap_usd > 10_000_000_000:
            return "large_cap"
        elif market_cap_usd > 1_000_000_000:
            return "mid_cap"
        return "small_cap"

    def _volatility_flag(self, record: Dict) -> bool:
        return abs(record.get("price_change_percentage_24h", 0)) > 10

    def _supply_emission_stage(self, record: Dict) -> str:
        supply_ratio = record.get("supply_ratio", 0)
        if supply_ratio < 0.5:
            return "early"
        elif supply_ratio < 0.8:
            return "mid"
        elif supply_ratio < 1.0:
            return "late"
        return "capped"

    def _weekly_trend(self, record: Dict) -> str:
        change_24h_pct = record.get("change_24h_pct", 0)
        change_7d_pct = record.get("change_7d_pct", 0)
        if change_24h_pct > 0 and change_7d_pct > 0:
            return "bullish_momentum"
        elif change_24h_pct < 0 and change_7d_pct < 0:
            return "bearish_momentum"
        elif change_24h_pct > 0 and change_7d_pct < 0:
            return "reversal_up"
        elif change_24h_pct < 0 and change_7d_pct > 0:
            return "reversal_down"
        return "neutral"

    def _data_quality_flag(self, record: Dict) -> int:
        coin_id = record.get("coin_id")
        price_usd = record.get("price_usd")
        market_cap = record.get("market_cap")
        volume_24h = record.get("volume_24h")
        if coin_id and price_usd and market_cap and volume_24h:
            return 0
        elif coin_id and price_usd:
            return 1
        return 2

    def _convert_to_timestamptz(self, iso_date: str) -> Any:
        if iso_date:
            try:
                return datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
            except ValueError:
                logging.error(f"Invalid date format: {iso_date}")
                return None
        return None