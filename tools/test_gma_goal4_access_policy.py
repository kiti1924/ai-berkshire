#!/usr/bin/env python3
"""
Test suite for Goal 4: Access policy, retrieval, and cache.
"""

import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.access_retrieval_cache import (
    AccessPolicyViolation, CacheManager, DocumentRetriever, RateLimiter, redact_secrets
)

def test_cache_hit_miss():
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = CacheManager(cache_dir=Path(tmp_dir), enabled=True)
        retriever = DocumentRetriever(cache_manager=cache)
        
        # Miss
        doc1, content1 = retriever.fetch_document(
            "US:AAPL", "doc_01", "10-K", "Annual Report", "SEC", "https://sec.gov/filing1",
            mock_http_response={"status": 200, "content": "Fresh Content 1"}
        )
        assert content1 == "Fresh Content 1"
        
        # Hit
        doc2, content2 = retriever.fetch_document(
            "US:AAPL", "doc_01", "10-K", "Annual Report", "SEC", "https://sec.gov/filing1",
            mock_http_response={"status": 200, "content": "Stale Content 2"}
        )
        assert content2 == "Fresh Content 1" # Cached content returned!

def test_cache_disabled():
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = CacheManager(cache_dir=Path(tmp_dir), enabled=False)
        retriever = DocumentRetriever(cache_manager=cache)
        
        doc1, content1 = retriever.fetch_document(
            "US:AAPL", "doc_01", "10-K", "Report", "SEC", "https://sec.gov/f1",
            mock_http_response={"status": 200, "content": "Content A"}
        )
        doc2, content2 = retriever.fetch_document(
            "US:AAPL", "doc_01", "10-K", "Report", "SEC", "https://sec.gov/f1",
            mock_http_response={"status": 200, "content": "Content B"}
        )
        assert content2 == "Content B" # Fresh fetch since cache is disabled

def test_http_status_403_and_429_policy():
    limiter = RateLimiter(min_interval=0.01)
    retriever = DocumentRetriever(rate_limiter=limiter)
    
    # 403 test
    try:
        retriever.fetch_document(
            "JP:7203", "doc_403", "IR", "Forbidden IR", "IR", "https://forbidden-site.com/doc",
            mock_http_response={"status": 403}
        )
        assert False, "Should have raised AccessPolicyViolation on 403"
    except AccessPolicyViolation as e:
        assert "403 Forbidden" in str(e)

    # Repeated 429 blocking
    domain = "blocked-domain.com"
    url = f"https://{domain}/doc"
    for _ in range(3):
        try:
            retriever.fetch_document("JP:7203", "doc", "IR", "T", "IR", url, mock_http_response={"status": 429, "retry_after": 2})
        except AccessPolicyViolation:
            pass

    # Next attempt should be blocked before making request
    try:
        retriever.fetch_document("JP:7203", "doc", "IR", "T", "IR", url, mock_http_response={"status": 200, "content": "OK"})
        assert False, "Should block access to domain after repeated 429"
    except AccessPolicyViolation as e:
        assert "blocked due to repeated 429" in str(e)

def test_secret_redaction():
    os.environ["EDINET_API_KEY"] = "SECRET_EDINET_KEY_12345"
    raw = "Fetching with EDINET_API_KEY=SECRET_EDINET_KEY_12345 and Authorization: Bearer secret_token_abc"
    clean = redact_secrets(raw)
    assert "SECRET_EDINET_KEY_12345" not in clean
    assert "secret_token_abc" not in clean
    assert "[REDACTED_API_KEY]" in clean

def test_corrupted_cache_fallback():
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = CacheManager(cache_dir=Path(tmp_dir), enabled=True)
        url = "https://sec.gov/corrupted"
        cache.put(url, "Valid initially", {})
        
        # Corrupt file on disk
        path = cache._get_path(url)
        with open(path, "w", encoding="utf-8") as f:
            f.write("{{INVALID_JSON}}")
            
        # Retrieval should handle corruption gracefully and treat as cache miss
        cached = cache.get(url)
        assert cached is None

def main():
    print("Running Goal 4 Access Policy tests...")
    test_cache_hit_miss()
    test_cache_disabled()
    test_http_status_403_and_429_policy()
    test_secret_redaction()
    test_corrupted_cache_fallback()
    print("Goal 4 Access Policy tests passed successfully!")

if __name__ == "__main__":
    main()
