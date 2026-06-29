"""
Security Resolver and Market Router for Global Market Adaptation.
Resolves company names, tickers, and codes across US, JP, CN_SH_A, and HK markets.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from tools.data_contracts import Security, SecurityIdentifiers, MarketID

OUT_OF_SCOPE_TYPES = {"etf", "etn", "reit", "bank", "insurance", "spac", "bond", "option", "future"}

@dataclass
class ResolutionCandidate:
    security: Security
    confidence: float  # 0.0 to 1.0
    reasoning: str
    is_supported: bool = True
    out_of_scope_reason: Optional[str] = None

@dataclass
class ResolutionResult:
    query: str
    resolved_security: Optional[Security]
    candidates: List[ResolutionCandidate]
    is_ambiguous: bool
    status: str  # 'resolved', 'ambiguous', 'out_of_scope', 'not_found'

class MarketRouter:
    @staticmethod
    def route(security: Security) -> str:
        return security.market_id

class SecurityResolver:
    def __init__(self):
        # Mock database of supported representative securities for resolution
        self.registry: List[Security] = [
            Security(
                security_id="US:AAPL",
                issuer_id="US:CIK0000320193",
                market_id="US",
                ticker="AAPL",
                exchange="NASDAQ",
                legal_name="Apple Inc.",
                display_name="Apple",
                security_type="equity",
                trading_currency="USD",
                reporting_currency="USD",
                primary_listing=True,
                identifiers=SecurityIdentifiers(cik="0000320193")
            ),
            Security(
                security_id="JP:7203",
                issuer_id="JP:EDINET_E02144",
                market_id="JP",
                ticker="7203",
                exchange="TSE",
                legal_name="トヨタ自動車株式会社",
                display_name="トヨタ自動車",
                security_type="equity",
                trading_currency="JPY",
                reporting_currency="JPY",
                primary_listing=True,
                identifiers=SecurityIdentifiers(edinet_code="E02144", exchange_code="7203.T")
            ),
            Security(
                security_id="CN_SH_A:600519",
                issuer_id="CN:600519",
                market_id="CN_SH_A",
                ticker="600519",
                exchange="SSE",
                legal_name="贵州茅台酒股份有限公司",
                display_name="贵州茅台",
                security_type="equity",
                trading_currency="CNY",
                reporting_currency="CNY",
                primary_listing=True,
                identifiers=SecurityIdentifiers(exchange_code="600519.SS")
            ),
            Security(
                security_id="HK:0700",
                issuer_id="HK:0700",
                market_id="HK",
                ticker="0700",
                exchange="HKEX",
                legal_name="Tencent Holdings Limited",
                display_name="騰訊控股 / Tencent",
                security_type="equity",
                trading_currency="HKD",
                reporting_currency="RMB",
                primary_listing=True,
                identifiers=SecurityIdentifiers(exchange_code="0700.HK")
            ),
            # ADR vs Hong Kong native shares test cases
            Security(
                security_id="US:BABA",
                issuer_id="GLOBAL:ALIBABA",
                market_id="US",
                ticker="BABA",
                exchange="NYSE",
                legal_name="Alibaba Group Holding Limited (ADR)",
                display_name="Alibaba ADR",
                security_type="adr",
                trading_currency="USD",
                reporting_currency="RMB",
                primary_listing=True,
                identifiers=SecurityIdentifiers()
            ),
            Security(
                security_id="HK:9988",
                issuer_id="GLOBAL:ALIBABA",
                market_id="HK",
                ticker="9988",
                exchange="HKEX",
                legal_name="Alibaba Group Holding Limited",
                display_name="Alibaba HK",
                security_type="equity",
                trading_currency="HKD",
                reporting_currency="RMB",
                primary_listing=False,
                identifiers=SecurityIdentifiers(exchange_code="9988.HK")
            ),
            # Out of scope security
            Security(
                security_id="US:SPY",
                issuer_id="US:SPY",
                market_id="US",
                ticker="SPY",
                exchange="NYSEARCA",
                legal_name="SPDR S&P 500 ETF Trust",
                display_name="SPY ETF",
                security_type="etf",
                trading_currency="USD",
                reporting_currency="USD",
                primary_listing=True,
                identifiers=SecurityIdentifiers()
            )
        ]

    def normalize_input(self, text: str) -> str:
        # Convert full-width ASCII to half-width and strip whitespace
        normalized = unicodedata.normalize("NFKC", text).strip()
        return normalized

    def resolve(self, query: str) -> ResolutionResult:
        raw_query = query
        norm_query = self.normalize_input(query).upper()
        
        candidates: List[ResolutionCandidate] = []
        
        # 1. Exact ticker match or exchange code match
        for sec in self.registry:
            ex_code = (sec.identifiers.exchange_code or "").upper()
            sec_ticker = sec.ticker.upper()
            
            # Match rules
            if norm_query == sec.security_id.upper():
                candidates.append(ResolutionCandidate(sec, 1.0, f"Exact security_id match '{sec.security_id}'"))
            elif norm_query == ex_code:
                candidates.append(ResolutionCandidate(sec, 0.98, f"Exact exchange code match '{ex_code}'"))
            elif norm_query == sec_ticker:
                candidates.append(ResolutionCandidate(sec, 0.95, f"Exact ticker match '{sec_ticker}'"))
            elif norm_query.isdigit() and len(norm_query) <= 4 and sec.market_id == "HK" and norm_query.zfill(4) == sec_ticker:
                candidates.append(ResolutionCandidate(sec, 0.90, f"Leading zero expanded HK ticker match '{norm_query.zfill(4)}'"))
            elif norm_query in sec.legal_name.upper() or norm_query in sec.display_name.upper() or raw_query in sec.legal_name or raw_query in sec.display_name:
                candidates.append(ResolutionCandidate(sec, 0.85, f"Name match in '{sec.legal_name}'"))

        # Sort candidates deterministically by confidence descending, then security_id ascending
        candidates.sort(key=lambda c: (-c.confidence, c.security.security_id))

        if not candidates:
            # Dynamically construct fallback resolution for standard ticker formats if unknown
            if re.match(r"^\d{4}$", norm_query): # Japanese 4-digit code
                sec = Security(
                    security_id=f"JP:{norm_query}", issuer_id=f"JP:{norm_query}", market_id="JP",
                    ticker=norm_query, exchange="TSE", legal_name=f"Company {norm_query}",
                    display_name=f"Company {norm_query}", security_type="equity", trading_currency="JPY",
                    reporting_currency="JPY", primary_listing=True, identifiers=SecurityIdentifiers(exchange_code=f"{norm_query}.T")
                )
                return ResolutionResult(query, sec, [ResolutionCandidate(sec, 0.8, "Inferred JP 4-digit code")], False, "resolved")
            elif re.match(r"^\d{6}$", norm_query) and norm_query.startswith(("60", "68")): # Shanghai A
                sec = Security(
                    security_id=f"CN_SH_A:{norm_query}", issuer_id=f"CN:{norm_query}", market_id="CN_SH_A",
                    ticker=norm_query, exchange="SSE", legal_name=f"A-Share {norm_query}",
                    display_name=f"A-Share {norm_query}", security_type="equity", trading_currency="CNY",
                    reporting_currency="CNY", primary_listing=True, identifiers=SecurityIdentifiers(exchange_code=f"{norm_query}.SS")
                )
                return ResolutionResult(query, sec, [ResolutionCandidate(sec, 0.8, "Inferred Shanghai A 6-digit code")], False, "resolved")
            elif norm_query.endswith(".HK") or (norm_query.isdigit() and len(norm_query) == 4):
                clean_code = norm_query.replace(".HK", "").zfill(4)
                sec = Security(
                    security_id=f"HK:{clean_code}", issuer_id=f"HK:{clean_code}", market_id="HK",
                    ticker=clean_code, exchange="HKEX", legal_name=f"HK Company {clean_code}",
                    display_name=f"HK Company {clean_code}", security_type="equity", trading_currency="HKD",
                    reporting_currency="CNY", primary_listing=True, identifiers=SecurityIdentifiers(exchange_code=f"{clean_code}.HK")
                )
                return ResolutionResult(query, sec, [ResolutionCandidate(sec, 0.8, "Inferred HK code")], False, "resolved")
            elif re.match(r"^[A-Z]{1,5}$", norm_query):
                sec = Security(
                    security_id=f"US:{norm_query}", issuer_id=f"US:{norm_query}", market_id="US",
                    ticker=norm_query, exchange="NASDAQ", legal_name=f"US Corporation {norm_query}",
                    display_name=norm_query, security_type="equity", trading_currency="USD",
                    reporting_currency="USD", primary_listing=True, identifiers=SecurityIdentifiers()
                )
                return ResolutionResult(query, sec, [ResolutionCandidate(sec, 0.8, "Inferred US ticker")], False, "resolved")

            return ResolutionResult(query, None, [], False, "not_found")

        # Check out of scope for top candidate
        top = candidates[0]
        if top.security.security_type in OUT_OF_SCOPE_TYPES:
            top.is_supported = False
            top.out_of_scope_reason = f"Security type '{top.security.security_type}' is out of initial scope"
            return ResolutionResult(query, top.security, candidates, False, "out_of_scope")

        # Ambiguity check
        if len(candidates) > 1 and abs(candidates[0].confidence - candidates[1].confidence) < 0.05:
            return ResolutionResult(query, None, candidates, True, "ambiguous")

        return ResolutionResult(query, top.security, candidates, False, "resolved")
