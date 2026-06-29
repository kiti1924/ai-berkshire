#!/usr/bin/env python3
"""
Comprehensive End-to-End Acceptance Test for Goal 13.
Validates all 31 specification requirements, 4-market workflows, installations, and security/terminology gates.
"""

import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.workflow_integration import ResearchWorkflowEngine
from tools.test_gma_quality_gate import main as run_quality_gate
from tools.test_gma_goal1_installation import test_installation_workflow
from tools.test_gma_goal2_data_contracts import main as run_goal2_tests
from tools.test_gma_goal3_security_resolution import main as run_goal3_tests
from tools.test_gma_goal4_access_policy import main as run_goal4_tests
from tools.test_gma_goal5_fact_snapshot import main as run_goal5_tests
from tools.test_gma_market_adapters import main as run_market_adapters_tests
from tools.test_gma_goal10_agent_methodology import main as run_goal10_tests
from tools.test_gma_goal11_skill_integration import main as run_goal11_tests
from tools.test_gma_goal12_reports_audit import main as run_goal12_tests

def run_all_e2e_checks():
    print("=== STARTING GLOBAL MARKET ADAPTATION FINAL E2E ACCEPTANCE ===")
    
    # 1. Quality gate
    run_quality_gate()
    
    # 2. Component tests (Goal 1 to 12)
    test_installation_workflow()
    run_goal2_tests()
    run_goal3_tests()
    run_goal4_tests()
    run_goal5_tests()
    run_market_adapters_tests()
    run_goal10_tests()
    run_goal11_tests()
    run_goal12_tests()
    
    # 3. 4-Market E2E execution simulation
    engine = ResearchWorkflowEngine(mode="on_demand_cached")
    targets = ["AAPL", "7203", "600519", "0700.HK"]
    for t in targets:
        res = engine.execute_research(t)
        assert res["status"] in ["completed", "partial"], f"E2E failed for target {t}"
        print(f"E2E execution for '{t}' passed with status: {res['status']}")

    print("=== ALL FINAL E2E ACCEPTANCE CHECKS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_all_e2e_checks()
