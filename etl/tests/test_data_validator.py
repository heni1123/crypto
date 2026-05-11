try:
    from validators.data_validator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock

@pytest.mark.asyncio
async def test_validate_batch_happy_path(sample_records):
    """Test validate_batch with valid records."""
    validator = DataValidator()
    result = await validator.validate_batch(sample_records)
    assert result.is_valid
    assert result.record_count == len(sample_records)
    assert len(result.errors) == 0

@pytest.mark.asyncio
async def test_validate_batch_empty_input(empty_records):
    """Test validate_batch with empty input."""
    validator = DataValidator()
    result = await validator.validate_batch(empty_records)
    assert not result.is_valid
    assert result.record_count == 0
    assert len(result.errors) == 0

@pytest.mark.asyncio
async def test_validate_batch_error_handling(invalid_records):
    """Test validate_batch with invalid records."""
    validator = DataValidator()
    result = await validator.validate_batch(invalid_records)
    assert not result.is_valid
    assert result.record_count == len(invalid_records)
    assert len(result.errors) > 0

def test_validate_record_happy_path(sample_records):
    """Test validate_record with valid record."""
    validator = DataValidator()
    result = validator.validate_record(sample_records[0])
    assert result.is_valid
    assert len(result.errors) == 0

def test_validate_record_empty_input():
    """Test validate_record with empty input."""
    validator = DataValidator()
    result = validator.validate_record({})
    assert not result.is_valid
    assert len(result.errors) > 0

def test_validate_record_error_handling(invalid_records):
    """Test validate_record with invalid record."""
    validator = DataValidator()
    result = validator.validate_record(invalid_records[0])
    assert not result.is_valid
    assert len(result.errors) > 0

def test_apply_rule_1_bullish():
    """Test _apply_rule_1 with bullish condition."""
    validator = DataValidator()
    record = {'price_change_percentage_24h': 6}
    result = validator._apply_rule_1(record)
    assert result == 'bullish'

def test_apply_rule_1_bearish():
    """Test _apply_rule_1 with bearish condition."""
    validator = DataValidator()
    record = {'price_change_percentage_24h': -6}
    result = validator._apply_rule_1(record)
    assert result == 'bearish'

def test_apply_rule_1_neutral():
    """Test _apply_rule_1 with neutral condition."""
    validator = DataValidator()
    record = {'price_change_percentage_24h': 0}
    result = validator._apply_rule_1(record)
    assert result == 'neutral'

def test_apply_rule_2_large_cap():
    """Test _apply_rule_2 with large cap condition."""
    validator = DataValidator()
    record = {'market_cap_usd': 15_000_000_000}
    result = validator._apply_rule_2(record)
    assert result == 'large_cap'

def test_apply_rule_2_mid_cap():
    """Test _apply_rule_2 with mid cap condition."""
    validator = DataValidator()
    record = {'market_cap_usd': 5_000_000_000}
    result = validator._apply_rule_2(record)
    assert result == 'mid_cap'

def test_apply_rule_2_small_cap():
    """Test _apply_rule_2 with small cap condition."""
    validator = DataValidator()
    record = {'market_cap_usd': 500_000_000}
    result = validator._apply_rule_2(record)
    assert result == 'small_cap'

def test_apply_rule_3_true():
    """Test _apply_rule_3 returns True for high volatility."""
    validator = DataValidator()
    record = {'price_change_percentage_24h': 15}
    result = validator._apply_rule_3(record)
    assert result is True

def test_apply_rule_3_false():
    """Test _apply_rule_3 returns False for low volatility."""
    validator = DataValidator()
    record = {'price_change_percentage_24h': 5}
    result = validator._apply_rule_3(record)
    assert result is False

def test_apply_rule_4_early():
    """Test _apply_rule_4 with early stage."""
    validator = DataValidator()
    record = {'supply_ratio': 0.3}
    result = validator._apply_rule_4(record)
    assert result == 'early'

def test_apply_rule_4_mid():
    """Test _apply_rule_4 with mid stage."""
    validator = DataValidator()
    record = {'supply_ratio': 0.7}
    result = validator._apply_rule_4(record)
    assert result == 'mid'

def test_apply_rule_4_late():
    """Test _apply_rule_4 with late stage."""
    validator = DataValidator()
    record = {'supply_ratio': 0.9}
    result = validator._apply_rule_4(record)
    assert result == 'late'

def test_apply_rule_5_bullish_momentum():
    """Test _apply_rule_5 with bullish momentum."""
    validator = DataValidator()
    record = {'change_24h_pct': 1, 'change_7d_pct': 1}
    result = validator._apply_rule_5(record)
    assert result == 'bullish_momentum'

def test_apply_rule_5_bearish_momentum():
    """Test _apply_rule_5 with bearish momentum."""
    validator = DataValidator()
    record = {'change_24h_pct': -1, 'change_7d_pct': -1}
    result = validator._apply_rule_5(record)
    assert result == 'bearish_momentum'

def test_apply_rule_5_reversal_up():
    """Test _apply_rule_5 with reversal up."""
    validator = DataValidator()
    record = {'change_24h_pct': 1, 'change_7d_pct': -1}
    result = validator._apply_rule_5(record)
    assert result == 'reversal_up'

def test_apply_rule_5_reversal_down():
    """Test _apply_rule_5 with reversal down."""
    validator = DataValidator()
    record = {'change_24h_pct': -1, 'change_7d_pct': 1}
    result = validator._apply_rule_5(record)
    assert result == 'reversal_down'

def test_apply_rule_5_neutral():
    """Test _apply_rule_5 with neutral condition."""
    validator = DataValidator()
    record = {'change_24h_pct': 0, 'change_7d_pct': 0}
    result = validator._apply_rule_5(record)
    assert result == 'neutral'

def test_apply_rule_6_valid():
    """Test _apply_rule_6 with valid data."""
    validator = DataValidator()
    record = {
        'coin_id': 'bitcoin',
        'price_usd': 50000,
        'market_cap': 1000000000,
        'volume_24h': 10000000
    }
    result = validator._apply_rule_6(record)
    assert result == 0

def test_apply_rule_6_partial_valid():
    """Test _apply_rule_6 with partially valid data."""
    validator = DataValidator()
    record = {
        'coin_id': 'bitcoin',
        'price_usd': 50000
    }
    result = validator._apply_rule_6(record)
    assert result == 1

def test_apply_rule_6_invalid():
    """Test _apply_rule_6 with invalid data."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_6(record)
    assert result == 2