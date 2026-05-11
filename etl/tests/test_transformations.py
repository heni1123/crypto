import pytest
from crypto_etl import transform

def test_sentiment_label_bullish():
    row = {'price_change_percentage_24h': 6}
    assert transform.sentiment_label(row) == 'bullish'

def test_sentiment_label_bearish():
    row = {'price_change_percentage_24h': -6}
    assert transform.sentiment_label(row) == 'bearish'

def test_sentiment_label_neutral():
    row = {'price_change_percentage_24h': 0}
    assert transform.sentiment_label(row) == 'neutral'

def test_market_cap_category_large_cap():
    row = {'market_cap_usd': 15000000000}
    assert transform.market_cap_category(row) == 'large_cap'

def test_market_cap_category_mid_cap():
    row = {'market_cap_usd': 5000000000}
    assert transform.market_cap_category(row) == 'mid_cap'

def test_market_cap_category_small_cap():
    row = {'market_cap_usd': 500000000}
    assert transform.market_cap_category(row) == 'small_cap'

def test_volatility_flag_true():
    row = {'price_change_percentage_24h': 15}
    assert transform.volatility_flag(row) is True

def test_volatility_flag_false():
    row = {'price_change_percentage_24h': 5}
    assert transform.volatility_flag(row) is False

def test_supply_emission_stage_early():
    row = {'supply_ratio': 0.4}
    assert transform.supply_emission_stage(row) == 'early'

def test_supply_emission_stage_mid():
    row = {'supply_ratio': 0.7}
    assert transform.supply_emission_stage(row) == 'mid'

def test_supply_emission_stage_late():
    row = {'supply_ratio': 0.9}
    assert transform.supply_emission_stage(row) == 'late'

def test_supply_emission_stage_capped():
    row = {'supply_ratio': 1.0}
    assert transform.supply_emission_stage(row) == 'capped'

def test_supply_emission_stage_capped_null():
    row = {'max_supply': None}
    assert transform.supply_emission_stage(row) == 'capped'

def test_weekly_trend_bullish_momentum():
    row = {'change_24h_pct': 1, 'change_7d_pct': 1}
    assert transform.weekly_trend(row) == 'bullish_momentum'

def test_weekly_trend_bearish_momentum():
    row = {'change_24h_pct': -1, 'change_7d_pct': -1}
    assert transform.weekly_trend(row) == 'bearish_momentum'

def test_weekly_trend_reversal_up():
    row = {'change_24h_pct': 1, 'change_7d_pct': -1}
    assert transform.weekly_trend(row) == 'reversal_up'

def test_weekly_trend_reversal_down():
    row = {'change_24h_pct': -1, 'change_7d_pct': 1}
    assert transform.weekly_trend(row) == 'reversal_down'

def test_weekly_trend_neutral():
    row = {'change_24h_pct': 0, 'change_7d_pct': 0}
    assert transform.weekly_trend(row) == 'neutral'

def test_data_quality_flag_ok():
    row = {'coin_id': 'bitcoin', 'price_usd': 50000, 'market_cap': 1000000000, 'volume_24h': 100000}
    assert transform.data_quality_flag(row) == 0

def test_data_quality_flag_partial():
    row = {'coin_id': 'bitcoin', 'price_usd': 50000, 'market_cap': None, 'volume_24h': 100000}
    assert transform.data_quality_flag(row) == 1

def test_data_quality_flag_critical():
    row = {'coin_id': None, 'price_usd': 50000, 'market_cap': 1000000000, 'volume_24h': 100000}
    assert transform.data_quality_flag(row) == 2