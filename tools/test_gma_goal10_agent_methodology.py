#!/usr/bin/env python3
"""
Test suite for Goal 10: Agent methodology integration.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.data_contracts import Security, SecurityIdentifiers
from tools.fact_snapshot_validation import FactSnapshot
from tools.market_adapters import MarketAdapterFactory
from tools.agent_methodology import (
    BusinessQualityAgent, FinancialCapitalAgent, GovernanceAllocatorAgent,
    ManagementOrganizationAgent, evaluate_deep_dive_triggers
)

def test_japan_lens_blending():
    sec_jp = Security("JP:7203", "JP:E02144", "JP", "7203", "TSE", "トヨタ自動車株式会社", "トヨタ", "equity", "JPY", "JPY", True, SecurityIdentifiers())
    snapshot = FactSnapshot("JP:7203")
    overlay = MarketAdapterFactory.create(sec_jp).analyze_overlay(snapshot)
    
    bq_agent = BusinessQualityAgent()
    fc_agent = FinancialCapitalAgent()
    
    bq_out = bq_agent.run_analysis(sec_jp, snapshot, overlay)
    fc_out = fc_agent.run_analysis(sec_jp, snapshot, overlay)
    
    assert any("Fujino-style" in c for c in bq_out.claims)
    assert any("Murakami-style" in c for c in fc_out.claims)

def test_non_japan_no_forced_lenses():
    sec_us = Security("US:AAPL", "US:CIK01", "US", "AAPL", "NASDAQ", "Apple Inc.", "Apple", "equity", "USD", "USD", True, SecurityIdentifiers())
    snapshot = FactSnapshot("US:AAPL")
    overlay = MarketAdapterFactory.create(sec_us).analyze_overlay(snapshot)
    
    bq_agent = BusinessQualityAgent()
    bq_out = bq_agent.run_analysis(sec_us, snapshot, overlay)
    assert not any("Fujino-style" in c for c in bq_out.claims)

def test_deep_dive_triggers():
    sec_jp = Security("JP:7203", "JP:E02144", "JP", "7203", "TSE", "トヨタ自動車株式会社", "トヨタ", "equity", "JPY", "JPY", True, SecurityIdentifiers())
    snapshot = FactSnapshot("JP:7203")
    overlay = MarketAdapterFactory.create(sec_jp).analyze_overlay(snapshot)
    
    triggers = evaluate_deep_dive_triggers(sec_jp, snapshot, overlay)
    assert "governance_allocator" in triggers

def test_terminology_gate_and_no_personality():
    bq_agent = BusinessQualityAgent()
    sec_us = Security("US:AAPL", "US:CIK01", "US", "AAPL", "NASDAQ", "Apple Inc.", "Apple", "equity", "USD", "USD", True, SecurityIdentifiers())
    out = bq_agent.run_analysis(sec_us, FactSnapshot("US:AAPL"), MarketAdapterFactory.create(sec_us).analyze_overlay(FactSnapshot("US:AAPL")))
    
    text = str(out.to_dict())
    assert "護城河" not in text
    assert "moat" in text.lower() or "モート" in text

def main():
    print("Running Goal 10 Agent Methodology tests...")
    test_japan_lens_blending()
    test_non_japan_no_forced_lenses()
    test_deep_dive_triggers()
    test_terminology_gate_and_no_personality()
    print("Goal 10 Agent Methodology tests passed successfully!")

if __name__ == "__main__":
    main()
