"""
Report Generator for TenantGuard AI.
Renders Terminal / Markdown / JSON audit reports for landlords.
"""
import json
from typing import Dict, Any
from .models import VerificationResult


class ReportGenerator:
    @staticmethod
    def to_dict(res: VerificationResult) -> Dict[str, Any]:
        return {
            "filename": res.filename,
            "timestamp": res.timestamp,
            "risk_score": res.risk_score,
            "risk_level": res.risk_level,
            "recommendation": res.recommendation,
            "red_flags_count": len(res.red_flags),
            "red_flags": [
                {
                    "code": f.code,
                    "severity": f.severity.value,
                    "category": f.category,
                    "title": f.title,
                    "description": f.description,
                    "evidence": f.evidence,
                    "suggested_action": f.suggested_action
                }
                for f in res.red_flags
            ],
            "clean_signals": res.clean_signals,
            "metadata_summary": res.metadata_summary
        }

    @staticmethod
    def to_json(res: VerificationResult, indent: int = 2) -> str:
        return json.dumps(ReportGenerator.to_dict(res), indent=indent, ensure_ascii=False)

    @staticmethod
    def to_markdown(res: VerificationResult) -> str:
        badge_color = "🔴" if res.risk_level == "HIGH RISK" else ("🟡" if res.risk_level == "MODERATE RISK" else "🟢")
        
        md = []
        md.append(f"# TenantGuard AI — Income Verification Report")
        md.append(f"**Target File**: `{res.filename}` | **Generated**: {res.timestamp}\n")
        md.append(f"## {badge_color} Overall Risk Verdict: {res.risk_level} (Score: {res.risk_score}/100)\n")
        md.append(f"> **Landlord Recommendation**:\n> {res.recommendation}\n")
        
        md.append("---")
        md.append("### 🚩 Detected Red Flags & Discrepancies")
        if not res.red_flags:
            md.append("*(No red flags detected. All parameters fall within normal ranges.)*\n")
        else:
            for i, flag in enumerate(res.red_flags, 1):
                md.append(f"#### {i}. [{flag.severity.value}] {flag.title}")
                md.append(f"- **Category**: {flag.category}")
                md.append(f"- **Finding**: {flag.description}")
                if flag.suggested_action:
                    md.append(f"- **Action**: *{flag.suggested_action}*")
                md.append("")

        md.append("---")
        md.append("### ✅ Verified Clean Signals")
        for sig in res.clean_signals:
            md.append(f"- [x] {sig}")
        md.append("")

        md.append("---")
        md.append("### ⚖️ Legal Disclaimer")
        md.append(
            "*TenantGuard AI provides automated document integrity and mathematical analysis for diligence purposes only. "
            "It does not constitute a consumer credit report under the Fair Credit Reporting Act (FCRA). Landlords remain "
            "solely responsible for evaluating applicants in compliance with federal, state, and local fair housing laws.*"
        )
        return "\n".join(md)

    @staticmethod
    def print_terminal(res: VerificationResult):
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        CYAN = "\033[96m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        color = RED if res.risk_level == "HIGH RISK" else (YELLOW if res.risk_level == "MODERATE RISK" else GREEN)
        
        print("\n" + "=" * 70)
        print(f"{BOLD}TENANTGUARD AI — DOCUMENT VERIFICATION AUDIT{RESET}")
        print("=" * 70)
        print(f"File: {res.filename} | Time: {res.timestamp}")
        print(f"Verdict: {color}{BOLD}{res.risk_level} [Risk Score: {res.risk_score}/100]{RESET}")
        print("-" * 70)
        print(f"{BOLD}Recommendation:{RESET}\n{res.recommendation}")
        print("-" * 70)
        
        if res.red_flags:
            print(f"{RED}{BOLD}RED FLAGS DETECTED ({len(res.red_flags)}):{RESET}")
            for i, f in enumerate(res.red_flags, 1):
                sev_color = RED if f.severity.value in ["CRITICAL", "HIGH"] else YELLOW
                print(f"  {i}. [{sev_color}{f.severity.value}{RESET}] {BOLD}{f.title}{RESET}")
                print(f"     Details: {f.description}")
                if f.suggested_action:
                    print(f"     Action : {CYAN}{f.suggested_action}{RESET}")
        else:
            print(f"{GREEN}✓ No fraud red flags detected.{RESET}")

        print("-" * 70)
        print(f"{GREEN}{BOLD}CLEAN SIGNALS ({len(res.clean_signals)}):{RESET}")
        for sig in res.clean_signals:
            print(f"  ✓ {sig}")
        print("=" * 70 + "\n")
