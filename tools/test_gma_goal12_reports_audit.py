#!/usr/bin/env python3
"""
Test suite for Goal 12: Reports, audit, and degraded operation.
"""

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.data_contracts import Security, SecurityIdentifiers, ResearchRun, Fact, Evidence, Document
from tools.reports_and_audit import ReportGenerator, MultiMarketReportAuditor

def test_report_generation_and_audit():
    with tempfile.TemporaryDirectory() as tmp_dir:
        gen = ReportGenerator(output_base_dir=Path(tmp_dir))
        
        sec = Security("JP:7203", "JP:E02144", "JP", "7203", "TSE", "トヨタ自動車株式会社", "トヨタ", "equity", "JPY", "JPY", True, SecurityIdentifiers())
        run = ResearchRun("run_001", "2026-06-29T10:00:00Z", "7203", "JP:7203", "JP", "on_demand", "2026-06-29T10:00:00Z", "investment-research", [], [], ["EDINET_API_KEY missing"], "partial")
        
        facts = [
            Fact("f1", "JP:7203", "revenue", 45000000000000, "2026-06-29T10:00:00Z", "https://tse.or.jp", 95, "consolidated", "reported", "official")
        ]
        evidence = [
            Evidence("ev1", "c1", "Toyota record revenue", "https://tse.or.jp", 95, "2026-06-29T10:00:00Z", True, "high")
        ]
        docs = [
            Document("d1", "JP:7203", "IR", "Financial Results", "2026-06-29T10:00:00Z", "TDnet", "official", "https://tse.or.jp", "ja", True)
        ]
        agent_outs = [{
            "agent_id": "business_quality",
            "score": 8.5,
            "confidence": "high",
            "conclusion": "Solid quality",
            "claims": ["Claim 1"]
        }]

        bundle = gen.generate_report_bundle(sec, run, facts, evidence, docs, agent_outs, detailed=True)
        assert bundle["standard_report"].exists()
        assert bundle["detailed_report"].exists()
        assert bundle["facts"].exists()
        assert bundle["evidence"].exists()
        assert bundle["documents"].exists()
        assert bundle["manifest"].exists()

        # Audit check
        audit_res = MultiMarketReportAuditor.audit_report(bundle["standard_report"])
        if not audit_res["is_valid"]:
            print("Audit issues:", audit_res["issues"])
        assert audit_res["is_valid"] == True

        assert len(audit_res["issues"]) == 0

def main():
    print("Running Goal 12 Reports and Audit tests...")
    test_report_generation_and_audit()
    print("Goal 12 Reports and Audit tests passed successfully!")

if __name__ == "__main__":
    main()
