#!/usr/bin/env python3
"""
Test suite for Goal 2: Canonical data contracts.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.data_contracts import (
    Security, SecurityIdentifiers, Document, Fact, Evidence, ResearchRun
)


def test_security_contract():
    sec_data = {
        "security_id": "JP:7203",
        "issuer_id": "JP:EDINET_E02144",
        "market_id": "JP",
        "ticker": "7203",
        "exchange": "TSE",
        "legal_name": "トヨタ自動車株式会社",
        "display_name": "トヨタ",
        "security_type": "equity",
        "trading_currency": "JPY",
        "reporting_currency": "JPY",
        "primary_listing": True,
        "identifiers": {
            "cik": None,
            "edinet_code": "E02144",
            "isin": "JP3633400001",
            "exchange_code": "7203.T"
        }
    }
    sec = Security.from_dict(sec_data)
    assert sec.market_id == "JP"
    json_str = sec.to_json()
    sec2 = Security.from_json(json_str)
    assert sec2 == sec

def test_naive_datetime_rejection():
    doc_data = {
        "document_id": "doc_001",
        "security_id": "US:AAPL",
        "document_type": "10-K",
        "title": "Annual Report",
        "retrieved_at": "2026-06-29T10:00:00", # Naive! No offset!
        "source_name": "SEC_EDGAR",
        "source_type": "official",
        "source_url": "https://www.sec.gov/edgar",
        "language": "en",
        "is_official": True
    }
    try:
        Document.from_dict(doc_data)
        assert False, "Should have rejected naive datetime!"
    except ValueError as e:
        assert "Naive datetime rejected" in str(e)

def test_invalid_enum_rejection():
    fact_data = {
        "fact_id": "fact_001",
        "security_id": "US:AAPL",
        "metric": "revenue",
        "value": 100000000,
        "retrieved_at": "2026-06-29T10:00:00Z",
        "source_url": "https://www.sec.gov",
        "source_rank": 100,
        "consolidation": "consolidated",
        "fact_type": "reported",
        "verification_status": "SUPER_VERIFIED" # Invalid enum!
    }
    try:
        Fact.from_dict(fact_data)
        assert False, "Should have rejected invalid enum!"
    except ValueError:
        pass

def test_unknown_field_policy():
    ev_data = {
        "evidence_id": "ev_001",
        "claim_id": "claim_001",
        "statement": "Valid statement",
        "source_url": "https://example.com",
        "source_rank": 90,
        "retrieved_at": "2026-06-29T10:00:00Z",
        "supports_claim": True,
        "confidence": "high",
        "extra_random_field": 123 # Unknown field!
    }
    try:
        Evidence.from_dict(ev_data)
        assert False, "Should have rejected unknown field!"
    except ValueError as e:
        assert "Unknown fields" in str(e)

def test_null_handling_and_deterministic_json():
    fact_data = {
        "fact_id": "fact_002",
        "security_id": "JP:7203",
        "metric": "market_cap",
        "value": 35000000000000,
        "unit": "currency_amount",
        "currency": "JPY",
        "period_start": None,
        "period_end": None,
        "as_of": "2026-06-29T10:00:00+09:00",
        "retrieved_at": "2026-06-29T10:00:00+09:00",
        "source_document_id": None,
        "source_url": "https://www.jpx.co.jp",
        "source_rank": 95,
        "accounting_standard": "IFRS",
        "consolidation": "consolidated",
        "fact_type": "reported",
        "verification_status": "official"
    }
    fact = Fact.from_dict(fact_data)
    assert fact.period_start is None
    json_str = fact.to_json()
    # Check deterministic sorting
    keys = list(json.loads(json_str).keys())
    assert keys == sorted(keys)

def test_research_run_contract():
    run_data = {
        "run_id": "run_123456",
        "started_at": "2026-06-29T10:00:00Z",
        "completed_at": "2026-06-29T10:05:00Z",
        "query": "7203",
        "resolved_security_id": "JP:7203",
        "market_id": "JP",
        "mode": "on_demand",
        "as_of": "2026-06-29T10:00:00Z",
        "skill": "investment-research",
        "documents_used": ["doc_1"],
        "facts_used": ["fact_1"],
        "warnings": [],
        "status": "completed"
    }
    run = ResearchRun.from_dict(run_data)
    assert run.market_id == "JP"
    assert run.status == "completed"

def main():
    print("Running Goal 2 data contract tests...")
    test_security_contract()
    test_naive_datetime_rejection()
    test_invalid_enum_rejection()
    test_unknown_field_policy()
    test_null_handling_and_deterministic_json()
    test_research_run_contract()
    print("Goal 2 data contract tests passed successfully!")

if __name__ == "__main__":
    main()
