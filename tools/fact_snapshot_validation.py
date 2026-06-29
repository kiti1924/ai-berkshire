"""
Fact Snapshot and Financial Validation for Global Market Adaptation.
Implements shared FactSnapshot, source conflict resolution, Evidence-on-use, and exact Decimal arithmetic for key metrics.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Set, Tuple
from tools.data_contracts import Fact, Evidence

class FinancialValidationCalculator:
    @staticmethod
    def to_decimal(val: Any) -> Optional[Decimal]:
        if val is None:
            return None
        try:
            return Decimal(str(val))
        except (InvalidOperation, ValueError):
            return None

    @classmethod
    def calculate_market_cap(cls, share_price: Any, shares_outstanding: Any) -> Optional[Decimal]:
        p = cls.to_decimal(share_price)
        s = cls.to_decimal(shares_outstanding)
        if p is None or s is None or s <= 0:
            return None
        return p * s

    @classmethod
    def calculate_net_cash(cls, cash_and_equivalents: Any, total_debt: Any) -> Optional[Decimal]:
        c = cls.to_decimal(cash_and_equivalents)
        d = cls.to_decimal(total_debt)
        if c is None or d is None:
            return None
        return c - d

    @classmethod
    def calculate_enterprise_value(cls, market_cap: Any, total_debt: Any, cash_and_equivalents: Any) -> Optional[Decimal]:
        mc = cls.to_decimal(market_cap)
        d = cls.to_decimal(total_debt)
        c = cls.to_decimal(cash_and_equivalents)
        if mc is None or d is None or c is None:
            return None
        return mc + d - c

    @classmethod
    def calculate_per(cls, share_price: Any, eps: Any) -> Optional[Decimal]:
        p = cls.to_decimal(share_price)
        e = cls.to_decimal(eps)
        if p is None or e is None or e == 0:
            return None
        return p / e

    @classmethod
    def calculate_pbr(cls, share_price: Any, bps: Any) -> Optional[Decimal]:
        p = cls.to_decimal(share_price)
        b = cls.to_decimal(bps)
        if p is None or b is None or b == 0:
            return None
        return p / b

    @classmethod
    def calculate_roe(cls, net_income: Any, total_equity: Any) -> Optional[Decimal]:
        ni = cls.to_decimal(net_income)
        eq = cls.to_decimal(total_equity)
        if ni is None or eq is None or eq == 0:
            return None
        return ni / eq

    @classmethod
    def calculate_fcf(cls, operating_cf: Any, capex: Any) -> Optional[Decimal]:
        ocf = cls.to_decimal(operating_cf)
        cap = cls.to_decimal(capex)
        if ocf is None or cap is None:
            return None
        return ocf - cap

    @classmethod
    def calculate_fcf_yield(cls, fcf: Any, market_cap: Any) -> Optional[Decimal]:
        f = cls.to_decimal(fcf)
        mc = cls.to_decimal(market_cap)
        if f is None or mc is None or mc <= 0:
            return None
        return f / mc

    @classmethod
    def calculate_shareholder_yield(cls, dividends: Any, buybacks: Any, market_cap: Any) -> Optional[Decimal]:
        div = cls.to_decimal(dividends) or Decimal("0")
        bb = cls.to_decimal(buybacks) or Decimal("0")
        mc = cls.to_decimal(market_cap)
        if mc is None or mc <= 0:
            return None
        return (div + bb) / mc

class FactSnapshot:
    def __init__(self, security_id: str):
        self.security_id = security_id
        self.facts: Dict[str, Fact] = {}  # keyed by metric
        self.evidence_registry: Dict[str, Evidence] = {}

    def add_fact(self, fact: Fact) -> None:
        if fact.security_id != self.security_id:
            raise ValueError(f"Fact security_id '{fact.security_id}' does not match snapshot '{self.security_id}'")
        
        existing = self.facts.get(fact.metric)
        if existing is None:
            self.facts[fact.metric] = fact
        else:
            # Source rank conflict resolution
            if fact.source_rank > existing.source_rank:
                self.facts[fact.metric] = fact
            elif fact.source_rank == existing.source_rank:
                # Deterministic selection or latest timestamp
                if fact.retrieved_at >= existing.retrieved_at:
                    self.facts[fact.metric] = fact

    def get_fact(self, metric: str) -> Optional[Fact]:
        return self.facts.get(metric)

    def register_evidence(self, evidence: Evidence) -> None:
        self.evidence_registry[evidence.evidence_id] = evidence

    def compute_derived_metrics(self) -> Dict[str, Optional[str]]:
        # Compute financial metrics dynamically and return formatted string representations
        results: Dict[str, Optional[str]] = {}
        
        price_fact = self.get_fact("share_price")
        shares_fact = self.get_fact("shares_outstanding")
        
        mcap = FinancialValidationCalculator.calculate_market_cap(
            price_fact.value if price_fact else None,
            shares_fact.value if shares_fact else None
        )
        results["market_cap"] = str(mcap) if mcap is not None else None
        
        debt_fact = self.get_fact("total_debt")
        cash_fact = self.get_fact("cash_and_equivalents")
        
        net_cash = FinancialValidationCalculator.calculate_net_cash(
            cash_fact.value if cash_fact else None,
            debt_fact.value if debt_fact else None
        )
        results["net_cash"] = str(net_cash) if net_cash is not None else None

        ev = FinancialValidationCalculator.calculate_enterprise_value(
            mcap, debt_fact.value if debt_fact else None, cash_fact.value if cash_fact else None
        )
        results["enterprise_value"] = str(ev) if ev is not None else None

        eps_fact = self.get_fact("eps")
        per = FinancialValidationCalculator.calculate_per(price_fact.value if price_fact else None, eps_fact.value if eps_fact else None)
        results["per"] = str(per) if per is not None else None

        return results
