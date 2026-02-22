import pytest
from app.services.binance.processor import BinanceProcessorMixin

class DummyProcessor(BinanceProcessorMixin):
    def __init__(self):
        self.history = {}
        self.trending_symbols = set()
        self.tvl_data = {}
        self.money_flows = {}
        self.prices = {}
        self.global_stats = {}

def test_calculate_rsi_upward():
    processor = DummyProcessor()
    
    prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    
    rsi = processor.calculate_rsi(prices, period=14)
    # Steady upward trend has no losses, RSI should be 100
    assert rsi == 100.0

def test_calculate_rsi_downward():
    processor = DummyProcessor()
    
    prices = [24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10]
    
    rsi = processor.calculate_rsi(prices, period=14)
    # Steady downward trend has no gains, RSI should be (100 - (100 / (1 + 0))) = 0
    # The default return is actually 50.0 if avg_gain is not > 0 and avg_loss == 0.
    # Wait, our logic sets avg_loss to 0 logic:
    # if avg_loss == 0: return 100.0 if avg_gain > 0 else 50.0
    # In strictly downward, avg_loss > 0, avg_gain = 0.
    # rs = 0 / avg_loss = 0. rsi = 100 - 100 = 0.
    assert rsi == 0.0

def test_calculate_rsi_neutral():
    processor = DummyProcessor()
    
    # Needs len > period
    prices = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    
    rsi = processor.calculate_rsi(prices, period=14)
    # No gains, no losses -> avg_loss == 0 -> avg_gain is 0 -> 50.0
    assert rsi == 50.0

def test_calculate_rsi_not_enough_data():
    processor = DummyProcessor()
    prices = [10, 11, 12]
    
    rsi = processor.calculate_rsi(prices, period=14)
    assert rsi == 50.0
