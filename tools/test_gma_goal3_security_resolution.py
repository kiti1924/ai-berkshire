#!/usr/bin/env python3
"""
Test suite for Goal 3: Security resolution and market routing.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.security_resolution import SecurityResolver, MarketRouter

def test_representative_tickers():
    resolver = SecurityResolver()
    
    # US
    res_us = resolver.resolve("AAPL")
    assert res_us.status == "resolved"
    assert res_us.resolved_security.market_id == "US"
    assert MarketRouter.route(res_us.resolved_security) == "US"
    
    # JP (with and without suffix)
    res_jp = resolver.resolve("7203")
    assert res_jp.status == "resolved"
    assert res_jp.resolved_security.market_id == "JP"
    assert MarketRouter.route(res_jp.resolved_security) == "JP"

    res_jp_s = resolver.resolve("7203.T")
    assert res_jp_s.status == "resolved"
    assert res_jp_s.resolved_security.market_id == "JP"

    # CN_SH_A
    res_cn = resolver.resolve("600519")
    assert res_cn.status == "resolved"
    assert res_cn.resolved_security.market_id == "CN_SH_A"
    assert MarketRouter.route(res_cn.resolved_security) == "CN_SH_A"

    # HK (with leading zero expansion)
    res_hk = resolver.resolve("700")
    assert res_hk.status == "resolved"
    assert res_hk.resolved_security.market_id == "HK"
    assert res_hk.resolved_security.ticker == "0700"

def test_fullwidth_input():
    resolver = SecurityResolver()
    res = resolver.resolve("７２０３") # Full-width
    assert res.status == "resolved"
    assert res.resolved_security.market_id == "JP"

def test_company_names():
    resolver = SecurityResolver()
    assert resolver.resolve("トヨタ自動車").resolved_security.market_id == "JP"
    assert resolver.resolve("贵州茅台").resolved_security.market_id == "CN_SH_A"

def test_adr_vs_native():
    resolver = SecurityResolver()
    baba_us = resolver.resolve("BABA").resolved_security
    baba_hk = resolver.resolve("9988").resolved_security
    assert baba_us.security_id != baba_hk.security_id
    assert baba_us.issuer_id == baba_hk.issuer_id

def test_out_of_scope():
    resolver = SecurityResolver()
    res = resolver.resolve("SPY")
    assert res.status == "out_of_scope"
    assert res.candidates[0].is_supported == False

def test_deterministic_candidate_ordering():
    resolver = SecurityResolver()
    res = resolver.resolve("Alibaba")
    assert len(res.candidates) >= 2
    # Confidences should be descending
    confidences = [c.confidence for c in res.candidates]
    assert confidences == sorted(confidences, reverse=True)

def main():
    print("Running Goal 3 Security Resolution tests...")
    test_representative_tickers()
    test_fullwidth_input()
    test_company_names()
    test_adr_vs_native()
    test_out_of_scope()
    test_deterministic_candidate_ordering()
    print("Goal 3 Security Resolution tests passed successfully!")

if __name__ == "__main__":
    main()
