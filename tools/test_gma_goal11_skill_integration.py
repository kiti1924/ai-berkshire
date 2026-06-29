#!/usr/bin/env python3
"""
Test suite for Goal 11: Skill and Codex workflow integration.
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.workflow_integration import ResearchWorkflowEngine

def test_4_markets_workflow():
    engine = ResearchWorkflowEngine(mode="on_demand_cached")
    
    # US
    res_us = engine.execute_research("AAPL")
    assert res_us["status"] in ["completed", "partial"]
    assert res_us["market_id"] == "US"
    
    # JP
    res_jp = engine.execute_research("7203")
    assert res_jp["status"] in ["completed", "partial"]
    assert res_jp["market_id"] == "JP"

    # CN_SH_A
    res_cn = engine.execute_research("600519")
    assert res_cn["status"] in ["completed", "partial"]
    assert res_cn["market_id"] == "CN_SH_A"

    # HK
    res_hk = engine.execute_research("0700.HK")
    assert res_hk.get("market_id") == "HK"

def test_out_of_scope_handling():
    engine = ResearchWorkflowEngine()
    res = engine.execute_research("SPY")
    assert res["status"] == "failed"
    assert "out of initial scope" in res["error"]

def test_unknown_query_handling():
    engine = ResearchWorkflowEngine()
    res = engine.execute_research("UNKNOWN_XYZ_999")
    assert res["status"] == "failed"
    assert "failed for query" in res["error"]

def main():
    print("Running Goal 11 Skill Integration tests...")
    test_4_markets_workflow()
    test_out_of_scope_handling()
    test_unknown_query_handling()
    print("Goal 11 Skill Integration tests passed successfully!")

if __name__ == "__main__":
    main()
