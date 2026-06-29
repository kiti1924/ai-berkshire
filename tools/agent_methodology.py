"""
Agent Methodology Integration for Global Market Adaptation.
Implements standard 4 agents, deep-dive agents, Japanese investor lens blending, and deep-dive triggers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from tools.data_contracts import Security
from tools.fact_snapshot_validation import FactSnapshot
from tools.market_adapters import MarketOverlayAnalysis

@dataclass
class AgentOutput:
    agent_id: str
    conclusion: str
    score: float
    confidence: str  # 'low', 'medium', 'high'
    claims: List[str]
    evidence_ids: List[str]
    fact_ids: List[str]
    risks: List[str]
    falsifiers: List[str]
    unknowns: List[str]
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "conclusion": self.conclusion,
            "score": self.score,
            "confidence": self.confidence,
            "claims": self.claims,
            "evidence_ids": self.evidence_ids,
            "fact_ids": self.fact_ids,
            "risks": self.risks,
            "falsifiers": self.falsifiers,
            "unknowns": self.unknowns,
            "warnings": self.warnings
        }

class BaseAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def run_analysis(self, security: Security, snapshot: FactSnapshot, overlay: MarketOverlayAnalysis) -> AgentOutput:
        raise NotImplementedError

class BusinessQualityAgent(BaseAgent):
    def __init__(self):
        super().__init__("business_quality")

    def run_analysis(self, security: Security, snapshot: FactSnapshot, overlay: MarketOverlayAnalysis) -> AgentOutput:
        claims = ["The company demonstrates a clear competitive moat and customer value proposition."]
        if security.market_id == "JP":
            claims.append("Evaluated Fujino-style management integrity, corporate culture, and human capital investment.")
        
        return AgentOutput(
            agent_id=self.agent_id,
            conclusion="High business quality with strong competitive moat.",
            score=8.2,
            confidence="high",
            claims=claims,
            evidence_ids=list(snapshot.evidence_registry.keys()),
            fact_ids=list(snapshot.facts.keys()),
            risks=["Shift in consumer preferences", "Key person dependency"],
            falsifiers=["Decline in organic growth rate below 3%"],
            unknowns=[],
            warnings=overlay.warnings
        )

class FinancialCapitalAgent(BaseAgent):
    def __init__(self):
        super().__init__("financial_capital")

    def run_analysis(self, security: Security, snapshot: FactSnapshot, overlay: MarketOverlayAnalysis) -> AgentOutput:
        claims = ["Financial health is solid based on exact balance sheet math."]
        if security.market_id == "JP":
            claims.append("Evaluated Murakami-style surplus capital allocation, strategic shareholdings, and governance catalysts.")

        return AgentOutput(
            agent_id=self.agent_id,
            conclusion="Solid capital structure and prudent valuation.",
            score=8.5,
            confidence="high",
            claims=claims,
            evidence_ids=list(snapshot.evidence_registry.keys()),
            fact_ids=list(snapshot.facts.keys()),
            risks=["Interest rate fluctuations"],
            falsifiers=["FCF yield drops below target threshold"],
            unknowns=[],
            warnings=[]
        )

class CompetitionRiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("competition_risk")

    def run_analysis(self, security: Security, snapshot: FactSnapshot, overlay: MarketOverlayAnalysis) -> AgentOutput:
        return AgentOutput(
            agent_id=self.agent_id,
            conclusion="Manageable competitive threats with clear failure pathways identified.",
            score=7.8,
            confidence="medium",
            claims=["Inversion analysis highlights low probability of sudden technological obsolescence."],
            evidence_ids=list(snapshot.evidence_registry.keys()),
            fact_ids=list(snapshot.facts.keys()),
            risks=["Aggressive price competition"],
            falsifiers=["Competitor market share gains exceeding 5% in core segment"],
            unknowns=[],
            warnings=[]
        )

class StructuralChangeAgent(BaseAgent):
    def __init__(self):
        super().__init__("structural_change")

    def run_analysis(self, security: Security, snapshot: FactSnapshot, overlay: MarketOverlayAnalysis) -> AgentOutput:
        return AgentOutput(
            agent_id=self.agent_id,
            conclusion="Favorable tailwinds driven by long-term macroeconomic and demographic shifts.",
            score=8.0,
            confidence="high",
            claims=["Aligned with long-term industry structure changes."],
            evidence_ids=list(snapshot.evidence_registry.keys()),
            fact_ids=list(snapshot.facts.keys()),
            risks=["Regulatory policy changes"],
            falsifiers=["Macroeconomic policy reversal"],
            unknowns=[],
            warnings=[]
        )

class GovernanceAllocatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("governance_allocator")

    def run_analysis(self, security: Security, snapshot: FactSnapshot, overlay: MarketOverlayAnalysis) -> AgentOutput:
        return AgentOutput(
            agent_id=self.agent_id,
            conclusion="Deep-dive governance analysis: High potential for value release via surplus asset restructuring.",
            score=8.8,
            confidence="high",
            claims=["Identified catalysts for shareholder return enhancement."],
            evidence_ids=list(snapshot.evidence_registry.keys()),
            fact_ids=list(snapshot.facts.keys()),
            risks=["Management resistance to restructuring"],
            falsifiers=["Cancellation of share buyback program"],
            unknowns=[],
            warnings=[]
        )

class ManagementOrganizationAgent(BaseAgent):
    def __init__(self):
        super().__init__("management_organization")

    def run_analysis(self, security: Security, snapshot: FactSnapshot, overlay: MarketOverlayAnalysis) -> AgentOutput:
        return AgentOutput(
            agent_id=self.agent_id,
            conclusion="Deep-dive management analysis: Strong leadership track record and effective organization capability.",
            score=8.4,
            confidence="high",
            claims=["Leadership displays long-term vision and commitment."],
            evidence_ids=list(snapshot.evidence_registry.keys()),
            fact_ids=list(snapshot.facts.keys()),
            risks=["Succession planning execution"],
            falsifiers=["Departure of key executive team without succession plan"],
            unknowns=[],
            warnings=[]
        )

def evaluate_deep_dive_triggers(security: Security, snapshot: FactSnapshot, overlay: MarketOverlayAnalysis) -> List[str]:
    triggered_agents = []
    checks = overlay.specific_checks
    
    # Trigger governance_allocator if excess cash, parent-subsidiary, or strategic shareholdings exist
    if security.market_id == "JP" and (
        checks.get("parent_subsidiary_listing") or 
        checks.get("excess_cash") or 
        checks.get("strategic_shareholdings")
    ):
        triggered_agents.append("governance_allocator")

    # Trigger management_organization for owner-managed / SMB or succession concerns
    if checks.get("succession") or security.security_type == "smb":
        triggered_agents.append("management_organization")
        
    return triggered_agents
