"""
Reports and Audit implementation for Global Market Adaptation.
Handles report generation, detailed artifact bundle creation, secret scanning, and multi-market report auditing.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from tools.data_contracts import Security, ResearchRun, Fact, Evidence, Document
from tools.access_retrieval_cache import redact_secrets

class ReportGenerator:
    def __init__(self, output_base_dir: Optional[Path] = None):
        self.base_dir = output_base_dir or Path(os.environ.get("AI_BERKSHIRE_REPORT_DIR", "./reports"))

    def _slugify(self, text: str) -> str:
        text = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "-", text) or "issuer"

    def generate_report_bundle(
        self,
        security: Security,
        run: ResearchRun,
        facts: List[Fact],
        evidence_list: List[Evidence],
        documents: List[Document],
        agent_outputs: List[Dict[str, Any]],
        detailed: bool = True
    ) -> Dict[str, Path]:
        
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        issuer_slug = self._slugify(security.display_name)
        folder_name = f"{security.ticker}-{issuer_slug}"
        
        market_dir = self.base_dir / security.market_id / folder_name
        market_dir.mkdir(parents=True, exist_ok=True)

        standard_report_path = market_dir / f"{date_str}-{run.skill}.md"

        # Construct markdown report
        md_content = self._build_markdown_content(security, run, facts, evidence_list, agent_outputs)
        md_clean = redact_secrets(md_content)
        
        # Strip local absolute username paths from user report
        home_str = os.path.expanduser("~")
        if home_str in md_clean:
            md_clean = md_clean.replace(home_str, "~")

        with open(standard_report_path, "w", encoding="utf-8") as f:
            f.write(md_clean)

        created_files = {"standard_report": standard_report_path}

        if detailed:
            run_dir = market_dir / run.run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            
            detailed_report_path = run_dir / "report.md"
            with open(detailed_report_path, "w", encoding="utf-8") as f:
                f.write(md_clean)
            created_files["detailed_report"] = detailed_report_path

            facts_path = run_dir / "facts.json"
            with open(facts_path, "w", encoding="utf-8") as f:
                json.dump([f.to_dict() for f in facts], f, indent=2, ensure_ascii=False)
            created_files["facts"] = facts_path

            evidence_path = run_dir / "evidence.json"
            with open(evidence_path, "w", encoding="utf-8") as f:
                json.dump([e.to_dict() for e in evidence_list], f, indent=2, ensure_ascii=False)
            created_files["evidence"] = evidence_path

            docs_path = run_dir / "documents.json"
            with open(docs_path, "w", encoding="utf-8") as f:
                json.dump([d.to_dict() for d in documents], f, indent=2, ensure_ascii=False)
            created_files["documents"] = docs_path

            manifest_path = run_dir / "run-manifest.json"
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(run.to_dict(), f, indent=2, ensure_ascii=False)
            created_files["manifest"] = manifest_path

        return created_files

    def _build_markdown_content(
        self,
        security: Security,
        run: ResearchRun,
        facts: List[Fact],
        evidence_list: List[Evidence],
        agent_outputs: List[Dict[str, Any]]
    ) -> str:
        lines = [
            f"# 投资研究报告: {security.display_name} ({security.ticker})",
            "",
            "## 1. 元数据 (Metadata)",
            f"- **Target Security**: {security.security_id} ({security.legal_name})",
            f"- **Market**: {security.market_id}",
            f"- **As Of**: {run.as_of}",
            f"- **Trading Currency**: {security.trading_currency}",
            f"- **Reporting Currency**: {security.reporting_currency}",
            f"- **Status**: {run.status}",
            "",
            "## 2. 主要出典 (Primary Sources)",
        ]
        
        for f in facts[:5]:
            lines.append(f"- [{f.metric}] {f.source_url} (Rank: {f.source_rank})")
            
        lines.extend([
            "",
            "## 3. データ不足・警告 (Warnings & Data Gaps)",
        ])
        if run.warnings:
            for w in run.warnings:
                lines.append(f"- ⚠️ {w}")
        else:
            lines.append("- 特出点なし (None)")

        lines.extend([
            "",
            "## 4. 综合分析结论 (Integrated Analysis)",
        ])
        for a in agent_outputs:
            lines.append(f"### Agent: {a['agent_id']} (Score: {a['score']}, Confidence: {a['confidence']})")
            lines.append(f"**Conclusion**: {a['conclusion']}")
            for claim in a.get("claims", []):
                lines.append(f"- Claim: {claim}")
            lines.append("")

        lines.extend([
            "## 5. 免责声明 (Disclaimer)",
            "本报告仅供学术及研究参考，不构成任何投资建议。"
        ])

        return "\n".join(lines)

class MultiMarketReportAuditor:
    @staticmethod
    def audit_report(report_path: Path) -> Dict[str, Any]:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        issues = []
        if re.search(r"EDINET_API_KEY\s*=\s*[A-Za-z0-9_-]{10,}", content) or "Bearer " in content or "[REDACTED_API_KEY]" in content:
            issues.append("Secret leaked or incomplete redaction in report!")
        
        home_str = os.path.expanduser("~")
        if home_str in content and home_str != "~":
            issues.append("Local user absolute path leaked in report!")

        return {
            "report_path": str(report_path),
            "is_valid": len(issues) == 0,
            "issues": issues
        }

