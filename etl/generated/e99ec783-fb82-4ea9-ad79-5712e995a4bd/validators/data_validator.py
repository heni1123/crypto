import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    record_count: int

class DataValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def validate_batch(self, records: List[Dict]) -> ValidationResult:
        total_errors = []
        total_warnings = []
        for record in records:
            result = self.validate_record(record)
            if not result.is_valid:
                total_errors.extend(result.errors)
            total_warnings.extend(result.warnings)
        return ValidationResult(
            is_valid=len(total_errors) == 0,
            errors=total_errors,
            warnings=total_warnings,
            record_count=len(records)
        )

    def validate_record(self, record: Dict) -> ValidationResult:
        errors = []
        warnings = []
        if 'coin_id' not in record or record['coin_id'] is None:
            errors.append("coin_id is required.")
        if 'price_usd' not in record or record['price_usd'] is None:
            errors.append("price_usd is required.")
        
        sentiment_label = self._apply_rule_1(record)
        market_cap_category = self._apply_rule_2(record)
        volatility_flag = self._apply_rule_3(record)
        supply_emission_stage = self._apply_rule_4(record)
        weekly_trend = self._apply_rule_5(record)
        data_quality_flag = self._apply_rule_6(record)

        record.update({
            'sentiment_label': sentiment_label,
            'market_cap_category': market_cap_category,
            'volatility_flag': volatility_flag,
            'supply_emission_stage': supply_emission_stage,
            'weekly_trend': weekly_trend,
            'data_quality_flag': data_quality_flag
        })

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            record_count=1
        )

    def _apply_rule_1(self, record: Dict) -> str:
        price_change = record.get('price_change_percentage_24h', 0)
        if price_change > 5:
            return 'bullish'
        elif price_change < -5:
            return 'bearish'
        return 'neutral'

    def _apply_rule_2(self, record: Dict) -> str:
        market_cap = record.get('market_cap_usd', 0)
        if market_cap > 10_000_000_000:
            return 'large_cap'
        elif market_cap > 1_000_000_000:
            return 'mid_cap'
        return 'small_cap'

    def _apply_rule_3(self, record: Dict) -> bool:
        price_change = abs(record.get('price_change_percentage_24h', 0))
        return price_change > 10

    def _apply_rule_4(self, record: Dict) -> str:
        supply_ratio = record.get('supply_ratio', 0)
        if supply_ratio < 0.5:
            return 'early'
        elif supply_ratio < 0.8:
            return 'mid'
        elif supply_ratio < 1.0:
            return 'late'
        return 'capped'

    def _apply_rule_5(self, record: Dict) -> str:
        change_24h_pct = record.get('change_24h_pct', 0)
        change_7d_pct = record.get('change_7d_pct', 0)
        if change_24h_pct > 0 and change_7d_pct > 0:
            return 'bullish_momentum'
        elif change_24h_pct < 0 and change_7d_pct < 0:
            return 'bearish_momentum'
        elif change_24h_pct > 0 and change_7d_pct < 0:
            return 'reversal_up'
        elif change_24h_pct < 0 and change_7d_pct > 0:
            return 'reversal_down'
        return 'neutral'

    def _apply_rule_6(self, record: Dict) -> int:
        if 'coin_id' in record and record['coin_id'] is not None and \
           'price_usd' in record and record['price_usd'] is not None and \
           'market_cap' in record and record['market_cap'] is not None and \
           'volume_24h' in record and record['volume_24h'] is not None:
            return 0
        elif 'coin_id' in record and record['coin_id'] is not None and \
             'price_usd' in record and record['price_usd'] is not None:
            return 1
        return 2