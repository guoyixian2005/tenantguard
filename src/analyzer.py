"""
Core Analysis Orchestrator for TenantGuard AI.
Integrates PDF Forensics, Regex Text Parser, and Statutory Tax Verifier.
"""
import re
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from .models import PaystubData, VerificationResult, RiskSeverity, RedFlag
from .pdf_forensics import PDFForensics
from .tax_verifier import TaxVerifier


class TenantGuardAnalyzer:
    def __init__(self):
        pass

    def analyze_bytes(self, file_bytes: bytes, filename: str = "document.pdf") -> VerificationResult:
        # Step 1: Run PDF Forensics
        forensics = PDFForensics(file_bytes)
        forensic_flags, forensic_clean, meta_summary, extracted_text = forensics.analyze()

        # Step 2: Parse Financial Data from extracted text
        parsed_data = self._parse_paystub_text(extracted_text)

        # Step 3: Run Statutory Tax & Math Verification
        tax_verifier = TaxVerifier(parsed_data)
        tax_flags, tax_clean = tax_verifier.verify()

        # Combine Flags and Clean Signals
        all_flags = forensic_flags + tax_flags
        all_clean = forensic_clean + tax_clean

        # Step 4: Calculate 0-100 Risk Score
        risk_score, risk_level, recommendation = self._compute_risk_score(all_flags)

        return VerificationResult(
            filename=filename,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            risk_score=risk_score,
            risk_level=risk_level,
            red_flags=all_flags,
            clean_signals=all_clean,
            parsed_data=parsed_data,
            metadata_summary=meta_summary,
            recommendation=recommendation
        )

    def analyze_structured_data(self, data: PaystubData, filename: str = "manual_entry.json") -> VerificationResult:
        """Analyze directly from structured payload or test fixtures."""
        tax_verifier = TaxVerifier(data)
        tax_flags, tax_clean = tax_verifier.verify()

        risk_score, risk_level, recommendation = self._compute_risk_score(tax_flags)

        return VerificationResult(
            filename=filename,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            risk_score=risk_score,
            risk_level=risk_level,
            red_flags=tax_flags,
            clean_signals=tax_clean,
            parsed_data=data,
            metadata_summary={"mode": "structured_data_verification"},
            recommendation=recommendation
        )

    def _parse_paystub_text(self, text: str) -> PaystubData:
        """Extract financial figures from unstructured paystub text using robust regex."""
        data = PaystubData(raw_text=text)

        def extract_amount(patterns) -> Optional[float]:
            for pat in patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    raw_val = m.group(1).replace(",", "").strip()
                    try:
                        return float(raw_val)
                    except ValueError:
                        pass
            return None

        # Gross Pay patterns
        data.gross_pay = extract_amount([
            r"Gross\s+Pay[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Total\s+Gross[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Gross\s+Earnings[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Gross\s+Wages[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Current\s+Gross[:\s]+\$?([0-9,]+\.[0-9]{2})"
        ])

        # Net Pay patterns
        data.net_pay = extract_amount([
            r"Net\s+Pay[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Take\s+Home\s+Pay[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Total\s+Net[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Net\s+Earnings[:\s]+\$?([0-9,]+\.[0-9]{2})"
        ])

        # Total Deductions
        data.total_deductions = extract_amount([
            r"Total\s+Deductions[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Deductions\s+Total[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Total\s+Taxes[:\s]+\$?([0-9,]+\.[0-9]{2})"
        ])

        # Social Security (FICA-OASDI)
        data.social_security_tax = extract_amount([
            r"(?:Social\s+Security|FICA[\s-]+SS|OASDI|Soc\s+Sec)[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"SS\s+Tax[:\s]+\$?([0-9,]+\.[0-9]{2})"
        ])

        # Medicare (FICA-HI)
        data.medicare_tax = extract_amount([
            r"(?:Medicare|FICA[\s-]+Med|FICA[\s-]+HI)[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Med\s+Tax[:\s]+\$?([0-9,]+\.[0-9]{2})"
        ])

        # Federal Income Tax
        data.federal_income_tax = extract_amount([
            r"(?:Federal\s+Withholding|Fed\s+Income\s+Tax|FIT|Federal\s+Tax)[:\s]+\$?([0-9,]+\.[0-9]{2})"
        ])

        # State Income Tax
        data.state_income_tax = extract_amount([
            r"(?:State\s+Withholding|State\s+Income\s+Tax|SIT|State\s+Tax)[:\s]+\$?([0-9,]+\.[0-9]{2})"
        ])

        # YTD Gross
        data.ytd_gross = extract_amount([
            r"YTD\s+Gross[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"Gross\s+YTD[:\s]+\$?([0-9,]+\.[0-9]{2})",
            r"YTD\s+Earnings[:\s]+\$?([0-9,]+\.[0-9]{2})"
        ])

        return data

    def _compute_risk_score(self, red_flags: list) -> Tuple[int, str, str]:
        """
        Calculates 0-100 Fraud Risk Score:
        - CRITICAL: +40 pts each
        - HIGH: +25 pts each
        - MEDIUM: +12 pts each
        - LOW: +5 pts each
        """
        score = 0
        critical_count = 0
        high_count = 0

        for flag in red_flags:
            if flag.severity == RiskSeverity.CRITICAL:
                score += 40
                critical_count += 1
            elif flag.severity == RiskSeverity.HIGH:
                score += 25
                high_count += 1
            elif flag.severity == RiskSeverity.MEDIUM:
                score += 12
            elif flag.severity == RiskSeverity.LOW:
                score += 5

        # Cap score at 100
        score = min(score, 100)

        # Classify Risk Level
        if score >= 50 or critical_count >= 1:
            risk_level = "HIGH RISK"
            recommendation = (
                "DO NOT APPROVE based solely on this document. Multiple severe red flags or "
                "mathematical impossibilities were detected. Demand original W-2, 1099, or "
                "direct bank-login verification (Plaid/Flinks)."
            )
        elif score >= 20:
            risk_level = "MODERATE RISK"
            recommendation = (
                "PROCEED WITH CAUTION. Document contains anomalies that deviate from standard "
                "payroll accounting or metadata conventions. Request applicant's most recent "
                "2 months of un-redacted official bank statements."
            )
        else:
            risk_level = "LOW RISK"
            recommendation = (
                "DOCUMENT VERIFIED. No material discrepancies, forbidden software footprints, or "
                "arithmetic inconsistencies were detected. Passes standard statutory thresholds."
            )

        return score, risk_level, recommendation
