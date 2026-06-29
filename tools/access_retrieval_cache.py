"""
Access Policy, Retrieval, and Cache layer for Global Market Adaptation.
Implements domain rate limiting, backoff, HTTP status handling, cache-first storage, secret redaction, and uniform Document output.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from tools.data_contracts import Document, SourceType

class AccessPolicyViolation(Exception):
    pass

class RateLimiter:
    def __init__(self, min_interval: float = 0.1, max_concurrent: int = 1):
        self.min_interval = min_interval
        self.max_concurrent = max_concurrent
        self.last_access_times: Dict[str, float] = {}
        self.domain_locks: Dict[str, int] = {}
        self.repeated_429_count: Dict[str, int] = {}

    def can_access(self, domain: str) -> bool:
        if self.repeated_429_count.get(domain, 0) >= 3:
            return False
        return True

    def record_access(self, domain: str) -> None:
        now = time.time()
        last = self.last_access_times.get(domain, 0.0)
        elapsed = now - last
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_access_times[domain] = time.time()

    def record_429(self, domain: str) -> None:
        self.repeated_429_count[domain] = self.repeated_429_count.get(domain, 0) + 1

    def reset_429(self, domain: str) -> None:
        self.repeated_429_count[domain] = 0

def redact_secrets(text: str) -> str:
    if not text:
        return text
    edinet_key = os.environ.get("EDINET_API_KEY")
    if edinet_key and len(edinet_key) > 4:
        text = text.replace(edinet_key, "[REDACTED_API_KEY]")
    text = re.sub(r"(Bearer\s+)[^\s\n;,]+", r"\1[REDACTED_SECRET]", text, flags=re.IGNORECASE)
    text = re.sub(r"(Authorization:\s*)[^\s\n;,]+", r"\1[REDACTED_SECRET]", text, flags=re.IGNORECASE)
    text = re.sub(r"(Cookie:\s*)[^\s\n;,]+", r"\1[REDACTED_SECRET]", text, flags=re.IGNORECASE)
    return text


class CacheManager:
    def __init__(self, cache_dir: Optional[Path] = None, enabled: bool = True):
        self.enabled = enabled and (os.environ.get("AI_BERKSHIRE_CACHE_ENABLED", "true").lower() == "true")
        self.cache_dir = cache_dir or Path(os.environ.get("AI_BERKSHIRE_CACHE_DIR", "./data/cache"))

    def _get_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return self.cache_dir / hashed[:2] / f"{hashed}.json"

    def get(self, key: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        if not self.enabled:
            return None
        path = self._get_path(key)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data["content"], data["meta"]
        except Exception:
            # Corrupted cache handling
            return None

    def put(self, key: str, content: str, meta: Dict[str, Any]) -> str:
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if not self.enabled:
            return content_hash
        path = self._get_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        meta_clean = {k: redact_secrets(str(v)) if isinstance(v, str) else v for k, v in meta.items()}
        data = {
            "key": key,
            "content_hash": content_hash,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "meta": meta_clean,
            "content": content
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return content_hash

class DocumentRetriever:
    def __init__(self, cache_manager: Optional[CacheManager] = None, rate_limiter: Optional[RateLimiter] = None):
        self.cache = cache_manager or CacheManager()
        self.limiter = rate_limiter or RateLimiter()

    def fetch_document(
        self,
        security_id: str,
        document_id: str,
        document_type: str,
        title: str,
        source_name: str,
        source_url: str,
        mock_http_response: Optional[Dict[str, Any]] = None,
        language: str = "en",
        is_official: bool = True
    ) -> Tuple[Document, str]:
        
        domain = source_url.split("//")[-1].split("/")[0]
        
        if not self.limiter.can_access(domain):
            raise AccessPolicyViolation(f"Access to domain '{domain}' blocked due to repeated 429 / 403 policy.")

        # Cache-first check
        cached = self.cache.get(source_url)
        if cached:
            content, meta = cached
            doc = Document(
                document_id=document_id,
                security_id=security_id,
                document_type=document_type,
                title=title,
                published_at=meta.get("published_at"),
                retrieved_at=meta.get("retrieved_at", datetime.now(timezone.utc).isoformat()),
                source_name=source_name,
                source_type=SourceType.OFFICIAL.value if is_official else SourceType.SECONDARY.value,
                source_url=source_url,
                local_cache_path=meta.get("local_cache_path"),
                content_hash=meta.get("content_hash"),
                language=language,
                is_official=is_official
            )
            return doc, content

        # Simulate network retrieval / mock HTTP response handling
        resp = mock_http_response or {"status": 200, "content": f"Sample document content for {title}"}
        status = resp.get("status", 200)

        if status == 403:
            self.limiter.record_429(domain) # block domain
            raise AccessPolicyViolation(f"HTTP 403 Forbidden for URL: {redact_secrets(source_url)}")
        elif status == 429:
            self.limiter.record_429(domain)
            retry_after = resp.get("retry_after", 5)
            raise AccessPolicyViolation(f"HTTP 429 Too Many Requests. Retry-After: {retry_after}s")
        elif status == 503:
            raise AccessPolicyViolation(f"HTTP 503 Service Unavailable for URL: {redact_secrets(source_url)}")

        self.limiter.record_access(domain)
        self.limiter.reset_429(domain)
        
        content = resp.get("content", "")
        now_iso = datetime.now(timezone.utc).isoformat()
        content_hash = self.cache.put(source_url, content, {
            "retrieved_at": now_iso,
            "published_at": resp.get("published_at", now_iso)
        })

        doc = Document(
            document_id=document_id,
            security_id=security_id,
            document_type=document_type,
            title=title,
            published_at=resp.get("published_at", now_iso),
            retrieved_at=now_iso,
            source_name=source_name,
            source_type=SourceType.OFFICIAL.value if is_official else SourceType.SECONDARY.value,
            source_url=redact_secrets(source_url),
            local_cache_path=str(self.cache._get_path(source_url)) if self.cache.enabled else None,
            content_hash=content_hash,
            language=language,
            is_official=is_official
        )
        return doc, content
