import pytest
from crypto_etl import validate_sentiment_label, validate_market_cap_category, validate_volatility_flag, validate_supply_emission_stage, validate_weekly_trend, validate_data_quality_flag

def test_validate_sentiment_label():
    assert validate_sentiment_label({'price_change_percentage_24h': 6}) == 'bullish'
    assert validate_sentiment_label({'price_change_percentage_24h': -6}) == 'bearish'
    assert validate_sentiment_label({'price_change_percentage_24h': 0}) == 'neutral'

def test_validate_market_cap_category():
    assert validate_market_cap_category({'market_cap_usd': 15000000000}) == 'large_cap'
    assert validate_market_cap_category({'market_cap_usd': 5000000000}) == 'mid_cap'
    assert validate_market_cap_category({'market_cap_usd': 500000000}) == 'small_cap'

def test_validate_volatility_flag():
    assert validate_volatility_flag({'price_change_percentage_24h': 11}) is True
    assert validate_volatility_flag({'price_change_percentage_24h': -11}) is True
    assert validate_volatility_flag({'price_change_percentage_24h': 5}) is False

def test_validate_supply_emission_stage():
    assert validate_supply_emission_stage({'supply_ratio': 0.4}) == 'early'
    assert validate_supply_emission_stage({'supply_ratio': 0.7}) == 'mid'
    assert validate_supply_emission_stage({'supply_ratio': 0.9}) == 'late'
    assert validate_supply_emission_stage({'supply_ratio': 1.0}) == 'capped'
    assert validate_supply_emission_stage({'max_supply': None}) == 'capped'

def test_validate_weekly_trend():
    assert validate_weekly_trend({'change_24h_pct': 1, 'change_7d_pct': 1}) == 'bullish_momentum'
    assert validate_weekly_trend({'change_24h_pct': -1, 'change_7d_pct': -1}) == 'bearish_momentum'
    assert validate_weekly_trend({'change_24h_pct': 1, 'change_7d_pct': -1}) == 'reversal_up'
    assert validate_weekly_trend({'change_24h_pct': -1, 'change_7d_pct': 1}) == 'reversal_down'
    assert validate_weekly_trend({'change_24h_pct': 0, 'change_7d_pct': 0}) == 'neutral'

def test_validate_data_quality_flag():
    assert validate_data_quality_flag({'coin_id': 'bitcoin', 'price_usd': 50000, 'market_cap': 1000000000, 'volume_24h': 100000}) == 0
    assert validate_data_quality_flag({'coin_id': 'bitcoin', 'price_usd': 50000, 'market_cap': None, 'volume_24h': 100000}) == 1
    assert validate_data_quality_flag({'coin_id': None, 'price_usd': 50000, 'market_cap': 1000000000, 'volume_24h': 100000}) == 2