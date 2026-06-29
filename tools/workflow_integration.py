"""
Workflow Integration for Global Market Adaptation.
Orchestrates Security Resolution, Market Routing, Fact Snapshot creation, Market Adapter Overlays, and Agent execution.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from tools.security_resolution import SecurityResolver, MarketRouter, ResolutionResult
from tools.access_retrieval_cache import DocumentRetriever, CacheManager
from tools.fact_snapshot_validation import FactSnapshot
from tools.market_adapters import MarketAdapterFactory, MarketOverlayAnalysis
from tools.agent_methodology import (
    BusinessQualityAgent, FinancialCapitalAgent, CompetitionRiskAgent,
    StructuralChangeAgent, GovernanceAllocatorAgent, ManagementOrganizationAgent,
    evaluate_deep_dive_triggers, AgentOutput
)

class ResearchWorkflowEngine:
    def __init__(self, mode: str = "on_demand_cached"):
        self.mode = mode
        self.resolver = SecurityResolver()
        self.cache_manager = CacheManager(enabled=(mode == "on_demand_cached"))
        self.retriever = DocumentRetriever(cache_manager=self.cache_manager)

    def execute_research(self, query: str, skill_name: str = "investment-research") -> Dict[str, Any]:
        # 1. Security Resolution
        resolution = self.resolver.resolve(query)
        if resolution.status == "not_found" or not resolution.resolved_security:
            return {
                "status": "failed",
                "error": f"Security resolution failed for query '{query}'.",
                "candidates": [c.security.security_id for c in resolution.candidates]
            }

        sec = resolution.resolved_security
        if resolution.status == "out_of_scope":
            return {
                "status": "failed",
                "error": f"Security '{sec.security_id}' is out of initial scope ({sec.security_type}).",
                "security": sec.to_dict()
            }

        # 2. Market Routing
        market_id = MarketRouter.route(sec)

        # 3. Create Fact Snapshot
        snapshot = FactSnapshot(sec.security_id)

        # 4. Market Adapter Overlay
        adapter = MarketAdapterFactory.create(sec)
        overlay = adapter.analyze_overlay(snapshot)

        # 5. Execute Standard 4 Agents
        agents = [
            BusinessQualityAgent(),
            FinancialCapitalAgent(),
            CompetitionRiskAgent(),
            StructuralChangeAgent()
        ]
        
        agent_outputs: List[AgentOutput] = []
        for agent in agents:
            out = agent.run_analysis(sec, snapshot, overlay)
            agent_outputs.append(out)

        # 6. Check and run deep-dive agents if triggered
        triggered_ids = evaluate_deep_dive_triggers(sec, snapshot, overlay)
        if "governance_allocator" in triggered_ids:
            agent_outputs.append(GovernanceAllocatorAgent().run_analysis(sec, snapshot, overlay))
        if "management_organization" in triggered_ids:
            agent_outputs.append(ManagementOrganizationAgent().run_analysis(sec, snapshot, overlay))

        return {
            "status": "completed" if not overlay.warnings else "partial",
            "query": query,
            "skill": skill_name,
            "security": sec.to_dict(),
            "market_id": market_id,
            "mode": self.mode,
            "overlay": {
                "specific_checks": overlay.specific_checks,
                "warnings": overlay.warnings
            },
            "agents": [a.to_dict() for a in agent_outputs]
        }
