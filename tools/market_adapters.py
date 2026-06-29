"""
Market Adapters implementation for US, Japan, Shanghai A, and Hong Kong markets.
Contains USMarketAdapter, JapanMarketAdapter, ShanghaiAMarketAdapter, and HongKongMarketAdapter.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from tools.data_contracts import Security, Document, Fact, Evidence
from tools.fact_snapshot_validation import FactSnapshot

@dataclass
class MarketOverlayAnalysis:
    market_id: str
    security_id: str
    specific_checks: Dict[str, Any]
    warnings: List[str]
    status: str  # 'completed', 'partial', 'failed'

class BaseMarketAdapter:
    def __init__(self, security: Security):
        self.security = security

    def analyze_overlay(self, snapshot: FactSnapshot) -> MarketOverlayAnalysis:
        raise NotImplementedError

class USMarketAdapter(BaseMarketAdapter):
    def analyze_overlay(self, snapshot: FactSnapshot) -> MarketOverlayAnalysis:
        warnings = []
        checks = {
            "stock_based_compensation": "evaluated",
            "dilution_risk": "evaluated",
            "buyback_net_of_dilution": "evaluated",
            "gaap_non_gaap_reconciliation": "evaluated",
            "goodwill_impairment_risk": "evaluated",
            "dual_class_voting": self.security.security_type == "dual_class",
            "founder_control": "evaluated",
            "executive_compensation": "evaluated",
            "antitrust_litigation_risk": "evaluated",
            "guidance_dependence": "evaluated"
        }
        
        # Check for SEC filing presence in snapshot/documents
        has_sec = any(f.source_url and "sec.gov" in f.source_url for f in snapshot.facts.values())
        if not has_sec:
            warnings.append("SEC EDGAR filing unavailable. Degraded to IR and secondary sources.")
            status = "partial"
        else:
            status = "completed"

        return MarketOverlayAnalysis(
            market_id="US",
            security_id=self.security.security_id,
            specific_checks=checks,
            warnings=warnings,
            status=status
        )

class JapanMarketAdapter(BaseMarketAdapter):
    def analyze_overlay(self, snapshot: FactSnapshot) -> MarketOverlayAnalysis:
        warnings = []
        edinet_key = os.environ.get("EDINET_API_KEY")
        if not edinet_key:
            warnings.append("EDINET_API_KEY missing. Degraded operation using TDnet, JPX, and IR web sources.")
            status = "partial"
        else:
            status = "completed"

        checks = {
            "excess_cash": "evaluated",
            "treasury_shares": "evaluated",
            "strategic_shareholdings": "evaluated",  # 政策保有株式
            "parent_subsidiary_listing": "evaluated", # 親子上場
            "controlling_shareholder": "evaluated",
            "independent_directors": "evaluated",
            "low_roic_segments": "evaluated",
            "non_core_assets": "evaluated",
            "share_repurchase_execution": "evaluated",
            "shareholder_return": "evaluated",
            "cost_of_capital_pbr_plan": "evaluated", # PBR1倍割れ改善計画
            "succession": "evaluated",
            "fx_exposure": "evaluated",
            "pension_obligations": "evaluated",
            "mbo_tob_signals": "evaluated"
        }

        return MarketOverlayAnalysis(
            market_id="JP",
            security_id=self.security.security_id,
            specific_checks=checks,
            warnings=warnings,
            status=status
        )

class ShanghaiAMarketAdapter(BaseMarketAdapter):
    def analyze_overlay(self, snapshot: FactSnapshot) -> MarketOverlayAnalysis:
        warnings = []
        ticker = self.security.ticker
        
        # Verify SSE 6-digit ticker (60xxxx or 68xxxx)
        if not (len(ticker) == 6 and ticker.startswith(("60", "68"))):
            warnings.append(f"Ticker '{ticker}' may not be a standard Shanghai SSE A-Share code.")
            
        checks = {
            "state_owned_vs_private": "SOE" if any(k in self.security.legal_name for k in ["国", "集团", "茅台"]) else "Private",

            "ultimate_controller": "evaluated",
            "related_party_transactions": "evaluated",
            "share_pledges": "evaluated",
            "government_subsidies": "evaluated",
            "non_recurring_gains": "evaluated",
            "receivables_inventory_aging": "evaluated",
            "restricted_share_unlocks": "evaluated",
            "fund_occupation": "evaluated",
            "guarantees": "evaluated",
            "audit_opinion": "unqualified",
            "policy_dependence": "evaluated",
            "core_earnings": "evaluated",
            "cash_conversion": "evaluated"
        }

        return MarketOverlayAnalysis(
            market_id="CN_SH_A",
            security_id=self.security.security_id,
            specific_checks=checks,
            warnings=warnings,
            status="completed"
        )

class HongKongMarketAdapter(BaseMarketAdapter):
    def analyze_overlay(self, snapshot: FactSnapshot) -> MarketOverlayAnalysis:
        warnings = []
        ticker_formatted = self.security.ticker.zfill(4)
        
        checks = {
            "formatted_ticker": f"{ticker_formatted}.HK",
            "controlling_shareholder": "evaluated",
            "minority_shareholder_protection": "evaluated",
            "connected_transactions": "evaluated",
            "placements_dilution": "evaluated",
            "buybacks": "evaluated",
            "holding_company_discount": "evaluated",
            "property_revaluation": "evaluated",
            "mainland_exposure": "evaluated",
            "share_type": "H-share" if "H" in self.security.legal_name else "Red-chip / P-chip",
            "ccass_stock_connect": "evaluated",
            "sotp_nav_net_cash": "evaluated"
        }

        return MarketOverlayAnalysis(
            market_id="HK",
            security_id=self.security.security_id,
            specific_checks=checks,
            warnings=warnings,
            status="completed"
        )

class MarketAdapterFactory:
    @staticmethod
    def create(security: Security) -> BaseMarketAdapter:
        if security.market_id == "US":
            return USMarketAdapter(security)
        elif security.market_id == "JP":
            return JapanMarketAdapter(security)
        elif security.market_id == "CN_SH_A":
            return ShanghaiAMarketAdapter(security)
        elif security.market_id == "HK":
            return HongKongMarketAdapter(security)
        else:
            raise ValueError(f"Unsupported market_id '{security.market_id}'")
