"""
Canonical Data Contracts implementation for Global Market Adaptation.
Provides dataclasses, enum validation, timezone-aware datetime validation, and deterministic JSON serialization.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

class MarketID(str, Enum):
    US = "US"
    JP = "JP"
    CN_SH_A = "CN_SH_A"
    HK = "HK"

class SourceType(str, Enum):
    OFFICIAL = "official"
    SECONDARY = "secondary"
    WEB = "web"

class Consolidation(str, Enum):
    CONSOLIDATED = "consolidated"
    STANDALONE = "standalone"
    UNKNOWN = "unknown"

class FactType(str, Enum):
    REPORTED = "reported"
    FORECAST = "forecast"
    ESTIMATE = "estimate"
    NORMALIZED = "normalized"

class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    SINGLE_SOURCE = "single_source"
    CROSS_CHECKED = "cross_checked"
    OFFICIAL = "official"

class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RunMode(str, Enum):
    ON_DEMAND = "on_demand"
    ON_DEMAND_CACHED = "on_demand_cached"

class RunStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"

def validate_iso_datetime(dt_str: Optional[str]) -> Optional[str]:
    if dt_str is None:
        return None
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError(f"Naive datetime rejected: {dt_str}. Timezone offset is required.")
    except Exception as e:
        raise ValueError(f"Invalid timezone-aware ISO datetime '{dt_str}': {e}")
    return dt_str

@dataclass
class SecurityIdentifiers:
    cik: Optional[str] = None
    edinet_code: Optional[str] = None
    isin: Optional[str] = None
    exchange_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cik": self.cik,
            "edinet_code": self.edinet_code,
            "isin": self.isin,
            "exchange_code": self.exchange_code
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SecurityIdentifiers:
        allowed = {"cik", "edinet_code", "isin", "exchange_code"}
        unknown = set(data.keys()) - allowed
        if unknown:
            raise ValueError(f"Unknown fields in SecurityIdentifiers: {unknown}")
        return cls(**data)

@dataclass
class Security:
    security_id: str
    issuer_id: str
    market_id: str
    ticker: str
    exchange: str
    legal_name: str
    display_name: str
    security_type: str
    trading_currency: str
    reporting_currency: str
    primary_listing: bool
    identifiers: SecurityIdentifiers

    def __post_init__(self):
        self.market_id = MarketID(self.market_id).value
        if isinstance(self.identifiers, dict):
            self.identifiers = SecurityIdentifiers.from_dict(self.identifiers)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "security_id": self.security_id,
            "issuer_id": self.issuer_id,
            "market_id": self.market_id,
            "ticker": self.ticker,
            "exchange": self.exchange,
            "legal_name": self.legal_name,
            "display_name": self.display_name,
            "security_type": self.security_type,
            "trading_currency": self.trading_currency,
            "reporting_currency": self.reporting_currency,
            "primary_listing": self.primary_listing,
            "identifiers": self.identifiers.to_dict()
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Security:
        allowed = {
            "security_id", "issuer_id", "market_id", "ticker", "exchange",
            "legal_name", "display_name", "security_type", "trading_currency",
            "reporting_currency", "primary_listing", "identifiers"
        }
        unknown = set(data.keys()) - allowed
        if unknown:
            raise ValueError(f"Unknown fields in Security: {unknown}")
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> Security:
        return cls.from_dict(json.loads(json_str))

@dataclass
class Document:
    document_id: str
    security_id: str
    document_type: str
    title: str
    retrieved_at: str
    source_name: str
    source_type: str
    source_url: str
    language: str
    is_official: bool
    published_at: Optional[str] = None
    local_cache_path: Optional[str] = None
    content_hash: Optional[str] = None
    supersedes_document_id: Optional[str] = None

    def __post_init__(self):
        self.source_type = SourceType(self.source_type).value
        self.retrieved_at = validate_iso_datetime(self.retrieved_at)
        if self.published_at is not None:
            self.published_at = validate_iso_datetime(self.published_at)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "security_id": self.security_id,
            "document_type": self.document_type,
            "title": self.title,
            "published_at": self.published_at,
            "retrieved_at": self.retrieved_at,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "local_cache_path": self.local_cache_path,
            "content_hash": self.content_hash,
            "language": self.language,
            "is_official": self.is_official,
            "supersedes_document_id": self.supersedes_document_id
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Document:
        allowed = {
            "document_id", "security_id", "document_type", "title", "published_at",
            "retrieved_at", "source_name", "source_type", "source_url",
            "local_cache_path", "content_hash", "language", "is_official",
            "supersedes_document_id"
        }
        unknown = set(data.keys()) - allowed
        if unknown:
            raise ValueError(f"Unknown fields in Document: {unknown}")
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> Document:
        return cls.from_dict(json.loads(json_str))

@dataclass
class Fact:
    fact_id: str
    security_id: str
    metric: str
    value: Union[float, int, str, bool]
    retrieved_at: str
    source_url: str
    source_rank: int
    consolidation: str
    fact_type: str
    verification_status: str
    unit: Optional[str] = None
    currency: Optional[str] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    as_of: Optional[str] = None
    source_document_id: Optional[str] = None
    accounting_standard: Optional[str] = None

    def __post_init__(self):
        self.consolidation = Consolidation(self.consolidation).value
        self.fact_type = FactType(self.fact_type).value
        self.verification_status = VerificationStatus(self.verification_status).value
        self.retrieved_at = validate_iso_datetime(self.retrieved_at)
        if self.as_of is not None:
            self.as_of = validate_iso_datetime(self.as_of)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "security_id": self.security_id,
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "currency": self.currency,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "as_of": self.as_of,
            "retrieved_at": self.retrieved_at,
            "source_document_id": self.source_document_id,
            "source_url": self.source_url,
            "source_rank": self.source_rank,
            "accounting_standard": self.accounting_standard,
            "consolidation": self.consolidation,
            "fact_type": self.fact_type,
            "verification_status": self.verification_status
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Fact:
        allowed = {
            "fact_id", "security_id", "metric", "value", "unit", "currency",
            "period_start", "period_end", "as_of", "retrieved_at",
            "source_document_id", "source_url", "source_rank",
            "accounting_standard", "consolidation", "fact_type", "verification_status"
        }
        unknown = set(data.keys()) - allowed
        if unknown:
            raise ValueError(f"Unknown fields in Fact: {unknown}")
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> Fact:
        return cls.from_dict(json.loads(json_str))

@dataclass
class Evidence:
    evidence_id: str
    claim_id: str
    statement: str
    source_url: str
    source_rank: int
    retrieved_at: str
    supports_claim: bool
    confidence: str
    source_document_id: Optional[str] = None
    published_at: Optional[str] = None

    def __post_init__(self):
        self.confidence = Confidence(self.confidence).value
        self.retrieved_at = validate_iso_datetime(self.retrieved_at)
        if self.published_at is not None:
            self.published_at = validate_iso_datetime(self.published_at)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "claim_id": self.claim_id,
            "statement": self.statement,
            "source_document_id": self.source_document_id,
            "source_url": self.source_url,
            "source_rank": self.source_rank,
            "published_at": self.published_at,
            "retrieved_at": self.retrieved_at,
            "supports_claim": self.supports_claim,
            "confidence": self.confidence
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Evidence:
        allowed = {
            "evidence_id", "claim_id", "statement", "source_document_id",
            "source_url", "source_rank", "published_at", "retrieved_at",
            "supports_claim", "confidence"
        }
        unknown = set(data.keys()) - allowed
        if unknown:
            raise ValueError(f"Unknown fields in Evidence: {unknown}")
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> Evidence:
        return cls.from_dict(json.loads(json_str))

@dataclass
class ResearchRun:
    run_id: str
    started_at: str
    query: str
    resolved_security_id: str
    market_id: str
    mode: str
    as_of: str
    skill: str
    documents_used: List[str]
    facts_used: List[str]
    warnings: List[str]
    status: str
    completed_at: Optional[str] = None

    def __post_init__(self):
        self.market_id = MarketID(self.market_id).value
        self.mode = RunMode(self.mode).value
        self.status = RunStatus(self.status).value
        self.started_at = validate_iso_datetime(self.started_at)
        self.as_of = validate_iso_datetime(self.as_of)
        if self.completed_at is not None:
            self.completed_at = validate_iso_datetime(self.completed_at)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "query": self.query,
            "resolved_security_id": self.resolved_security_id,
            "market_id": self.market_id,
            "mode": self.mode,
            "as_of": self.as_of,
            "skill": self.skill,
            "documents_used": list(self.documents_used),
            "facts_used": list(self.facts_used),
            "warnings": list(self.warnings),
            "status": self.status
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ResearchRun:
        allowed = {
            "run_id", "started_at", "completed_at", "query", "resolved_security_id",
            "market_id", "mode", "as_of", "skill", "documents_used",
            "facts_used", "warnings", "status"
        }
        unknown = set(data.keys()) - allowed
        if unknown:
            raise ValueError(f"Unknown fields in ResearchRun: {unknown}")
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> ResearchRun:
        return cls.from_dict(json.loads(json_str))
