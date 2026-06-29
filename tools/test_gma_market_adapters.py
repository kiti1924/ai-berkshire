#!/usr/bin/env python3
"""
Test suite for Goals 6-9: Market Adapters (US, Japan, Shanghai A, Hong Kong).
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.data_contracts import Security, SecurityIdentifiers, Fact
from tools.fact_snapshot_validation import FactSnapshot
from tools.market_adapters import MarketAdapterFactory, USMarketAdapter, JapanMarketAdapter, ShanghaiAMarketAdapter, HongKongMarketAdapter

def test_us_market_adapter():
    sec = Security("US:AAPL", "US:CIK01", "US", "AAPL", "NASDAQ", "Apple Inc.", "Apple", "equity", "USD", "USD", True, SecurityIdentifiers())
    adapter = MarketAdapterFactory.create(sec)
    assert isinstance(adapter, USMarketAdapter)
    
    snapshot = FactSnapshot("US:AAPL")
    res = adapter.analyze_overlay(snapshot)
    assert res.market_id == "US"
    assert "stock_based_compensation" in res.specific_checks
    assert "SEC EDGAR filing unavailable" in res.warnings[0] # Degraded since no SEC url in facts

def test_japan_market_adapter():
    sec = Security("JP:7203", "JP:E02144", "JP", "7203", "TSE", "トヨタ自動車株式会社", "トヨタ", "equity", "JPY", "JPY", True, SecurityIdentifiers())
    adapter = MarketAdapterFactory.create(sec)
    assert isinstance(adapter, JapanMarketAdapter)
    
    # Test without EDINET_API_KEY
    os.environ.pop("EDINET_API_KEY", None)
    snapshot = FactSnapshot("JP:7203")
    res = adapter.analyze_overlay(snapshot)
    assert res.status == "partial"
    assert any("EDINET_API_KEY missing" in w for w in res.warnings)
    assert "strategic_shareholdings" in res.specific_checks # 政策保有株 check present

def test_shanghai_a_market_adapter():
    sec = Security("CN_SH_A:600519", "CN:600519", "CN_SH_A", "600519", "SSE", "贵州茅台酒股份有限公司", "贵州茅台", "equity", "CNY", "CNY", True, SecurityIdentifiers())
    adapter = MarketAdapterFactory.create(sec)
    assert isinstance(adapter, ShanghaiAMarketAdapter)
    
    snapshot = FactSnapshot("CN_SH_A:600519")
    res = adapter.analyze_overlay(snapshot)
    assert res.market_id == "CN_SH_A"
    assert res.specific_checks["state_owned_vs_private"] == "SOE"

def test_hong_kong_market_adapter():
    sec = Security("HK:0700", "HK:0700", "HK", "700", "HKEX", "Tencent Holdings Limited", "Tencent", "equity", "HKD", "RMB", True, SecurityIdentifiers())
    adapter = MarketAdapterFactory.create(sec)
    assert isinstance(adapter, HongKongMarketAdapter)
    
    snapshot = FactSnapshot("HK:0700")
    res = adapter.analyze_overlay(snapshot)
    assert res.market_id == "HK"
    assert res.specific_checks["formatted_ticker"] == "0700.HK"

def main():
    print("Running Goals 6-9 Market Adapters tests...")
    test_us_market_adapter()
    test_japan_market_adapter()
    test_shanghai_a_market_adapter()
    test_hong_kong_market_adapter()
    print("Goals 6-9 Market Adapters tests passed successfully!")

if __name__ == "__main__":
    main()
