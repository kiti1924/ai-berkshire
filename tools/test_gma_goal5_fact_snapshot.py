#!/usr/bin/env python3
"""
Test suite for Goal 5: Fact snapshot and financial validation.
"""

import sys
from decimal import Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.data_contracts import Fact, Evidence
from tools.fact_snapshot_validation import FactSnapshot, FinancialValidationCalculator

def test_source_conflict_resolution():
    snapshot = FactSnapshot("US:AAPL")
    
    # Low rank secondary fact
    fact1 = Fact(
        fact_id="f1", security_id="US:AAPL", metric="revenue", value=380000000000,
        retrieved_at="2026-06-29T10:00:00Z", source_url="https://finance.portal",
        source_rank=60, consolidation="consolidated", fact_type="reported", verification_status="unverified"
    )
    # Official high rank fact
    fact2 = Fact(
        fact_id="f2", security_id="US:AAPL", metric="revenue", value=383285000000,
        retrieved_at="2026-06-29T10:05:00Z", source_url="https://sec.gov",
        source_rank=100, consolidation="consolidated", fact_type="reported", verification_status="official"
    )
    
    snapshot.add_fact(fact1)
    snapshot.add_fact(fact2)
    
    selected = snapshot.get_fact("revenue")
    assert selected.fact_id == "f2" # Official higher rank fact won!
    assert selected.value == 383285000000

def test_decimal_math_and_edge_cases():
    # Market cap computation
    mc = FinancialValidationCalculator.calculate_market_cap("150.50", "1000000000")
    assert mc == Decimal("150500000000.00")

    # Divide by zero check
    per_zero = FinancialValidationCalculator.calculate_per("150.50", "0")
    assert per_zero is None

    # Missing shares check
    mc_missing = FinancialValidationCalculator.calculate_market_cap("150.50", None)
    assert mc_missing is None

    # Negative earnings check
    per_neg = FinancialValidationCalculator.calculate_per("150.50", "-5.0")
    assert per_neg == Decimal("-30.1")

def test_evidence_on_use():
    snapshot = FactSnapshot("JP:7203")
    ev = Evidence(
        evidence_id="ev_1", claim_id="c_1", statement="Toyota reported record EV sales",
        source_url="https://news.jp", source_rank=90, retrieved_at="2026-06-29T10:00:00Z",
        supports_claim=True, confidence="high"
    )
    snapshot.register_evidence(ev)
    assert "ev_1" in snapshot.evidence_registry

def main():
    print("Running Goal 5 Fact Snapshot tests...")
    test_source_conflict_resolution()
    test_decimal_math_and_edge_cases()
    test_evidence_on_use()
    print("Goal 5 Fact Snapshot tests passed successfully!")

if __name__ == "__main__":
    main()
